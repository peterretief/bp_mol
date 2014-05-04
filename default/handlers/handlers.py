# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'libs')
# standard library imports
import logging
# related third party imports
import webapp2

from google.appengine.ext import db

from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from webapp2_extras.i18n import gettext as _
from bp_includes.external import httpagentparser
# local application/library specific imports
from bp_includes.lib.basehandler import BaseHandler
from bp_includes.lib.decorators import user_required
from bp_includes.lib import captcha, utils, xlrd
import bp_includes.models as models_boilerplate
import forms as forms

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.blobstore import BlobReader


import urllib
import codecs

from datetime import datetime
import time

from collections import defaultdict

import models

#constants
#start of data
C_START = 32

#TODO fetch remote files 

class ViewFileHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)


class VesselListHandler(BaseHandler):
  def get(self, vessel):
	dictd = lambda: defaultdict(dictd)
	file_data = dictd()
	wb = ""
	sh = ""
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(vessel).read())
	for s in range(0,wb.nsheets):   
		sh = wb.sheet_by_index(s)
		file_data["filename"] = blobstore.BlobInfo.get(vessel).filename
		file_data["key"] = blobstore.BlobInfo.get(vessel).key()
		file_data["vesselname"][s] = sh.cell_value(8,1)
		file_data["sheetname"][s] =  sh.name
      		file_data["voyage"][s] =  sh.cell_value(9,1)
      		file_data["product"][s] =  sh.cell_value(10,1)
     		file_data["port"][s] = sh.cell_value(11,0)
		if not (sh.cell_value(11,1) == ""):
			file_data["date_of_loading"][s] =  (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(11,1), 0))[0:6])).strftime('%d-%m-%Y')
		if not (sh.cell_value(12,1) == ""):
			file_data["date_of_loading2"][s] =  (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(12,1), 0))[0:6])).strftime('%d-%m-%Y')
 
    	params = {
	    "file_data": file_data,
	    "vesselnumber": "vesselnumber",

    	}
   	return self.render_template('vessellist.html', **params)


class ContainerListHandler(BaseHandler):
  def get(self, container, sheet_name):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(container).read())
	sh = wb.sheet_by_name(sheet_name)        
        to_container = (sh.nrows-C_START)/2
        con_range = range(C_START, C_START+(to_container*2),2)

	for i in range(0, sh.nrows):
	    try:
		y["container"][i] =  sh.cell_value(con_range[i],0)
		y["container"]["ppecbcode"][i] = sh.cell_value(con_range[i],1)
    		y["container"]["vent"][i] =  sh.cell_value(con_range[i],2)
		y["container"]["setpoint"][i] = sh.cell_value(con_range[i],3)

	    except:
        	print "Maximum recursion depth exceeded."

 
    	params = {
	    "y": y,

    	}
   	return self.render_template('containerlist.html', **params)


class FileListHandler(BaseHandler):
  def get(self):
	get_data = blobstore.BlobInfo.all()
	dictd = lambda: defaultdict(dictd)
	list_data = dictd()
	for s in range(0,get_data.count()):
		list_data["filename"][s] = get_data[s].filename
		list_data["key"][s] = get_data[s].key()
		list_data["count"][s] = get_data.count()
	
    	params = {
	    "list_data": list_data,

    	}
   	return self.render_template('filelist.html', **params)


class ResultsHandler(BaseHandler):
  def get(self):
#TODO set requests
      #  from_container = 0
	
        to_container = 3
	from_container = self.request.get('from_container')

    		#query = Suggestion.query().order(-Suggestion.when)
    	if from_container:
		from_container = self.request.get('from_container')
	else:
        	from_container = 0
#TODO select key from request get
	blob_key="-3cfYPZI8Rx1VLEkofj-DQ=="
	blob_reader = blobstore.BlobReader(blob_key)

	wb = xlrd.open_workbook(file_contents=blob_reader.read())
	#sh = wb.sheet_by_index(0)
#TODO add cape town durban etc
        sh = wb.sheet_by_name("FDEC")

        con_range = range(C_START, C_START+(to_container*2),2)
     
	dictd = lambda: defaultdict(dictd)
	y = dictd()
        for i in range(from_container,to_container):
		y["voyage"] =  sh.cell_value(9,1)
                y["date_of_loading"] =  (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(11,1), 0))[0:6])).strftime('%d-%m-%Y')
                y["product"] =  sh.cell_value(10,1)
                y["port"] = sh.cell_value(11,0)
                y["vesselname"] = sh.cell_value(8,1)
    		y["container"][i] =  sh.cell_value(con_range[i],0)
		y["container"]["ppecbcode"][i] = sh.cell_value(con_range[i],1)
    		y["container"]["vent"][i] =  sh.cell_value(con_range[i],2)
		y["container"]["setpoint"][i] = sh.cell_value(con_range[i],3)
		for j in range(0,4):
			y["container"]["DAtemp"][i][j] = sh.cell_value(con_range[i],5+j)
			y["container"]["RAtemp"][i][j] = sh.cell_value(con_range[i]+1,5+j)			
          		y["container"]["date_"][i][j] = (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(29, 5 + j), 0))[0:6])).strftime('%d-%m-%Y')
			y["container"]["day"][i][j] = str(j+1)+" Day "	


    	params = {
	    "y": y,
	    "from_container": from_container,
	    "to_container": to_container,

    	}


#   	return self.render_template('results.html', **params)
   	return self.render_template('shiplist.html', **params)



class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    #resource = str(urllib.unquote(resource))
    upload_files = self.get_uploads('file') 
    blob_info = upload_files[0]
    blobfilendb = models.UserUpload_ndb(blob=blob_info.key())
    blobfilendb.put()

    self.redirect('/secure')		


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    params = {
        "blob_info": blob_info
    }

    return self.render_template('results.html', **params)

 
class ContactHandler(BaseHandler):
    """
    Handler for Contact Form
    """

    def get(self):
        """ Returns a simple HTML for contact form """
        if self.user:
            user_info = models_boilerplate.User.get_by_id(long(self.user_id))
            if user_info.name or user_info.last_name:
                self.form.name.data = user_info.name + " " + user_info.last_name
            if user_info.email:
                self.form.email.data = user_info.email
        params = {
            "exception": self.request.get('exception')
        }

        return self.render_template('contact.html', **params)

    def post(self):
        """ validate contact form """

        if not self.form.validate():
            return self.get()
        remoteip = self.request.remote_addr
        user_agent = self.request.user_agent
        exception = self.request.POST.get('exception')
        name = self.form.name.data.strip()
        email = self.form.email.data.lower()
        message = self.form.message.data.strip()
        template_val = {}

        try:
            # parsing user_agent and getting which os key to use
            # windows uses 'os' while other os use 'flavor'
            ua = httpagentparser.detect(user_agent)
            _os = ua.has_key('flavor') and 'flavor' or 'os'

            operating_system = str(ua[_os]['name']) if "name" in ua[_os] else "-"
            if 'version' in ua[_os]:
                operating_system += ' ' + str(ua[_os]['version'])
            if 'dist' in ua:
                operating_system += ' ' + str(ua['dist'])

            browser = str(ua['browser']['name']) if 'browser' in ua else "-"
            browser_version = str(ua['browser']['version']) if 'browser' in ua else "-"

            template_val = {
                "name": name,
                "email": email,
                "browser": browser,
                "browser_version": browser_version,
                "operating_system": operating_system,
                "ip": remoteip,
                "message": message
            }
        except Exception as e:
            logging.error("error getting user agent info: %s" % e)

        try:
            subject = _("Contact") + " " + self.app.config.get('app_name')
            # exceptions for error pages that redirect to contact
            if exception != "":
                subject = "{} (Exception error: {})".format(subject, exception)

            body_path = "emails/contact.txt"
            body = self.jinja2.render_template(body_path, **template_val)

            email_url = self.uri_for('taskqueue-send-email')
            taskqueue.add(url=email_url, params={
                'to': self.app.config.get('contact_recipient'),
                'subject': subject,
                'body': body,
                'sender': self.app.config.get('contact_sender'),
            })

            message = _('Your message was sent successfully.')
            self.add_message(message, 'success')
            return self.redirect_to('contact')

        except (AttributeError, KeyError), e:
            logging.error('Error sending contact form: %s' % e)
            message = _('Error sending the message. Please try again later.')
            self.add_message(message, 'error')
            return self.redirect_to('contact')

    @webapp2.cached_property
    def form(self):
        return forms.ContactForm(self)


class SecureRequestHandler(BaseHandler):
    """
    Only accessible to users that are logged in
    """
    @user_required
    def get(self, **kwargs):
        user_session = self.user
        user_session_object = self.auth.store.get_session(self.request)
        user_info = models_boilerplate.User.get_by_id(long(self.user_id))
        user_info_object = self.auth.store.user_model.get_by_auth_token(
            user_session['user_id'], user_session['token'])

        try:
            upload_url = blobstore.create_upload_url('/upload')
            params = {
		"upload_url": upload_url,
		"more_stuff": dir(xlrd),
                "user_session": user_session,
                "user_session_object": user_session_object,
                "user_info": user_info,
                "user_info_object": user_info_object,
                "userinfo_logout-url": self.auth_config['logout_url'],
            }
            return self.render_template('secure_zone.html', **params)
        except (AttributeError, KeyError), e:
            return "Secure zone error:" + " %s." % e


class DeleteAccountHandler(BaseHandler):

    @user_required
    def get(self, **kwargs):
        chtml = captcha.displayhtml(
            public_key=self.app.config.get('captcha_public_key'),
            use_ssl=(self.request.scheme == 'https'),
            error=None)
        if self.app.config.get('captcha_public_key') == "PUT_YOUR_RECAPCHA_PUBLIC_KEY_HERE" or \
                        self.app.config.get('captcha_private_key') == "PUT_YOUR_RECAPCHA_PUBLIC_KEY_HERE":
            chtml = '<div class="alert alert-error"><strong>Error</strong>: You have to ' \
                    '<a href="http://www.google.com/recaptcha/whyrecaptcha" target="_blank">sign up ' \
                    'for API keys</a> in order to use reCAPTCHA.</div>' \
                    '<input type="hidden" name="recaptcha_challenge_field" value="manual_challenge" />' \
                    '<input type="hidden" name="recaptcha_response_field" value="manual_challenge" />'
        params = {
            'captchahtml': chtml,
        }
        return self.render_template('delete_account.html', **params)

    def post(self, **kwargs):
        challenge = self.request.POST.get('recaptcha_challenge_field')
        response = self.request.POST.get('recaptcha_response_field')
        remote_ip = self.request.remote_addr

        cResponse = captcha.submit(
            challenge,
            response,
            self.app.config.get('captcha_private_key'),
            remote_ip)

        if cResponse.is_valid:
            # captcha was valid... carry on..nothing to see here
            pass
        else:
            _message = _('Wrong image verification code. Please try again.')
            self.add_message(_message, 'error')
            return self.redirect_to('delete-account')

        if not self.form.validate() and False:
            return self.get()
        password = self.form.password.data.strip()

        try:

            user_info = models_boilerplate.User.get_by_id(long(self.user_id))
            auth_id = "own:%s" % user_info.username
            password = utils.hashing(password, self.app.config.get('salt'))

            try:
                # authenticate user by its password
                user = models_boilerplate.User.get_by_auth_password(auth_id, password)
                if user:
                    # Delete Social Login
                    for social in models_boilerplate.SocialUser.get_by_user(user_info.key):
                        social.key.delete()

                    user_info.key.delete()

                    ndb.Key("Unique", "User.username:%s" % user.username).delete_async()
                    ndb.Key("Unique", "User.auth_id:own:%s" % user.username).delete_async()
                    ndb.Key("Unique", "User.email:%s" % user.email).delete_async()

                    #TODO: Delete UserToken objects

                    self.auth.unset_session()

                    # display successful message
                    msg = _("The account has been successfully deleted.")
                    self.add_message(msg, 'success')
                    return self.redirect_to('home')


            except (InvalidAuthIdError, InvalidPasswordError), e:
                # Returns error message to self.response.write in
                # the BaseHandler.dispatcher
                message = _("Incorrect password! Please enter your current password to change your account settings.")
                self.add_message(message, 'error')
            return self.redirect_to('delete-account')

        except (AttributeError, TypeError), e:
            login_error_message = _('Your session has expired.')
            self.add_message(login_error_message, 'error')
            self.redirect_to('login')

    @webapp2.cached_property
    def form(self):
        return forms.DeleteAccountForm(self)

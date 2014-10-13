import sys
sys.path.insert(0, 'libs')
# standard library imports
import logging
# related third party imports
import webapp2

import excelreader as exc
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

from decimal import *

from google.appengine.api import search

def validate(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def CreateDocument(text, date_,num,sheet, row, col ):
    return search.Document(
        fields=[search.TextField(name='text', value=text),
                search.DateField(name='date_', value=date_.date()),
                search.NumberField(name='num', value=num),
                search.TextField(name='sheet', value=sheet),
                search.NumberField(name='row', value=row),
                search.NumberField(name='col', value=col),
                search.DateField(name='date', value=datetime.now().date())])

def logIndexes():
	for index in search.get_indexes(fetch_schema=True):
    		logging.info("index %s", index.name)
    		logging.info("schema: %s", index.schema)


def delete_all_in_index(index_name, namespace):
    doc_index = search.Index(name=index_name, namespace=namespace)

    # looping because get_range by default returns up to 100 documents at a time
    while True:
        # Get a list of documents populating only the doc_id field and extract the ids.
        document_ids = [document.doc_id
                        for document in doc_index.get_range(ids_only=True)]
        if not document_ids:
            break
        # Delete the documents for the given ids from the Index.
        doc_index.delete(document_ids)

#++++++++++++++++++++++++global methods+++++++++++++++++++++++++++

class TestHandler(BaseHandler):
	def get(self):
		y="test"



		params = {
		 		"y": y,
	    		}
		return self.render_template("testman.html", **params)



                               
"""
class UpdateLinks(BaseHandler):
	def get(self):
		query = models.Manifest.query().order(-models.Manifest.created)
		data = query.fetch(query.count())
		for d in data:
			manifest_key = d.key
			indexname = "PL08AfDu0UYiouteo6EMNA=="
			s = updateContainerStatus(indexname, manifest_key)
		params = {
	  		"y": s,
    			}
		return self.render_template("testman.html", **params)

"""

def getWorkbook(filekey):
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
	return wb

def SaveManifestDetail(manifest_key, y, count, vessel_name, voyage, port):
	man_detail = models.ManifestDetail()
	man_detail.manifest = manifest_key
	man_detail.booking_number = str(y["readings"][count][0])
	man_detail.sfx = str(y["readings"][count][1])
	man_detail.container_number = str(y["readings"][count][2])
	man_detail.commodity = str(y["readings"][count][3])
	man_detail.disch_port = str(y["readings"][count][4])
	man_detail.temp = str(y["myfloat"][count])
	man_detail.code = str(y["readings"][count][6])
	man_detail.vents = str(y["readings"][count][7])
	man_detail.equipment_type = str(y["readings"][count][8])
	man_detail.empty_dsp = str(y["readings"][count][9])
	man_detail.count = count-4
	man_detail.put()

def makeManifestPickle(wb):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	for i, x in enumerate(wb.sheets()):
    		header_cells = x.row(0)
    		sh = wb.sheet_by_index(i)
    		num_rows = x.nrows - 1
    		curr_row = 0
    		mid_row = 0
    		header = [each.value for each in header_cells]
    		if 'MOL REEFER MANIFEST' in header:
			y["header"] = "manifest"
	    		while curr_row < num_rows:
	        		curr_row += 1

	        		row = [int(each.value)
	               		if isinstance(each.value, float)
	               		else each.value
	               		for each in sh.row(curr_row)]

	        		value_dict = dict(zip(header, row))
	        		value_dict['title'] = x.name
	        		if 'Vessel:' in row:
	           			y["voyage"] = row[row.index('Voyage:')+1]
	           			y["vessel"] = row[row.index('Vessel:')+1]
	           			y["port"] = row[row.index('Port:')+1]
	        		if 'BOOKING NO' in row:
	           			y["labels"] = row

		        	y["readings"][curr_row] = row
				y["myfloat"][curr_row] = sh.cell_value(curr_row,5)
				y["numrows"] = num_rows+1
		else:
			num_rows = sh.nrows - 1
			num_cells = sh.ncols - 1
			curr_row = -1
			while curr_row < num_rows:
				curr_row += 1
				row = sh.row(curr_row)

	return y

class ManifestDetailHandler(BaseHandler):
	def get(self, keyval):
		mykey = ndb.Key(models.Manifest, keyval)
		l = models.Manifest().find_manifest_details(long(mykey.id()))

		params = {
			"l": l,
    			}
		return self.render_template("manifest_detail.html", **params)

class VesselHandler(BaseHandler):
	def get(self, keyval):
		mykey = ndb.Key(models.Vessel, long(keyval))
		y = models.Vessel.query(models.Vessel.key==mykey).get()
		params = {
			"y": y,
    			}
		return self.render_template("vesselview.html", **params)


PAGE_SIZE=20

class ManifestHandler(BaseHandler):
    def get(self):
        
       cursor = None
       bookmark = self.request.get('bookmark')
       search = (self.request.get('search')).strip()
       if bookmark:
           cursor = ndb.Cursor.from_websafe_string(bookmark)
       if search:
#ndb.AND(Video.tags == tag, Video.key != video.key)
		query = models.Manifest.query(ndb.OR(models.Manifest.voyage == search, models.Manifest.port == search, models.Manifest.vessel_name == search)).order(-models.Manifest._key)
       else:
       		query = models.Manifest.query().order(-models.Manifest.created)
       
       data, next_cursor, more = query.fetch_page(PAGE_SIZE, start_cursor=cursor)

       next_bookmark = None
       if more:
            next_bookmark = next_cursor.to_websafe_string()

       is_prev = self.request.get('prev', False)
       if is_prev:
        query = q_reverse
        cursor = cursor.reversed()
       else:
        query = next_bookmark

        if is_prev:
            prev_bookmark = cursor.reversed().to_websafe_string() if more else None
            next_bookmark = bookmark
        else:
            prev_bookmark = bookmark
            next_bookmark = None
            if more:
                next_bookmark = next_cursor.to_websafe_string()

        params = {
            "data": data,
            "bookmark": next_bookmark,
            "prev_bookmark": prev_bookmark,
                }
        return self.render_template("manifest.html", **params)


#++++manifest data+++++++++++++++++++++

def addVesselData(wb, filename):
	dictd = lambda: defaultdict(dictd)
	data = dictd()
	for i, x in enumerate(wb.sheets()):
		header_cells = x.row(0)
    		sh = wb.sheet_by_index(i)
    		num_rows = x.nrows - 1
                num_cells = sh.ncols - 1
    		curr_row = 0
    		mid_row = 0
    		header = [each.value for each in header_cells]
 	       # delete_all_in_index(filename)
    		while curr_row < num_rows:
	       		curr_row += 1
        		row = [int(each.value)
               		if isinstance(each.value, float)
               		else each.value
               		for each in sh.row(curr_row)]
               		value_dict = dict(zip(header, row))
        		value_dict['title'] = x.name
                        curr_cell = -1
	                while curr_cell < num_cells:
		            curr_cell += 1
			# Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
		            cell_type = sh.cell_type(curr_row, curr_cell)
                            cell_value = sh.cell_value(curr_row, curr_cell)
                            if (cell_type==1):
				search.Index(name=filename, namespace="text").put(CreateDocument(cell_value.strip() ,datetime.now(),0 ,sh.name, int(curr_row), int(curr_cell)))
                            if (cell_type==3):
				try:
					a1_as_datetime = datetime(*xlrd.xldate_as_tuple(cell_value, 0)[0:6])
					search.Index(name=filename, namespace="date").put(CreateDocument("", a1_as_datetime,0 ,sh.name,int(curr_row), int(curr_cell)))
				except:
					pass #if i cant read it i cant use it
                            if (cell_type==2):
				search.Index(name=filename, namespace="number").put(CreateDocument("",datetime.now(),int(cell_value),sh.name, int(curr_row), int(curr_cell)))

	return True

def updateContainerStatus(indexname):
	query1 = models.Manifest.query()
	data = query1.fetch(query1.count())
	for d in data:
		query2 = models.ManifestDetail.query(models.ManifestDetail.manifest == d.key)
		detail = query2.fetch(query2.count())
		for e in detail:
			a = index_search(e.container_number, indexname)
			if (a):
				e.container_status=True
				e.put()

	return a

def index_search(query_string,indexname):
	index = search.Index(name=indexname, namespace="text")
	try:
	    results = index.search(query_string)
	    # Iterate over the documents in the results
	    for scored_document in results:
		return results, index.name
	       # handle results
	except search.Error:
		logging.exception('Search failed')

def matchManifest(indexfile):
	query = models.Manifest.query()
	data = query.fetch(query.count())
	index = search.Index(name=indexfile, namespace="text")
	for s in data:
		query_string = "col < 4 AND text="+s.voyage
        	results = index.search(query_string)
	        for scored_document in results:
			s.voyage_link=indexfile
			s.put()
	return s


class SaveManifestHandler1(BaseHandler):
	def get(self, keyval):
		resource = str(urllib.unquote(keyval))
    		blob_info = blobstore.BlobInfo.get(resource)

		wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(blob_info.key()).read())
		sheet = wb.sheet_by_index(0)
		data = [sheet.cell_value(0, col) for col in range(sheet.ncols)]
		if not ("MOL REEFER MANIFEST" in data):
			iname = str(blob_info.filename.replace(" ", ""))
			delete_all_in_index(iname, "text")
			delete_all_in_index(iname, "date")
			delete_all_in_index(iname, "number")
                	y = addVesselData(wb, iname)
			s = matchManifest(iname)
			updateContainerStatus(iname)
			
		else:
			y = makeManifestPickle(wb)
			if not (models.Manifest().find_duplicate(y["vessel"],y["voyage"],y["port"])):
				man = models.Manifest()
				man.blob = blob_info.key()
				man.vessel_name = y["vessel"]
				man.voyage = y["voyage"]
				man.port = y["port"]
				man.put()
				for c in range(5, y["numrows"]):
					SaveManifestDetail(man.key, y, c, man.vessel_name, man.voyage, man.port)
			else:
				y="Manifest added already"

		params = {
	 			"y": y,
    			}
		return self.render_template("testman.html", **params)



#end manifest
#++++++++++++++++++++++++++blobstore handlers++++++++++++++++++++++++++
class ViewFileHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
  def get(self, resource):
    resource = str(urllib.unquote(resource))
    blob_info = blobstore.BlobInfo.get(resource)
    self.send_blob(blob_info)



#+++++++system handlers++++++++++++++++++++++++

class UploadHandler1(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    #resource = str(urllib.unquote(resource))
    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]
#    blobfilendb = models.UserUpload_ndb(blob=blob_info.key())
#    blobfilendb.put()
 

    self.redirect('/save_manifest1/%s' % blob_info.key())

"""
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    #resource = str(urllib.unquote(resource))
    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]
    blobfilendb = models.UserUpload_ndb(blob=blob_info.key())
    blobfilendb.put()

    self.redirect('/save_manifest/')
#    self.redirect('/secure')
"""

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
            upload_url = blobstore.create_upload_url('/upload1')
            params = {
		"upload_url": upload_url,
		#"more_stuff": dir(xlrd),
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

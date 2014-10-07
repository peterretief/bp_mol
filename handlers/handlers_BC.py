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

from decimal import *

#+++++constants++++++
#start of data
C_START = 32



#++++++++++++++++++++++++global methods+++++++++++++++++++++++++++ 
def validate(date_text):
    try:
	datetime.strptime(date_text,'%d-%m-%Y')
	return 1
    except:
        return 0


def getWorkbook(filekey):
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
	return wb


def makePickle(filekey):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
	for i, x in enumerate(wb.sheets()):
    		header_cells = x.row(0)
    		sh = wb.sheet_by_index(i)
    		num_rows = x.nrows - 1
    		curr_row = 0
    		mid_row = 0
    		header = [each.value for each in header_cells]
    		if 'MOL REEFER MANIFEST' in header:
        		y["manifest"] = 'MOL REEFER MANIFEST'
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
	           			mid_row = curr_row+1
	
		        	y["acv"][curr_row] = row
				y["myfloat"][curr_row] = sh.cell_value(curr_row,5)
				y["numrows"] = num_rows+1


		else:

			y["key"] = blobstore.BlobInfo.get(filekey).key()
			y["sheetname"][i] = sh.name
			y["index"][i] = i
			y["nsheets"] = wb.nsheets
			for a in range(5, 15):
				if "VESSEL" in sh.cell_value(a,0):
	                                if (len(sh.cell_value(a,1)) > 0):
						y["vesselname"][i] = sh.cell_value(a,1)
					else:
						y["vesselname"][i] = "NA"

				if "VOYAGE" in sh.cell_value(a,0):
	                                if (len(sh.cell_value(a,1)) > 0):
						y["voyage"][i] = sh.cell_value(a,1)
						y["voyage_fixed"] = sh.cell_value(a,1)

					else:
						y["voyage"][i] = "NA"


				if "DATE of LOADING" in sh.cell_value(a,0):
					try:
						if (validate((datetime(*(xlrd.xldate_as_tuple(sh.cell_value(a, 1), 0))[0:6])).strftime('%d-%m-%Y'))):
							y["date_of_loading"][i] = (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(a, 1), 0))[0:6])).strftime('%d-%m-%Y')
					except:
						y["date_of_loading"][i] = "None"
			
	
        
			y["colour"] = "lightred"
                
			#y["bool"] = addDataFilename(y["vesselname"][i],	y["voyage_fixed"], "", i, y["date_of_loading"][i])


	return y

def addDataFilename(vesselname, voyage, blob_key, sheet, date_loading):
	try:
		newd = models.FileList()	
		newd.vessel = vesselname
		newd.voyage = voyage
#		newd.manifest = get_voyage(voyage).key
#		newd.blob = blob_key
       		newd.put()
	except:
		return 0

def readingList(filekey):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
	sh = wb.sheet_by_index(int(sheet_name))      
#find col were readings start
	for a in range(0, 10):
		y["DAT"] = sh.cell_value(row, a)
		try: 
			if "Dat/Sup" in y["DAT"]:
				start_col = a+1
		except:
			pass

        row = int(row) 
	cols = sh.ncols
	y["filename"] = blobstore.BlobInfo.get(filekey).filename
	y["product"] = sh.cell_value(10,1)

	end_col = 22

    	params = {
	    "y": y,

    	}
   	return params

#++++++++++++++++++++++++++base handlers+++++++++++++++++++++++++++++++

class TestHandler(BaseHandler):
	def get(self):
		get_data = blobstore.BlobInfo.all()
		fkey = get_data.fetch(get_data.count())
		for dat in range(0, get_data.count()):
			filekey = fkey[dat]
			wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
			y = makeVesselPickle(wb)
#			if not "manifest" in y:
#				pass
#			man = models.Vessel()
#			man.blob = filekey.key()
#				man.vessel = y["vessel"]
#				man.voyage = y["voyage"]
			#	man.port = y["port"]
#			man.put()
#				for c in range(5, y["numrows"]):
#					SaveManifestDetail(man.key, y, c)
    	
			params = {
		  		"y": y,
	    			}
		return self.render_template("testman.html", **params)

def makeVesselPickle(wb):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	for i, x in enumerate(wb.sheets()):
   		header_cells = x.row(0)
		sh = wb.sheet_by_index(i)

		num_rows = x.nrows - 1
    		curr_row = 0
		header = [each.value for each in header_cells]
    		if 'MOL REEFER MANIFEST' in header:
			y["header"] = "manifest"
		else:
	
#			y["key"] = blobstore.BlobInfo.get(filekey).key()
			y["sheetname"][i] = sh.name
			y["index"][i] = i
			y["nsheets"] = wb.nsheets
			for a in range(5, 15):
				if "VESSEL" in sh.cell_value(a,0):
	                                if (len(sh.cell_value(a,1)) > 0):
						y["vesselname"][i] = sh.cell_value(a,1)
						vessel_name = sh.cell_value(a,1)
						a_vessel = models.Vessel()
						a_vessel.vessel=sh.cell_value(a,1).strip()
						a_vessel.port=sh.name
#						a_vessel.put()
					else:
						y["vesselname"][i] = "NA"

				if "VOYAGE" in sh.cell_value(a,0):
	                                if (len(sh.cell_value(a,1)) > 0):
						y["voyage"][i] = sh.cell_value(a,1)
						a_vessel.voyage=str(sh.cell_value(a,1)).strip()
#						a_vessel.put()
#						a_vessel.manifest = models.Vessel().find_manifest(a_vessel.voyage, a_vessel.port, vessel_name).key
						a_vessel.manifest = models.Vessel().find_manifest(a_vessel.voyage, a_vessel.port).key
#						a_vessel.put()
						y["voyage_fixed"] = sh.cell_value(a,1)

					else:
						y["voyage"][i] = "NA"


				if "DATE of LOADING" in sh.cell_value(a,0):
					try:
						if (validate((datetime(*(xlrd.xldate_as_tuple(sh.cell_value(a, 1), 0))[0:6])).strftime('%d-%m-%Y'))):
							y["date_of_loading"][i] = (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(a, 1), 0))[0:6])).strftime('%d-%m-%Y')
							a_vessel.loaded=(datetime(*(xlrd.xldate_as_tuple(sh.cell_value(a, 1), 0))[0:6])).strftime('%d-%m-%Y')
							a_vessel.put()
							qry = models.Vessel.query(ancestor=a_vessel.key).get()

	#						qrey = models.Vessel.query(ancestor=qry.key).get()
							zz = models.Vessel().update_manifest(qry)


						

					except:
						y["date_of_loading"][i] = "None"
					#_vessel = Vessel().query().get()
				#	manifest = Manifest(models.Manifest.key == ).query().get()
				#	manifest.vessel = vessel.key
				#	manifest.put()


				
					#models.Vessel().update_manifest("_vessel", "_vessel.manifest")
#					_vessel.put()
			
	
        
			y["colour"] = "lightred"

	return y


def SaveManifestDetail(manifest_key, y, count):
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


def SaveVesselContainers(vessel_key, y, count):
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

	return y

#+++++



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
	#	y = models.Vessel.query(ancestor=a_vessel.key).get()

#		mykey = ndb.Key(models.Vessel, keyval)
#		y = models.Vessel(ancestor=mykey).query().get()
		params = {
			"y": y,
    			}
		return self.render_template("vesselview.html", **params)  

class ManifestHandler(BaseHandler):
	def get(self):
		data = models.Manifest.query().fetch(100)

		params = {
	  		"data": data,
    			}
		return self.render_template("manifest.html", **params)  


#++++manifest data+++++++++++++++++++++

class SaveManifestHandler(BaseHandler):
	def get(self):
		get_data = blobstore.BlobInfo.all()
		fkey = get_data.fetch(get_data.count())
		for dat in range(0, get_data.count()):
			filekey = fkey[dat]
			wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
			y = makeManifestPickle(wb)
			if (y["header"] == "manifest"):
				if not (models.Manifest().find_duplicate(y["vessel"],y["voyage"],y["port"])):
					man = models.Manifest()
					man.blob = filekey.key()
					man.vessel_name = y["vessel"]
					man.voyage = y["voyage"]
					man.port = y["port"]
					man.put()
					for c in range(5, y["numrows"]):
						SaveManifestDetail(man.key, y, c)
    	
		params = {
	  		"y": y,
    			}
		return self.render_template("testman.html", **params)    	

#end manifest

class VesselListHandler(BaseHandler):
  def get(self, filekey):
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
#	s = wb.sheet_by_index(0)
	y = makePickle(filekey)
	if (y["manifest"] == 'MOL REEFER MANIFEST'):
		filename = "manifestlist.html"		
	else:
		filename = "vessellist.html"

	params = {
	    "y": y,

    	}

#	filename = "manifestlist.html"
   	return self.render_template(filename, **params)



class ReadingsListHandler(BaseHandler):
  def get(self, filekey, sheet_name, row):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	start_col =1
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
	sh = wb.sheet_by_index(int(sheet_name))      
 	y["filekey"] = filekey 
 	y["sheet_name"] = sheet_name 
 	y["row"] = row
#whats happening with this -1?
        row = int(row) 
	cols = sh.ncols
	y["filename"] = blobstore.BlobInfo.get(filekey).filename
	y["product"] = sh.cell_value(10,1)
#find col were readings start
	for a in range(0, 10):
		y["DAT"] = sh.cell_value(row, a)
		try: 
			if "Dat/Sup" in y["DAT"]:
				start_col = a+1
		except:
			pass

#find col were readings end
	for a in range(start_col, 40):
		try:
			y["DAT"] = sh.cell_value(row, a) 
#			if "Dat/Sup" in y["DAT"]:
#				pass
		except:
			end_col = 21

#find start date
	for c in range(start_col, 20):
		if "Dat/Sup" in y["DAT"]:
			start_col = a+1

	end_col = 22

	y["start_col"] = start_col
	y["end_col"] = end_col
	y["container"] =  sh.cell_value(row,0)
	for j in range(start_col, end_col):
		y["count"][j] = j - start_col + 1
		try:
			y["DAtemp"][j] = sh.cell_value(row, j)
			foo = sh.cell_value(row, j)
			y["DAtempAM"][j], y["DAtempPM"][j] = foo.split("/") 

		except:
			y["DAtemp"][j] = "NA"

		try:
	       		y["RAtemp"][j] = sh.cell_value(row+1, j)
			foo = sh.cell_value(row+1, j)
			y["RAtempAM"][j], y["RAtempPM"][j] = foo.split("/") 
		except:
	       		y["RAtemp"][j] = "NA"
		try:                
			y["date_"][j] = (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(28, j), 0))[0:6])).strftime('%d-%m-%Y')
			y["day_"][j] = (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(28, j), 0))[0:6])).strftime('%d')
			y["month_"][j] = (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(28, j), 0))[0:6])).strftime('%m')
			y["year_"][j] = (datetime(*(xlrd.xldate_as_tuple(sh.cell_value(28, j), 0))[0:6])).strftime('%Y')
		except:       		
		 	y["date_"][j] = "Date error"

#diffences
		try:
			foo = sh.cell_value(row, j)
			amDAtemp, pmDAtemp = foo.split("/") 
			foo2 = sh.cell_value(row+1, j)
			amRAtemp, pmRAtemp = foo2.split("/") 
                      #  amt = amDAtemp - amRAtemp
			AMdiff = Decimal(amDAtemp) - Decimal(amRAtemp)
			PMdiff = Decimal(pmDAtemp) - Decimal(pmRAtemp)
	       		y["AMDiff"][j] = AMdiff     
	       		y["PMDiff"][j] = PMdiff
       			y["AMDiff"]["class"][j] = "default"
       			y["PMDiff"]["class"][j] = "default"
		        if (Decimal(AMdiff) <= Decimal(-1.0)): 
		       			y["AMDiff"]["class"][j] = "lightred"
	
		        if (Decimal(AMdiff) >= Decimal(-0.5)): 
		       			y["AMDiff"]["class"][j] = "lightgreen"

		        if (Decimal(AMdiff) >= Decimal(-0.2)): 
		       			y["AMDiff"]["class"][j] = "darkgreen"

		        if (Decimal(AMdiff) <= Decimal(-2.0)): 
		       			y["AMDiff"]["class"][j] = "darkred"


#			PMdiff

		        if (Decimal(PMdiff) <= Decimal(-1.0)): 
		       			y["PMDiff"]["class"][j] = "lightred"
	
		        if (Decimal(PMdiff) >= Decimal(-0.5)): 
		       			y["PMDiff"]["class"][j] = "lightgreen"

		        if (Decimal(PMdiff) >= Decimal(-0.2)): 
		       			y["PMDiff"]["class"][j] = "darkgreen"

		        if (Decimal(PMdiff) <= Decimal(-2.0)): 
		       			y["PMDiff"]["class"][j] = "darkred"

		except:
	       		y["AMDiff"][j] = "NA"


 
    	params = {
	    "y": y,

    	}
   	return self.render_template('readingslist.html', **params)

class ContainerListHandler(BaseHandler):
  def get(self, filekey, sheet_name):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
	sh = wb.sheet_by_index(int(sheet_name))
	row = 33
#find col were readings start
	for a in range(0, 10):
		y["DAT"] = sh.cell_value(row, a)
		try: 
			if "Dat/Sup" in y["DAT"]:
				start_col = a+1
		except:
			pass
	y["start_col"] = start_col

	for a in range(25, 32):
		if "Number" in sh.cell_value(a,0):
			y["start"] = a + 3
  	for c in range(y["start"], sh.nrows , 2):
            y["container"][c] =  sh.cell_value(c,0)
	    y["container"]["ppecbcode"][c] = sh.cell_value(c,1)
    	    y["container"]["vent"][c] =  sh.cell_value(c,2)
	    y["container"]["setpoint"][c] = sh.cell_value(c,3)
            y["rows"] =  sh.nrows
            y["filekey"] =  filekey
            y["sheet_name"] =  sheet_name
       	    for g in range(5, 10):
		try:			     	
	            foo = sh.cell_value(c, g)
		    amDAtemp, pmDAtemp = foo.split("/") 
		    foo2 = sh.cell_value(c+1, g)
		    amRAtemp, pmRAtemp = foo2.split("/") 
   		    AMdiff = Decimal(amDAtemp) - Decimal(amRAtemp)
		    PMdiff = Decimal(pmDAtemp) - Decimal(pmRAtemp)
	       	    y["AMDiff"][g] = AMdiff     
	       	    y["PMDiff"][g] = PMdiff
       		    y["AMDiff"]["class"][g] = "default"
       		    y["PMDiff"]["class"][g] = "default"
 	            if (Decimal(AMdiff) >= Decimal(-0.2)): 
		    	y["AMDiff"]["class"][c][g] = "darkgreen"
#			y["colour"][c] = "darkgreen"
	            if (Decimal(AMdiff) >= Decimal(-0.5)): 
		    	y["AMDiff"]["class"][c][g] = "lightgreen"
#			y["colour"][c] = "lightgreen"
		    if (Decimal(AMdiff) <= Decimal(-1.0)): 
		    	y["AMDiff"]["class"][c][g] = "lightred"
			y["colour"][c] = "lightred"
  	            if (Decimal(AMdiff) <= Decimal(-2.0)): 
		    	y["AMDiff"]["class"][c][g] = "darkred"
			y["colour"][c] = "darkred"
		except:
			pass
	
 
    	params = {
	    "y": y,

    	}
   	return self.render_template('containerlist.html', **params)

class getBlobInfo():
	pass

class FileListHandler(BaseHandler):
  def get(self):
	get_data = blobstore.BlobInfo.all()
	dictd = lambda: defaultdict(dictd)
	list_data = dictd()
#	f = 0
	for f in range(0, get_data.count()):
	    list_data["filename"][f] = get_data[f].filename
	    list_data["key"][f] = get_data[f].key()
	    list_data["count"] = get_data.count()
	
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


   	return self.render_template('shiplist.html', **params)

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

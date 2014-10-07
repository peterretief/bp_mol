
import sys
#sys.path.append('/home/peter/google_appengine/')
sys.path.append('/home/peter/google_appengine/')
import google
from datetime import datetime
import time
import xlrd

from collections import defaultdict

from decimal import *

#from google.appengine.api import search

#from google import appengine.api.search

#from google.appengine.api import search
import search

def NewDocument(f_1):
    # Let the search service supply the document id.
    return search.Document(
        fields=[search.TextField(name="f_1", value=f_1),
                search.DateField(name="updated", value=datetime.now().date())])



def getWorkbook(filekey):
	wb = xlrd.open_workbook(filekey)
	return wb

def testme():
	print "Hello I am here"

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


def makeVesselPickle(wb):
	dictd = lambda: defaultdict(dictd)
	y = dictd()
	for i, x in enumerate(wb.sheets()):
   		header_cells = x.row(0)
		sh = wb.sheet_by_index(i)

		num_rows = x.nrows - 1
    		curr_row = 0
		header = [each.value for each in header_cells]
    		y["sheetname"][i] = sh.name
		y["index"][i] = i
		y["nsheets"] = wb.nsheets

		while curr_row < num_rows:
	        	curr_row += 1
			row = [int(each.value)
	               		if isinstance(each.value, float)
	               		else each.value
	               		for each in sh.row(curr_row)]

        		value_dict = dict(zip(header, row))
        		value_dict['title'] = x.name
			y["value_dict"][curr_row] = row


			if "VOYAGE :" in row:
				y["aaa"][curr_row][i] = row
	    


	return y


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




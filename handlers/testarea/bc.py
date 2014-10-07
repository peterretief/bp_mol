from google.appengine.api import search
from datetime import datetime
from bp_includes.lib import captcha, utils, xlrd
from google.appengine.ext import blobstore

_INDEX_NAME = 'ship_report'

def getWorkbook(filekey):
	wb = xlrd.open_workbook(file_contents=blobstore.BlobReader(filekey).read())
	return wb

def CreateDocument(text, date):
    return search.Document(
        fields=[search.TextField(name='text', value=text),
                search.TextField(name='date', value=date),
                search.DateField(name='date', value=datetime.now().date())])

search.Index(name=_INDEX_NAME).put(CreateDocument("more content", "and more"))

wb=getWorkbook("5c5RIx8JYpOQRzU_A6itfA==")



worksheet = wb.sheet_by_index(0)

num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = -1
while curr_row < num_rows:
	curr_row += 1
	row = worksheet.row(curr_row)
#	print 'Row:', curr_row
	curr_cell = -1
	while curr_cell < num_cells:
		curr_cell += 1
		# Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
		cell_type = worksheet.cell_type(curr_row, curr_cell)
	        if (cell_type > -1):
     	            cell_value = worksheet.cell_value(curr_row, curr_cell)
     		   # print '	', cell_type, ':', cell_value
	        if (cell_type == 3):
                  try:
		    print (datetime(*(xlrd.xldate_as_tuple(cell_value, 0))[0:6])).strftime('%d-%m-%Y')
		  except:
		    print worksheet.cell_value(curr_row, curr_cell)

                  # print (datetime(*(xlrd.xldate_as_tuple(cell_value, 0))[0:6])).strftime('%d-%m-%Y')

       		#if (cell_type == 2):
		#    print('%0.2f %s %s' % (cell_value, curr_row, curr_cell) )


       		if (cell_type == 1):
		    print('%s %s %s' % (cell_value, curr_row, curr_cell) )



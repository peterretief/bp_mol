import xlrd
from datetime import datetime
from decimal import *

#context = Context(prec=2, rounding=ROUND_HALF_DOWN)
#getcontext().prec = 2

workbook = xlrd.open_workbook('b.xls')
worksheet = workbook.sheet_by_index(1)

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
	        if (cell_type > 0):
     	            cell_value = worksheet.cell_value(curr_row, curr_cell)
     		   # print '	', cell_type, ':', cell_value
	        if (cell_type == 3):
                    print (datetime(*(xlrd.xldate_as_tuple(cell_value, 0))[0:6])).strftime('%d-%m-%Y')

       		if (cell_type == 2):
		    print('%0.2f %s %s' % (cell_value, curr_row, curr_cell) )


       		if (cell_type == 1):
		    print('%s %s %s' % (cell_value, curr_row, curr_cell) )


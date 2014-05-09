#
# Python script to download all Excel spreadsheets that make up the USGS dataset:
#   "Historical Statistics for Mineral Commodoties in the United States, 
#    Data Series 2005-140" #"http://templogs.ppecb.com//tlogs/Tlog_MHG_140409_N005.xls"


import urllib
from BeautifulSoup import BeautifulSoup


location = "http://templogs.ppecb.com//tlogs/"

page = urllib.urlopen(location)
soup = BeautifulSoup(page)


# Find each <a href="...">XLS</a> and download the file pointed to by href="..."
for link in soup.findAll('a'):
    if link.string == 'XLS':
       	filename = link.get('href')
       	print("Retrieving " + filename)
       	url = location + filename
       	urllib.urlretrieve(url,filename)



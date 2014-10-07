from google.appengine.ext import ndb

class UserUpload_ndb(ndb.Model):
    description = ndb.StringProperty()
    blob = ndb.BlobKeyProperty()
    filename = ndb.StringProperty()

class Containers():
	pass


class Files():
	pass
#have many containers

class readings():
	pass

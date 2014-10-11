from google.appengine.ext import ndb

class UserUpload_ndb(ndb.Model):
    description = ndb.StringProperty()
    blob = ndb.BlobKeyProperty()
    filename = ndb.StringProperty()

class Invoice(ndb.Model):
    description = ndb.StringProperty()
    blob = ndb.BlobKeyProperty()
    filename = ndb.StringProperty()


class fileAdd(ndb.Model):
    name = ndb.StringProperty()
    text = ndb.StringProperty()
    blob = ndb.BlobKeyProperty()
    row = ndb.IntegerProperty()

class Contributor(ndb.Model):
   count = ndb.IntegerProperty(default=0)
   
   @classmethod
   @ndb.transactional
   def unique_id(cls, email):
        """Increments contributor suggestion count and creates unique ID."""
        contributor = cls.get_by_id(email)
        if contributor == None:
            contributor = cls(id=email)
        contributor.count += 1
        contributor.put()

        return '{}|{:d}'.format(email, contributor.count)


class Manifest(ndb.Model):
    	file_name = ndb.StringProperty()
    	vessel_name = ndb.StringProperty()
	vessel_name_lower = ndb.ComputedProperty(lambda self: self.vessel_name.lower())
    	voyage = ndb.StringProperty()
    	voyage_link = ndb.StringProperty()
	voyage_lower = ndb.ComputedProperty(lambda self: self.voyage.lower())
    	port = ndb.StringProperty()
	port_lower = ndb.ComputedProperty(lambda self: self.port.lower())
        blob = ndb.BlobKeyProperty()
        vessel = ndb.KeyProperty('Vessel')
	created = ndb.DateProperty(auto_now_add=True)
	updated = ndb.DateProperty(auto_now=True)

	@classmethod
	def find_duplicate(self, _vessel, _voyage, _port):
		 get_manifest = Manifest.query(Manifest.vessel_name == _vessel, Manifest.voyage == _voyage, Manifest.port == _port)
  	         return get_manifest.get()
	@classmethod
	def find_filelist(self, _vessel, _voyage):
		 get_filelist = FileList.query(FileList.vessel_name == _vessel, FileList.voyage == _voyage)
  	         return get_filelist.get()

	@classmethod
	def find_manifest(self, _manifest):
		 get_manifest = Manifest.query(Manifest.key==ndb.Key(Manifest, _manifest))
  	         return get_manifest.fetch(1)

	@classmethod
	def find_manifest_details(self, _manifest):
		 get_manifest = ManifestDetail.query(ManifestDetail.manifest==ndb.Key(Manifest, _manifest)).order(+ManifestDetail.count)
  	         return get_manifest.fetch(10000)

	@classmethod
	def search_by_vessel(self, _vessel):
		 get_manifest = ManifestDetail.query(ManifestDetail.vessel==_vessel)
  	         return get_manifest.fetch(10000)

	@classmethod
	def search_by_(self, _header, _term):
		 get_manifest = ManifestDetail.query(ManifestDetail._header==_term)
  	         return get_manifest.fetch(10000)


class ManifestDetail(ndb.Model):
    	booking_number = ndb.StringProperty()
    	sfx = ndb.StringProperty()
    	container_number = ndb.StringProperty()
    	container_status = ndb.BooleanProperty(default = False)
    	commodity = ndb.StringProperty()
    	disch_port = ndb.StringProperty()
    	temp = ndb.StringProperty()
    	temp_status = ndb.BooleanProperty(default = False)
    	code = ndb.StringProperty()
    	code_status = ndb.BooleanProperty(default = False)
    	vents = ndb.StringProperty()
    	vents_status = ndb.BooleanProperty(default = False)
    	equipment_type = ndb.StringProperty()
    	empty_dsp = ndb.StringProperty()
    	count = ndb.IntegerProperty()
        manifest = ndb.KeyProperty('Manifest')
	created = ndb.DateProperty(auto_now_add=True)
	updated = ndb.DateProperty(auto_now=True)

	@classmethod
	def find_manifest(self, _manifest):
		 get_manifest = ManifestDetail.query(ManifestDetail.manifest==ndb.Key(Manifest, _manifest))
  	         return get_manifest.get()

class VesselContainer(ndb.Model):
	container_code = ndb.StringProperty()
	ppecbcode = ndb.StringProperty()
	vent = ndb.StringProperty()
	setpoint = ndb.StringProperty()
    	vessel = ndb.KeyProperty("Vessel") 
	created = ndb.DateProperty(auto_now_add=True)
	updated = ndb.DateProperty(auto_now=True)


class ContainerTempLog(ndb.Model):
	readingdate = ndb.StringProperty()
	RAT = ndb.StringProperty()
	DAT = ndb.StringProperty()
	Diff = ndb.StringProperty()
    	container = ndb.KeyProperty("VesselContainer") 
	created = ndb.DateProperty(auto_now_add=True)
	updated = ndb.DateProperty(auto_now=True)

class Vessel(ndb.Model):
    	vessel = ndb.StringProperty()
	vessel_lower = ndb.ComputedProperty(lambda self: self.vessel.lower())
	voyage = ndb.StringProperty()
	voyage_lower = ndb.ComputedProperty(lambda self: self.voyage.lower())
	port = ndb.StringProperty()
	port_lower = ndb.ComputedProperty(lambda self: self.port.lower())
   	loaded = ndb.StringProperty()
        blob = ndb.BlobKeyProperty()
    	manifest = ndb.KeyProperty("Manifest") 
	created = ndb.DateProperty(auto_now_add=True)
	updated = ndb.DateProperty(auto_now=True)

	@classmethod
#	def find_manifest(self, _voyage, _port, _vessel):
	def find_manifest(self, _voyage, _port):
		port = str(_port).lower()
		voyage = str(_voyage).lower()
		q = Manifest.query()
		q = q.filter(Manifest.voyage_lower == voyage)
		q = q.filter(Manifest.port_lower >= port)
  		return q.get()
	@classmethod
	def update_manifest(self, qry):
		manifest = Manifest().query(ancestor=qry.manifest).get()
		manifest.vessel = qry.key
		manifest.put()
		return manifest

class FileList(ndb.Model):
    	vessel = ndb.StringProperty()
	voyage = ndb.StringProperty()
   	loaded = ndb.StringProperty()
        blob = ndb.BlobKeyProperty()
    	manifest = ndb.KeyProperty()
	created = ndb.DateProperty(auto_now_add=True)
	updated = ndb.DateProperty(auto_now=True)
	@classmethod
	def get_voyage(self, _voyage):
		 get_voyage = Manifest.query(Manifest.voyage == _voyage)
  	         return get_voyage.get()

	


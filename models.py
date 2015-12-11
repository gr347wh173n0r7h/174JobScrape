from google.appengine.ext import ndb

class Job(ndb.Model):
  title = ndb.StringProperty()
  company = ndb.StringProperty()
  location = ndb.StringProperty()
  description = ndb.StringProperty()
  href = ndb.StringProperty()
  site = ndb.StringProperty()

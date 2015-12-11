from google.appengine.ext import ndb
'''
Object to store job data
  Auto-generated hash key for O(1) search time
'''
class Job(ndb.Model):
  title = ndb.StringProperty()
  company = ndb.StringProperty()
  location = ndb.StringProperty()
  description = ndb.StringProperty()
  href = ndb.StringProperty()
  site = ndb.StringProperty()

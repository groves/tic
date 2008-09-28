from google.appengine.ext import db

class Activity(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    start = db.DateTimeProperty(auto_now_add=True)
    end = db.DateTimeProperty()

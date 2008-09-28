import logging
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.utils import simplejson as json

from model import Activity

def render(name, **values):
    path = os.path.join(os.path.dirname(__file__), '../templates/%s.html' % name)
    return template.render(path, values)

class Index(webapp.RequestHandler):
    def get(self):
        self.response.out.write(render("index",
            activities=Activity.all().filter("end =", None).order("-start")))

class Add(webapp.RequestHandler):
    def post(self):
        name = self.request.get("name")
        if not name:
            self.response.out.write(json.dumps({"success":False, "reason":"Name must be given"}))
            return
        activity = Activity(name=name)
        activity.put()
        self.response.out.write(json.dumps({"success":True,
            "activity":render("activity", activity=activity)}))

class Delete(webapp.RequestHandler):
    def post(self):
        key = self.request.get("key")
        if not key:
            self.response.out.write(json.dumps({"success":False, "reason":"Key must be given"}))
            return
        Activity.get(db.Key(key)).delete()
        self.response.out.write(json.dumps({"success":True, "activity":key}))

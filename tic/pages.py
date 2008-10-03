import logging
import os
from datetime import datetime, timedelta

from pytz import common_timezones
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from model import Activity, UserPrefs, prefs, user

def render(name, **values):
    path = os.path.join(os.path.dirname(__file__), '../templates/%s.html' % name)
    return template.render(path, values)

class Index(webapp.RequestHandler):
    def get(self):
        yesterday = datetime.now() - timedelta(1)
        self.response.out.write(render("index",
            activities=Activity.all().filter("user =", user()).filter("stop =", None).order("-start"),
            inactivities=Activity.all().filter("stop >", yesterday).order("-stop")))

class Preferences(webapp.RequestHandler):
    def get(self):
        zones = common_timezones
        index = zones.index(prefs().timezone.zone)
        self.response.out.write(render("preferences", **locals()))

    def post(self):
        pref = prefs()
        pref.tzname = self.request.get("timezone")
        pref.put()
        self.get()

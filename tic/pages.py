import logging
import os

from datetime import datetime, timedelta

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from django.utils import simplejson as json

from model import Activity

def render(name, **values):
    path = os.path.join(os.path.dirname(__file__), '../templates/%s.html' % name)
    return template.render(path, values)

def user():
    return users.get_current_user()

class Index(webapp.RequestHandler):
    def get(self):
        yesterday = datetime.now() - timedelta(1)
        self.response.out.write(render("index",
            activities=Activity.all().filter("user =", user()).filter("stop =", None).order("-start"),
            inactivities=Activity.all().filter("stop >", yesterday).order("-stop")))

class ParamMissingError(Exception):
    pass

class JsonHandler(webapp.RequestHandler):
    def require(self, param):
        val = self.request.get(param)
        if not val:
            self.response.out.write(json.dumps({"success":False,
                "reason":"%s must be given" % param}))
            raise ParamMissingError
        return val

    def post(self):
        try:
            data = self.json()
            data["success"] = True
            self.response.out.write(json.dumps(data)) 
        except ParamMissingError:
            pass # Handled by require

class Add(JsonHandler):
    def json(self):
        activity = Activity(name=self.require("name"), user=user())
        activity.put()
        return {"activity":render("activity", activity=activity)}

class ActivityModifier(JsonHandler):
    def json(self):
        result = self.modify(Activity.get(db.Key(self.require("key"))))
        if result:
            result.put()
            return {"activity":render("activity", activity=result)}
        return {}

class Delete(ActivityModifier):
    def modify(self, activity):
        activity.delete()

class Stop(ActivityModifier):
    def modify(self, activity):
        activity.stop = datetime.now()
        return activity

class Again(ActivityModifier):
    def modify(self, activity):
        return Activity(name=activity.name, start=activity.start, user=user())

class Restart(ActivityModifier):
    def modify(self, activity):
        activity.stop = None
        return activity

class Rename(ActivityModifier):
    def modify(self, activity):
        activity.name = self.require("value")
        return activity

class EditStart(ActivityModifier):
    def modify(self, activity):
        activity.start = datetime.strptime(self.require("value"), "%Y/%m/%d %H:%M")
        return activity

class EditDuration(ActivityModifier):
    def modify(self, activity):
        activity.duration = self.require("value")
        return activity

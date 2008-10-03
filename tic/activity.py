from datetime import datetime

from pytz import utc
from google.appengine.ext import webapp
from google.appengine.ext import db
from django.utils import simplejson as json

from model import Activity, UserPrefs, prefs, user
from pages import render

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
        return Activity(name=activity.name, user=user())

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
        newstart = datetime.strptime(self.require("value"), "%Y/%m/%d %H:%M")
        activity.start = prefs().timezone.localize(newstart).astimezone(utc)
        return activity

class EditDuration(ActivityModifier):
    def modify(self, activity):
        activity.duration = self.require("value")
        return activity

urls = [('/', Add),
    ('/delete', Delete),
    ('/again', Again),
    ('/restart', Restart),
    ('/rename', Rename),
    ('/start', EditStart),
    ('/duration', EditDuration),
    ('/stop', Stop)]

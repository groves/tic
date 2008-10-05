import logging
import re
from datetime import timedelta

import pytz

from google.appengine.api import users
from google.appengine.ext import db, search

def format(value, unit):
    if value > 1:
        return '%s %ss ' % (value, unit)
    elif value == 1:
        return '%s %s ' % (value, unit)
    else:
        return ''

duration_parser = re.compile(" *((?P<hours>\d+) *h(ours?)?)? *((?P<minutes>\d+) *m(inutes?)?)? *")
hour = 60 * 60
tag_parser = re.compile("\w+")

class Activity(search.SearchableModel):
    user = db.UserProperty()
    name = db.StringProperty()
    start = db.DateTimeProperty(auto_now_add=True)
    stop = db.DateTimeProperty()
    tags = db.StringListProperty()

    def __str__(self):
        return "Activity(name=%s, user=%s, start=%s, stop=%s, tags=%s)" % (self.name, self.user,
                self.start, self.stop, self.tags)


    def getDuration(self):
        duration = self.stop - self.start
        return ('%s%s' % (format(duration.seconds / hour, 'hour'),
                format(duration.seconds % hour / 60, 'minute'))).strip()

    def setDuration(self, newDuration):
        m = duration_parser.search(newDuration)
        if not m.group("hours") and not m.group("minutes"):
            raise ValueError("Invalid duration %s" % newDuration)
        hours = int(m.group("hours")) if m.group("hours") else 0
        minutes = int(m.group("minutes")) if m.group("minutes") else 0
        self.stop = self.start + timedelta(hours=hours, minutes=minutes)

    duration = property(getDuration, setDuration)

    def getLocalstart(self):
        tz = prefs().timezone
        return tz.normalize(self.start.replace(tzinfo=pytz.utc).astimezone(tz))
    localstart = property(getLocalstart)

    @classmethod
    def locate(cls, start=None, end=None, names=[], tags=[]):
        q = cls.foruser()
        if start:
            q = q.filter("start >=", start)
        if end:
            q = q.filter("start <=", end)
        for tag in tags:
            q = q.filter("tags =", tag)
        if names:
            activities = set()
            for name in names:
                matches = set(q.search(name))
                activities.update(matches)
        else:
            activities = set(q)
        return activities

    @classmethod
    def foruser(cls):
        return Activity.all().filter("user =", users.get_current_user())

    @classmethod
    def parsetags(cls, tags):
        return tag_parser.findall(tags)

def user():
    return users.get_current_user()

def prefs():
    prefs = UserPrefs.all().filter("user =", user()).fetch(1)
    if len(prefs) == 1:
        return prefs[0]
    return UserPrefs(user=user(), tzname=pytz.utc.zone)


class UserPrefs(db.Model):
    user = db.UserProperty()
    tzname = db.StringProperty()

    timezone = property(lambda x: pytz.timezone(x.tzname))

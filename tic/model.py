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

class Activity(search.SearchableModel):
    user = db.UserProperty()
    name = db.StringProperty()
    start = db.DateTimeProperty(auto_now_add=True)
    stop = db.DateTimeProperty()

    def __str__(self):
        return "Activity(name=%s, user=%s, start=%s, stop=%s)" % (self.name, self.user, self.start, self.stop)


    def getDuration(self):
        duration = self.stop - self.start
        return '%s%s' % (format(duration.seconds / hour, 'hour'),
                format(duration.seconds % hour / 60, 'minute'))

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
    def locate(cls, start, end, *names):
        logging.info("Searching for activities from %s to %s" % (start, end))
        base = cls.all().filter("user =", user()).filter("start >=", start).filter("start <=", end)
        activities = set()
        for name in names:
            matches = set(base.search(name))
            logging.info("Found %s matches for %s" % (len(matches), name))
            activities.update(matches)
        logging.info("Found %s total" % len(activities))
        return activities


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

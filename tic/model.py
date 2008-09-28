import re
from datetime import timedelta

from google.appengine.ext import db

def format(value, unit):
    if value > 1:
        return '%s %ss ' % (value, unit)
    elif value == 1:
        return '%s %s ' % (value, unit)
    else:
        return ''

duration_parser = re.compile("((?P<hours>\d+) hours? ?)?((?P<minutes>\d+) minutes?)?")
hour = 60 * 60
class Activity(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    start = db.DateTimeProperty(auto_now_add=True)
    stop = db.DateTimeProperty()

    def getDuration(self):
        duration = self.stop - self.start
        return '%s%s' % (format(duration.seconds / hour, 'hour'),
                format(duration.seconds % hour / 60, 'minute'))

    def setDuration(self, newDuration):
        m = duration_parser.search(newDuration)
        hours = int(m.group("hours")) if m.group("hours") else 0
        minutes = int(m.group("minutes")) if m.group("minutes") else 0
        self.stop = self.start + timedelta(hours=hours, minutes=minutes)

    duration = property(getDuration, setDuration)

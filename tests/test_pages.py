from datetime import datetime, timedelta

import pytz
from nose.tools import eq_
from webtest import TestApp

from tic import application, pages
from tic.model import Activity, UserPrefs, prefs
from datasets import ActivityData, get_base, make_data

def test_empty():
    app = TestApp(application)
    resp = app.get('/')
    assert "<table" in resp
    assert "<tr" not in resp

class TestPages:
    def setUp(self):
        self.app = TestApp(application)
        self.data = make_data()
        self.act = get_base()
        self.key = self.act.key()

    def tearDown(self):
        self.data.teardown()
        for a in Activity.all():
            a.delete()
        for p in UserPrefs.all():
            p.delete()

    def testDisplayedActivities(self):
        resp = self.app.get("/")
        eq_(ActivityData.horking_on_tic.name, resp.html.find("table", id="active").tr.td.string)
        eq_(ActivityData.sleeping.name, resp.html.find("table", id="inactive").tr.td.string)

    def testAdd(self):
        response = self.app.post('/activity/', {'name': 'new activity'})
        response.mustcontain("true", 'new activity')
        response = self.app.post('/activity/')
        response.mustcontain("false", "name must be given")

    def testDelete(self):
        response = self.app.post('/activity/delete', {'key': self.key})
        response.mustcontain("true")
        assert Activity.get(self.key) is None
        response = self.app.post('/activity/delete')
        response.mustcontain("false", "key must be given")

    def testStop(self):
        assert self.act.stop is None
        response = self.app.post('/activity/stop', {'key': self.key})
        response.mustcontain("true", self.act.name)
        assert Activity.get(self.key) is not None

    def testRestart(self):
        self.act.stop = datetime.now()
        self.act.put()
        response = self.app.post("/activity/restart", {'key': self.key})
        response.mustcontain("true", self.act.name)
        assert Activity.get(self.key).stop is None

    def testAgain(self):
        response = self.app.post("/activity/again", {'key': self.key})
        response.mustcontain("true", self.act.name)
        assert Activity.all().filter("user =", pages.user()).filter("name =", self.act.name).count() == 3

    def testRename(self):
        response = self.app.post("/activity/rename", {'key': self.key, 'value':'new name'})
        assert Activity.get(self.key).name == "new name"

    def testEditStart(self):
        newstart = datetime(2008, 9, 17, 12, 15)
        self.app.post("/activity/start",
                {'key': self.key, 'value':newstart.strftime("%Y/%m/%d %H:%M")})
        eq_(newstart, Activity.get(self.key).start)

    def testEditDuration(self):
        self.act.stop = datetime.now()
        self.act.put()
        newstop = self.act.start + timedelta(hours=1)
        self.app.post("/activity/duration", {"key": self.key, 'value':"1 hours"})
        eq_(newstop, Activity.get(self.key).stop)

    def testSetTimeZone(self):
        eq_(pytz.utc, prefs().timezone)
        resp = self.app.post("/preferences", {"timezone": "US/Pacific"})
        selected = resp.html.findAll("option", selected="true")
        eq_(1, len(selected))
        eq_("US/Pacific", selected[0].string)

    def testLocalstart(self):
        pref = prefs()
        pref.tzname = "US/Pacific"
        pref.put()
        eq_("US/Pacific", Activity.all()[0].localstart.tzinfo.zone)

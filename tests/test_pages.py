import os
from datetime import datetime, timedelta

from nose.tools import eq_
from webtest import TestApp
from fixture import GoogleDatastoreFixture
from fixture.style import NamedDataStyle

from tic import application, model, pages
from tic.model import Activity
from datasets import ActivityData

os.environ['USER_EMAIL'] = "test@blah.com"
datafixture = GoogleDatastoreFixture(env=model, style=NamedDataStyle())

def test_empty():
    app = TestApp(application)
    resp = app.get('/')
    assert "<table" in resp
    assert "<tr" not in resp

class TestPages:
    def setUp(self):
        self.app = TestApp(application)
        self.data = datafixture.data(ActivityData)
        self.data.setup()
        self.act = Activity.all()[0]
        self.key = self.act.key()

    def tearDown(self):
        self.data.teardown()
        for a in Activity.all():
            a.delete()

    def testSingleActivity(self):
        assert ActivityData.working_on_tic.name in self.app.get("/")

    def testAdd(self):
        response = self.app.post('/add', {'name': 'new activity'})
        response.mustcontain("true", 'new activity')
        response = self.app.post('/add')
        response.mustcontain("false", "name must be given")

    def testDelete(self):
        response = self.app.post('/delete', {'key': self.key})
        response.mustcontain("true")
        assert Activity.get(self.key) is None
        response = self.app.post('/delete')
        response.mustcontain("false", "key must be given")

    def testStop(self):
        assert self.act.stop is None
        response = self.app.post('/stop', {'key': self.key})
        response.mustcontain("true", self.act.name)
        assert Activity.get(self.key) is not None

    def testRestart(self):
        self.act.stop = datetime.now()
        self.act.put()
        response = self.app.post("/restart", {'key': self.key})
        response.mustcontain("true", self.act.name)
        assert Activity.get(self.key).stop is None

    def testAgain(self):
        response = self.app.post("/again", {'key': self.key})
        response.mustcontain("true", self.act.name)
        assert Activity.all().filter("user =", pages.user()).filter("name =", self.act.name).count() == 2

    def testRename(self):
        response = self.app.post("/rename", {'key': self.key, 'value':'new name'})
        assert Activity.get(self.key).name == "new name"

    def testEditStart(self):
        newstart = datetime(2008, 9, 17, 12, 15)
        self.app.post("/editstart", {'key': self.key, 'value':newstart.strftime("%Y/%m/%d %H:%M")})
        eq_(newstart, Activity.get(self.key).start)

    def testEditDuration(self):
        self.act.stop = datetime.now()
        self.act.put()
        newstop = self.act.start + timedelta(hours=1)
        self.app.post("/editduration", {"key": self.key, 'value':"1 hours"})
        eq_(newstop, Activity.get(self.key).stop)

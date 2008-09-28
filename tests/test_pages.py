import os
from datetime import datetime

from nose.tools import eq_
from webtest import TestApp
from fixture import GoogleDatastoreFixture
from fixture.style import NamedDataStyle

from tic import application, model
from tic.model import Activity
from datasets import ActivityData

os.environ['USER_EMAIL'] = "test@blah.com"
datafixture = GoogleDatastoreFixture(env=model, style=NamedDataStyle())

def test_empty():
    app = TestApp(application)
    response = app.get('/')
    tables = response.html.findAll("table")
    eq_(len(tables), 2)
    eq_(len(tables[0].findAll("tr")), 0)

class TestPages:
    def setUp(self):
        self.app = TestApp(application)
        self.data = datafixture.data(ActivityData)
        self.data.setup()
        self.act = Activity.all()[0]
        self.key = self.act.key()

    def tearDown(self):
        self.data.teardown()

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

    def testRename(self):
        response = self.app.post("/rename", {'key': self.key, 'name':'new name'})
        assert Activity.get(self.key).name == "new name"


from nose.tools import eq_
from webtest import TestApp
from fixture import GoogleDatastoreFixture
from fixture.style import NamedDataStyle

from tic import application, model
from tic.model import Activity
from datasets import ActivityData


datafixture = GoogleDatastoreFixture(env=model, style=NamedDataStyle())

def test_empty():
    app = TestApp(application)
    response = app.get('/')
    tables = response.html.findAll("table")
    eq_(len(tables), 1)
    eq_(len(tables[0].findAll("tr")), 0)

def test_single_activity():
    app = TestApp(application)
    data = datafixture.data(ActivityData)
    data.setup()
    response = app.get('/')
    assert ActivityData.working_on_tic.name in response
    data.teardown()

def test_add():
    app = TestApp(application)
    response = app.post('/add', {'name': 'new activity'})
    response.mustcontain("true", 'new activity')
    response = app.post('/add')
    response.mustcontain("false", "Name must be given")

def test_delete():
    app = TestApp(application)
    data = datafixture.data(ActivityData)
    data.setup()
    key = Activity.all()[0].key()
    response = app.post('/delete', {'key': key})
    response.mustcontain("true", key)
    assert Activity.get(key) is None
    response = app.post('/delete')
    response.mustcontain("false", "Key must be given")
    data.teardown()



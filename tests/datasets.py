import os
from datetime import datetime, timedelta

from fixture import DataSet, GoogleDatastoreFixture
from fixture.style import NamedDataStyle
from google.appengine.api.users import User

from tic import model

class ActivityData(DataSet):
    class simplest:
        name = "Doing something"
        start = datetime.now() - timedelta(hours=1, minutes=30)
        user = User("test@blah.com")

    class working_on_tic(simplest):
        name = "Working on tic"
        tags = ['tic']

    class horking_on_tic(working_on_tic):
        name = "Horking on tic"
        start = datetime.now() - timedelta(hours=1)

    class different_time_same_name(working_on_tic):
        start = datetime.now() - timedelta(days=1)

    class sleeping(simplest):
        name = "Sleeping"
        start = datetime.now() - timedelta(hours=8)
        stop = start - timedelta(hours=2)

os.environ['USER_EMAIL'] = "test@blah.com"
datafixture = GoogleDatastoreFixture(env=model, style=NamedDataStyle())

def make_data():
    data = datafixture.data(ActivityData)
    data.setup()
    return data

def get_base():
    return model.Activity.all().filter("name =", ActivityData.working_on_tic.name).filter("start =", ActivityData.working_on_tic.start)[0]


import os
from datetime import datetime, timedelta

from fixture import DataSet, GoogleDatastoreFixture
from fixture.style import NamedDataStyle
from google.appengine.api.users import User

from tic import model

u = User("test@blah.com")
class ActivityData(DataSet):
    class working_on_tic:
        name = "Working on tic"
        user = u
        start = datetime.now() - timedelta(hours=1, minutes=30)

    class horking_on_tic:
        name = "Horking on tic"
        user = u
        start = datetime.now() - timedelta(hours=1)

    class same_time_different_name:
        name = "some other thing "
        user = u
        start = datetime.now() - timedelta(hours=1, minutes=30)

    class different_time_same_name:
        name = "Working on tic"
        user = u
        start = datetime.now() - timedelta(days=1)

    class sleeping:
        name = "Sleeping"
        user = u
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


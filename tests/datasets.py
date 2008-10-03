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

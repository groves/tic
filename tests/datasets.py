from datetime import datetime, timedelta

from fixture import DataSet

from google.appengine.api.users import User

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

from fixture import DataSet

from google.appengine.api.users import User

class ActivityData(DataSet):
    class working_on_tic:
        name = "Working on tic"
        user = User("test@blah.com")

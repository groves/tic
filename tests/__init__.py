import os

from google.appengine.tools import dev_appserver_index

def teardown():

    appdir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    updater = dev_appserver_index.IndexYamlUpdater(appdir)
    updater.UpdateIndexYaml()

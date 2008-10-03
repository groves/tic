import wsgiref.handlers

from google.appengine.ext import webapp

import activity, pages

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


urls = [('/', pages.Index), ('/preferences', pages.Preferences)]
urls.extend((('/activity%s' % url, handler) for url, handler in activity.urls))
application = webapp.WSGIApplication(urls, debug=True)

if __name__ == '__main__':
    wsgiref.handlers.CGIHandler().run(application)

import wsgiref.handlers

from google.appengine.ext import webapp

import pages

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')


application = webapp.WSGIApplication(
        [('/', pages.Index),
            ('/add', pages.Add),
            ('/delete', pages.Delete),
            ('/again', pages.Again),
            ('/restart', pages.Restart),
            ('/rename', pages.Rename),
            ('/editstart', pages.EditStart),
            ('/stop', pages.Stop)], debug=True)

if __name__ == '__main__':
    wsgiref.handlers.CGIHandler().run(application)

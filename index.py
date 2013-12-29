# Adding scripts directory to PATH
import sys
sys.path.insert(0, 'app/scripts')

# Script imports
from BaseHandler import *
from IVLE import *

# Handlers
class MainHandler(Handler):
    def get(self):
        self.render("ivle.html", IVLEKey=IVLE_LAPI_KEY)


# Handler Routing
app = webapp2.WSGIApplication([('/', MainHandler),
    ('/ivle', IVLEHandler)], debug=True)
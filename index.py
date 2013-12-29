# Adding scripts directory to PATH
import sys
sys.path.insert(0, 'app/scripts')

# Script imports
from base_handler import *
from ivle import *
from step_one import *

# Handler Routing
app = webapp2.WSGIApplication([('/', StepOneHandler),
    ('/ivle', IVLEHandler)], debug=True)
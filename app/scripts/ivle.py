# Handler for IVLE Callback

from base_handler import *

IVLE_LAPI_KEY = "nR7o7vzmqBA3BAXxPrLLD"
CURRENT_YEAR = "2013/2014"
CURRENT_SEM = "1"


class IVLEHandler(Handler):
    def get(self):
        self.render("ivle_logged_in.html", IVLEKey=IVLE_LAPI_KEY, Token=self.request.get('token'),
                    CurrentYear=CURRENT_YEAR, CurrentSem=CURRENT_SEM)

from base_handler import *
from ivle import IVLE_LAPI_KEY


class StepOneHandler(Handler):
    def get(self):
        self.render("step1.html", IVLEKey=IVLE_LAPI_KEY)
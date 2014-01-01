from base_handler import *


class StepTwoHandler(Handler):
    def get(self):
        self.render("step2.html")
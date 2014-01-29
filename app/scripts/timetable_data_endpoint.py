from base_handler import *
import json


data = json.load(open("app/data/modInfo.json"), encoding='latin1')

class TimeTableDataEndpoint(Handler):
    def get(self):
        module = self.request.get('module').upper()
        sem = self.request.get('sem')
        self.response.headers['Content-Type'] = "application/json"
        self.response.headers['Cache-Control'] = "max-age=30"
        if module in data:
            self.response.out.write(json.dumps(data[modName]))
            return
        self.response.out.write(json.dumps({}))
        return
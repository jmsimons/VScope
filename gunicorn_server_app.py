#!/usr/bin/python3.5

from gunicorn import glogging, workers.sync
from gunicorn.app.base import BaseApplication

class GunicornServerApp(BaseApplication):

    def __init__(self, app, options):
        self.app = app
        self.options = options
        super().__init__()
    
    def load_config(self):
        config = {k: v for k, v in self.options.items() if k in self.cfg.settings and v != None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)
    
    def load(self):
        return self.app
#!/usr/bin/python3.5

import os, sys, gunicorn
from psutil import cpu_count
import gunicorn.glogging, gunicorn.workers.sync
from gunicorn.app.base import BaseApplication
import setup


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


if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
    from webapp import app
    # from gunicorn_server_app import GunicornServerApp
    if 'vscope.conf' not in os.listdir():
        setup.main()
    else:
        print('Webapp running with PID:', os.getpid())
        options = {'bind': '0.0.0.0:5000', 'workers': cpu_count()}
        GunicornServerApp(app, options).run()
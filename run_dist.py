#!/usr/bin/python3.5

import os, sys
from psutil import cpu_count
import setup


if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        os.chdir(sys._MEIPASS)
        print(os.getcwd())
    from webapp import app
    from webapp.gunicorn_server_app import GunicornServerApp
    if 'vscope.conf' not in os.listdir():
        setup.main()
    else:
        print('Webapp running with PID:', os.getpid())
        options = {'bind': '0.0.0.0:5000', 'workers': 2}
        GunicornServerApp(app, options).run()
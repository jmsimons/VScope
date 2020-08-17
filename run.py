#!/usr/bin/python3.5

import os
from webapp import app

if __name__ == '__main__':
    print('Webapp running with PID:', os.getpid())
    app.run(debug = True, host = '0.0.0.0', port = 5000)

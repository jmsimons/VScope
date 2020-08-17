#!/usr/bin/python3.5

import os

real_path = os.path.realpath(__file__)
filename = __file__.split('/')[-1]
dir_path = real_path.rstrip(filename).rstrip('/')

def base_path():
    with open('vscope.conf') as f:
        for line in f:
            if 'BASE_PATH' in line:
                path = line.strip().split(':')[-1]
                return path

def all():
    with open('vscope.conf') as f:
        config = {}
        for line in f:
            key, value = line.strip().split(':')
            config[key] = value
        return config

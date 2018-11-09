#!/usr/bin/python
# -*- coding: utf-8 -*-
#from flask import request, render_template, send_file, flash, redirect, abort, make_response
import logging
from gevent.pywsgi import WSGIServer
from gevent import monkey
monkey.patch_all()
import os
from os.path import join, abspath, isfile
import traceback
import time

from views import app

BASE_DIR = abspath(os.path.dirname(__file__))
    
DEFAULT_SERVER_LISTEN_IP = "0.0.0.0"
DEFAULT_SERVER_LISTEN_PORT = 59876
    
def init_and_run_frontend_server(server_ip=DEFAULT_SERVER_LISTEN_IP, server_port=DEFAULT_SERVER_LISTEN_PORT):
    server = WSGIServer((server_ip, server_port), app)
                  
    logging.info("Starting server")
    server.serve_forever()
    
def main():
    init_and_run_frontend_server()

if __name__ == "__main__":
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, request, render_template, send_file, flash, redirect, abort, make_response
import os
from os.path import join, abspath, isfile
import traceback
import time
import json

BASE_DIR = abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Don't think this is used or required at all.
app.secret_key = '3c0d2982b1026847cf82fdeebf1c4cc7'
app.config['SESSION_TYPE'] = 'redis'

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")
        
@app.route('/search_addr/<btc_addr>', methods=['GET'])
def search_addr(btc_addr):
    addrs = json.load(open("dirty_addrs_about_20_layers.json", "r"))
    addr = addrs.get(btc_addr)
    prime_black = json.load(open("primeblacks.json", "r"))
    if addr is None:
        addr = prime_black.get(btc_addr)
        if addr is None:
            res = {"infected": False}
        else:
            res = addr
            resp = make_response(json.dumps(res))
            resp.headers['Access-Control-Allow-Origin'] = '*'
            return resp
    else:
        res = addr
        infection_data = res["infection_data"]
        res.update(infection_data)
        res.pop("infection_data", None)
        res.pop("processed", None)
        res["amount_btc"] = "%.2f" % (float(res["amount_btc"]) / 100000000.0)
        res["amount_usd"] = "%.2f" % float(res["amount_usd"])
        res["infected"] = True
    resp = make_response(json.dumps(res))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.before_request
def before_request():
    pass
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

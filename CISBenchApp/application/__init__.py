from flask import Flask
from os import path

import sys, json, datetime, time, hashlib, urllib.request, urllib.parse, subprocess, importlib
from configparser import ConfigParser

def respJson(code, msg):
    js = {}
    js['returnCode'] = code
    js['returnMessage'] = msg
    return js

def mylogging(content):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    w_file = open("logs/access_%s.log" % today, "a")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    w_file.write("%s %s\n" % (now, content))
    w_file.close()

def config_get(section, name):
    parser = ConfigParser()
    parser.OPTCRE
    parser.read("conf/main.conf")
    return parser.get(section, name)
    
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

    from .views import views
    from .bench import bench
    from .harden import harden

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(bench, url_prefix='/bench')
    app.register_blueprint(harden, url_prefix='/harden')
    
    return app

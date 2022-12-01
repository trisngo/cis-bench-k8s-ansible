#!/usr/bin/python3

import sys, json, datetime, time, hashlib, urllib.request, urllib.parse, subprocess, importlib
from flask import Flask, jsonify, request, redirect, abort

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


app = Flask(__name__)

@app.route('/submitOptions', methods=['GET'])
def storeOption():
    post_data = '{"task": ["3.1.1", "3.2.2", "3.3.1"]}'
    try:
        # date = request.headers.get('date')
        file_name = "%s/options.yml" % (config_get("data_store", "dir"))
        # post_data = request.get_data()
    
        data  = json.loads(post_data)
        print (data['task'])

        # w_file = open(file_name, "w")
        # w_file.write(data.decode("utf-8"))

        with open(file_name, 'w') as w_file:
            for item in data['task']:
                w_file.write("task_%s: true\n" % item)

        # w_file.close()
        
        mylogging("INFO: Selections store succeed")
        return jsonify(respJson(0, "Store selection succeed"))

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))

@app.route('/runRemediation', methods=['GET'])
def remediation():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        cmd = ["%s" % (config_get("remediation", "bin")),"-i" ,"%s" % (config_get("remediation", "inventory")),"%s" % (config_get("remediation", "path"))]
        file_name = "logs/playbook_logs/playbook_%s.log" % now
        
        with open(file_name, "w") as w_file:
            subprocess.run(cmd, stdout=w_file)
    
        mylogging("INFO: Run remediation playbook succeed")
        return jsonify(respJson(0, "Run remediation playbook succeed, view at %s" % file_name))

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))


if __name__ == '__main__':
    try:
        config_get("remediation", "bin")
        config_get("remediation", "inventory")
        config_get("remediation", "path")
        config_get("data_store", "dir")
        app.run(host=config_get("web_server", "host"), port=int(config_get("web_server", "port")), debug=False, threaded=True)
    except Exception as ex:
        mylogging("ERROR: Config: %s" %ex)
        print ("API start failed")
        exit()


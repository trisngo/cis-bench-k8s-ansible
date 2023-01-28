from flask import Blueprint, Flask, render_template, request, flash, jsonify, redirect, url_for, session, Response

import sys, json, datetime, time, hashlib, urllib.request, urllib.parse, subprocess, importlib, configparser, os
from werkzeug.utils import secure_filename
from uuid import uuid4
from . import mylogging, config_get, respJson
from jinja2 import Environment,FileSystemLoader

harden = Blueprint('harden', __name__)

@harden.route('/submit', methods=['POST']) #POST
def harden_option():
    try:
        post_data = request.get_json()
        print(post_data)
        if not post_data:
            print ("Do not have tasks in request")
            return jsonify(respJson(-500, "Something went wrong!"))

        if 'tags' not in session:
            session['tags'] = [] 
        tags_list = session['tags']
        for t in post_data:
            tags_list.append(t)
        session['tags'] = sorted(set(tags_list))
        print(session)

        mylogging("INFO: Selections store succeed")
        return jsonify(respJson(0, "Store selection succeed"))

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))

@harden.route('/run', methods=['GET'])
def run_harden():
    return render_template("run_harden.html")

@harden.route('/stream_harden')
def stream_harden_config():
    try:
        platform = session['platform']
        print(platform)
        tags_list = session['tags']
        all_tags = ""
        for tag in tags_list:
            all_tags += tag + ","
        all_tags = all_tags[:-1] 
        cmd = ["%s" % (config_get("ansible", "bin")),"-i" ,"%s" % (config_get("ansible", "inventory")),"%s" % (config_get(platform.lower(), "config")), "--tags", "%s" % all_tags]
        print(cmd)
        def inner():
            proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,)
            for line in proc.stdout:
                yield line.rstrip().decode("utf-8")  + '<br/>'

        env = Environment(loader=FileSystemLoader('application/templates'))
        tmpl = env.get_template('benchmark_progress.html')
        return Response(tmpl.generate(result=inner()),mimetype='text/html')

    except Exception as ex:
        return jsonify(respJson(-500, "Something went wrong!"))

# @harden.route('/result', methods=['GET'])
# def result_harden():
#     log = session.get('harden_log')
#     b_lines = [row for row in list(open(log))]

#     return render_template("run_harden.html", b_lines=b_lines)

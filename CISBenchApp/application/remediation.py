from flask import Blueprint, Flask, render_template, request, flash, jsonify, redirect, url_for, session

import sys, json, datetime, time, hashlib, urllib.request, urllib.parse, subprocess, importlib, configparser, os
# from flask import Flask, jsonify, request, redirect, abort
from werkzeug.utils import secure_filename
from uuid import uuid4
from . import mylogging, config_get, respJson

remediation = Blueprint('remediation', __name__)

# @remediation.route('/get_option', methods=['POST']) #POST
# def getOption():
#     try:
#         # date = request.headers.get('date')
#         task = request.form.get('task')
#         if 'tasks' not in session:
#             session['tasks'] = []
#         tasks_list = session['tasks']
#         tasks_list.append(task)
#         session['tasks'] = tasks_list
#         print(session)

#         mylogging("INFO: Selections store session succeed")
#         return jsonify(respJson(0, "Store selection succeed"))

#     except Exception as ex:
#         mylogging("ERROR: %s" %ex)
#         return jsonify(respJson(-500, "Something went wrong!"))



@remediation.route('/submit', methods=['POST']) #POST
def remedation_option():
    # post_data = '{"task": ["1.1.20"]}'
    try:
        # date = request.headers.get('date')
        file_name = "%s/options.yml" % (config_get("data_store", "dir"))
        post_data = request.get_data()
    
        data  = json.loads(post_data)
        print (data)

        if not data:
            print ("Do not have tasks in request")
            return jsonify(respJson(-500, "Something went wrong!"))

        with open(file_name, 'w') as w_file:
            for item in data:
                w_file.write("task_%s: true\n" % item)

        mylogging("INFO: Selections store succeed")
        return jsonify(respJson(0, "Store selection succeed"))

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))

@remediation.route('/run', methods=['GET'])
def run_remediation():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        cmd = ["%s" % (config_get("ansible", "bin")),"-i" ,"%s" % (config_get("ansible", "inventory")),"%s" % (config_get("minikube", "config"))]
        file_name = "logs/playbook_logs/playbook_%s.log" % now
        
        with open(file_name, "w") as w_file:
            subprocess.run(cmd, stdout=w_file)
    
        mylogging("INFO: Run remediation playbook succeed")
        session['remediation_log'] = file_name
        return jsonify(respJson(0, "Run succeed"))

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))

@remediation.route('/result', methods=['GET'])
def result_remediation():
    log = session.get('remediation_log')
    b_lines = [row for row in list(open(log))]

    return render_template("remediation_result.html", b_lines=b_lines)

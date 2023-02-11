from flask import Blueprint, render_template, request, flash, jsonify, session

# import json
import psutil, subprocess
from . import mylogging, config_get, respJson

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def home():
    session.clear()
    # cmd = ["rm", "%s/*" % config_get("data_store", "dir")]
    # print(cmd)
    # subprocess.run(cmd)
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if 'kubectl' in proc.info['name']:
            proc.kill()
    return render_template("home.html")
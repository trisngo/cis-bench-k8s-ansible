from flask import Blueprint, render_template, request, flash, jsonify

# import json
import psutil

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])

def home():
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if 'kubectl' in proc.info['name']:
            proc.kill()
    return render_template("home.html")
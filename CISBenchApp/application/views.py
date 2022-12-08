from flask import Blueprint, render_template, request, flash, jsonify

# import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])

def home():
    return render_template("home.html")


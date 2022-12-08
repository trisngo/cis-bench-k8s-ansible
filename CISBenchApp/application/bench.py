from flask import Blueprint, Flask, render_template, request, flash, jsonify, redirect, url_for, session

import sys, json, datetime, time, hashlib, urllib.request, urllib.parse, subprocess, importlib, configparser, os
# from flask import Flask, jsonify, request, redirect, abort
from werkzeug.utils import secure_filename
from uuid import uuid4
from . import mylogging, config_get, respJson

bench = Blueprint('bench', __name__)

ALLOWED_EXTENSIONS = {''}

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"

@bench.route('/select_ip_mini', methods=['GET', 'POST'])
def select_ip_mini():
    post_data = '{"task": ["3.1.1", "3.2.2", "3.3.1"]}'
    if request.method == 'POST':
        session['ip_0'] = request.form.get('ip_0')
        numWorker = request.form.get('num_worker')
        session['num_worker'] = numWorker
        if (numWorker != 0 ):
            for i in range (0,int(numWorker)):
                session["ip_%s" % (i + 1)] = request.form.get("ip_%s" % (i + 1))
        return redirect(url_for('bench.upload_key_mini'))
    return render_template("home.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bench.route('/upload_key_mini', methods=['GET'])
def upload_key_mini():
    numWorker = session.get('num_worker')
    listFile = [None] * (int(numWorker)+1)
    print(len(listFile))
    for i in range (0,int(numWorker)+1):
        if session.get('filename_%s' % i) is not None:
            listFile[i] = session.get("filename_%s" % i)
        # else:
        #     listFile[i] = "None"
    return render_template("upload_mini.html", files = listFile)

@bench.route('/upload/<name>', methods=['GET', 'POST'])
def upload(name):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        # if file and allowed_file(file.filename):
        if file:
            ip_index = request.form.get('ip')
            filename = secure_filename(file.filename)
            unique_filename = make_unique(filename)
            file.save(os.path.join("/home/trind/ansible-projects/cis-bench-k8s-ansible/CISBenchApp/upload", unique_filename))
            session['filename_%s' % ip_index] = unique_filename
            return redirect(url_for('bench.upload_key_mini'))
    return render_template("upload.html", name=name)

@bench.route('/overview', methods=['GET'])
def overview():
    numWorker = session.get('num_worker')
    listIP = []
    listFile = []
    if (numWorker != 0 ):
        print(int(numWorker))
        for i in range (0,int(numWorker)+1):
            print(i)
            listIP.append(session.get("ip_%s" % i))
            listFile.append(session.get("filename_%s" % i))
    print(listIP)
    print(listFile)
    return render_template("overview.html", ips=listIP, files=listFile)

@bench.route('/run_bench', methods=['GET'])
def run_bench():
    numWorker = session.get('num_worker')
    listIP = []
    listFile = []
    if (numWorker != 0 ):
        print(int(numWorker))
        for i in range (0,int(numWorker)+1):
            print(i)
            listIP.append(session.get("ip_%s" % i))
            listFile.append(session.get("filename_%s" % i))
    print(listIP)
    print(listFile)

    print("Request received1")
    writeInventory_mini(listIP, listFile)
    bench_mini()
    print("Request received2")

    return render_template("run_bench.html")

def writeInventory_mini(listIP, listFile):

    file_name = config_get("ansible", "inventory")

    masterSsh = os.path.join("/home/trind/ansible-projects/cis-bench-k8s-ansible/CISBenchApp/upload", listFile[0])

    cmd = ["chmod", "600", "%s" % masterSsh]
    subprocess.run(cmd)

    hosts_data = "[masters]\n" + \
                "%s ansible_ssh_private_key_file=%s\n" % (listIP[0], masterSsh)

    hosts_data += "[workers]\n" 

    for i in range(1,len(listIP)):
        workerSsh = os.path.join("/home/trind/ansible-projects/cis-bench-k8s-ansible/CISBenchApp/upload", listFile[i])
        cmd = ["chmod", "600", "%s" % workerSsh]
        subprocess.run(cmd)
        hosts_data += "%s ansible_ssh_private_key_file=%s\n" % (listIP[i], workerSsh)

    hosts_data += "[k8s:children]\n" + \
                "masters\n" + \
                "workers\n" + \
                "[k8s:vars]\n" + \
                "ansible_user=docker\n" + \
                "[local]\n" + \
                "localhost ansible_connection=local"
    with open(file_name, 'w') as configfile:
        configfile.write(hosts_data)

def bench_mini():
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        cmd = ["%s" % (config_get("ansible", "bin")),"-i" ,"%s" % (config_get("ansible", "inventory")),"%s" % (config_get("minikube", "bench"))]
        file_name = "logs/playbook_logs/playbook_%s.log" % now
        
        with open(file_name, "w") as w_file:
            subprocess.run(cmd, stdout=w_file)
    
        mylogging("INFO: Run bench playbook succeed")
        return jsonify(respJson(0, "Run bench playbook succeed, view at %s" % file_name))

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))

@bench.route('/result/<name>', methods=['GET'])
def result(name):
    if name == "master":
        return render_template("result/minikube/master_benchmark_output.html")
    if name == "worker":
        return render_template("result/minikube/worker_benchmark_output.html")
    return redirect(request.url)
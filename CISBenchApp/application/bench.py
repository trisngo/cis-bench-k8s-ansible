from flask import Blueprint, Flask, render_template, request, flash, jsonify, redirect, url_for, session, Response
import sys, json, datetime, time, hashlib, urllib.request, urllib.parse, subprocess, importlib, configparser, os
from werkzeug.utils import secure_filename
from uuid import uuid4
from . import mylogging, config_get, respJson
from jinja2 import Environment,FileSystemLoader

bench = Blueprint('bench', __name__)

ALLOWED_EXTENSIONS = {''}

def make_unique(string):
    ident = uuid4().__str__()
    return f"{ident}-{string}"


@bench.route('/input', methods=['GET', 'POST'])
def handle_input():
    if request.method == 'POST':
        session.clear()
        platform = request.form.get('platform')
        session['platform'] = platform.lower()
        print(platform)
        if platform == "Minikube":
            num_node = request.form.get('cta-num-select')
            print(num_node)
            type_dict = {}
            ipadd_dict = {}
            filename_dict = {}

            for key, val in request.form.items():
                #print(key,val)
                if key.startswith("type"):
                    type_dict[key] = val
                if key.startswith("ipadd_mini"):
                    ipadd_dict[key] = val

            print("Type dictionary is: ", type_dict)
            print("Ip add dictionary is: ", ipadd_dict)
            print(request.files)

            for key, val in request.files.items():
                if val.filename == '':
                    print('No selected file')
                    return redirect(request.url)
                if val:
                    filename = secure_filename(val.filename)
                    unique_filename = make_unique(filename)
                    val.save(os.path.join(config_get("data_store", "dir"), unique_filename))
                    filename_dict[key] = unique_filename
            print("Filename dictionary is: ", filename_dict)
            writeInventory_mini(ipadd_dict, filename_dict)
            session['ipadd_dict'] = ipadd_dict
            session['filename_dict'] = filename_dict
            return render_template('run_mini.html')
        elif platform == "AKS":
            ipadd_dict = {}
            rg = request.form.get('az_rg')
            cluster_name = request.form.get('az_aks_cluster')
            print(rg)
            print(cluster_name)
            for key, val in request.form.items():
                if key.startswith("ipadd_aks"):
                    ipadd_dict[key] = val
            if check_aks_cluster(rg,cluster_name):
                create_ssh_aks(rg, cluster_name)
                writeInventory_aks(ipadd_dict)
                session['ipadd_dict'] = ipadd_dict
                return render_template('run_aks.html')
    return redirect(url_for('views.home'))

def check_aks_cluster(rg,name):
    linecount = int(subprocess.check_output("az aks show --resource-group %s --name %s 2>/dev/null | wc -l" % (rg, name), shell=True).split()[0])
    print(linecount)
    if linecount > 0:
        return True
    return False

def create_ssh_aks(rg, name):
    script_path = config_get("DEFAULT", "aks_ssh")
    cmd = "bash %s -g %s -n %s -d any -c 'echo \"Finish create ssh proxy on $(hostname)\"'" % (script_path, rg, name)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    return_code = process.wait()
    if return_code == 0:
        pod_ssh = "aks-ssh-session"
        cmdPortForward = "kubectl port-forward %s 2022:22" % pod_ssh
        processPortForward = subprocess.Popen(cmdPortForward, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)

def writeInventory_aks(dictIP):
    file_name = config_get("ansible", "inventory")
    pod_ssh = "aks-ssh-session"
    nodeName = str(subprocess.check_output("kubectl get pods -o wide | grep %s | awk -v OFS='\t\t' '{print $7}'" % (pod_ssh), shell=True).split()[0].decode("utf-8"))
    keyPath = "~/.ssh/aks_ssh_%s" % nodeName
    hosts_data = "[aks_masters]\n"

    hosts_data += "[aks_workers]\n"

    for i in range(0,len(dictIP)):
        hosts_data += "%s ansible_ssh_private_key_file=%s\n" % (dictIP["ipadd_aks" + str(i)], keyPath)

    hosts_data += "[aks:children]\n" + \
                "aks_masters\n" + \
                "aks_workers\n" + \
                "[aks:vars]\n" + \
                "ansible_user=azureuser\n" + \
                f"ansible_ssh_common_args='-o ProxyCommand=\"ssh -i {keyPath} -p 2022 -W %h:%p root@127.0.0.1\" -o StrictHostKeyChecking=no'\n" + \
                "[local]\n" + \
                "localhost ansible_connection=local"
    with open(file_name, 'w') as configfile:
        configfile.write(hosts_data)

@bench.route('/bench_aks',methods=['GET'])
def bench_aks():
    try:
        now = datetime.datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")
        session['bench_time'] = dt
        cmd = ["%s" % (config_get("ansible", "bin")),"-i" ,"%s" % (config_get("ansible", "inventory")),"%s" % (config_get("aks", "bench"))]
        def inner():
            proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,)
            for line in proc.stdout:
                yield line.rstrip().decode("utf-8")  + '<br/>'

        mylogging("INFO: Run bench playbook succeed")
        env = Environment(loader=FileSystemLoader('application/templates'))
        tmpl = env.get_template('benchmark_progress.html')
        return Response(tmpl.generate(result=inner()),mimetype='text/html')

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))

@bench.route('/harden', methods=['GET'])
def bench_again():
    platform = session['platform']
    if platform == "minikube":
        ipadd_dict = {}
        filename_dict = { }
        ipadd_dict = session['ipadd_dict']
        filename_dict = session['filename_dict']
        writeInventory_mini(ipadd_dict, filename_dict)
        return render_template('run_mini.html')
    elif platform == "aks":
        ipadd_dict = {}
        ipadd_dict = session['ipadd_dict']
        writeInventory_aks(ipadd_dict)
        return render_template('run_aks.html')
    return redirect(url_for('views.home'))

def writeInventory_mini(dictIP, dictFilename):
    file_name = config_get("ansible", "inventory")
    masterSsh = os.path.join(config_get("data_store", "dir"), dictFilename["file0"])
    cmd = ["chmod", "600", "%s" % masterSsh]
    subprocess.run(cmd)

    hosts_data = "[masters]\n" + \
                "%s ansible_ssh_private_key_file=%s\n" % (dictIP["ipadd_mini0"], masterSsh)

    hosts_data += "[workers]\n" 

    for i in range(1,len(dictIP)):
        workerSsh = os.path.join(config_get("data_store", "dir"), dictFilename["file" + str(i)])

        cmd = ["chmod", "600", "%s" % workerSsh]
        subprocess.run(cmd)
        hosts_data += "%s ansible_ssh_private_key_file=%s\n" % (dictIP["ipadd_mini" + str(i)], workerSsh)

    hosts_data += "[k8s:children]\n" + \
                "masters\n" + \
                "workers\n" + \
                "[k8s:vars]\n" + \
                "ansible_user=docker\n" + \
                "ansible_ssh_common_args='-o StrictHostKeyChecking=no'\n" + \
                "[local]\n" + \
                "localhost ansible_connection=local"
    with open(file_name, 'w') as configfile:
        configfile.write(hosts_data)

@bench.route('/bench_mini',methods=['GET'])
def bench_mini():
    try:
        now = datetime.datetime.now()
        dt = now.strftime("%d/%m/%Y %H:%M:%S")
        session['bench_time'] = dt
        cmd = ["%s" % (config_get("ansible", "bin")),"-i" ,"%s" % (config_get("ansible", "inventory")),"%s" % (config_get("minikube", "bench"))]
        def inner():
            proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,)
            for line in proc.stdout:
                yield line.rstrip().decode("utf-8")  + '<br/>'

        mylogging("INFO: Run bench playbook succeed")
        env = Environment(loader=FileSystemLoader('application/templates'))
        tmpl = env.get_template('benchmark_progress.html')
        return Response(tmpl.generate(result=inner()),mimetype='text/html')

    except Exception as ex:
        mylogging("ERROR: %s" %ex)
        return jsonify(respJson(-500, "Something went wrong!"))


@bench.route('/result', methods=['GET'])
def result():
    today = datetime.datetime.now(datetime.timezone.utc)
    bench_time = session['bench_time']
    date = today.strftime("%Y-%m-%d")
    multi_dict = request.args
    for key in multi_dict:
        print(multi_dict.get(key))
        print(multi_dict.getlist(key))

    if 'ipadd' in request.args:
        # parameter 'varname' is specified
        ipadd = request.args.get("ipadd")
        return render_template("result/minikube/%s_benchmark_%s.html" % (ipadd,date), ip_address=ipadd, bench_time=bench_time)
    else:
        print("IPadd Argument not provided, go to Dashboard")
        ipadd_dict = session['ipadd_dict']
        return render_template("result_dashboard.html", ipadd_dict=ipadd_dict)


# @bench.route('/submitRemediation', methods=['GET']) #POST
# def storeOption():
#     post_data = '{"task": ["3.1.1", "3.2.2", "3.3.1"]}'
#     try:
#         # date = request.headers.get('date')
#         file_name = "%s/options.yml" % (config_get("data_store", "dir"))
#         # post_data = request.get_data()
    
#         data  = json.loads(post_data)
#         print (data['task'])

#         # w_file = open(file_name, "w")
#         # w_file.write(data.decode("utf-8"))

#         with open(file_name, 'w') as w_file:
#             for item in data['task']:
#                 w_file.write("task_%s: true\n" % item)

#         # w_file.close()
#         mylogging("INFO: Selections store succeed")
#         return jsonify(respJson(0, "Store selection succeed"))

#     except Exception as ex:
#         mylogging("ERROR: %s" %ex)
#         return jsonify(respJson(-500, "Something went wrong!"))

# @bench.route('/runRemediation', methods=['GET'])
# def remediation():
#     try:
#         now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
#         cmd = ["%s" % (config_get("ansible", "bin")),"-i" ,"%s" % (config_get("ansible", "inventory")),"%s" % (config_get("minikube", "config"))]
#         file_name = "logs/playbook_logs/playbook_%s.log" % now
        
#         with open(file_name, "w") as w_file:
#             subprocess.run(cmd, stdout=w_file)
    
#         mylogging("INFO: Run remediation playbook succeed")
#         return jsonify(respJson(0, "Run remediation playbook succeed, view at %s" % file_name))

#     except Exception as ex:
#         mylogging("ERROR: %s" %ex)
#         return jsonify(respJson(-500, "Something went wrong!"))
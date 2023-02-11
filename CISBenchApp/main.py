#!/usr/bin/python3

from application import create_app, mylogging, config_get

# from flask import Flask, jsonify, request, redirect, abort


if __name__ == '__main__':
    try:
        config_get("ansible", "bin")
        config_get("logging", "dir")
        config_get("data_store", "dir")
        config_get("minikube", "result_dir")
        config_get("aks", "result_dir")
        UPLOAD_FOLDER = config_get("data_store", "dir")
        app = create_app()
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
        app.run(host=config_get("web_server", "host"), port=int(config_get("web_server", "port")), debug=False, threaded=True)
    except Exception as ex:
        mylogging("ERROR: Config: %s" %ex)
        print ("API start failed")
        exit()

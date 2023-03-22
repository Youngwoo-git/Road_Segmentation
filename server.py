import numpy as np
import os, sys

import json
import base64
import io
import json
from flask import Flask, jsonify, request
from PIL import Image

import csv
import base64
import argparse
import hydra
import torch
import subprocess


parser = argparse.ArgumentParser(description='PreLabel')
parser.add_argument('-p', '--port', default=9876, help='Port Number')
args = parser.parse_args()
app = Flask(__name__)



current_pid = None

@app.route('/stop', methods=['POST'])
def stop():
    
    current_pid.kill()

    with open('log.txt', 'r') as f:
        try:
            curr_state = f.readlines()[-1].strip()
        except:
            curr_state = "Initializing..."
    
    f.close()
    
    with open('log.txt', 'w') as f:
        f.write("No process is currently running")
        curr_state = "No process is currently running"
    f.close()
    
    return jsonify({'state':curr_state})

@app.route('/progress', methods=['POST'])
def progress():
    
    with open('log.txt', 'r') as f:
        try:
            curr_state = f.readlines()[-1].strip()
        except:
            curr_state = "Initializing..."
    
    f.close()
    
    return jsonify({'state':curr_state})

@app.route('/prelabel', methods=['POST'])
def predict():
    if request.method == 'POST':
        
        r = request
        
        data_json = r.data
        data_dict = json.loads(data_json)
        
        #img_path는 폴더위치;
        img_dir = data_dict['img_dir']
        data_type = data_dict['type']
        
        cwd = os.getcwd()
        if data_type == "prelabel":
            os.chdir("hybridnets")
            global current_pid
            current_pid = subprocess.Popen(["python", "prelabel_seg.py", "++source={}".format(img_dir)])
            current_pid.wait()
            os.chdir(cwd)
            
            os.chdir("yolov5")
            current_pid = subprocess.Popen(["python", "prelabel_det.py", "++source={}".format(img_dir)])
            current_pid.wait()
            os.chdir(cwd)
#         elif data_type == "det_only"
#         elif data_type == "seg_only"
        else:
            return sonify({'state':"fail"})

        return jsonify({'state':"success"})

if __name__ == '__main__':
    if not os.path.isfile("log.txt"):
        with open('log.txt', 'w') as f:
            f.write("No process is currently running")    
    
    app.run(host='0.0.0.0', port=args.port, debug=True)
    
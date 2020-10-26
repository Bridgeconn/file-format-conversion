import os
import urllib.request
# from app2 import app
from flask import Flask, request, redirect, jsonify,send_from_directory,url_for
from werkzeug.utils import secure_filename
from usfm_to_csv import usfm_to_csv
from md_to_csv import md_to_csv
from html_to_csv import html_to_csv
from csv_to_usfm import csv_to_usfm
from txt_to_usfm import txt_to_usfm
# from docx_to_usfm import docx_to_usfm

ALLOWED_EXTENSIONS = set(['usfm','csv','md','xlsx'])
Target_type  = ['usfm','csv','md','docx']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = '/home/savitha/Pictures/File_conversion_26-10-2020_final'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['POST'])
def file_conversion():
    if 'file' not in request.files:
        resp = jsonify({'message' : 'file is not selected'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    print (file)
    
    file_read = file.readlines()
    print (file_read)
    
    tareget_file_type = request.form["tareget_file_type"]

    if file.filename == '':
        resp = jsonify({'message' : 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    
    # file = request.files['file']
    # print (file)
    
    # file_read = file.read()
    # print (file_read)
    # tareget_file_type = request.form["tareget_file_type"]
    
    if tareget_file_type == '':
        resp = jsonify({'message' : 'please input target type'})
        resp.status_code = 400
        
    if tareget_file_type not in Target_type:
        resp = jsonify({'message' : 'invalid target type'})
        resp.status_code = 400
    
    if file and allowed_file(file.filename) and Target_type:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    if filename:
        file_extension = filename.split(".")[-1]
        if file_extension == 'usfm' and Target_type == 'csv':
            usfm_to_csv(file_read)
            return 'usfm to csv conversion is done!'
        
        elif file_extension == 'csv' and Target_type == 'usfm':
            csv_to_usfm(file_read)
            return 'csv to usfm conversion is done!'
        
        elif file_extension == 'html' and Target_type == 'csv':
            html_to_csv(file_read)
            return 'html to csv conversion is done!'
        
        elif file_extension == 'docx' and Target_type == 'usfm':
            docx_to_usfm(file_read)
            return 'docx to usfm conversion is done!'
        
        elif file_extension == 'md' and Target_type == 'csv':
            md_to_csv(file_read)
            return 'md to csv conversion is done!'
        
        elif file_extension == 'txt' and Target_type == 'usfm':
            txt_to_usfm(file_read)
            return 'txt to usfm conversion done!'
        
    else:
        resp = jsonify({'message' : 'method not allowed'})
        resp.status_code = 400
        return resp
    
if __name__ == "__main__":
     app.run()
        
        
        
    

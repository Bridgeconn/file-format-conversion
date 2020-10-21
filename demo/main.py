import os
import urllib.request
# from app2 import app
from flask import Flask, request, redirect, jsonify,send_from_directory,url_for
from werkzeug.utils import secure_filename
from usfm_to_csv import usfm_to_csv
from md_to_csv import md_to_csv
from csv_to_usfm import csv_to_usfm
# from html_to_csv import html_to_csv

ALLOWED_EXTENSIONS = set(['usfm', 'csv', 'md', 'docx', 'tsv', 'xlsx','html'])
# ALLOWED_EXTENSIONS = set(['usfm'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from flask import Flask, send_from_directory
import os

UPLOAD_FOLDER = '/home/savitha/Music/Python_class/file-format-conversion/demo'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

out_put_csv = 'csv'
out_put_usfm = 'usfm'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/file-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # usfm_to_csv(filename)
        # print (filename)
        
		resp = jsonify({'message' : 'File uploaded successfully!'})
        # print (filename)
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file type is usfm'})
		resp.status_code = 400
		return resp

@app.route('/file_conversion/<filename>',methods=['POST'])
def file_conversion(filename):
    # out_put_file_type = 'csv'
    file_extension = filename.split(".")[-1]
    if file_extension == "usfm" and out_put_csv == "csv":
        usfm_to_csv(filename)
        resp = jsonify({'message' : 'usfm to csv conversion is done'})
        resp.status_code = 201
        return resp
    elif file_extension == "md" and out_put_csv == "csv":
        md_to_csv(filename)
        resp = jsonify({'message' : 'md to csv conversion is done'})
        resp.status_code = 201
        return resp
    # elif file_extension == "html" and out_put_csv == "csv":
    #     html_to_csv(filename)
    #     resp = jsonify({'message' : 'html to csv conversion is done'})
    #     resp.status_code = 201
    #     return resp
    
    elif file_extension == "csv" and out_put_usfm == "usfm":
        csv_to_usfm(filename)
        resp = jsonify({'message' : 'md to csv conversion is done'})
        resp.status_code = 201
        return resp
    
    
	# elif 
    
    
    else:
        resp = jsonify({'message' : 'method is not allowed'})
        resp.status_code = 400

# @app.route('/usfm-csv', methods=['POST'])
# def usfm_csv_conversion():
#     out_put_file_type = 'csv'
#     if filename:
#         file_extension = filename.split(".")[-1]
#         if file_extension == "usfm" and out_put_file_type == "csv":
#             usfm_to_csv(input_file)
#             resp = jsonify({'message' : 'usfm to csv conversion is done'})
#             resp.status_code = 201
#         else:
#             resp = jsonify({'message' : 'mrthod is not allowed'})
#             resp.status_code = 400
            
if __name__ == "__main__":
    app.run()
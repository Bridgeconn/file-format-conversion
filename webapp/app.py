import os, sys, uuid, datetime, json, logging, requests, pdb
from datetime import timedelta

import flask
from flask import Flask, request, session, redirect, jsonify, make_response, send_from_directory, render_template, url_for, flash, send_file, Response
from mimetypes import MimeTypes
from tempfile import mkdtemp

from flask_paginate import Pagination, get_page_parameter

from flask_cors import CORS, cross_origin

from werkzeug import serving
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from forms import SourceUploadForm

if 'logs' not in os.listdir(os.getcwd() + '/'):
    os.mkdir(os.getcwd() + '/logs')

logging.basicConfig(filename='logs/file_webapp_logs.log', format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('logs/file_webapp_logs.log')
logger.setLevel(logging.DEBUG)

app = Flask(__name__)
CORS(app)

api_base_url = os.getenv('', 'http://localhost:8088/v1')
app.secret_key = "secret_key"
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

@app.before_request
def make_session_permanent():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(hours=24)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'GET':
		return render_template('registration.html')
	if request.method == 'POST':

		userName = request.form.get('user_name')
		email = request.form.get('email')
		password = request.form.get('password')
		cnfpassword = request.form.get('confirmpassword')
		if email == None:
			flash("Please provide email")
			return redirect(url_for('signup'))
		if password != cnfpassword:
			flash("Please check your password")
			return redirect(url_for('signup'))

		params = {"email" : email, "password":password, "user_name" : userName}
		headers = {"Content-type": "application/json"}
		resp = requests.post(api_base_url + "/registration/",
								 data=json.dumps(params), headers=headers)

		res = resp.json()
		if resp.status_code == 409:
			flash(res["message"])
			return redirect(url_for('signup'))
		if resp.status_code == 201:
			flash(res["message"])
			return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	if session.get("token") is None:
		if request.method == 'GET':
			return render_template('login.html')
		if request.method == 'POST':
			email = request.form.get('email')
			password = request.form.get('password')

			params = {"email":email, "password":password}
			headers = {"Content-type": "application/json"}
			resp = requests.post(api_base_url + "/login/",
									 data=json.dumps(params), headers=headers)

			res = resp.json()
			if resp.status_code == 401:
				flash(res['message'])
				return redirect(url_for('login'))

			if resp.status_code == 200:
				session['token'] = res['token']
				return redirect(url_for('index'))
	else:
		flash("Already logged in...")
		return redirect(url_for('index'))

@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
	if not session.get("token") is None:
		headers = {"x-access-token" : session["token"]}
		return render_template('home.html')
		# return jsonify({"message": "Successfully loged In"}), 201
	else:
		return redirect(url_for("login")) 

@app.route('/logout')
def logout():
	session.pop('token', None)
	return redirect(url_for('login'))

@app.route('/forgetpassword', methods=['GET', 'POST'])
def forgetpassword():
	if request.method == 'GET':
		return render_template('forget_password.html')
	if request.method == 'POST':
		email = request.form.get('email')
		logger.info("%s initiated password reset..", email)
		if email == None:
			flash("Please provide email")
			return redirect(url_for('forgetpassword'))

		params = {"email" : email}
		headers = {"Content-type": "application/json"}
		resp = requests.post(api_base_url + "/forgetpassword", data=json.dumps(params), headers=headers)

		res = resp.json()
		print(resp)
		if resp.status_code == 401:
			flash(res["message"])
			return redirect(url_for('forgetpassword'))

		if resp.status_code == 201:
			flash(res["message"])
			return redirect(url_for('resetpassword'))

@app.route('/resetpassword', methods=['GET', 'POST'])
def resetpassword():
	if request.method == 'GET':
		return render_template('reset_password.html')
	if request.method == 'POST':
		temporaryPassword = request.form.get('temporaryPassword')
		password = request.form.get('password')
		
		logger.info("temp password = %s and password = %s", temporaryPassword, password)
		if (password == None) and (temporaryPassword == None):
			flash("Please enter valid entry!")
			return redirect(url_for('resetpassword'))

		params = {"temporaryPassword" : temporaryPassword, "password" : password}
		headers = {"Content-type": "application/json"}
		resp = requests.post(api_base_url + "/resetpassword",
								 data=json.dumps(params), headers=headers)

		res = resp.json()

		if resp.status_code == 401:
			flash(res["message"])
			return redirect(url_for('resetpassword'))

		if resp.status_code == 201:
			flash(res["message"])
			return redirect(url_for('login'))

@app.route('/source_upload/', methods=['GET'])
@app.route('/source_upload', methods=['GET'])
def source_upload():
	if (not session['token'] is None) and (session.get("role") in ['super_admin', 'project_admin', 'translator']):
		form = SourceUploadForm()
		if form.validate_on_submit():
			sourceLanguage = form.sourceLanguage.data
			sourceDomain = form.sourceDomain.data
			file = file
			return redirect(url_for('upload_file', sourceDomain=sourceDomain, sourceLanguage=sourceLanguage,file=file))
		return render_template('source_upload.html', form=form)

@app.route('/files/', methods=['GET','POST'])
@app.route('/files', methods=['GET','POST'])
def upload_file():
	if not session.get("token") is None:
		if request.method == 'GET':
			#TODO START: pagination
			search = False
			q = request.args.get('q')
			page = request.args.get(get_page_parameter(), type=int, default=1)

			#TODO END:
			headers = {"x-access-token" : session["token"]}
			sources = requests.get(api_base_url+"/files", headers=headers)
			source_data = sources.json()
			pagination = Pagination(page=page, css_framework='bootstrap3', total=len(source_data['sources']), search=search, record_name='sources')
			if source_data:
				return render_template('sources.html', sources=source_data['sources'], pagination=pagination, languages=source_data['languages'])

		if request.method == 'POST':
			file = request.files["file"]
			sourceFileName = secure_filename(file.filename)

			cwd = os.getcwd()+'/'
			if 'temp' not in os.listdir(cwd):
				os.mkdir(cwd + 'temp')
			file.save(os.path.join(cwd + 'temp', sourceFileName))
			
			targetType = request.form.get('targetType')

			params = {"targetType": targetType}
			headers = {"x-access-token": session["token"]}

			with open(cwd + 'temp/'+ sourceFileName, 'rb') as f:
				data_file = ImmutableMultiDict([("file", f)])
				resp = requests.post(api_base_url + "/file_upload",
									 files=data_file, data=params, headers=headers)

			if resp.status_code == 201:
				files = requests.get(api_base_url+"/files", headers=headers)
				file_data = files.json()
				if file_data:
					return render_template('sources.html', sources=file_data['files'])
	else:
		flash("not permitted this page!")
		return redirect(url_for("login"))

# @app.errorhandler(500)
# def internal_server_error(error):
# 	app.logger.error('Server Error: %s', (error))
# 	return render_template('500.html'), 500

# @app.errorhandler(Exception)
# def unhandled_exception(e):
# 	app.logger.error('Unhandled Exception: %s', (e))
# 	return render_template('500.html'), 500


if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8081)

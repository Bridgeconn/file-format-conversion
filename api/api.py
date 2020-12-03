import os
import re
import jwt
import json
import uuid
import logging
import requests
import datetime
import traceback
from random import randint

from functools import wraps
from collections import defaultdict
from unicodedata import normalize
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from flask import Flask, request, session, redirect, jsonify, make_response, send_from_directory

from configs.config import get_db, close_db, allowed_file

from converters.converter_script import * #usfm_to_csv, html_to_csv,md_to_csv,xlsx_to_txt,csv_to_usfm

import pdb

if 'logs' not in os.listdir(os.getcwd() + '/'):
    os.mkdir(os.getcwd() + '/logs')
logging.basicConfig(filename='logs/file_api_logs.log', format='%(asctime)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
logger = logging.getLogger('logs/file_api_logs.log')
logger.setLevel(logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = "fileconverterapis"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024

PREFIX = "/v1"
be_api_url = os.getenv("", "localhost:8088")


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        logger.info('Token: %s', token)
        if not token:
            return jsonify({"message": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            connection = get_db()
            cursor = connection.cursor()
            cursor.execute(
                "select public_id from users where public_id=%s",
                (data['public_id'],))
            current_user = cursor.fetchone()
        except:
            traceback.print_exc()
            return jsonify({"message": "Token is invalid!"}), 401
        return f(current_user, *args, **kwargs)

    return decorator


@app.route(PREFIX + "/registration/", methods=['POST'])
@app.route(PREFIX + "/registration", methods=['POST'])
def registration():
    # pdb.set_trace()
    logger.info("---------------------- User registration api ----------------------")
    data = request.get_json(True)
    print(request)
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("select email from users where email=%s", (data['email'],))

    existing_user = cursor.fetchone()
    if existing_user:
        logger.info("An email address already exists.")
        return jsonify({"message": "An email address already exists."}), 409
    else:
        verification_code = str(uuid.uuid4()).replace("-", "")
        cursor.execute(
            "INSERT INTO users (email, public_id, password, user_name, verification_code) VALUES (%s,%s,%s,%s,%s);",
            (data['email'], str(uuid.uuid4()), hashed_password, data['user_name'],verification_code))
        connection.commit()

        print("\nSending email verification .....\n")
        logger.info("Sending email verification")
        headers = {"api-key": '3nXcT1fANr7UYwD5'}
        url = "https://api.sendinblue.com/v2.0/email"
        msg = '''Hello %s,<br/><br/>Thanks for your interest to use the BCS File Conveter web service! <br/>\
		<br/>You need to confirm your email address by opening this link: <a href="http://%s/v1/verifications/%s" >click me</a> \
		<br/><br/>Thanks,<br/>BCS File Conveter web service''' % (data['user_name'], be_api_url, verification_code)
        payload = {
            "to": {data['email']: ""},
            "from": ["bridgengine@gmail.com"],
            "subject": "BCS FILE CONVETER - Please verify your email address",
            "html": msg,
        }
        logger.info(msg)
        print(msg)
        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        logger.info("User created!")
        return jsonify({"message": "Account created, Please check email and confirm your account!"}), 201


@app.route(PREFIX + "/verifications/<code>/", methods=["GET"])
@app.route(PREFIX + "/verifications/<code>", methods=["GET"])
def new_registration(code):
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM users WHERE verification_code = %s AND email_verified = False", (code,))
    if cursor.fetchone():
        cursor.execute("UPDATE users SET email_verified = True WHERE verification_code = %s", (code,))
    cursor.close()
    connection.commit()
    logger.info("User verified!")
    return jsonify({"message": "Account verified"}), 201
    # return redirect("http://%s/" % (be_ui_url))
    


@app.route(PREFIX + "/forgetpassword", methods=["POST"])
def request_reset_password():
    data = request.get_json(True)
    email = data['email']
    logger.info("%s initiated password reset..", email)
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT email, email_verified from users WHERE email = %s", (email,))
    rst = cursor.fetchone()
    if not rst:
        return jsonify({"message": "Email has not yet been registered"}), 401
    else:
        status = rst[1]
        if not True:
            return '{"message":"Your account/email is not verified!"}'

        headers = {"api-key": '3nXcT1fANr7UYwD5'}
        url = "https://api.sendinblue.com/v2.0/email"

        verification_code = randint(100001, 999999)

        msg = '''Hello,<br/><br/>Your request for resetting the password has been recieved. <br/>
		Your temporary password is %s. Use this to create a new password at <a href="%s/resetpassword">link</a> . 

		<br/><br/>Thanks,<br/>BCS File Conveter Web Service''' % \
              (verification_code, be_api_url)
        payload = {
            "to": {email: ""},
            "from": ["bridgengine@gmail.com", "Bridge Engine"],
            "subject": "BCS FILE CONVETER - Password reset verification mail",
            "html": msg,
        }
        logger.info(msg)
        cursor.execute("UPDATE users SET verification_code= %s WHERE email = %s", \
                       (verification_code, email))
        cursor.close()
        connection.commit()
        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        return jsonify({"message": "Link to reset password has been sent to the registered mail ID"}), 201


@app.route(PREFIX + "/resetpassword", methods=["POST"])
def reset_password():
    data = request.get_json(True)

    temp_password = data['temporaryPassword']
    password = data['password']
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute("SELECT email FROM users WHERE verification_code = %s \
		AND email_verified = True", (temp_password,))
    rst = cursor.fetchone()
    if not rst:
        return jsonify({"success": False, "message": "Invalid temporary password."}), 401
    else:
        email = rst[0]
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        cursor.execute("UPDATE users SET verification_code = %s, password = %s \
			WHERE email = %s", (temp_password, hashed_password, email))
        cursor.close()
        connection.commit()
        logger.info("temp password = %s and password = %s given by  %s", temp_password, password, email)

        logger.info("%s changed password successfully ", email)
        return jsonify({"success": True, "message": "Password has been reset. Login with the new password."}), 201


@app.route(PREFIX + "/login/", methods=['POST'])
@app.route(PREFIX + "/login", methods=['POST'])
def login():
    logger.info("---------------------- Login api ----------------------")
    data = request.get_json(True)
    logger.info('Email : %s', data['email'])
    if not data or not data['email'] or not data['password']:
        logger.info('Could not verify : data not available')
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic relm="Login Required!"'})

    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(
        "select public_id, password, email_verified from users where email=%s",
        (data['email'],))
    user = cursor.fetchone()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic relm="Login Required!"'})

    if user[2] != True:
        return jsonify({'message': 'Please verify your email!'}), 401

    if check_password_hash(user[1], data['password']):
        token = jwt.encode({'public_id': user[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8'), 'verified': user[2]}), 200
    else:
        return jsonify({'message': 'Password or email is incorrect!'}), 401

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic relm="Login Required!"'})


@app.route(PREFIX + '/files/', methods=['GET'])
@app.route(PREFIX + '/files', methods=['GET'])
@token_required
def fetch_file(current_user):
    if request.method == 'GET':
        logger.info("---------------------- Fetch file api ----------------------")
        try:
            connection = get_db()
            cursor = connection.cursor()
            cursor.execute("select user_id from users where public_id=%s", (current_user[0],))
            user_id = cursor.fetchone()

            q = request.args.get('q')  # params q as data limit send by user
            if q:
                cursor.execute(
                    "select file_id, file_path, file_name from files_data where user_id=%s order by file_id desc limit %s",
                    (user_id, int(q)))
            else:
                cursor.execute(
                    "select file_id, file_path, file_name from files_data where user_id=%s order by file_id desc",
                    (user_id,))
            rows = cursor.fetchall()

            resp = jsonify({'files': rows})
            resp.status_code = 201
            return resp
            close_db()
        except Exception as e:
            print(e)
            resp = jsonify({'message': 'Server Error'})
            resp.status_code = 500
            return resp

@app.route(PREFIX + '/source_upload/', methods=['POST'])
@app.route(PREFIX + '/source_upload', methods=['POST'])
@token_required
def upload_file2(current_user):
    if request.method == 'POST':
        logger.info("---------------------- File upload api ----------------------")
        try:
            if 'file' not in request.files:
                resp = jsonify({'message': 'No file part in the request'})
                resp.status_code = 400
                logger.info("No file part in the request")
                return resp
            file = request.files['file']
            if file.filename == '':
                resp = jsonify({'message': 'No file selected for uploading'})
                resp.status_code = 400
                logger.info("No file selected for uploading")
                return resp
            if file and allowed_file(file.filename):
                sourceFileName = secure_filename(file.filename)
                targetType = request.form.get('targetType')

                logger.info("Source file : %s", sourceFileName)

                fileType = file.filename.split("/")[-1].split(".")[-1]

                combineDir = UPLOAD_FOLDER + '/' + current_user[0] + '/'
                source_directory = str(combineDir)
                os.makedirs(os.path.join(source_directory), exist_ok=True)

                connection = get_db()
                cursor = connection.cursor()

                cursor.execute("select user_id from users where public_id=%s", (current_user[0],))
                userId = cursor.fetchone()


                file.save(os.path.join(source_directory, sourceFileName))
                logger.info("File saved in directory : %s", source_directory)

                sourceFilePath = source_directory
                
                cursor.execute(
                    "INSERT INTO files_data (file_path, file_name, target_type, user_id) VALUES (%s,%s,%s,%s);",
                    (sourceFilePath, sourceFileName, targetType, userId))
                connection.commit()
                logger.info("Saved source file content in db")
                
                
                path = sourceFilePath +sourceFileName
                 
                if fileType == "usfm" and targetType == "csv":
                    target_file_csv = usfm_to_csv(path)
                    # print(target_file)

                    target_file_path_1, file_name = os.path.split(target_file_csv)

                    cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
                    connection.commit()
                    resp = jsonify({'message': 'File successfully converted'})
                    resp.status_code = 201
                    return resp
                    close_db()
                    
                    
                elif fileType == "csv" and targetType == "usfm":
                    target_file_usfm = csv_to_usfm(path)
                    # print(target_file)

                    target_file_path_2, file_name = os.path.split(target_file_usfm)

                    cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
                    connection.commit()
                    resp = jsonify({'message': 'File successfully converted'})
                    resp.status_code = 201
                    return resp
                    # close_db()
                    
                elif fileType == "html" and targetType == "csv":
                    target_file_html_csv = html_to_csv(path)
                    # print(target_file)

                    target_file_path_3, file_name = os.path.split(target_file_html_csv)

                    cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
                    connection.commit()
                    resp = jsonify({'message': 'File successfully converted'})
                    resp.status_code = 201
                    return resp
                
                elif fileType == "md" and targetType == "csv":
                    target_file_md_csv = md_to_csv(path)
                    # print(target_file)

                    target_file_path_4, file_name = os.path.split(target_file_md_csv)
                    cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
                    connection.commit()
                    resp = jsonify({'message': 'File successfully converted'})
                    resp.status_code = 201
                    return resp
                
                elif fileType == "xlsx" and targetType == "txt":
                    target_file_xlsx_txt = xlsx_to_txt(path)
                    # print(target_file)

                    target_file_path_5, file_name = os.path.split(target_file_xlsx_txt)
                    # cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
                    # connection.commit()
                    # resp = jsonify({'message': 'File successfully converted'})
                    # resp.status_code = 201
                    # return resp
                    # close_db()
                    resp = jsonify({'message': 'File successfully converted'})
                    resp.status_code = 201
                    return resp
                    close_db()
                
                else:
                    resp = jsonify({'message': 'Method is not allowed'})
                    resp.status_code = 201
                    return resp


            # resp = jsonify({'message': 'File successfully converted', 'root_path':uploaded_file, 'file_name': sourceFileName})
            resp = jsonify({'message': 'File successfully converted'})
            resp.status_code = 201
            return resp
            close_db()

        except Exception as e:
            print(e)
            logger.info("Exception source: %s", e)
            resp = jsonify({'message': 'Server Error'})
            resp.status_code = 500
            return resp

@app.route(PREFIX + '/file_upload/', methods=['POST'])
@app.route(PREFIX + '/file_upload', methods=['POST'])
@token_required
def upload_file(current_user):
    if request.method == 'POST':
        logger.info("---------------------- File upload api ----------------------")
        try:
            if 'file' not in request.files:
                resp = jsonify({'message': 'No file part in the request'})
                resp.status_code = 400
                logger.info("No file part in the request")
                return resp
            file = request.files['file']
            if file.filename == '':
                resp = jsonify({'message': 'No file selected for uploading'})
                resp.status_code = 400
                logger.info("No file selected for uploading")
                return resp
            if file and allowed_file(file.filename):
                sourceFileName = secure_filename(file.filename)
                targetType = request.form.get('targetType')
                print (targetType)
                
                logger.info("Source file : %s", sourceFileName)

                fileType = file.filename.split("/")[-1].split(".")[-1]

                combineDir = UPLOAD_FOLDER + '/' + current_user[0] + '/'
                source_directory = str(combineDir)
                os.makedirs(os.path.join(source_directory), exist_ok=True)

                connection = get_db()
                cursor = connection.cursor()

                cursor.execute("select user_id from users where public_id=%s", (current_user[0],))
                userId = cursor.fetchone()
                print (userId)


                file.save(os.path.join(source_directory, sourceFileName))
                logger.info("File saved in directory : %s", source_directory)

                sourceFilePath = source_directory

                cursor.execute(
                    "INSERT INTO files_data (file_path, file_name, target_type, user_id) VALUES (%s,%s,%s,%s);",
                    (sourceFilePath, sourceFileName, targetType, userId))
                connection.commit()
                logger.info("Saved source file content in db")
                

                cursor.execute("select file_id, file_path from files_data WHERE user_id=%s ORDER BY file_id DESC LIMIT 1",(userId))
                uploaded_file = cursor.fetchone()
                print (uploaded_file)
                
                fileId = uploaded_file [0]
                print (fileId)

                cursor.execute("select file_id, file_path, file_name from files_data where user_id=%s and file_id=%s", (userId,fileId))
                selected_file = cursor.fetchone()
                print (selected_file)
                selected_file_name = selected_file[2]
                print(selected_file_name)
                file_extension = selected_file_name.split(".")[-1]
                print(file_extension)
                source_file_path = selected_file[1] + selected_file[2]
                convert_file(file_extension,targetType,source_file_path,fileId,userId)
                
                # convert_file(fileID,targetType,userID)
                resp = jsonify({'message': 'File converted successfully', 'root_path':uploaded_file, 'file_name': sourceFileName})
                resp.status_code = 201
                return resp
                # close_db()


        except Exception as e:
            print(e)
            logger.info("Exception source: %s", e)
            resp = jsonify({'message': 'Server Error'})
            resp.status_code = 500
            return resp
    
# @app.route(PREFIX + '/file_convert/', methods=['POST'])
# @app.route(PREFIX + '/file_convert', methods=['POST'])
# @token_required
def convert_file(file_extension,targetType,source_file_path,fileId,userId):
        
    if file_extension == "usfm" and targetType == "csv":
        target_file_csv = usfm_to_csv(source_file_path)
        # print(target_file)

        target_file_path_1, file_name = os.path.split(target_file_csv)
        connection = get_db()
        cursor = connection.cursor()

        cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
        connection.commit()
        resp = jsonify({'message': 'File successfully converted'})
        resp.status_code = 201
        return resp
        close_db()
        
        
    elif file_extension == "CSV" and targetType == "usfm":
        target_file_usfm = csv_to_usfm(source_file_path)
        # print(target_file)

        target_file_path_2, file_name = os.path.split(target_file_usfm)

        cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
        connection.commit()
        resp = jsonify({'message': 'File successfully converted'})
        resp.status_code = 201
        return resp
        # close_db()
        
    elif file_extension == "html" and targetType == "csv":
        target_file_html_csv = html_to_csv(source_file_path)
        # print(target_file)

        target_file_path_3, file_name = os.path.split(target_file_html_csv)

        cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
        connection.commit()
        resp = jsonify({'message': 'File successfully converted'})
        resp.status_code = 201
        return resp
    
    elif file_extension == "md" and targetType == "csv":
        target_file_md_csv = md_to_csv(source_file_path)
        # print(target_file)

        target_file_path_4, file_name = os.path.split(target_file_md_csv)
        cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
        connection.commit()
        resp = jsonify({'message': 'File successfully converted'})
        resp.status_code = 201
        return resp
    
    elif file_extension == "xlsx" and targetType == "txt":
        target_file_xlsx_txt = xlsx_to_txt(source_file_path)
        # print(target_file)

        target_file_path_5, file_name = os.path.split(target_file_xlsx_txt)
        # cursor.execute("UPDATE files_data SET target_file_name = %s, file_converted = %s WHERE file_id = %s AND user_id = %s",(file_name, True, fileId, userId))
        # connection.commit()
        # resp = jsonify({'message': 'File successfully converted'})
        # resp.status_code = 201
        # return resp
        # close_db()
        resp = jsonify({'message': 'File successfully converted'})
        resp.status_code = 201
        return resp
        close_db()
    
    else:
        resp = jsonify({'message': 'Method is not allowed'})
        resp.status_code = 201
        return resp


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8088)

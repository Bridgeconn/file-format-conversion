from configparser import ConfigParser
import psycopg2
from psycopg2 import sql
import os


# absolute_file_path = os.getenv('', '/home/uday/WorkStation/BCS/file-convesion/file-format-conversion/api/config/database.ini')
# absolute_file_path = "/home/uday/WorkStation/BCS/file-convesion/file-format-conversion/api/config/database.ini"
def config(filename='database.ini', section='postgresql'):
	parser = ConfigParser()
	parser.read(filename)
 
	db = {}
	if parser.has_section(section):
		params = parser.items(section)
		for param in params:
			db[param[0]] = param[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))
	return db

def get_db():
	# params = config()
	# conn = psycopg2.connect(**params)
	conn = psycopg2.connect("dbname=file_converter_data user=postgres password=password")
	return conn

def close_db():
	# params = config()
	# conn = psycopg2.connect(**params)
	conn = psycopg2.connect("dbname=file_converter_data user=postgres password=password")
	return conn.close()

def validate_api(request):
	headers = request.headers
	api_key = headers.get("X-Api-Key")
	return api_key

ALLOWED_SOURCE_EXTENSIONS = set(['csv','usfm','md','xlsx','docx','html'])

def allowed_file(filename):
		return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_SOURCE_EXTENSIONS
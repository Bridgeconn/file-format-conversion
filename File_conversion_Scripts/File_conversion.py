import csv
import re
import sys
import glob
from werkzeug.utils import secure_filename
import os
import openpyxl
from xlsx_to_md import xlsx_to_md
# from docx
#  import Document
from usfm_to_csv import usfm_to_csv
from csv_to_usfm import csv_to_usfm
from md_to_csv import md_to_csv
from xlsx_to_md_Notes import xlsx_to_md_notes
# from docx_to_usfm import docx_to_usfm

ALLOWED_EXTENSIONS = ["json", "usfm", "docx", "csv", "tsv","md","xlsx"]
# path = str(input("enter the input folder path:"))
# file_path = os.path.abspath(path) 
# name = str(input("enter the inputput file name:"))

# file = glob.glob(name)
files = glob.glob('1JN.usfm')
fileread = open('1JN.csv')
files_md = glob.glob('.//hindi_irv_dict/*.md')
files_xlsx = glob.glob(os.getcwd() + "/Source/*.xlsx")
files_xlsx_md_notes = glob.glob('**/*.xlsx')

# files_docx = glob.glob('**/*.docx')
while True:
    try:
        input_file_type = str(input("enter the inputput file type:"))
        if input_file_type in ALLOWED_EXTENSIONS:
            print("It is valid file type")
        break
    except ValueError:
        print ("\n invalid input file type, valid file types are:json,usfm,docx,csv and tsv, chose any one")
        
while True:
    try:
        output_file_type = str(input("enter the outtput file type:"))
        if output_file_type in ALLOWED_EXTENSIONS:
            print("It is valid file type")
        break
    except ValueError:
        print ("\n invalid output file type, valid file types are:json,usfm,docx,csv and tsv, chose any one")

print ("please make sure entered inputs are correct")

print ("This is your file name:",files)
print ("This is your input file:",input_file_type)
print ("This is your output file type:",output_file_type)

if input_file_type == "usfm" and output_file_type == "csv":
    usfm_to_csv(files)
    print ("file conversion is successful")
 
elif input_file_type == "csv" and output_file_type == "usfm":
    csv_to_usfm(fileread)
    print ("file conversion is successful")
    
elif input_file_type == "md" and output_file_type == "csv":
    md_to_csv(files_md)
    print ("file conversion is successful")
    
    
elif input_file_type == "xlsx" and output_file_type == "md":
    xlsx_to_md(files_xlsx)
    print ("file conversion is successful")
    
elif input_file_type == "xlsx" and output_file_type == "md":
    xlsx_to_md_notes(files_xlsx_md_notes)
    print ("file conversion is successful")
    
# elif input_file_type == "docx" and output_file_type == "usfm":
#     md_to_csv(files_docx)
#     print ("file conversion is successful")

else:
    print ("method not allowed, try again")
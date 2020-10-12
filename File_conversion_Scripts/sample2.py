import csv
import re
import sys
import glob
from werkzeug.utils import secure_filename
import os
from usfm_to_csv import usfm_to_csv

ALLOWED_EXTENSIONS = ["json", "usfm", "docx", "csv", "tsv"]
# path = str(input("enter the input folder path:"))
# file_path = os.path.abspath(path) 
# name = str(input("enter the inputput file name:"))

# file = glob.glob(name)
files = glob.glob('1JN.usfm')

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
else:
    print ("method not allowed, try again")
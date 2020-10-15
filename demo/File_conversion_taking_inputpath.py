import csv
import re
import sys
import glob
from werkzeug.utils import secure_filename
import os
from md_to_csv import md_to_csv

inputdirectory = input ("please enter input directory path:")
inputfileextensions = input ("please enter input file extentenstion:")
output_file_type = input ("please enter output file type:")
path = inputdirectory+"*."+inputfileextensions
print (path)
files = glob.glob(os.path.join(inputdirectory, "*."+inputfileextensions))
files_md = glob.glob(os.path.join('files'))
from md_to_csv import md_to_csv

if inputfileextensions == "md" and output_file_type == "csv":
    md_to_csv(files_md)
    print ("file conversion is successful")
    
else:
    print ("method is not allowed")

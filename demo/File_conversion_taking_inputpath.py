import sys
import os
from usfm_to_csv import usfm_to_csv

try:

    # if len(sys.argv) != 4:
    #     raise ValueError('Please provide correct argumnets')

    path = sys.argv[1]
    
    input_file = sys.argv[2]

    out_put_file_type = sys.argv[3]
    print('output file type ', out_put_file_type)


    if os.path.exists(path):
        print ("filename : " + path.split("/")[-1])
        file_name = path.split("/")[-1]
        if file_name == input_file:
            file_extension = file_name.split(".")[-1]
            if file_extension == "usfm" and out_put_file_type == "csv":
                usfm_to_csv(input_file)
                print ("file conversion is successful")
                                
            else:
                print ("method not allowed, try again")
        else:
            print ("File type is not acceptable")
    else:
        ("file does not exist")
except:
    print (" arguments are not paased properly")

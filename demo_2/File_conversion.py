import sys
from usfm_to_csv import usfm_to_csv

print (" Please provide the input file name and output  in proper order as arguments")

if len(sys.argv) != 4:
    raise ValueError('Please provide correct argumnets')

input_file = sys.argv[1]
print('input file name ', input_file)

input_file_type = sys.argv[2]
 
print('inputput file type is ', input_file_type)

out_put_file_type = sys.argv[3]

print('output file name ', out_put_file_type)

if input_file_type == "usfm" and out_put_file_type == "csv":
    usfm_to_csv(input_file)
    print ("file conversion is successful")
else:
    print ("method not allowed, try again")
    
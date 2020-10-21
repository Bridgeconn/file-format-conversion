from bs4 import BeautifulSoup
import re
import csv
import sys
import glob
import errno
import os

def html_to_csv(files):
# files = glob.glob('**/*.html')
    for name in files:
        file_name = os.path.splitext(name)[0]
        csv_file = file_name + '.csv'
        # print csv_file

        soup = BeautifulSoup(open(name), "lxml")

        outfile = open(csv_file, 'w')

        # Create the csv writer object
        csvwriter = csv.DictWriter(outfile, fieldnames = ["Chapter", "Verse", "Eng Word"], delimiter ='\t')
        csvwriter.writeheader()

        # Open html and obtain the table as input
        csvwriter = csv.writer(outfile, delimiter ='\t')
        print ("Parsing HTML file")

        for t in soup.find_all('div', id = re.compile("test_")):
            s = t['id'].split('_')
            s = s[2]
            s = s.split('-')
            chapter = s[0]
            verse = s[1]
            en = t.get_text().strip()
            csvwriter.writerow([chapter, verse, en])

        print ("Converted to CSV !")
        outfile.close()
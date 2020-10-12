#!/usr/bin/python
# -*- coding: utf-8 -*-

import openpyxl
import re
import os
import sys
import glob
import errno

# files = glob.glob('**/*.xlsx')
def xlsx_to_md_notes(files_xlsx_md_notes):
    for name in xlsx_to_md_notes:
        file_name = name.split('/')[1]
        print (file_name)

        # Open xlsx file
        wb = openpyxl.load_workbook(name)

        # Initialization of variables
        f = file_name.split('.')
        folder = f[0]

        # Check if directory exists
        if not os.path.exists(folder):
            os.mkdir(folder)
        print ("Conversion in progress")

        # Access each element of a column row by row and write it to md file
        sheet = wb.get_sheet_by_name("Sheet1")
        for row in range(2, sheet.max_row+1):

            try:
                # Read chapter number
                chapter = str(sheet['B' + str(row)].value)
                if len(chapter) < 2:
                    chapter = '0' + chapter

                if re.search('\d+', chapter):
                    if not os.path.exists('%s/%s' %(folder, chapter)):
                            os.mkdir("%s/%s/" %(folder, chapter))

                # Read verse
                verse = sheet['C' + str(row)].value
                if verse != None:
                    if re.search('-',verse):
                        verse = verse.split('-')[0]
                        if len(verse) < 2:
                            verse = '0' + verse

                # Read text associated with reference
                text = sheet['E' + str(row)].value

                # Write data into separate md files
                if chapter!= None and verse != None and text!= None:
                    txt = text.replace(u"\u2022", '# ')
                    txt = txt.replace("*", '# ')
                    txt1 = txt.replace('-', '\n\n')
                    txt2 = txt1.replace(u"\u2013", '\n\n')
                    outfile = open('%s/%s/%s.md' %(folder,chapter,verse), "w")
                    outfile.write(unicode(txt2).encode('utf-8').strip())

            except:
                print ("There is an error in %sth row of '%s' " %(row, folder))

        # Close the file
        #wb.close()
        print ('Conversion Done !')
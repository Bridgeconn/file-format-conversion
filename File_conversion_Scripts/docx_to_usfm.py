# from docx import Document
import os
import re
import sys
import glob
import errno

def docx_to_usfm(files_docx):
    # files = glob.glob('**/*.docx')
    for name in files_docx:
        filename = os.path.splitext(name)[0]
        outfile = open(filename.split('/')[1] + ".usfm", "w")
        print (filename)

        document = Document(name)
        for para in document.paragraphs:
            if para.text.startswith('Haggai'):
                bookname = para.text
                outfile.write('\id HAG' + '\n')
            elif re.match(r'\d+', para.text[-1:]):
                chapter = '\c ' + para.text[-2] + para.text[-1]
                outfile.write(chapter + '\n')
            elif re.match(r'\d+', para.text[0:1]):
                verse = '\\v ' + para.text.encode('utf-8')
                outfile.write(verse + '\n')

        outfile.close()
        print ("Conversion done !")
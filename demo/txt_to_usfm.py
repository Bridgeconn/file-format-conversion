'''
 Converting the txt file content into usfm file by adding tags
'''


import glob
import re
import os

# txt_files = glob.glob("*.txt")

def write_usfm(content):
	line = ""
	complete_content = content.split("\n")
	
	for row in complete_content:
		book_name = re.search(r"\\id (.*)", row)
	
		if book_name:
			if line != "":
				
				'''Write into usfm file'''
				usfm_file.write(line)
				line = ""
				usfm_file = open(book_name.group(1)+".usfm","w")
				line += "\id " + book_name.group(1) + "\n"
			else:
				''' Open an usfm file'''
				usfm_file = open(book_name.group(1)+".usfm","w")
				line += "\id " + book_name.group(1) + "\n"

		chapter_number = re.search(r"(\s?\d+\s?\n)",n)
		if chapter_number:
			number = chapter_number.group(1)
			line += "\\c " + number + "\n"

		verse = re.search(r"(\d+) ?(.*)",n)
		if verse:
			verse_number = verse.group(1)
			note = verse.group(2)
			if verse_number and note:
				line += "\\v " + verse_number + " " + note + "\n"
			elif verse_number:
				line += "\\c " + verse_number + "\n"

	print(line)
	usfm_file.write(line)
	os.chdir("..")

def txt_to_usfm():
	for txt_file in txt_files:
		content = ""
		align_content = ""
		file_name = re.sub(r"docx.txt","",txt_file)
		read_file = open (txt_file,'r',encoding = 'utf-8')
		
		'''Folder for each lanuage or text file'''
		try:
			if not os.path.exists(file_name):
				os.makedirs(file_name)
				os.chdir(file_name)
			else:
				os.chdir(file_name)
		except OSError:
			print ('Error: Creating directory.' + file_name)

		'''Reading the content line by line and aligning it.'''
		for lines in read_file:
			extra_line = re.sub(r"\n","",lines)
			new_line = re.sub(r"(\\id)","\\n\\1",extra_line)
			new_lines = re.sub(r"(\d+)","\\n\\1",new_line)
			content+=new_lines

		search_obj = re.sub(r"(\\id ?)\n","\\1",content)
		if search_obj:
			write_usfm(search_obj)
		else:
			write_usfm(content)

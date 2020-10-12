import csv
import glob
import os
import re

def md_to_csv(files_md):
    csv_file = 'outputcsv_file.csv'
    outfile = open(csv_file,'w')
    csvwriter = csv.writer(outfile)
    csvwriter.writerow([ "id" ,"keyword", "wordforms","strongs","definition", "translationhelp","seealso","ref","examples"])


    # files_md = glob.glob('.//hindi_irv_dict/*.md')
    idCount=0
    for name in files_md:
            f = open (name)
            d = f.readlines()
            f.seek(0)
            wordforms = d[0].replace('#','').strip()
            idCount+= 1
            keyword=os.path.basename(name).replace(".md","")
            for line in d:
                    if  "* Strong's:" in line:
                        strongs= line.replace("* Strong","").strip()
                        continue;
                    if  "यह भी देखें:" in line:
                        seealso= line.replace("(यह भी देखे:","").strip()
                        continue

            i = 4
            definition=""
            translationhelp=""
            while i < len(d) :
                    if "यह भी देखें" in d[i] or d[i].startswith("## बाइबल स"):
                            break
                    elif d[i].startswith("## अनुवाद के सुझाव") or translationhelp!="":
                            ranslationhelp=translationhelp+d[i]
                    else:
                            definition=definition+d[i]
                    i+=1

            ref=""
            refContentIndex = 0;
            i=6
            while i < len(d):
                    if d[i].startswith("## बाइबल स"):
                            refContentIndex=i+1
                            break
                    i+=1
            while  refContentIndex >0 and refContentIndex < len(d):
                    if d[refContentIndex].startswith("## शब्द तथ्य") or d[refContentIndex].startswith("## बाइबल कहानियों से उदाहरण") or d[refContentIndex].startswith("* Strong") :
                            break
                    else:
                            ref = ref + d[refContentIndex]
                    refContentIndex += 1

            examples=""
            examplesContentIndex = 0;
            i = 9
            while i < len(d):
                    if d[i].startswith("## बाइबल कहानियों से उदाहरण"):
                            examplesContentIndex = i + 1
                            break
                    i += 1
            while examplesContentIndex > 0 and examplesContentIndex < len(d):
                    if d[examplesContentIndex].startswith("## शब्द तथ्य") or d[examplesContentIndex].startswith("* Strong"):
                            break
                    else:
                            examples = examples + d[examplesContentIndex]
                    examplesContentIndex += 1
            csvwriter.writerow([idCount,keyword,wordforms,strongs,definition,translationhelp,seealso,ref,examples])
            f.close()
    outfile.close()


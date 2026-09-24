#!/usr/bin/env python3
#requires a stock_gscs.txt file at dev root, stock gscs to eliminate from consideration
#requires a listing of gsc files from the finalunzippedfiles directory
#this has processed the toplevel map gscs, but there are more gscs, looking at these with the program
#you will need to modify the file locations

import subprocess
import os
import sys
import re
import hashlib
from collections import defaultdict

def create_stock_list():
    #this is a list of stock files, tested against to skip
    stock = []
    with open("/home/dev/stock_gscs.txt") as f:
        for line in f:
            stock.append(line.strip())
    return stock

def get_map_list(source_file):
    #source file is the gsc.txt file containing md5 and gscs
    files = []
    with open(source_file,"r") as f:
        for line in f:  #examine listing of gscs line by line
            line_split = line.strip().split("  ") #split md5sum output into md5 and thefile
            md5,gsc_file_with_path = line_split
            gsc_file_parts = gsc_file_with_path.split("/") #split path/thefile section
            gsc_filename = gsc_file_parts[-1] #the gsc file found by the find . -iname "*gsc" in gsc.txt
            themap = gsc_file_parts[1] #the map directory in the unzipped directory, no gsc
            #only process top level gsc files, associated with the map
            if gsc_filename.replace(".gsc","") != themap :
                continue #bypass files that are not top-level map gsc files
            files.append(themap.lower()) #add mapname, no path, to gscs to be searched
    return files #returns list of files that are mapname and also the top-level gsc names

def bypass_test(line):
    if "::" not in line \
        or "_introscreen" in line \
        or "println" in line \
        or "level." in line:
        return True
    else :
        return False

def strip_multiline_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

def replacer(line):
    replaces = [[";",""],["\\","/"]]
    regexes = [[r"//.*$", ""],[r"^ *\{ *",""],[r"\(.*$",""],[r" +:: +","::"]]
    for token,replacer_text in replaces:
        line = line.replace(token,replacer_text)
    for regex, replacer_text in regexes:
        line = re.sub(regex,replacer_text,line)
    return line

def process_line(line):
    line = replacer(line.strip())
    bypass = bypass_test(line)
    if bypass:
        file_path = routine = filename = ""
    else:
        file_path,routine = line.split("::") #function file
        file_path = re.sub(r"^.* +","",file_path).strip()
        filename = file_path.split("/")[-1].strip() #ignore all but last item on line
        routine=routine.strip()
        #file_path is the path to the called file, that the routine is in
        # filename is the name of the called file, that the routine is in
        # routine is the name of the routine
    return [bypass,file_path,filename,routine]

def recurse(gsc_path): #search gsc includes path
    # example
    # /home/dev/source/final_server_items/finalunzippediwds/mp_glossis_trainstation_v2/maps/mp/mp_glossis_trainstation_v2.gsc
    global stock
    gsc_path_split = gsc_path.strip().split("/")
    gsc_themap = gsc_path_split[6] #always in sixth
    gsc_path_filename = gsc_path_split[-1] #use for recursion test below
    # example mp_glossis_trainstation_v2.gsc
    with open(gsc_path, encoding = "cp1252") as f:
        cleaned = strip_multiline_comments(f.read())

    for line in cleaned.splitlines():
        linestrip = line.strip().lower()
        bypass,file_path,filename,routine = process_line(linestrip)
        #if gsc_themap == "mp_roseline" and bypass == False:
        #    print("line",linestrip)
        #    print("routine=", routine)
        #    print("gsc_themap",gsc_themap)
        #    print("gsc_path_filename", gsc_path_filename)
        #    print("file_path", file_path)
        #    print("filename",filename,"\n")

        if bypass: continue
        if filename in stock:
            #print(f"Bypassing {filename}")
            continue
        subfile = os.path.join( unzipped_dir, gsc_themap, file_path + ".gsc")
        #do an md5sum of the subfile
        #result = subprocess.run(["md5sum", subfile], capture_output=True, text=True)
        try:
            md5 = hashlib.md5(open(subfile, "rb").read()).hexdigest()
        except:
            #print("\ngsc_themap==",gsc_themap,"\nline==",line, "\nroutine==",routine)
            #print(f"error on subfile = {subfile}\n")
            #mp_devilaim is missing lift.gsc
            #mp_dawnville_cl_final is missing maps/mp/gametypes/_teams.gsc
            continue
        called = file_path.split("/")[-1]

        data[called].append([md5,gsc_themap,file_path,routine])
        gsc_path_testing = gsc_path.split("/")[7:]
        testpath= ""
        for i in gsc_path_testing:
            testpath+=f"/{i}"  #make testpath /maps/mp or whatever
        if testpath != "/" + file_path + ".gsc":
            recurse(subfile) #don't call a file from itself

#####################
data = defaultdict(list)
files = []
stock = create_stock_list
source_file = "/home/dev/gsc.txt"
unzipped_dir = "/home/dev/source/final_server_items/finalunzippediwds/"
stock = create_stock_list()
maps_to_search = get_map_list(source_file)
for map in maps_to_search: #process top level gsc files
    map_gsc_path = os.path.join(unzipped_dir,map,"maps/mp",map +".gsc")
    recurse(map_gsc_path)
#print(f"md5\tMap\tScriptfile\troutine")
with open("/home/dev/calls_sorted.txt","w") as f :
    for i in data:
        if len(data[i]) > 1:
            current = data[i][0][0]
            allequal = True
            for j in data[i]:
                if j[0] != current:
                    allequal = False

            if allequal == False:
                #print(i)
                data[i].sort()
                for j in data[i]:
                    if len(data[i]) > 1:
                        f.write(f"{j[0]}\t{j[1]}\t{i}\t{j[2]}\n")

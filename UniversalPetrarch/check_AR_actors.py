"""
check_AR_actors.py

Program to tabulate the number of duplicates in the ES actor and agent dictionaries and also check for variations
in the code assignments, writing these results to files. Also checks both words and phrases found in the 
validate file against the dictionaries and writes lists of actors found, agents found, and missing cases.

TO RUN PROGRAM:

python3 check_AR_actors.py

PROGRAMMING NOTES: 

1. File names are currently hard coded.

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.13.6; it is standard Python 3.7 so it should also run in Unix or Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://parusanalytics.com

This program was developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

Copyright (c) 2018	Philip A. Schrodt.	All rights reserved.

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
11-Dec-2018:	Initial version, adapted from earlier check_AR_actor_dups.py

=========================================================================================================
"""

import collections
import os

dirname = "validate/arabic/"
actor_filename = "actor_dict_ar_v4.txt"
agent_filename = "agents.all.ar_v3.txt"
validate_filename = "arabic_gsr_validation_18-11-14.xml"

def check_text(thetag):
    """ checks for non-null contents of thetag, both the complete phrase and words, in dictionaries, and updates counters """
    global foundact, foundagt, missct
    
    if thetag + "\"" not in line:
        idx = line.find(thetag) + len(thetag) 
        thetext = line[idx:line.find("\"", idx + 1)]
    else:
        return
    alist = [thetext]
    if " " in thetext:
        alist.extend(thetext.split(" "))
#            print(line[:-1])
    print(alist)
    for li in alist:
        if li in actorpat:
            print ("Actor:",actorpat[li])
            foundact[li] += 1
        elif li in agentpat:
            print ("Agent:",agentpat[li])
            foundagt[li] += 1
        else:
            missct[li] += 1
            #print("Missing",li)

def write_dups(thepat, thect, thetot, outfilename):
    """ write duplicate counts to file """
    totdp = 0
    with open(outfilename,"w") as fout:
        for el in thect.most_common():
            if el[1] == 1: break
            totdp += el[1] - 1
            print(el[0])
            fout.write(el[0]  + "\n")
            patct = collections.Counter()
            for pt in thepat[el[0]]:
                patct[pt] += 1
            for pt in patct.most_common():
                print("    {:2d}  {:s}".format(pt[1], pt[0]))
                fout.write("    {:2d}  {:s}\n".format(pt[1], pt[0]))
            
        thetype = "actor" if "actor" in outfilename else "agent"
        print("Total {:s}s: {:d} Total duplicates {:d} ({:6.2f}%)".format(thetype, thetot, totdp, totdp * 100/thetot))
        fout.write("Total {:s}s: {:d} Total duplicates {:d} ({:6.2f}%)\n".format(thetype, thetot, totdp, totdp * 100/thetot))
    

def read_file(thepat, thect, filename):
    """reads actor or agent file, returns total number of actors """
    ka = 0
    thetot = 0
    for line in open(os.path.join(dirname, filename), "r"):
        if len(line) < 2 or line.startswith("#"):
            continue
        if line.startswith("\t"):  # only relevant for actors
            thepat[key].append(line[1:-1])
            continue
        if " " in line:                   # note this assumes entries are connected with "_"
            key = line[:line.find(" ")]
        else:
            key = line[:-1]
        if not key:
            continue
        if key[-1] == "_":
            key = key[:-1]
        thect[key] += 1
        thetot += 1
        if key in thepat:
            if "[" in line:
                thepat[key].append("[" + line[:-1].partition("[")[2])
        else:
            if "[" in line:
                thepat[key] = ["[" + line[:-1].partition("[")[2]]
            else:
                thepat[key] = []
    
        ka += 1 
    return thetot       
    #    if ka > 3600: break

actorpat = {}
actorct = collections.Counter()
acttot = read_file(actorpat, actorct, actor_filename)
write_dups(actorpat, actorct, acttot, "AR_actor_analysis.txt")

agentpat = {}
agentct = collections.Counter()
agttot = read_file(agentpat, agentct, agent_filename)
write_dups(agentpat, agentct, agttot, "AR_agent_analysis.txt")

missct = collections.Counter()
foundact = collections.Counter()
foundagt = collections.Counter()
ka = 0
for line in open(os.path.join(dirname, validate_filename), "r"):
    if line.startswith("<EventText"):
        check_text("sourcetext=\"")
        check_text("targettext=\"")
        ka += 1        
#        if ka > 128: break
with open("AR_missing_texts.txt","w") as fout:
    fout.write("Actors found:\n")
    for li in foundact.most_common():
        fout.write("{:4d}  {:s}\n".format(li[1], li[0]))
    fout.write("\nAgents found:\n")
    for li in foundagt.most_common():
        fout.write("{:4d}  {:s}\n".format(li[1], li[0]))
    fout.write("\nMissing:\n")
    for li in missct.most_common():
        fout.write("{:4d}  {:s}\n".format(li[1], li[0]))

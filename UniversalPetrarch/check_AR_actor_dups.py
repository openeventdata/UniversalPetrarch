"""
check_AR_actor_dups.py

Program to tabulate the number of duplicates in the ES actor and agent dictionaries and also check for variations
in the code assignments. Writes results to a file.

TO RUN PROGRAM:

python3 check_AR_actor_dups.py

PROGRAMMING NOTES: As is presumably obvious, select between actor and agent by rearranging the "filename" assignments

SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.10.5; it is standard Python 3.5 so it should also run in Unix or Windows. 

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
05-Dec-2018:	Initial version

=========================================================================================================
"""

import collections
import os

dirname = "validate/arabic/"
filename = "actor_dict_ar_v4.txt"
filename = "agents.all.ar_v3.txt"

actorpat = {}
actorct = collections.Counter()
ka = 0
tot = 0
for line in open(os.path.join(dirname, filename), "r"):
    if len(line) < 2 or line.startswith("#"):
        continue
    if line.startswith("\t"):
        actorpat[key].append(line[1:-1])
        continue
    if " " in line:
        key = line[:line.find(" ")]
    else:
        key = line[:-1]
    if not key:
        continue
    if key[-1] == "_":
        key = key[:-1]
    actorct[key] += 1
    tot += 1
    if key in actorpat:
        if "[" in line:
            actorpat[key].append("[" + line[:-1].partition("[")[2])
    else:
        if "[" in line:
            actorpat[key] = ["[" + line[:-1].partition("[")[2]]
        else:
            actorpat[key] = []
    
    ka += 1        
#    if ka > 3600: break
totdp = 0
if filename.startswith("actor"):
    outfilename = "AR_actor_analysis.txt"
else:
    outfilename = "AR_agent_analysis.txt"
with open(outfilename,"w") as fout:
    for el in actorct.most_common():
        if el[1] == 1: break
        totdp += el[1] - 1
        print(el[0])
        fout.write(el[0]  + "\n")
        patct = collections.Counter()
        for pt in actorpat[el[0]]:
            patct[pt] += 1
        for pt in patct.most_common():
            print("    {:2d}  {:s}".format(pt[1], pt[0]))
            fout.write("    {:2d}  {:s}\n".format(pt[1], pt[0]))
            
print("File:", filename)
print("Total actors:", tot, "Total duplicates", totdp, "({:6.2f}%)".format(totdp * 100/tot))
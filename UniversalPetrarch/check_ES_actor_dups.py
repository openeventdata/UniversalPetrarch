"""
check_ES_actor_dups.py

Very simple program to tabulate the number of duplicates in the ES actor and agent dictionaries. Results are only written to 
screen.

TO RUN PROGRAM:

python3 check_ES_actor_dups.py

PROGRAMMING NOTES: As is presumably obvious, select the file to be analyzed by rearranging the "filename" assignments

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

#~/Analytics/RIDIR-UDP-18-11/validate/spanish/ELBOW_SPANISH_Phoenix.Countries.actors_UPDATED_noaccent.txt
#<Actorfile>
#ELBOW_SPANISH_Phoenix_International_actors_UPDATED_noaccent.txt,
#ELBOW_SPANISH_Phoenix_MilNonState_actors_UPDATED_mod.txt,
#ELBOW_SPANISH_Phoenix.Countries.actors_UPDATED_noaccent.txt</Actorfile>
#<Agentfile>Agents_ESP_Bablenet_20171114_mod.txt</Agentfile>
import collections
import os

dirname = "validate/spanish/"
filename = "Agents_ESP_Bablenet_20171114_mod.txt"
filename = "ELBOW_SPANISH_Phoenix.Countries.actors_UPDATED_noaccent.txt"
filename = "ELBOW_SPANISH_Phoenix_MilNonState_actors_UPDATED_mod.txt"
filename = "ELBOW_SPANISH_Phoenix_International_actors_UPDATED_noaccent.txt"

actorct = collections.Counter()

ka = 0
tot = 0
for line in open(os.path.join(dirname, filename), "r"):
    if line.startswith("#") or line.startswith("\t"):
        continue
    if line.startswith("+"):
        line = line[1:]
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
    ka += 1        
#    if ka > 3600: break
totdp = 0
for el in actorct.most_common():
    if el[1] == 1: break
    totdp += el[1] - 1
    print(el)        
print("File:", filename)
print("Total actors:", tot, "Total duplicates", totdp, "({:6.2f}%)".format(totdp * 100/tot))
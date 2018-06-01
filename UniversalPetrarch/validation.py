# -*- coding: utf-8 -*-

"""
validation.py

Runs validation -- functional testing -- cases for UniversalPetrarch. For details, see README.md on 
https://github.com/openeventdata/UniversalPetrarch/tree/dev-validate  

TO RUN PROGRAM:

python validation.py [-d] [-i filename] [-p1] [-p2]

  -d: use alternatve file with dictionaries in validate/, typically a debug file. Input files are hard coded.
  -i <filename>: use alternative file with dictionaries in data/dictionaries
  -p1/-p2: batch comparison 
  

PROGRAMMING NOTES:

1.  This combines code from the validation suite of TABARI and PETRARCH-1 with the code accessing UD-PETR 
    and its data structures from the script test_script_ud.py (last update: 5 July 2017). This output is
    a combination of the two approaches, and some of the options that were tested in TABARI and PETRARCH-1 
    are not relevant to UD-PETR and haven't been implemented.
    
2.  The PETR_Validate_records_2_02.xml file is currently XML and could be read as such, but in all likelihood this will soon to 
    transitioned over to YAML, so the fields are being processed without using XML tools.
    
3. In the current version, only PETR-2 dictionaries are used, even for the -p1 option.
    
SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.10.5; it is standard Python 3.5 so it should also run in Unix or Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

This program was developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

Copyright (c) 2018	Philip A. Schrodt.	All rights reserved.

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
27-Jul-17:	Initial version based on parallel function in PETRARCH-1
24-May-18: Modified to work with Universal-PETR off-the-shelf
01-Jun-18: -p1 and -p2 options added

=========================================================================================================
"""
from __future__ import print_function

import utilities
import datetime
import textwrap
import os.path
import logging
import codecs
import ast
import sys

import PETRreader
import PETRgraph 
import petrarch_ud
import PETRglobals

doing_compare = False
doing_P1 = False
doing_P2 = False

# ========================== VALIDATION FUNCTIONS ========================== #

def read_validate_dictionaries():
    """modification of petrarch_ud.read_dictionaries() to read from validate/"""

    print('Internal Coding Ontology:', PETRglobals.InternalCodingOntologyFileName)
    pico_path = utilities._get_data(directory_name, PETRglobals.InternalCodingOntologyFileName)
    PETRreader.read_internal_coding_ontology(pico_path)

    print('Verb dictionary:', PETRglobals.VerbFileName)
    verb_path = utilities._get_data(directory_name, PETRglobals.VerbFileName)
    PETRreader.read_verb_dictionary(verb_path)

    if PETRglobals.CodeWithPetrarch1:
        print('Petrarch 1 Verb dictionary:', PETRglobals.P1VerbFileName)
        verb_path = utilities._get_data(directory_name, PETRglobals.P1VerbFileName)
        PETRreader.read_petrarch1_verb_dictionary(verb_path)

    print('Actor dictionaries:', PETRglobals.ActorFileList)
    for actdict in PETRglobals.ActorFileList:
        actor_path = utilities._get_data(directory_name, actdict)
        PETRreader.read_actor_dictionary(actor_path)

    print('Agent dictionary:', PETRglobals.AgentFileList)
    for agentdict in PETRglobals.AgentFileList:
        agent_path = utilities._get_data(directory_name, agentdict)
        PETRreader.read_agent_dictionary(agent_path)

    print('Discard dictionary:', PETRglobals.DiscardFileName)
    discard_path = utilities._get_data(directory_name, PETRglobals.DiscardFileName)
    PETRreader.read_discard_list(discard_path)



def get_environment():
    """ Light-weight routine for reading the <Environment> block: does most of the work through side effects on PETRglobals """
    ValidExclude = None
    ValidInclude = None
    ValidOnly = True
    ValidPause = 0
    
    PETRglobals.CodeWithPetrarch1 = False
    
    line = fin.readline() 
    while len(line) > 0 and not line.startswith("<Environment>"):  # loop through the file
        line = fin.readline()
    if len(line) == 0:
        print("Can't find <Environment> block")
        exit()

    line = fin.readline() 
    while "</Environment>" not in line:  # loop through the file
        print(line[:-1])
        if '<Verbfile' in line:
            PETRglobals.VerbFileName = line[line.find(">") + 1:line.find("</")]

        elif '<Actorfile' in line:
            PETRglobals.ActorFileList = line[line.find(">") + 1:line.find("</")].split(',')

        elif '<Agentfile' in line:
            PETRglobals.AgentFileList = [line[line.find(">") + 1:line.find("</")]]
            
        elif '<Discardfile' in line:
            PETRglobals.DiscardFileName = line[line.find(">") + 1:line.find("</")]

        elif '<PICOfile' in line:
            PETRglobals.InternalCodingOntologyFileName = line[line.find(">") + 1:line.find("</")]

        elif '<Include' in line:
            ValidInclude = line[line.find(">") + 1:line.find("</")].split()
            print('<Include> categories', ValidInclude)
            if 'valid' in ValidInclude:
                ValidOnly = True
                ValidInclude.remove('valid')

        elif '<Exclude' in line:
            ValidExclude = line[line.find(">") + 1:line.find("</")].split()
            print('<Exclude> categories', ValidExclude)

        elif '<Pause' in line:
            theval = line[line.find(">") + 1:line.find("</")]
            if 'lways' in theval:
                ValidPause = 1   # skip first char to allow upper/lower case
            elif 'ever' in theval:
                ValidPause = 2
            elif 'top' in theval:
                ValidPause = 3

        line = fin.readline() 

    print(PETRglobals.VerbFileName, PETRglobals.ActorFileList[0], PETRglobals.AgentFileList[0], PETRglobals.DiscardFileName)
    print(ValidInclude, ValidExclude)
    print(ValidPause, ValidOnly)
    return ValidInclude, ValidExclude, ValidPause, ValidOnly



def validate_record(valrecord):
    """ primary procedure which calls the coder with the parse in valrecord and compares the coded results with the expected 
        as well as writing assorted intermediate data structures to fout per test_script_ud.py """

    def process_event_output(str):
        """ from test_script_ud.py """
        logger.debug("pso(): " + str)
        str = str.replace("{","")
        str = str.replace("}","")
        res = ""
        events = str[str.find(":"):].split("':")
        for event in events:
            event = event[0:event.rfind("]")]
            event = event.replace(" ","")
            event = event.replace(":","")
            event = event.replace("u","")
            event = event.replace("\'","")
            event = event[1:]
            event = event.replace("~","")
            res = res+"\n("+event+")"
        return res[1:]
    
    def parse_parser(parse):
        """ from test_script_ud.py """
        phrase_dict = {}
        for line in parse.splitlines():
            lines = line.split('\t')
            num = lines[0].strip()
            str = lines[1].strip()
            phrase_dict[num]=str
            #print(num)
            #print(str)
        phrase_dict['-'] = " "
        return phrase_dict	

    def parse_verb(phrase_dict,sentence):
        """ from test_script_ud.py with minor modifications """
        if 'verbs' not in return_dict[idstrg]['sents']['0']:
            return
        str_arr = str(return_dict[idstrg]['sents']['0']['verbs']).strip("{").split(",")
        fout.write("Verbs found:\n") 
        for x in str_arr[:1]:
            str_num = x.find(":")		
            try:        
                np = sentence.get_verbPhrase(int(x[:str_num].strip()))
                str_add = x[:str_num].strip() + " : text = " + str(np.text) +", head="+ str(np.head) +", meaning="+ str(np.meaning)+", code="+ str(np.code)+" ,passive="+str(np.passive) + "\n"
                fout.write("    " + str_add)
            except Exception as e:
                print(e)
                fout.write(" --> Exception generating sentence.get_verbPhrase(): " + str(e) + '\n')
        return


    def parse_triplets(phrase_dict):
        """ from test_script_ud.py with minor modifications """
        if 'triplets' not in return_dict[idstrg]['sents']['0']:
            return
        triplets=return_dict[idstrg]['sents']['0']['triplets']
        fout.write("Triplets found:\n") 
        for triple in triplets:
            strs = triplets[triple]
            meaning = strs['meaning']
            verbcode = strs['verbcode']
            matched_text = strs['matched_txt']
            codes = str(triple).split("#")
            event = "(" + phrase_dict[codes[0]] + "," + phrase_dict[codes[1]] + "," + phrase_dict[codes[2]] + ")"
            str_add = str(triple) + event +": Meaning = " + str(meaning) + ", VerbCode = " + str(verbcode) + ", Matched Text = " + str(matched_text) + "\n"
            fout.write("    " + str_add)                
        return 

    logger = logging.getLogger('petr_log.validate')
#        logger.addFilter(NoLoggingFilter())  # uncomment to decactivate logging for this function      
    parse = valrecord['parse']
    idstrg = valrecord['id']
    print("evaluating", idstrg)
    logger.debug("\nevaluating: "+ idstrg)
    fout.write("Record ID: " + idstrg + '\n')
    if not doing_compare:
        fout.write("Text:\n")
        for li in textwrap.wrap(valrecord['text'], width = 100):
            fout.write("    " + li + '\n')
        fout.write("Parse:\n")
        for strg in parse[:-1].split("\n"):
            fout.write("    " +  strg  + '\n')
    fout.write("Expected events:\n")
    for edict in valrecord['events']:
        if "noevents" in edict:
            fout.write("    noevents\n")                 
        else:
            fout.write("    " + edict['eventcode']  + ' ' + edict['sourcecode']  + ' ' + edict['targetcode']  + '\n') 
    
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {idstrg: {u'sents': {u'0': {u'content': valrecord['text'], u'parsed': parsed}},
        u'meta': {u'date': valrecord['date']}}}
    return_dict = "" 
    return_dict = petrarch_ud.do_coding(dict)

    fout.write("Coded events:\n")
    if 'events' in return_dict[idstrg]['sents']['0'] and len(return_dict[idstrg]['sents']['0']['events']) > 0:
        print(return_dict[idstrg]['sents']['0']['events'])
        event_out = process_event_output(str(return_dict[idstrg]['sents']['0']['events']))
        
        nfound, ncoded, nnull = 0, 0, 0
        for key, evt in return_dict[idstrg]['sents']['0']['events'].items():
            try:
                if evt[0][0].startswith("---") or evt[1][0].startswith("---") or evt[2].startswith("---") :
                    nnull += 1
                    continue
            except:   # handles [] cases
                nnull += 1
                continue       
            try:
                fout.write("    " + evt[2] + ' ' + evt[0][0] + ' ' + evt[1][0] + "  (" + key + ")")                        
                ncoded += 1
                for edict in valrecord['events']:
                    if "noevents" in edict:
                        fout.write("  ERROR: NO EVENTS\n")
                        break                 
                    else:
                        if (edict['eventcode'] == evt[2] and
                            edict['sourcecode'] == evt[0][0] and
                            edict['targetcode'] == evt[1][0]) :
                            fout.write("  CORRECT\n")
                            nfound += 1
                            break
                else:
                    fout.write("  ERROR\n") # do we ever hit this now?

                if doing_compare and len(valrecord['events']) == 1 and len(return_dict[idstrg]['sents']['0']['events']) == 1:
                    type_counts[0] += 1
                    if valrecord['events'][0]['eventcode'] == evt[2]:
                        type_counts[1] += 1
                    if valrecord['events'][0]['eventcode'][:2] == evt[2][:2]:  # cue category
                        type_counts[2] += 1
                    if valrecord['events'][0]['sourcecode'] == evt[0][0]:
                        type_counts[3] += 1
                    if valrecord['events'][0]['sourcecode'][:3] == evt[0][0][:3]: # country code
                        type_counts[4] += 1
                    if valrecord['events'][0]['targetcode'] == evt[1][0]:
                        type_counts[5] += 1
                    if valrecord['events'][0]['targetcode'][:3] == evt[1][0][:3]:
                        type_counts[6] += 1
                                                        
            except:
                pass
        if ncoded == 0:
            fout.write("    No events returned ")
            if "noevents" in valrecord['events'][0]:
                fout.write("CORRECT\n")
            else:
                fout.write("ERROR\n")
        if nnull > 0:
            fout.write("Null events: " + str(nnull)  + '\n')                
        if not doing_compare:
            fout.write("Event source:\n")
            for key, val in return_dict[idstrg]['sents']['0']['events'].items():
                fout.write("    " + key  + ': ' + str(val) + '\n')
    else:
        fout.write("    No events returned")
        if "noevents" in valrecord['events'][0]:
            nfound, ncoded, nnull = 1, 1, 0  # count this as a match
            fout.write("  CORRECT\n")            
        else:
            nfound, ncoded, nnull = 0, 0, 0
            fout.write("  ERROR\n")
        
        
    fout.write("Stats:\n    Correct: " + str(nfound) + "   Not coded: " + str(len(valrecord['events']) - nfound) 
                + "   Extra events: " + str(ncoded - nfound)  + "   Null events: " + str(nnull) + '\n') 
    if valrecord['category'] in valid_counts:
        valid_counts[valrecord['category']][0] += 1  # records
        valid_counts[valrecord['category']][1] += nfound  # correct
        valid_counts[valrecord['category']][2] += len(valrecord['events']) - nfound  # uncoded
        valid_counts[valrecord['category']][3] += ncoded - nfound  # extra
        valid_counts[valrecord['category']][4] += nnull            # null
    else:
        valid_counts[valrecord['category']] = [1, nfound, len(valrecord['events']) - nfound, ncoded - nfound, nnull]
        valid_counts['catlist'].append(valrecord['category'])  # keep track of the order of the categories found
    
    try:        
        sentence = PETRgraph.Sentence(parsed, valrecord['text'] , 0000)  # 18.05.22: what the heck is this doing???
    except Exception as e:
        print(" --> Exception generating PETRgraph.Sentence(): ",e)
        fout.write(" --> Exception generating PETRgraph.Sentence(): " + str(e) + '\n')

    if not doing_compare:
        parse_verb(phrase_dict, sentence)
        parse_triplets(phrase_dict)
    fout.write('\n')


def do_validation():
    """ Functional tests using a validation file. """

    def get_line_attribute(target):
        """ quick and dirty function for extracting well-formed XML attributes"""
        part = line.partition(target)
        return part[2][2:part[2].find('"',3)]

    ka = 0 # debugging counters
    kb = 0
    line = fin.readline() 
    while len(line) > 0:  # loop through the file
        ka += 1
#        if ka > 36: break
        if line.startswith("<Stop"):
            print("\nExiting: <Stop> record ")
            break

        if line.startswith("<Sentence "):
            valrecord = {}
            recordType = 'Sentence'
            valrecord['sentence'] = line[line.find(" ") + 1:line.find(">")]
            valrecord['date'] = get_line_attribute('date')
            valrecord['category'] = get_line_attribute('category')
            valrecord['id'] = get_line_attribute('id')
            valrecord['valid'] = True if get_line_attribute('evaluate').lower() == "true" else False
            idline = line
            line = fin.readline() # get the rest of the record
            while len(line) > 0: 
                if line.startswith("<EventCoding") and not doing_compare:
                    if 'noevents="True"' in line:
                        valrecord['events'] = ["noevents"]    
                    else:
                        theevent = {
                                    'coding' : line[line.find(" ") + 1:line.find(">")],  # not actually using this
                                    'eventcode': get_line_attribute('eventcode'),
                                    'sourcecode' :  get_line_attribute('sourcecode'),
                                    'targetcode' : get_line_attribute('targetcode'),
                                    'coded': False
                                    }
                        if 'events' in valrecord:
                            valrecord['events'].append(theevent)
                        else:
                            valrecord['events'] = [theevent]    

                elif (line.startswith("<P1Event ") and doing_P1) or (line.startswith("<P2Event ") and doing_P2):
                     thelist = ast.literal_eval(line[9:-2])
                     valrecord['events'] = []
                     for li in thelist:
                        theevent = {'eventcode'  : li[2],
                                    'sourcecode' : li[0],
                                    'targetcode' : li[1],
                                    'coded': False
                                    }
                        valrecord['events'].append(theevent)
                elif line.startswith("<Text"):
                    thetext = ""
                    line = fin.readline() 
                    while not line.startswith("</Text"):
                        thetext += line[:-1] + ' '
                        line = fin.readline() 
                    valrecord['text'] = thetext
 
                elif line.startswith("<Parse"):
                    line = fin.readline() 
                    parse = ""
                    while not line.startswith("</Parse"):
                        parse += line
                        line = fin.readline() 
                    valrecord['parse'] = parse
                    break
                line = fin.readline() 

            print("\nRecord:",valrecord['id'])
            if recordType == 'Sentence' and valrecord['category'] in ValidInclude and valrecord['valid']:
                validate_record(valrecord)
                kb += 1
            elif not valrecord['valid']:
                fout.write("Skipping " + valrecord['id']  + "\n" + idline  + "\n")
#            if kb > 60: break

        line = fin.readline() 


if __name__ == '__main__':
 # get path to validation file
    if "-d" in sys.argv:
        directory_name = "validate"
        filename = "PETR_Validate_records_2_02.debug.xml" 
    elif "-i" in sys.argv:
        directory_name = "data/text"
        filename = sys.argv[sys.argv.index("-i") + 1] 
    elif "-p1" in sys.argv or "-p2" in sys.argv:
        doing_compare = True
        directory_name = "P1-2_compare"
        filename = "P1-2_compare_dictionaries.xml" 
        if "-p1" in sys.argv:
            doing_P1 = True
        else:
            doing_P2 = True 
    else:
        directory_name = "validate"
        filename = "PETR_Validate_records_2_02.xml"  # path to validation file

    try:
        fin = open(os.path.join(directory_name, filename),'r')
    except:
        print("can't find the validation file", os.path.join(directory_name, filename))
        exit()
    print("Reading validation file ",os.path.join(directory_name, filename))
    fout = open("Validation_output.txt", 'w')

    utilities.init_logger('UD-PETR_Validate.log', debug = False)
    timestamp =  datetime.datetime.now().strftime("%Y%m%d")[2:] + "-" + datetime.datetime.now().strftime("%H%M%S")
    fout.write("UD-PETRARCH functional validation\nRun date-time: " + timestamp + "\nValidation file:    " + filename + "\n")

    ValidInclude, ValidExclude, ValidPause, ValidOnly = get_environment()
    print("Reading dictionaries")
    if directory_name == "validate":
        read_validate_dictionaries()
    else:
        petrarch_ud.read_dictionaries()
        
    valid_counts = {'catlist': []}
    if doing_compare:
        type_counts = [0,0,0,0,0,0,0]

    fout.write('Verb dictionary:    ' + PETRglobals.VerbFileName + "\n")
    if PETRglobals.CodeWithPetrarch1:
        fout.write('Petrarch 1 Verb dictionary: ', PETRglobals.P1VerbFileName + "\n")
    fout.write('Actor dictionaries: ' + str(PETRglobals.ActorFileList) + "\n")
    fout.write('Agent dictionaries: ' + str(PETRglobals.AgentFileList) + "\n")
    fout.write('Discard dictionary: ' + PETRglobals.DiscardFileName + "\n")
    fout.write('PICO file:          ' + PETRglobals.InternalCodingOntologyFileName + "\n\n" )

    if not doing_compare:
        do_validation()
    else:
        fin.close()
        for filename in open(os.path.join(directory_name, "files.list.txt"),'r'):
            if filename.startswith("==="):
                break
            fin = open(os.path.join(directory_name, filename[:-1]),'r')
            do_validation()
            fin.close()

    if doing_compare:
        filename = "P1/2 comparison files"
    fout.write("\nSummary: " + filename + " at " + timestamp + "\n")
#    fout.write("Categories included: " + str(ValidInclude) + "\n")
    fout.write("Category     Records   Correct   Uncoded     Extra      Null      TP        FN        FP  \n")
    valid_counts['Total'] = [0, 0, 0, 0, 0]
    valid_counts['catlist'].append('Total')
    for catstrg in valid_counts['catlist']:
        fout.write("{:10s}".format(catstrg))
        print(catstrg + ": " + str(valid_counts[catstrg]))
        for ka in range(5):
            fout.write("{:10d}".format(valid_counts[catstrg][ka]))
            if catstrg != "Total":
                valid_counts['Total'][ka] += valid_counts[catstrg][ka]
        fout.write(" {:8.2f}%".format((valid_counts[catstrg][1] * 100.0)/(valid_counts[catstrg][1] + valid_counts[catstrg][2])))
        fout.write(" {:8.2f}%".format((valid_counts[catstrg][2] * 100.0)/(valid_counts[catstrg][1] + valid_counts[catstrg][2])))
        fout.write(" {:8.2f}%".format((valid_counts[catstrg][3] * 100.0)/(valid_counts[catstrg][0])))  # this as percent of records
        fout.write('\n')
    fout.write("TP = correct/(correct + uncoded) \n")
    fout.write("FN = uncoded/(correct + uncoded) = 100 - TP \n")
    fout.write("FP = extra/records\n")
    print("\nRecords evaluated:{:8d}".format(valid_counts['Total'][0]))
    print("Correct events:   {:8d} {:8.2f}%".format(valid_counts['Total'][1], (valid_counts['Total'][1] * 100.0)/(valid_counts['Total'][1] + valid_counts['Total'][2])))
    print("Uncoded events:   {:8d} {:8.2f}%".format(valid_counts['Total'][2], (valid_counts['Total'][2] * 100.0)/(valid_counts['Total'][1] + valid_counts['Total'][2])))
    print("Extra events:     {:8d} {:8.2f}%".format(valid_counts['Total'][3], (valid_counts['Total'][3] * 100.0)/valid_counts['Total'][0]))
    print("===========================\n")
    if doing_compare:
        print("Accuracy on coded single event cases:")
        fout.write("\nAccuracy on coded single event cases:\n")
        for ka, lbl in enumerate(["", "Event", "Cue category", "Source", "Source primary", "Target", "Target primary"]):
            if ka == 0: continue
            print("{:14s}:   {:8d} {:8.2f}%".format(lbl, type_counts[ka], (type_counts[ka] * 100.0)/type_counts[0]))
            fout.write("{:14s}:   {:8d} {:8.2f}%\n".format(lbl, type_counts[ka], (type_counts[ka] * 100.0)/type_counts[0]))
        print("===========================\n")

    fin.close()
    fout.close()

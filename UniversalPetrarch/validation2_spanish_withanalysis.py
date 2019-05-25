# -*- coding: utf-8 -*-

"""
###requirements
1. install python package "pandas" by running:
    conda install pandas

2. install python package "openpyxl" by running:
    pip install openpyxl

###input
1. validation file: 
    e.g. data/text/spanish_protest_cameo_4_jj_validation.xml
2. configuration file: 
    e.g. data/config/PETR_config_es.ini
3. doc list (optional): list of document names that UDpetrarch will run on those stories only
4. skip list (optional): skip some of the records. Defaults is not skipping any records. This option is used for analyzing
    usage example: -s "noun_sentence#noun_gold"
    - "noun_sentence": skip sentences that the parsed tree don't contain verbs (usually title of news articles, or capitalized sentence)
    - "noun_gold": skip sentences that gold events are nouns instead of verbs

###output
1. validation output: the detailed output for each record
    e.g. Validation_output_[date].txt
2. validation output analysis: an excel file contains error analysis
    e.g. Validation_output_analysis_[date].xlsx

###usage
python validation2_spanish_withanalysis.py validate [-i validation_file] [-c configuration file] [-l document list (optional)] [-s skip list (optional)]

example:
1. run entrie validation set
python validation2_spanish_withanalysis.py validate -i data/text/spanish_protest_cameo_4_jj_validation.xml -c data/config/PETR_config_es.ini

2. run selected stories in the validation set
python validation2_spanish_withanalysis.py validate -i data/text/spanish_protest_cameo_4_jj_validation.xml -c data/config/PETR_config_es.ini -l doclist.txt

###notes
The code skips the records with noun actions automatically.

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
import argparse

import PETRreader
import PETRgraph 
import petrarch_ud
import PETRglobals

import numpy as np
import pandas as pd 

doing_compare = False
doing_P1 = False
doing_P2 = False

#noun_sentences = []
#noun_sentences_filenames = []

none_verb = []
none_verb_id = []
none_verb_filenames = []

unmatched_patterns = []
unmatched_filenames = []

missing_patterns = []

gold_nouns = []
gold_nouns_filenames = []


correct_files = []
incorrect_files = []

stats_dict = {}
stats = []


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

    print(len(PETRglobals.P1VerbDict['verbs']))
    input()

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
    
    #PETRglobals.CodeWithPetrarch1 = True
    #PETRglobals.CodeWithPetrarch2 = False

    
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
            PETRglobals.AgentFileList = line[line.find(">") + 1:line.find("</")].split(',')
            
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
        if '0' not in return_dict[idstrg]['sents']:
            return
        if 'verbs' not in return_dict[idstrg]['sents']['0']:
            return
        str_arr = str(return_dict[idstrg]['sents']['0']['verbs']).strip("{").split(",")
        
        fout.write("Verbs found:\n") 

        for verbID in return_dict[idstrg]['sents']['0']['verbs']:
            verb = return_dict[idstrg]['sents']['0']['verbs'][verbID]
            str_add = str(verbID) + " : text = " + str(verb.text) +", head="+ str(verb.head) +", meaning="+ str(verb.meaning)+", code="+ str(verb.code)+" ,passive="+str(verb.passive) + "\n"
            fout.write("    " + str_add)

        '''
        for x in str_arr[:1]:
            str_num = x.find(":")		
            try:        
                np = sentence.get_verbPhrase(int(x[:str_num].strip()))
                str_add = x[:str_num].strip() + " : text = " + str(np.text) +", head="+ str(np.head) +", meaning="+ str(np.meaning)+", code="+ str(np.code)+" ,passive="+str(np.passive) + "\n"
                fout.write("    " + str_add)
            except Exception as e:
                print(e)
                fout.write(" --> Exception generating sentence.get_verbPhrase(): " + str(e) + '\n')
        '''
        return

    def check_none_verb(expected):
        """ from test_script_ud.py with minor modifications """
        if '0' not in return_dict[idstrg]['sents']:
            return
        if 'verbs' not in return_dict[idstrg]['sents']['0']:
            return
        
        found = False
        for verbID in return_dict[idstrg]['sents']['0']['verbs']:
            verb = return_dict[idstrg]['sents']['0']['verbs'][verbID]
            for i in range(0,len(expected['events'])):
                goldevent = expected['events'][i]
                goldeventtext = expected['eventtexts'][i]
                if verb.rawtext in goldeventtext['eventtext'] and verb.code == None:
                    code = verb.code if verb.code != None else "None"
                    #noneverb = idstrg+"\t"+"verb_raw:"+verb.rawtext+"\tverb_lemma:"+verb.text+"\tgold:"+edict['eventtext']+"\tcode:"+code
                    #noneverb = idstrg+"\t"+expected['text']+"\t"+verb.text+"\t["+code+"]\t"+ goldeventtext['eventtext']+"\t["+goldevent['eventcode']+"]"+"\t"+ goldevent['plover']+"\t"+goldeventtext['sourcetext']+"\t"+goldeventtext['targettext']
                    noneverb = [idstrg,expected['text'],verb.text,"["+code+"]", goldeventtext['eventtext'],"["+goldevent['eventcode']+"]"]

                    none_verb.append(noneverb)
                    none_verb_filenames.append(idstrg)
                    found = True


        '''
        for x in str_arr[:1]:
            str_num = x.find(":")       
            try:        
                np = sentence.get_verbPhrase(int(x[:str_num].strip()))
                str_add = x[:str_num].strip() + " : text = " + str(np.text) +", head="+ str(np.head) +", meaning="+ str(np.meaning)+", code="+ str(np.code)+" ,passive="+str(np.passive) + "\n"
                fout.write("    " + str_add)
            except Exception as e:
                print(e)
                fout.write(" --> Exception generating sentence.get_verbPhrase(): " + str(e) + '\n')
        '''
        return found


    def parse_triplets(phrase_dict):
        """ from test_script_ud.py with minor modifications """
        if '0' not in return_dict[idstrg]['sents']:
            return
        if 'triplets' not in return_dict[idstrg]['sents']['0']:
            return
        triplets=return_dict[idstrg]['sents']['0']['triplets']
        fout.write("Triplets found:\n") 
        '''
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
        '''
        for triple in triplets:
            strs = triplets[triple]
            source_text = strs['source_text']
            target_text = strs['target_text']
            verb_text = strs['verb_text']
            matched_text = strs['matched_txt']
            codes = str(triple).split("#")
            #event = "(" + phrase_dict[codes[0]] + "," + phrase_dict[codes[1]] + "," + phrase_dict[codes[2]] + ")"
            event = "(" + source_text + "," + target_text + "," + verb_text +")"
            str_add = str(triple) + event + ": Matched Text = " + str(matched_text) + "\n"
            fout.write("    " + str_add)                
        return 

    def check_unmatched_triplets(valrecord):
        """ from test_script_ud.py with minor modifications """
        if '0' not in return_dict[idstrg]['sents']:
            return
        if 'triplets' not in return_dict[idstrg]['sents']['0']:
            return
        triplets=return_dict[idstrg]['sents']['0']['triplets']
        
        found = False

        for triple in triplets:
            strs = triplets[triple]
            source_text = strs['source_text']
            target_text = strs['target_text']
            verb_text = strs['verb_text']
            matched_text = strs['matched_txt']
            code = strs['verbcode']
            codes = str(triple).split("#")
            #event = "(" + phrase_dict[codes[0]] + "," + phrase_dict[codes[1]] + "," + phrase_dict[codes[2]] + ")"
            #event = "(" + source_text + "," + target_text + "," + verb_text +")"
            event = verb_text
            for i in range(0,len(valrecord['events'])):
                goldevent = valrecord['events'][i]
                goldeventtext = valrecord['eventtexts'][i]
                if verb_text != None and verb_text.lower() in goldeventtext['eventtext'] and goldevent['eventcode'] not in code:
                    #raw_input(event+"\tsyscode:"+code+"\tmatched:"+matched_text.strip()+"\tgold:"+goldeventtext['eventtext']+","+goldevent['eventcode'])
                   
                    #unmatched_patterns.append(idstrg+"\t"+valrecord['text']+"\t"+event+"\t["+code+"]\t"+matched_text.strip().replace("\t"," ")+"\t"+
                    #    goldeventtext['eventtext']+"\t["+goldevent['eventcode']+"]"+"\t"+ goldevent['plover']) #+"\t"+goldeventtext['sourcetext']+"\t"+goldeventtext['targettext'])
                    unmatched_patterns.append([idstrg,valrecord['text'],event,"["+code+"]",matched_text.strip().replace("\t"," "),goldeventtext['eventtext'],"["+goldevent['eventcode']+"]"])
                    unmatched_filenames.append(idstrg)
                    found = True


        return found

    def check_missing_pattern(expected):
        """ from test_script_ud.py with minor modifications """
        if '0' not in return_dict[idstrg]['sents']:
            return
        if 'triplets' not in return_dict[idstrg]['sents']['0']:
            return

        found = False

        for verbID in return_dict[idstrg]['sents']['0']['verbs']:
            verb = return_dict[idstrg]['sents']['0']['verbs'][verbID]
            for i in range(0,len(expected['events'])):
                goldevent = expected['events'][i]
                goldeventtext = expected['eventtexts'][i]
                if verb.rawtext in goldeventtext['eventtext'] and verb.code == '---':
                    code = verb.code if verb.code != None else "None"
                    #noneverb = idstrg+"\t"+"verb_raw:"+verb.rawtext+"\tverb_lemma:"+verb.text+"\tgold:"+edict['eventtext']+"\tcode:"+code
                    #noneverb = idstrg+"\t"+expected['text']+"\t"+verb.text+"\t["+code+"]\t"+ goldeventtext['eventtext']+"\t["+goldevent['eventcode']+"]"+"\t"+ goldevent['plover']+"\t"+goldeventtext['sourcetext']+"\t"+goldeventtext['targettext']
                    noneverb = [idstrg,expected['text'],verb.text,"["+code+"]", goldeventtext['eventtext'],"["+goldevent['eventcode']+"]", goldevent['plover']]
                    missing_patterns.append(noneverb)

                    found = True

        return found


    '''
    def check_if_matched(return_dict, idstrg):

        if '0' in return_dict[idstrg]['sents'] and  'events' in return_dict[idstrg]['sents']['0'] and len(return_dict[idstrg]['sents']['0']['events']) > 0:
            print(return_dict[idstrg]['sents']['0']['events'])
            event_out = process_event_output(str(return_dict[idstrg]['sents']['0']['events']))
            
            nfound, ncoded, nnull = 0, 0, 0
            for key, evt in return_dict[idstrg]['sents']['0']['events'].items():
                try:
                    #if evt[0][0].startswith("---") or evt[1][0].startswith("---") or evt[2].startswith("---") :
                    if evt[2].startswith("---") :
                        nnull += 1
                        continue
                except:   # handles [] cases
                    nnull += 1
                    continue       
                try:
                    ncoded += 1
                    for edict in valrecord['events']:
                        if "noevents" in edict:
                            break                 
                        else:
                            
                            sourcematch = True
                            targetmatch = True
                            #if (edict['eventcode'] == evt[2] and
                            #    edict['sourcecode'] == evt[0][0] and
                            #    edict['targetcode'] == evt[1][0]) :
                            if edict['eventcode'][:2] not in ["18","19"]:
                                if edict['eventcode'][:2] == evt[2][:2] and  (sourcematch and targetmatch): # for spanish now only match event code
                                    fout.write("  CORRECT\n")
                                    nfound += 1
                                    edict['found'] = True
                                    matched = True
                                    break
                       
                            else:
                                # if 2-digit system event code is 18 and 2-digit gold code is 19, it is counted as correct
                                # and vice-versa
                                if evt[2][:2] in ["18","19"] and (sourcematch and targetmatch):
                                    fout.write("  CORRECT\n")
                                    nfound += 1
                                    edict['found'] = True
                                    matched = True
                                    break
                                                         
                except:
                    pass
        else:
            if "noevents" in valrecord['events'][0]:
                nfound, ncoded, nnull = 1, 1, 0  # count this as a match
            else:
                nfound, ncoded, nnull = 0, 0, 0

        return nfound,ncoded,nnull
    '''

    logger = logging.getLogger('petr_log.validate')
#        logger.addFilter(NoLoggingFilter())  # uncomment to decactivate logging for this function      
    parse = valrecord['parse']
    idstrg = valrecord['id']
    print("evaluating", idstrg)
   
    
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {idstrg: {u'sents': {u'0': {u'content': valrecord['text'], u'parsed': parsed}},
        u'meta': {u'date': valrecord['date']}}}


    return_dict = "" 
    return_dict = petrarch_ud.do_coding(dict)

    #numcorrect, numcoded, numnull = check_if_matched(return_dict,idstrg)

    #if not (numnull < 1 and numcorrect > 0):
    #    return

    '''
    if numcorrect == 0:
        check_none_verb(valrecord)
        check_unmatched_triplets(valrecord)
        if idstrg in none_verb_filenames or idstrg in unmatched_filenames:
            #raw_input(idstrg)
            return
    '''

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

    for i in range(len(valrecord['events'])):    
        edict =  valrecord['events'][i]
        if "noevents" in edict:
            fout.write("    noevents\n")                 
        else:
            fout.write("    " + edict['eventcode']  + ' ' + edict['sourcecode']  + ' ' + edict['targetcode']  + '\n') 
            #fout.write("    " + edict['eventcode']  + ' ' + valrecord['eventtexts'][i]['eventtext'] + '\n') 

    fout.write("Coded events:\n")
    if '0' not in return_dict[idstrg]['sents']:
        print(return_dict[idstrg])
        #raw_input()

    if '0' in return_dict[idstrg]['sents'] and  'events' in return_dict[idstrg]['sents']['0'] and len(return_dict[idstrg]['sents']['0']['events']) > 0:
        print(return_dict[idstrg]['sents']['0']['events'])
        event_out = process_event_output(str(return_dict[idstrg]['sents']['0']['events']))
        
        nfound, ncoded, nnull = 0, 0, 0
        for key, evt in return_dict[idstrg]['sents']['0']['events'].items():
            try:
                #if evt[0][0].startswith("---") or evt[1][0].startswith("---") or evt[2].startswith("---") :
                if evt[2].startswith("---") :
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
                        
                        sourcematch = False
                        targetmatch = False

                        if edict['sourcecode'].replace("---","") == evt[0][0].replace("---",""):
                            sourcematch = True
                        #elif edict['sourcecode'] == "---" and evt[0][0] != "---":
                        #    sourcematch = True
                        else:
                            #allow partial actor code match in some cases
                            goldsrcset = []
                            goldtemp = edict['sourcecode'].replace("---","").replace("COL","")
                            goldn = len(goldtemp)//3
                            for i in range(goldn):
                                goldsrcset.append(goldtemp[i*3:(i+1)*3])
                            print("g:",goldsrcset)
                            #input(" ")

                            syssrcset = []
                            systemp = evt[0][0].replace("---","").replace("COL","")
                            sysn = len(systemp)//3
                            for i in range(sysn):
                                syssrcset.append(systemp[i*3:(i+1)*3])
                            print("s:",syssrcset)
                            #input(" ")
                            if len(syssrcset) >0 and len(goldsrcset)>0:
                                if len(syssrcset)<= len(goldsrcset):
                                    fc = 0
                                    for src in syssrcset:
                                        if src in goldsrcset:
                                            fc += 1
                                    if fc/len(syssrcset) >= 0.5:
                                        sourcematch = True
                                        #input(" ")
                                else:
                                    fc = 0
                                    for src in goldsrcset:
                                        if src in syssrcset:
                                            fc += 1
                                    if fc/len(goldsrcset) >= 0.5:
                                        sourcematch = True
                                        #input(" ")

                        if edict['targetcode'].replace("---","") == evt[1][0].replace("---",""):
                            targetmatch = True
                        #elif edict['targetcode'] == "---" and evt[1][0] != "---":
                        #    targetmatch = True
                        else:
                            goldsrcset = []
                            goldtemp = edict['targetcode'].replace("---","").replace("COL","")
                            goldn = len(goldtemp)//3
                            for i in range(goldn):
                                goldsrcset.append(goldtemp[i*3:(i+1)*3])
                            print("g:",goldsrcset)
                            #input(" ")

                            syssrcset = []
                            systemp = evt[1][0].replace("---","").replace("COL","")
                            sysn = len(systemp)//3
                            for i in range(sysn):
                                syssrcset.append(systemp[i*3:(i+1)*3])
                            print("s:",syssrcset)
                            #input(" ")
                            if len(syssrcset) >0 and len(goldsrcset)>0:
                                if len(syssrcset)<= len(goldsrcset):
                                    fc = 0
                                    for src in syssrcset:
                                        if src in goldsrcset:
                                            fc += 1
                                    if fc/len(syssrcset) >= 0.5:
                                        targetmatch = True
                                        #input(" ")
                                else:
                                    fc = 0
                                    for src in goldsrcset:
                                        if src in syssrcset:
                                            fc += 1
                                    if fc/len(goldsrcset) >= 0.5:
                                        targetmatch = True
                                    #input(" ")
                        #if (edict['eventcode'] == evt[2] and
                        #    edict['sourcecode'] == evt[0][0] and
                        #    edict['targetcode'] == evt[1][0]) :
                        if edict['eventcode'][:2] not in ["18","19"]:
                            if edict['eventcode'][:2] == evt[2][:2] and  (sourcematch and targetmatch): # for spanish now only match event code
                                fout.write("  CORRECT\n")
                                nfound += 1
                                edict['found'] = True
                                matched = True
                                break
                        else:
                            # if 2-digit system event code is 18 and 2-digit gold code is 19, it is counted as correct
                            # and vice-versa
                            if evt[2][:2] in ["18","19"] and (sourcematch and targetmatch):
                                fout.write("  CORRECT\n")
                                nfound += 1
                                edict['found'] = True
                                matched = True
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
        
    if nfound > 0:
        correct_files.append(idstrg)

    num_found = 0
    num_notcoded = 0
    numcoded = 0

    for edict in valrecord['events']:
        if "noevents" in edict:
            num_found = 1
            num_coded = 1
        else:
            if 'found' in edict and edict['found'] == True:
                num_found +=1
            else:
                num_notcoded +=1


    #fout.write("Stats:\n    Correct: " + str(nfound) + "   Not coded: " + str(len(valrecord['events']) - nfound) 
    #            + "   Extra events: " + str(ncoded - nfound)  + "   Null events: " + str(nnull) + '\n') 

    fout.write("Stats:\n    Correct: " + str(num_found) + "   Not coded: " + str(num_notcoded) 
                + "   Extra events: " + str(ncoded - nfound)  + "   Null events: " + str(nnull) + '\n') 
    if valrecord['category'] in valid_counts:
        valid_counts[valrecord['category']][0] += 1  # records
        valid_counts[valrecord['category']][1] += num_found #nfound  # correct
        valid_counts[valrecord['category']][2] += num_notcoded #len(valrecord['events']) - nfound  # uncoded
        valid_counts[valrecord['category']][3] += ncoded - nfound  # extra
        valid_counts[valrecord['category']][4] += nnull            # null
    else:
        #valid_counts[valrecord['category']] = [1, nfound, len(valrecord['events']) - nfound, ncoded - nfound, nnull]
        valid_counts[valrecord['category']] = [1, num_found, num_notcoded, ncoded - nfound, nnull]
        valid_counts['catlist'].append(valrecord['category'])  # keep track of the order of the categories found
    
    try:        
        sentence = PETRgraph.Sentence(parsed, valrecord['text'] , 0000)  # 18.05.22: what the heck is this doing???
    except Exception as e:
        print(" --> Exception generating PETRgraph.Sentence(): ",e)
        fout.write(" --> Exception generating PETRgraph.Sentence(): " + str(e) + '\n')

    if not doing_compare:
        parse_verb(phrase_dict, sentence)

        
        if idstrg not in correct_files:
            noneverbflag = check_none_verb(valrecord)
            unmatchflag = check_unmatched_triplets(valrecord)
            missingflag = check_missing_pattern(valrecord)

            if valrecord['id'] not in stats_dict:
                stats_dict[valrecord['id']] = {}

            stats_dict[valrecord['id']]['noneverb'] = noneverbflag
            stats_dict[valrecord['id']]['unmatch'] = unmatchflag
            stats_dict[valrecord['id']]['missing'] = missingflag
            stats_dict[valrecord['id']]['correct'] = False

            #stats.append(idstrg+"False\t"+str(noneverbflag)+"\t"+str(unmatchflag)+"\t"+str(missingflag)+"\t"+str(nfound) + "\t" + str(len(valrecord['events']) - nfound) 
            #    + "\t" + str(ncoded - nfound)  + "\t" + str(nnull))
        else:

            if valrecord['id'] not in stats_dict:
                stats_dict[valrecord['id']] = {}

            stats_dict[valrecord['id']]['noneverb'] = False
            stats_dict[valrecord['id']]['unmatch'] = False
            stats_dict[valrecord['id']]['missing'] = False
            stats_dict[valrecord['id']]['correct'] = True
            #stats.append(idstrg+"True\t"+"False\t"+"False\t"+"False\t"+str(nfound) + "\t" + str(len(valrecord['events']) - nfound) 
            #    + "\t" + str(ncoded - nfound)  + "\t" + str(nnull))

        stats_dict[valrecord['id']]['numbers'] = [nfound,(len(valrecord['events']) - nfound),(ncoded-nfound),nnull]
        parse_triplets(phrase_dict)
    fout.write('\n')


def do_validation():
    """ Functional tests using a validation file. """
    #PETRglobals.PauseBySentence = False
    #PETRglobals.CodeWithPetrarch1 = True
    #PETRglobals.CodeWithPetrarch2 = False


    def get_line_attribute(target):
        """ quick and dirty function for extracting well-formed XML attributes"""
        part = line.partition(target)
        return part[2][2:part[2].find('"',3)]

    ka = 0 # debugging counters
    kb = 0
    line = fin.readline() 
    while len(line) > 0:  # loop through the file
        ka += 1
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
                                    'plover': get_line_attribute('plover'),
                                    'coded': False
                                    }
                        if 'events' in valrecord:
                            valrecord['events'].append(theevent)
                        else:
                            valrecord['events'] = [theevent]

                        #valrecord['category'] = theevent['eventcode'] #test

                elif line.startswith("<EventText") and not doing_compare:
                    if 'noevents="True"' in line:
                        valrecord['eventtexts'] = ["noevents"]    
                    else:
                        theevent = {
                                    'coding' : line[line.find(" ") + 1:line.find(">")],  # not actually using this
                                    'eventtext': get_line_attribute('eventtext'),
                                    'sourcetext' :  get_line_attribute('sourcetext'),
                                    'targettext' : get_line_attribute('targettext'),
                                    'coded': False
                                    }
                        if 'eventtexts' in valrecord:
                            valrecord['eventtexts'].append(theevent)
                        else:
                            valrecord['eventtexts'] = [theevent]

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
                    found_verb = False

                    if 'events' in valrecord:
                        gold_is_noun = [False]*len(valrecord['events'])
                        gold_is_verb = [False]*len(valrecord['events'])
                        postags = [""]*len(valrecord['events'])

                    while not line.startswith("</Parse"):
                        tmp = line.split("\t")

                        if valrecord['valid'] and 'events' in valrecord and "noevents" not in valrecord['eventtexts']:

                            for eid in range(0,len(valrecord['events'])):
                                #print(tmp)
                                if tmp[1] in valrecord['eventtexts'][eid]['eventtext']:
                                    postags[eid] = postags[eid] + " " + tmp[3]
                                    if "VERB" in line:
                                        gold_is_verb[eid] = True
                                    elif "NOUN" in line or "PROPN" in line or "ADJ" in line:
                                        gold_is_noun[eid] = True

                        if "VERB" in line:
                            found_verb = True
                        parse += line
                        line = fin.readline() 

                    valrecord['parse'] = parse

                    #print("gold is verb:",gold_is_verb)
                    #print("gold is noun:",gold_is_noun)
                    #print(found_verb)
                    #input(" ")
                    
                    #check if verb is found in the sentence
                    if not found_verb:
                        #noun_sentences.append(valrecord['sentence']+" "+valrecord['text'])
                        #noun_sentences_filenames.append(valrecord['id'])

                        if "noun_sentence" in skiplist:
                            valrecord['valid'] = False
                            print(valrecord['id']+" doesn't contain verbs")

                        if valrecord['id'] in stats_dict:
                            stats_dict[valrecord['id']]['nounsent'] = True
                        else:
                            stats_dict[valrecord['id']] = {}
                            stats_dict[valrecord['id']]['nounsent'] = True
                    else:
                        if valrecord['id'] in stats_dict:
                            stats_dict[valrecord['id']]['nounsent'] = False
                        else:
                            stats_dict[valrecord['id']] = {}
                            stats_dict[valrecord['id']]['nounsent'] = False
                        #raw_input("")
                        #input(" ")
                    if valrecord['valid'] and 'events' in valrecord:
                        for eid in range(0,len(valrecord['events'])):
                            if gold_is_noun[eid] and not gold_is_verb[eid]:
                                gold_nouns.append(valrecord['id']+"\t"+valrecord['text']+"\t"+valrecord['eventtexts'][eid]['eventtext']+"\t"+postags[eid])
                                #print(valrecord['sentence']+"\t"+valrecord['text']+"\t"+valrecord['eventtexts'][eid]['eventtext'])
                                if "noun_gold" in skiplist:
                                    valrecord['valid'] = False
                                    print(valrecord['id']+" contain noun actions")

                                gold_nouns_filenames.append(valrecord['id'])
                                if valrecord['id'] in stats_dict:
                                    stats_dict[valrecord['id']]['nounaction'] = True
                                else:
                                    stats_dict[valrecord['id']] = {}
                                    stats_dict[valrecord['id']]['nounaction'] = True
                            else:
                                if valrecord['id'] in stats_dict:
                                    stats_dict[valrecord['id']]['nounaction'] = False
                                else:
                                    stats_dict[valrecord['id']] = {}
                                    stats_dict[valrecord['id']]['nounaction'] = False
                                #raw_input("")

                    #if valrecord['id'] in none_verb_id:
                        #valrecord['valid'] = False
                        #raw_input(valrecord['id'])
                    

                    break
                line = fin.readline() 

            print("\nRecord:",valrecord['id'],recordType)
            docname = valrecord['id'][0:valrecord['id'].rindex("_",)]
            if len(doclist)> 0 and docname not in doclist:
                #print(docname,doclist)
                valrecord['valid'] = False
                fout.write("Not in the doc list: " + valrecord['id']  + "\n" + idline  + "\n")
                #input(" ")

            if 'events' not in valrecord:
                valrecord['valid'] = False

            if recordType == 'Sentence' and valrecord['category'] in ValidInclude and valrecord['valid']:
                validate_record(valrecord)
                kb += 1
            elif not valrecord['valid']:
                fout.write("Skipping " + valrecord['id']  + "\n" + idline  + "\n")
#            if kb > 60: break

        line = fin.readline() 

def parse_cli_args():
    """Function to parse the command-line arguments for PETRARCH."""
    __description__ = """
PETRARCH
(https://openeventdata.github.io/) (v. 0.01)
    """
    aparse = argparse.ArgumentParser(prog='petrarch',
                                     description=__description__)

    sub_parse = aparse.add_subparsers(dest='command_name')

    validation_command = sub_parse.add_parser('validate')
    validation_command.add_argument('-i', '--inputs',
                               help='File, or directory of files, to parse.',
                               required=True)
    validation_command.add_argument('-d', '--debug', action = 'store_true', default = False,
                               help="""Enable debug info""")
    validation_command.add_argument('-c', '--config',
                               help="""Filepath for the PETRARCH configuration
                               file. Defaults to PETR_config.ini""",
                               required=False)
    validation_command.add_argument('-l', '--doclist', help = """list of document names to parse""",required=False)
    ##--skip option: skip some of the records. This option is used for analyzing
    ## usage example: -s "noun_sentence#noun_gold"
    ## "noun_sentence": skip sentences that the parsed tree don't contain verbs (usually title of news articles, or capitalized sentence)
    ## "noun_gold": skip sentences that gold actions are nouns instead of verbs
    validation_command.add_argument('-s', '--skip',help = """types of records to skip. Defaults to none""", default = "none", required=False)

    args = aparse.parse_args()
    return args

if __name__ == '__main__':
 # get path to validation file
    '''
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
    '''

    cli_args = parse_cli_args()

    if cli_args.config:
        print('Using user-specified config: {}'.format(cli_args.config))
        PETRglobals.ConfigFileName = cli_args.config

        PETRreader.parse_Config(cli_args.config)
    else:
        print('Using default config file.')
        PETRglobals.ConfigFileName = 'PETR_config.ini'
        PETRreader.parse_Config(utilities._get_data('data/config/',
                                                    'PETR_config.ini'))

    if cli_args.inputs:
        directory_name = "data/text"
        filename = cli_args.inputs

    doclist = []
    if cli_args.doclist:
        print('Process documents in the list only: {}'.format(cli_args.doclist))
        with open(cli_args.doclist,'r') as file:
            doc = file.readline()
            while len(doc)>0:
                doclist.append(doc.strip())
                doc = file.readline()

    try:
        #fin = open(os.path.join(directory_name, filename),'r')
        fin = open(filename,'r')
    except:
        print("can't find the validation file", filename)
        exit()

    skiplist = ""
    if cli_args.skip:
        print('Skipping records of type: {}'.format(cli_args.skip))
        skiplist = cli_args.skip
    
    print("Reading validation file ",filename)
    foutfilname = "Validation_output_"+datetime.datetime.now().strftime("%Y%m%d")[2:]+".txt"
    fout = open(foutfilname, 'w')

    #PETRglobals.CodeWithPetrarch1 = True
    #PETRglobals.CodeWithPetrarch2 = False

    utilities.init_logger('UD-PETR_Validate.log', debug = False)
    timestamp =  datetime.datetime.now().strftime("%Y%m%d")[2:] + "-" + datetime.datetime.now().strftime("%H%M%S")
    fout.write("UD-PETRARCH functional validation\nRun date-time: " + timestamp + "\nValidation file:    " + filename + "\n")

    ValidInclude, ValidExclude, ValidPause, ValidOnly = get_environment()
    print("Reading dictionaries")
    if directory_name == "validate":
        read_validate_dictionaries()
    else:
        petrarch_ud.read_dictionaries()
        #input(" ")
        

    valid_counts = {'catlist': []}
    if doing_compare:
        type_counts = [0,0,0,0,0,0,0]

    fout.write('Verb dictionary:    ' + PETRglobals.VerbFileName + "\n")
    if PETRglobals.CodeWithPetrarch1:
        fout.write('Petrarch 1 Verb dictionary: ' + PETRglobals.P1VerbFileName + "\n")
    fout.write('Actor dictionaries: ' + str(PETRglobals.ActorFileList) + "\n")
    fout.write('Agent dictionaries: ' + str(PETRglobals.AgentFileList) + "\n")
    fout.write('Discard dictionary: ' + PETRglobals.DiscardFileName + "\n")
    fout.write('PICO file:          ' + PETRglobals.InternalCodingOntologyFileName + "\n\n" )

    if not doing_compare:
        do_validation()
        #raw_input("enter do validation")
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
        fout.write(" {:8.2f}%".format(np.divide((valid_counts[catstrg][1] * 100.0),(valid_counts[catstrg][1] + valid_counts[catstrg][2]))))
        fout.write(" {:8.2f}%".format(np.divide((valid_counts[catstrg][2] * 100.0),(valid_counts[catstrg][1] + valid_counts[catstrg][2]))))
        fout.write(" {:8.2f}%".format(np.divide((valid_counts[catstrg][3] * 100.0),(valid_counts[catstrg][0]))))  # this as percent of records
        fout.write('\n')
    fout.write("TP = correct/(correct + uncoded) \n")
    fout.write("FN = uncoded/(correct + uncoded) = 100 - TP \n")
    fout.write("FP = extra/records\n")
    print("\nRecords evaluated:{:8d}".format(valid_counts['Total'][0]))
    print("Correct events:   {:8d} {:8.2f}%".format(valid_counts['Total'][1], np.divide((valid_counts['Total'][1] * 100.0),(valid_counts['Total'][1] + valid_counts['Total'][2]))))
    print("Uncoded events:   {:8d} {:8.2f}%".format(valid_counts['Total'][2], np.divide((valid_counts['Total'][2] * 100.0),(valid_counts['Total'][1] + valid_counts['Total'][2]))))
    print("Extra events:     {:8d} {:8.2f}%".format(valid_counts['Total'][3], np.divide((valid_counts['Total'][3] * 100.0),valid_counts['Total'][0])))
    print("===========================\n")
    if doing_compare:
        print("Accuracy on coded single event cases:")
        fout.write("\nAccuracy on coded single event cases:\n")
        for ka, lbl in enumerate(["", "Event", "Cue category", "Source", "Source primary", "Target", "Target primary"]):
            if ka == 0: continue
            print("{:14s}:   {:8d} {:8.2f}%".format(lbl, type_counts[ka], np.divide((type_counts[ka] * 100.0),type_counts[0])))
            fout.write("{:14s}:   {:8d} {:8.2f}%\n".format(lbl, type_counts[ka], np.divide((type_counts[ka] * 100.0),type_counts[0])))
        print("===========================\n")

    '''
    analysis_filename = "Validation_output_analysis_"+datetime.datetime.now().strftime("%Y%m%d")[2:]+".xlsx"
    
    writer = pd.ExcelWriter(analysis_filename)

    stats_head = ["ID","Correct","NounSentence","NounEvent","VerbNotFound","CodeNotMatch","MissingPattern","#Found Events" , "#Missing Events","#Extra Event" ,"#Null Events"]
    for key in stats_dict:
        if 'correct' in stats_dict[key]:
            stats.append([key,str(stats_dict[key]['correct']),"False", "False", str(stats_dict[key]['noneverb']),str(stats_dict[key]['unmatch'])
                ,str(stats_dict[key]['missing']),str(stats_dict[key]['numbers'][0]),str(stats_dict[key]['numbers'][1]) 
                ,str(stats_dict[key]['numbers'][2]),str(stats_dict[key]['numbers'][3])])
        else:
            row = [key,"False",str(stats_dict[key]['nounsent']),str(stats_dict[key]['nounaction'])] 
            row = row + [[""]] * (len(stats_head) - len(row))
            stats.append(row)

    stats_df = pd.DataFrame(stats,columns=stats_head)
    stats_df.to_excel(writer, sheet_name = 'statistics', index = False)

    
    unmatched_head = ["ID","Sentence","System verb(lemma)","System Code","Matched pattern","Gold event text","Gold Code"]
    unmatched_df = pd.DataFrame(unmatched_patterns, columns=unmatched_head)
    unmatched_df.to_excel(writer,sheet_name = "mismatched", index = False)

    none_verb_head = ["ID","Sentence","System verb(lemma)","System Code","Gold event text","Gold Code"]
    none_verb_df = pd.DataFrame(none_verb, columns=none_verb_head)
    none_verb_df.to_excel(writer,sheet_name = "not found", index = False)
    writer.save()
    '''

    fin.close()
    fout.close()

       






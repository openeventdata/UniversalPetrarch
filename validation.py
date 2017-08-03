# -*- coding: utf-8 -*-

"""
validation.py

Runs validation cases for UniversalPetrarch

TO RUN PROGRAM:

python3 validation.py

PROGRAMMING NOTES:

1.  This combines code from the validation suite of TABARI and PETRARCH-1 with the code accessing UD-PETR 
    and its data structures from the script test_script_ud.py (last update: 5 July 2017). This output is
    a combination of the two approaches, and some of the options that were tested in TABARI and PETRARCH-1 
    are not relevant to UD-PETR and haven't been implemented.
    
2.  The PETR.UnitTest.records.parsing_parsed_udpipe_2.1.xml file is currently XML and could be read as 
    such, but in all likelihood this will soon to transitioned over to JSON, so the fields are being
    processed without using XML tools.
    
SYSTEM REQUIREMENTS
This program has been successfully run under Mac OS 10.10.5; it is standard Python 3.5
so it should also run in Unix or Windows. 

PROVENANCE:
Programmer: Philip A. Schrodt
            Parus Analytics
            Charlottesville, VA, 22901 U.S.A.
            http://eventdata.parusanalytics.com

This program was developed as part of research funded by a U.S. National Science Foundation "Resource 
Implementations for Data Intensive Research in the Social Behavioral and Economic Sciences (RIDIR)" 
project: Modernizing Political Event Data for Big Data Social Science Research (Award 1539302; 
PI: Patrick Brandt, University of Texas at Dallas)

Copyright (c) 2017	Philip A. Schrodt.	All rights reserved.

This code is covered under the MIT license: http://opensource.org/licenses/MIT

Report bugs to: schrodt735@gmail.com

REVISION HISTORY:
27-July-17:	Initial version based on parallel function in PETRARCH-1

=========================================================================================================
"""
from __future__ import print_function

import codecs
import logging
import utilities
import PETRreader
import PETRgraph 
import petrarch_ud
import PETRglobals

global allrecords, allcorrect, alluncoded, allextra, allnull, ValidInclude

# ========================== VALIDATION FUNCTIONS ========================== #


def change_Config_Options(line):
    """Changes selected configuration options: THIS IS PETR-1 CODE AND HASN'T BEEN IMPLEMENTED YET """
    # need more robust error checking
    theoption = line['option']
    value = line['value']
    print("<Config>: changing", theoption, "to", value)
    if theoption == 'new_actor_length':
        try:
            PETRglobals.NewActorLength = int(value)
        except ValueError:
            logger.warning("<Config>: new_actor_length must be an integer; command ignored")
    elif theoption == 'require_dyad':
        PETRglobals.RequireDyad = not 'false' in value.lower()
    elif theoption == 'stop_on_error':
        PETRglobals.StoponError = not 'false' in value.lower()
    elif 'comma_' in theoption:
        try:
            cval = int(value)
        except ValueError:
            logger.warning("<Config>: comma_* value must be an integer; command ignored")
            return
        if '_min' in theoption:
            PETRglobals.CommaMin = cval
        elif '_max' in theoption:
            PETRglobals.CommaMax = cval
        elif '_bmin' in theoption:
            PETRglobals.CommaBMin = cval
        elif '_bmax' in theoption:
            PETRglobals.CommaBMax = cval
        elif '_emin' in theoption:
            PETRglobals.CommaEMin = cval
        elif '_emax' in theoption:
            PETRglobals.CommaEMax = cval
        else:
            logger.warning("<Config>: unrecognized option beginning with comma_; command ignored")
    # insert further options here in elif clauses as this develops; also
    # update the docs in open_validation_file():
    else:
        logger.warning("<Config>: unrecognized option")


def get_environment():
    """ Light-weight routine for reading the <Environment> block """
    ValidExclude = None
    ValidInclude = None
    ValidOnly = True
    ValidPause = 0

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
            PETRglobals.ActorFileList = [line[line.find(">") + 1:line.find("</")]]

        elif '<Agentfile' in line:
            PETRglobals.AgentFileName = line[line.find(">") + 1:line.find("</")]
            
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

    print(PETRglobals.VerbFileName, PETRglobals.ActorFileList[0], PETRglobals.AgentFileName, PETRglobals.DiscardFileName)
    print(ValidInclude, ValidExclude)
    print(ValidPause, ValidOnly)
    return ValidInclude, ValidExclude, ValidPause, ValidOnly


def process_reciprocals(returnevents):
    """ temporary function to resolve the reciprocal codes """
    for key, evt in returnevents.items():
        if evt[2] and ":" in evt[2]:
            returnevents.pop(key, None)
            part = evt[2].partition(":")
            returnevents[key + "R1"] = [evt[0], evt[1], part[0]]
            returnevents[key + "R2"] = [evt[1], evt[0], part[2]]


def validate_record(valrecord):
    """ primary procedure which calls the coder with the parse in valrecord and compares the coded results with the expected 
        as well as writing assorted intermediate data structures to fout per test_script_ud.py """

    global allrecords, allcorrect, alluncoded, allextra, allnull

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
#        print("Verb/Noun", str_arr)
        fout.write("Verbs found:\n") 
        for x in str_arr:
            str_num = x.find(":")		
            try:        
                np = sentence.get_verbPhrase(int(x[:str_num].strip()))
                str_add = x[:str_num].strip() + " : text = " + str(np.text) +", head="+ str(np.head) +", meaning="+ str(np.meaning)+", code="+ str(np.code)+" ,passive="+str(np.passive) + "\n"
                fout.write(str_add)
            except Exception as e:
                print(e)
                fout.write(" --> Exception generating sentence.get_verbPhrase(): " + str(e) + '\n')
        return

    def parse_noun(phrase_dict,sentence):
        """ from test_script_ud.py with minor modifications """
        if 'nouns' in return_dict[idstrg]['sents']['0']:
            return
        str_arr = str(return_dict[idstrg]['sents']['0']['nouns']).strip("{").split(",")
        fout.write("Nouns found:\n") 
        for x in str_arr:
            str_num = x.find(":")		
            try:        
                np = sentence.get_nounPharse(int(x[:str_num].strip()))
                np.get_meaning()
                str_add =  x[:str_num].strip() + " : head = " + str(np.head) +", text="+ str(np.text) +", meaning="+str(np.meaning)+", matched_txt="+str(np.matched_txt)+ "\n"
                fout.write(str_add)                
            except Exception as e:
                print(e)
                fout.write(" --> Exception generating sentence.get_nounPharse(): " + str(e) + '\n')
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
            fout.write(str_add)                
        return 

    logger = logging.getLogger('petr_log.validate')
#        logger.addFilter(NoLoggingFilter())  # uncomment to decactivate logging for this function      
    parse = valrecord['parse']
    idstrg = valrecord['id']
    print("evaluating", idstrg)
    logger.debug("\nevaluating: "+ idstrg)
#    allrecords += 1
    fout.write("Record ID: " + idstrg + '\n')
    fout.write("Text:\n" + valrecord['text'] + '\n')
    fout.write("Parse:\n " + parse)
    fout.write("Expected events:\n")
    for edict in valrecord['events']:
        if "noevents" in edict:
            fout.write("noevents\n")                 
        else:
            fout.write(edict['eventcode']  + ' ' + edict['sourcecode']  + ' ' + edict['targetcode']  + '\n') 
    
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {idstrg: {u'sents': {u'0': {u'content': valrecord['text'], u'parsed': parsed}},
        u'meta': {u'date': u'19950101'}}}
    return_dict = "" 
    return_dict = petrarch_ud.do_coding(dict)  # 17.07.31: by-pass the try block for now so errors can be isolated
    """try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        fout.write("petrarch_ud.do_coding() runtime error " + str(e) + '\n')"""

#    try:  # 17.07.31: by-pass the try block for now so errors can be isolated
    if 'events' in return_dict[idstrg]['sents']['0']:
        print(return_dict[idstrg]['sents']['0']['events'])
        process_reciprocals(return_dict[idstrg]['sents']['0']['events'])
        event_out = process_event_output(str(return_dict[idstrg]['sents']['0']['events']))
        fout.write("Coded events:\n")
        
        nfound, ncoded, nnull = 0, 0, 0
        for key, evt in return_dict[idstrg]['sents']['0']['events'].items():
            try:
                if evt[0][0][:3] == "---" or evt[1][0][:3] == "---" :
                    nnull += 1
                    continue
            except:   # handles [] cases
                nnull += 1
                continue       
            try:
                fout.write(evt[2] + ' ' + evt[0][0] + ' ' + evt[1][0] + "  (" + key + ")")                        
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
                    fout.write("  ERROR\n")
                                                        
            except:
                pass
        if nnull > 0:
            fout.write("Null events: " + str(nnull)  + '\n')                
        fout.write("Event source:\n")
        fout.write(str(return_dict[idstrg]['sents']['0']['events']) + '\n')
    else:
        fout.write("No events returned\n")
        if "noevents" in valrecord['events'][0]:
            nfound, ncoded, nnull = 1, 1, 0  # count this as a match
        else:
            nfound, ncoded, nnull = 0, 0, 0
        
    """except:
        fout.write(idstrg + " Failed\n")  # not clear why we'd hit this, or more to the point, that 'try' block should be more compartmentalized
        print(idstrg + " Failed")
        fout.write('\n')
        return"""
        
    fout.write("Correct: " + str(nfound) + "   Not coded: " + str(len(valrecord['events']) - nfound) 
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
        sentence = PETRgraph.Sentence(parsed, valrecord['text'] , 0000)
    except Exception as e:
        print(" --> Exception generating PETRgraph.Sentence(): ",e)
        fout.write(" --> Exception generating PETRgraph.Sentence(): " + str(e) + '\n')

    parse_verb(phrase_dict, sentence)
    parse_noun(phrase_dict, sentence)
    parse_triplets(phrase_dict)
    fout.write('\n')


def do_validation():
    """ Unit tests using a validation file. """
    global valid_counts, ValidInclude

    def get_line_attribute(target):
        """ quick and dirty function for extracting well-formed XML attributes"""
        part = line.partition(target)
        return part[2][2:part[2].find('"',3)]

    ValidInclude, ValidExclude, ValidPause, ValidOnly = get_environment()
    print("Reading dictionaries")
    petrarch_ud.read_dictionaries()

    valid_counts = {'catlist': []}
    allrecords, allcorrect, alluncoded, allextra, allnull = 0, 0, 0, 0, 0
    ka = 0 # debugging counters
    kb = 0
    line = fin.readline() 
    while len(line) > 0:  # loop through the file
        ka += 1
#        if ka > 36: break
        if line.startswith("<Stop"):
            print("Exiting: <Stop> record ")
            break

        if line.startswith("<Sentence "):
            valrecord = {}
            recordType = 'Sentence'
            valrecord['sentence'] = line[line.find(" ") + 1:line.find(">")]
            valrecord['date'] = get_line_attribute('date')
            valrecord['category'] = get_line_attribute('category')
            valrecord['id'] = get_line_attribute('id')
            if get_line_attribute('valid').lower() == 'true':
                valrecord['valid'] = True
            else:
                valrecord['id'] = get_line_attribute('id')

            line = fin.readline() # get the rest of the record
            while len(line) > 0: 
                if line.startswith("<EventCoding"):
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
            """for k, v in valrecord.items():
                print(k)
                print(v)"""
            """if valrecord['category'] != 'DEMO':  # debugging option to stop evaluation after the DEMO records
                break """
            if recordType == 'Sentence' and valrecord['category'] in ValidInclude:
                validate_record(valrecord)
                kb += 1
            else:
                print("  Category not coded")
#            if kb > 60: break
            
            """  # this is the code for the main validation loop from PETR-1 and probably is largely redundant now but leave it here
                 # for the time being
            if recordType == 'Config':
                change_Config_Options(valrecord.attrib)
            if recordType == 'Sentence':
                try:
                    vresult = evaluate_validation_record(valrecord)
                    if vresult:
                        print("Events correctly coded in", SentenceID, '\n')
                        nvalid += 1
                    else:
                        print("Error: Mismatched events in", SentenceID, '\n')
                        if ValidPause == 3:
                            sys.exit()  # debug

                    if ValidPause == 2:
                        continue  # evaluate pause conditions
                    elif ValidPause == 1 or not vresult:
                        inkey = input("Press <Return> to continue; 'q' to quit-->")
                        if 'q' in inkey or 'Q' in inkey:
                            break

                except EOFError:
                    print("Exiting: end of file")
                    PETRreader.close_FIN()
                    print("Records coded correctly:", nvalid)
                    sys.exit()
                except SkipRecord:
                    print("Skipping this record.")
                except HasParseError:
                    print("Exiting: parsing error ")
                    PETRreader.close_FIN()
                    sys.exit()

        PETRreader.close_FIN()
        print("Normal exit from validation\nRecords coded correctly:", nvalid)
        sys.exit()"""
            
        line = fin.readline() 


if __name__ == '__main__':
    filepath="data/text/PETR.UnitTest.records.parsing_parsed_udpipe_2.1.xml"  # eventually this and output file should be read from sys.argv[]
    try:
        fin = open(filepath,'r')
    except:
        print("can't find the file", filepath)
        exit()
    fout = open("Validations_out1.txt", 'w')

    utilities.init_logger('UD-PETR_Validate.log', False)

    do_validation()

    fout.write("\nSummary:\n")
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
    print("\nRecords evaluated:{:4d}".format(valid_counts['Total'][0]))
    print("Correct events:   {:4d}".format(valid_counts['Total'][1]))
    print("Uncoded events:   {:4d}".format(valid_counts['Total'][2]))
    print("Extra events:     {:4d}".format(valid_counts['Total'][3]))

    fin.close()
    fout.close()

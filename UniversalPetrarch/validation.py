# -*- coding: utf-8 -*-

"""
validation.py

Runs validation cases for UniversalPetrarch

TO RUN PROGRAM:

python3 PETR-CD_to_UP.py

PROGRAMMING NOTES: None

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
21-July-17:	Initial version based on parallel functionss PETRARCH-1

=========================================================================================================
"""
from __future__ import print_function
import petrarch_ud, PETRglobals, PETRreader, utilities, codecs, PETRgraph 

global SentenceDate, SentenceID, SentenceCat, SentenceLoc, SentenceValid

# ========================== VALIDATION FUNCTIONS ========================== #


def change_Config_Options(line):
    """Changes selected configuration options."""
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

def evaluate_validation_record(item):
    """
    def evaluate_validation_record(): Read validation record, setting EventID
    and a list of correct coded events, code using read_TreeBank(), then check
    the results. Returns True if the lists of coded and expected events match
    or the event is skipped; false otherwise; also prints the
    mismatches
    Raises EOFError exception if EOF hit.
    Raises SkipRecord if <Skip> found or record is skipped due to In/Exclude
    category lists
    """
    global SentenceDate, SentenceID, SentenceCat, SentenceText, SentenceValid
    global CodedEvents, ValidEvents, ValidError, ValidErrorType
    global ValidInclude, ValidExclude, ValidPause, ValidOnly
    global ParseList
    #TODO: remove this and make read_TreeBank take it as an arg
    global treestr

    def extract_EventCoding_info(codings):
        """Extracts fields from <EventCoding record and appends to ValidEvents."""
    # currently does not raise errors if the information is missing but instead
    # sets the fields to null strings
        """
        Structure of ValidEvents
        noevents: empty list
        otherwise list of triples of [sourcecode, targetcode, eventcode]
        """
        global ValidEvents, ValidErrorType

        for coding in codings:
            event_attrs = coding.attrib
            if 'noevents' in event_attrs:
                ValidEvents = []
                return
            if 'error' in event_attrs:
                ValidEvents = []
                ValidErrorType = event_attrs['error']
                return
            else:
                ValidEvents.append([event_attrs['sourcecode'],
                                    event_attrs['targetcode'],
                                    event_attrs['eventcode']])


    ValidEvents = []  # code triples that should be produced
    # code triples that were produced; set in make_event_strings
    CodedEvents = []
    ValidErrorType = ''
#		print line
    extract_Sentence_info(item.attrib)

    if ValidOnly and not SentenceValid:
        raise SkipRecord
        return True

    if len(ValidInclude) > 0 and SentenceCat not in ValidInclude:
        raise SkipRecord
        return True

    if len(ValidExclude) > 0 and SentenceCat in ValidExclude:
        raise SkipRecord
        return True

    extract_EventCoding_info(item.findall('EventCoding'))

    SentenceText = item.find('Text').text.replace('\n', '')

    if item.find('Skip'):  # handle skipping -- leave fin at end of tree
        raise SkipRecord
        return True

    parsed = item.find('Parse').text
    treestr = utilities._format_parsed_str(parsed)

    try:
        read_TreeBank()
    except IrregularPattern:
#        print('==',ValidError, '==',ValidErrorType)
        if ValidErrorType != '':
            if ValidError != ValidErrorType:
                print(SentenceID, 'did not trigger the error "'+ValidErrorType+'"')
                return False
            else:
                return True

    print('\nSentence:', SentenceID, '[', SentenceCat, ']')
    print(SentenceText)
#   print '**',ParseList

    disc = check_discards()
#    print(disc,ValidErrorType)
    if ((disc[0] == 0 and 'discard' in ValidErrorType) 
        or (disc[0] == 1 and ValidErrorType != 'sentencediscard')
        or (disc[0] == 2 and ValidErrorType != 'storydiscard')):
        if disc[0] == 0:
            print('"' + ValidErrorType + '" was not triggered in ' + SentenceID)
        else:
            print(disc[1] + ' did not trigger  "'+ValidErrorType+'" in ' + SentenceID)
        return False
    if disc[0]>0:
        return True

    try:
        check_commas()
    except IndexError:
        raise_ParseList_error('Initial index error on UpperSeq in get_loccodes()')

    assign_NEcodes()
#	print '**+',ParseList
    if False:
        print('EV-1:')
        show_tree_string(' '.join(ParseList))
    if ShowParseList:
        print('EVR-Parselist::', ParseList)

    check_verbs()  # this can throw HasParseError which is caught in do_validation    

#	print 'EVR-2.1:',ValidEvents
#	print 'EVR-2.2:',CodedEvents

    if len(ValidEvents) > 0:
        print('Expected Events:')
        for event in ValidEvents:
            print(event)

    if len(CodedEvents) > 0:
        print('Coded Events:')
        for event in CodedEvents:
            print(SentenceID + '\t' + event[0] + '\t' + event[1] + '\t' + event[2])

    if (len(ValidEvents) == 0) and (len(CodedEvents) == 0):
        return True  # noevents option

    # compare the coded and expected events
    allokay = True
    ke = 0
    while ke < len(CodedEvents):  # check that all coded events have matches
        kv = 0
        while kv < len(ValidEvents):
            if (len(ValidEvents[kv]) > 3):
                kv += 1
                continue  # already matched
            else:
                if (CodedEvents[ke][0] == ValidEvents[kv][0]) and (CodedEvents[ke][1] == ValidEvents[kv][1]) and (CodedEvents[ke][2] == ValidEvents[kv][2]):
                    CodedEvents[ke].append('+')  # mark these as matched
                    ValidEvents[kv].append('+')
                    break
            kv += 1
        if (len(CodedEvents[ke]) == 3):
            print("No match for the coded event:", CodedEvents[ke])
            allokay = False
        ke += 1

    for vevent in ValidEvents:  # check that all expected events were matched
        if (len(vevent) == 3):
            print("No match for the expected event:", vevent)
            allokay = False
    return allokay


def open_validation_file(xml_root):
    """
    1. Opens validation file TextFilename as FIN
    2. After "</Environment>" found, closes FIN, opens ErrorFile, sets various
    validation options, then reads the dictionaries (exits if these are not set)
    3. Can raise MissingXML
    4. Can exit on EOFError, MissingAttr
    """
    global ValidInclude, ValidExclude, ValidPause, ValidOnly
    logger = logging.getLogger('petr_log')

    environment = xml_root.find('Environment')
    if environment is None:
        print('Missing <Environment> block in validation file')
        print('Exiting program.')
        sys.exit()

    ValidInclude, ValidExclude, ValidPause, ValidOnly = _check_envr(environment)

    check1 = [len(PETRglobals.VerbFileName) == 0,
              len(PETRglobals.ActorFileList) == 0,
              len(PETRglobals.AgentFileName) == 0]
    if any(check1):
        print("Missing <Verbfile>, <AgentFile> or <ActorFile> in validation file <Environment> block")
        print("Exiting: This information is required for running a validation file")
        sys.exit()

    logger.info('Validation file: ' + PETRglobals.TextFileList[0] +
                '\nVerbs file: ' + PETRglobals.VerbFileName +
                '\nActors file: ' + PETRglobals.ActorFileList[0] + 
                '\nAgents file: ' + PETRglobals.ActorFileList[0] + '\n')
    if len(PETRglobals.DiscardFileName) > 0:
        logger.info('Discard file: ' + PETRglobals.DiscardFileName + '\n')
    if len(ValidInclude):
        logger.info('Include list: ' + ', '.join(ValidInclude) + '\n')
    if len(ValidExclude):
        logger.info('Exclude list: ' + ', '.join(ValidExclude) + '\n')

    print('Verb dictionary:', PETRglobals.VerbFileName)
    verb_path = utilities._get_data('data/dictionaries',
                                    PETRglobals.VerbFileName)
    PETRreader.read_verb_dictionary(verb_path)

    print('Actor dictionaries:', PETRglobals.ActorFileList[0])
    actor_path = utilities._get_data('data/dictionaries',
                                     PETRglobals.ActorFileList[0])
    PETRreader.read_actor_dictionary(actor_path)

    print('Agent dictionary:', PETRglobals.AgentFileName)
    agent_path = utilities._get_data('data/dictionaries',
                                     PETRglobals.AgentFileName)
    PETRreader.read_agent_dictionary(agent_path)

    if len(PETRglobals.DiscardFileName) > 0:
        print('Discard list:', PETRglobals.DiscardFileName)
        discard_path = utilities._get_data('data/dictionaries',
                                         PETRglobals.DiscardFileName)
        PETRreader.read_discard_list(discard_path)



# ================== TEXTFILE INPUT ================== #


def do_validation(filepath="data/text/PETR.UnitTest.records.parsing_parsed_udpipe_2.1.xml"):
    """ Unit tests using a validation file. """
    global allrecords, allcorrect, alluncoded, allextra

    def get_line_attribute(target):
        """ quick and dirty function for extracting well-formed attributes"""
        part = line.partition(target)
        return part[2][2:part[2].find('"',3)]

    def get_environment():
        ValidExclude = None
        ValidInclude = None
        ValidOnly = True
        ValidPause = 0
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
        
    def parse_parser(parse):
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

    def process_event_output(str):
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

    def parse_verb(strs,phrase_dict,text,parsed):
        str_arr = str(strs).strip("{").split(",")
        #print("Verb/Noun")
        fout.write("Verbs found:\n") 
        for x in str_arr:
            str_num = x.find(":")		
            try:        
                sentence = PETRgraph.Sentence(parsed, text, 0000)
                np = sentence.get_verbPhrase(int(x[:str_num].strip()))
                str_add = x[:str_num].strip() + " : text = " + str(np.text) +", head="+ str(np.head) +", meaning="+ str(np.meaning)+", code="+ str(np.code)+" ,passive="+str(np.passive) + "\n"
                fout.write(str_add)
            except Exception as e:
                print(e)
                fout.write(" --> Exception: " + e + '\n')
        return

    def parse_noun(strs,phrase_dict,text,parsed):
        str_arr = str(strs).strip("{").split(",")
        fout.write("Nouns found:\n") 
        for x in str_arr:
            str_num = x.find(":")		
            try:        
                sentence = PETRgraph.Sentence(parsed, text, 0000)
                np = sentence.get_nounPharse(int(x[:str_num].strip()))
                np.get_meaning()
                str_add =  x[:str_num].strip() + " : head = " + str(np.head) +", text="+ str(np.text) +", meaning="+str(np.meaning)+", matched_txt="+str(np.matched_txt)+ "\n"
                fout.write(str_add)                
            except Exception as e:
                print(e)
                fout.write(" --> Exception: " + str(e) + '\n')
        return

    def parse_triplets(triplets, phrase_dict):
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

    def validate_record(idstrg, text, parse):
        global allrecords, allcorrect, alluncoded, allextra
        print("Entering", idstrg)
        allrecords += 1
        fout.write("Record ID: " + idstrg + '\n')
        fout.write("Text:\n" + text + '\n')
        fout.write("Parse:\n " + parse)
        fout.write("Expected events:\n")
        for edict in valrecord['events']:
            if "noevents" in edict:
                fout.write("noevents\n")                 
            else:
                fout.write(edict['eventcode']  + ' ' + edict['sourcecode']  + ' ' + edict['targetcode']  + '\n') 
        
        phrase_dict = parse_parser(parse)
        parsed = utilities._format_ud_parsed_str(parse)
        dict = {idstrg: {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
            u'meta': {u'date': u'19950101'}}}
        return_dict = "" 
        try: 
            return_dict = petrarch_ud.do_coding(dict)
        except Exception as e: 
            fout.write("Petrarch Runtime Error " + str(e) + '\n')
#        fout.write("Mk0: " + str(return_dict[idstrg]['sents']['0']['events']))
        try:
            if 'events' in return_dict[idstrg]['sents']['0']:
                print(return_dict[idstrg]['sents']['0']['events'])
#                fout.write("Mk1: " + str(return_dict[idstrg]['sents']['0']['events']))
                event_out = process_event_output(str(return_dict[idstrg]['sents']['0']['events']))
                fout.write("Coded events:\n")
                nfound = 0
                ncoded = 0
                for key, evt in return_dict[idstrg]['sents']['0']['events'].items():
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
                fout.write("Event source:\n")
                fout.write(str(return_dict[idstrg]['sents']['0']['events']) + '\n')
            else:
                fout.write("No events returned\n")
        except:
            fout.write(idstrg + " Failed\n")  # not clear why we'd hit this...
            print(idstrg + " Failed")
        fout.write("Correct: " + str(nfound) + "   Not coded: " + str(len(valrecord['events']) - nfound) + "   Extra events: " + str(ncoded - nfound)  + '\n') 
        allcorrect += nfound
        alluncoded += len(valrecord['events']) - nfound
        allextra += ncoded - nfound
        if 'verbs' in return_dict[idstrg]['sents']['0']:
            parse_verb(return_dict[idstrg]['sents']['0']['verbs'],phrase_dict,text,parsed)
        if 'nouns' in return_dict[idstrg]['sents']['0']:
            parse_noun(return_dict[idstrg]['sents']['0']['nouns'],phrase_dict,text,parsed)
        if 'triplets' in return_dict[idstrg]['sents']['0']:
            parse_triplets(return_dict[idstrg]['sents']['0']['triplets'],phrase_dict)
        fout.write('\n')

    fin = open(filepath,'r')
    fout = open("Validations_out1.txt", 'w')
    # trap an except
    line = fin.readline() 
    while len(line) > 0 and not line.startswith("<Environment>"):  # loop through the file
        line = fin.readline() 
#  trap missing block here

    get_environment()
    config = utilities._get_data('data/config/', 'PETR_config.ini')
    """print("reading config")
    PETRreader.parse_Config(config) # don't want this if the dicts are set in the file """
    print("reading dicts")
    petrarch_ud.read_dictionaries()


    nvalid = 0
    allrecords, allcorrect, alluncoded, allextra = 0, 0, 0, 0
    ka = 0
    kb = 0
    line = fin.readline() 
    while len(line) > 0:  # loop through the file
        ka += 1
#        if ka > 36: break
#        print(line[:-1])

        if line.startswith("<Sentence "):
            valrecord = {}
            recordType = 'Sentence'
            valrecord['sentence'] = line[line.find(" ") + 1:line.find(">")]
            valrecord['date'] = get_line_attribute('date')
            #SentenceOrdDate = PETRreader.dstr_to_ordate(SentenceDate)
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
                        print('Mk-2')
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

            if valrecord['category'] != "DEMO":
                break
            print("\nRecord:",valrecord['id'])
            """for k, v in valrecord.items():
                print(k)
                print(v)"""
            validate_record(valrecord['id'], valrecord['text'], valrecord['parse'])
            kb += 1
#            if kb > 60: break
            
            """if recordType == 'Config':
                change_Config_Options(valrecord.attrib)
            if recordType == 'Stop':
                print("Exiting: <Stop> record ")
                break
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

    fout.write("\nSummary:\n")
    fout.write("Record evaluated:" + str(allrecords) + "\n")
    fout.write("Correct events:" + str(allcorrect) + "\n")
    fout.write("Uncoded events:" + str(alluncoded) + "\n")
    fout.write("Extra events:" + str(allextra) + "\n")
    fin.close()
    fout.close()
    exit()


if __name__ == '__main__':
    do_validation()

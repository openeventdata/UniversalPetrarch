# -*- coding: utf-8 -*-

import petrarch_ud, PETRglobals, PETRreader, utilities
import xml.etree.ElementTree as ET
import networkx as nx
import PETRgraph
import sys


def run():
	events = read_xml_input(filepaths)
	updated_events = extract_phrases(events)
	write_output(updated_events)

def _format_ud_parsed_str(parsed_str):
    
    parsed = parsed_str.split('\n')

    cleanparsed=[]
    for p in parsed:
    	if not p:
    		continue
    	if len(p.split("\t"))==8:
    		cleanparsed.append(p)
    	else:
    		print("number of field is not 8:"+p)
    		# raw_input("Press Enter to continue...")


    treestr = '\n'.join(cleanparsed)
    return treestr


def extract_actor_code(event_dict):
	NStory = 0
	NSent = 0
	result = []
	for key, val in sorted(event_dict.items()):
		NStory += 1
		print('\n\nProcessing story {}'.format(key))
		StoryDate = event_dict[key]['meta']['date']

		for sent in val['sents']:
			NSent += 1
			print('Processing sentence ' + sent)
			if 'parsed' in event_dict[key]['sents'][sent]:
				SentenceText = event_dict[key]['sents'][sent]['content']
				SentenceParsed = event_dict[key]['sents'][sent]['parsed']
				SentenceDate = event_dict[key]['sents'][sent]['date'] if 'date' in event_dict[key]['sents'][sent] else StoryDate
				Date = SentenceDate
				sentence = PETRgraph.Sentence(SentenceParsed,SentenceText,Date)

				sentence.get_events()
				tempnouns, compound_nouns = sentence.get_all_nounPhrases()
				# sentence.get_verb_code()
				if len(tempnouns) > 0 and tempnouns[0].meaning[0]  != '---' : 
					print('--->sentence.text() : ', tempnouns[0].text )
					print('--->sentence.meaning() : ', tempnouns[0].meaning )
					print('--->sentence.matched_text() : ', tempnouns[0].matched_txt )
					print('--->sentence.sentence() : ', SentenceText )

					result.append([SentenceText, tempnouns[0].matched_txt[0].strip(), tempnouns[0].meaning[0].strip()])

				else : 
					result.append([SentenceText, '---' , '---'])


	return result


def write_output(results,outputfile):
	print('output file : ' , outputfile)
	with open(outputfile , 'w') as outputf : 
		for  i in results : 
			print('i : ' , i )
			outputf.write('{}\n'.format(','.join(i)))


utilities.init_logger('PETRARCH.log',True)
config = utilities._get_data('data/config/', 'PETR_AR_config.ini')
print("reading config")
sys.stdout.write('Mk1\n')
PETRreader.parse_Config(config)
print("reading dicts")
petrarch_ud.read_dictionaries()
inputFile=sys.argv[1]
#inputFile=sys.argv[1].replace(".xml","")+"_parsed.xml"
outputFile = sys.argv[2]
# events = read_xml_input([inputFile], True)
events = PETRreader.read_xml_input([inputFile] , True)
'''
print(len(events))
for key in events.keys():
	print(len(events[key]['sents']))
	for subkey,v in events[key]['sents'].items():
		print(subkey)
		print(v)
'''
updated_events = extract_actor_code(events)
write_output(updated_events,outputFile)

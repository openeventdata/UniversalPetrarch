# -*- coding: utf-8 -*-

import petrarch_ud, PETRglobals, PETRreader, utilities
import xml.etree.ElementTree as ET
import networkx as nx
import PETRgraph
import sys


def run():
	events = read_xml_input(filepaths)
	updated_events = extract_phrases(events)
	write_phrases(updated_events)

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
    		raw_input("Press Enter to continue...")


    treestr = '\n'.join(cleanparsed)
    return treestr

def read_xml_input(filepaths, parsed=False):
	
	eventdict = {}

	for path in filepaths:
		tree = ET.iterparse(path)

		for event, elem in tree:
			if event == "end" and elem.tag == "Sentence":
				story = elem

				# Check to make sure all the proper XML attributes are included
				attribute_check = [key in story.attrib for key in ['date', 'id', 'sentence', 'source']]
				if not attribute_check:
					print('Need to properly format your XML...')
					break

				if parsed:
					parsed_content = story.find('Parse').text
					parsed_content = _format_ud_parsed_str(parsed_content)
					#print(parsed_content) # add graph
				else:
					parsed_content = ''

				if story.attrib['sentence'] == 'True':
					entry_id =  story.attrib['id'][0:story.attrib['id'].rindex('_')]
					sent_id = story.attrib['id'][story.attrib['id'].rindex('_')+1:]

					text = story.find('Text').text
					text = text.replace('\n', ' ').replace('  ', ' ')
					sent_dict = {'content': text, 'parsed': parsed_content}
					#print(text)
					#print(parsed_content)

					meta_content = {'date': story.attrib['date'],
					'source': story.attrib['source']}
					content_dict = {'sents': {sent_id: sent_dict},
					'meta': meta_content}
				else:
					entry_id = story.attrib['id']

					text = story.find('Text').text
					text = text.replace('\n', ' ').replace('  ', ' ')
					#split_sents = _sentence_segmenter(text)
			
					# TODO Make the number of sents a setting
					sent_dict = {}
					#for i, sent in enumerate(split_sents[:7]):
					#	sent_dict[i] = {'content': sent, 'parsed':
					#	parsed_content}

					#	meta_content = {'date': story.attrib['date']}
					#	content_dict = {'sents': sent_dict, 'meta': meta_content}

				if entry_id not in eventdict:
					eventdict[entry_id] = content_dict
				else:
					eventdict[entry_id]['sents'][sent_id] = sent_dict

				#raw_input("Press Enter to continue...")


				elem.clear()

	return eventdict



def extract_actor_code(event_dict):
	NStory = 0
	NSent = 0

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
				#print(sentence.udgraph.node[1]['pos'])
				#print(sentence.udgraph.edges())
				#print(nx.dfs_successors(sentence.udgraph,6))

				sentence.get_phrases()
				#print('verbs:')
				#for v in sentence.metadata['verbs']: 
					#print(v.text)
					#if(len(v.vpIDs)>1):
						#raw_input("Press Enter to continue...")
				print('nouns:')
				for n in sentence.metadata['nouns']: 
					codes,roots,matched_txt = n.get_meaning();
					print("noun:"+n.text+"\tnumber of codes: "+str(len(codes)))
					for i in range(0,len(codes)):
						#print("code:"+str(codes[i])+"\tdictionary entry:"+str(roots[i])+"\tmatched text:"+matched_txt[i])
						print("code:"+str(codes[i])+"\tmatched text:"+matched_txt[i])
				#print('triplets:')
				#for triple in sentence.metadata['triplets']: print("s: "+triple[0]+"\tt: "+triple[1].text+"\tv: "+triple[2]+"\to: "+(" ").join(triple[3].text)+"\n")
				
				print('verbs:')
				sentence.get_verb_code()
				for tkey, triple in sentence.triplets.items():
					print("verb:"+triple['triple'][2].text)
					print("code:"+(triple['verbcode'] if triple['verbcode']!= None else '-'))
					print("matched_txt:"+triple['matched_txt'])

		
				event_dict[key]['sents'][sent]['phrase_dict'] = sentence.metadata

			#raw_input("Press Enter to continue...")

	return event_dict


def write_phrases(event_dict,outputfile):
	root = ET.Element("Sentences")

	for key, val in sorted(event_dict.items()):
		
		StoryDate = event_dict[key]['meta']['date']

		for sent in val['sents']:
			#source = key[0:key.index('_')]
			sentence = ET.SubElement(root, "Sentence", {"date":StoryDate,"id":key+"_"+sent,"source":key,"sentence":"True"})
			ET.SubElement(sentence,"Text").text = event_dict[key]['sents'][sent]['content']
			ET.SubElement(sentence,"Parse").text = event_dict[key]['sents'][sent]['parsed']
			verbs=""
			for v in event_dict[key]['sents'][sent]['phrase_dict']['verbs']:
				verbs= verbs+v.text+"\n"
			ET.SubElement(sentence,"Verbs").text = verbs

			nouns=""
			for n in event_dict[key]['sents'][sent]['phrase_dict']['nouns']:
				nouns=nouns+n.text+"\n"
			ET.SubElement(sentence,"Nouns").text = nouns


			tuples =""
			for triple in event_dict[key]['sents'][sent]['phrase_dict']['triplets']:
				source = triple[0] if isinstance(triple[0],basestring) else triple[0].text
				target = triple[1] if isinstance(triple[1],basestring) else triple[1].text
				others = ""
				for other in triple[3]:
					others = others+other.text+","
				tuples = tuples+"source: "+source+"\ttarget: "+target+"\tverb: "+triple[2].text+"\tother_noun: "+others+"\n"
			ET.SubElement(sentence,"Triplets").text = tuples


	tree = ET.ElementTree(root)
	tree.write(outputfile,'UTF-8')

utilities.init_logger('PETRARCH.log',True)
config = utilities._get_data('data/config/', 'PETR_config.ini')
print("reading config")
sys.stdout.write('Mk1\n')
PETRreader.parse_Config(config)
print("reading dicts")
petrarch_ud.read_dictionaries()
inputFile=sys.argv[1]
#inputFile=sys.argv[1].replace(".xml","")+"_parsed.xml"
outputFile = inputFile.replace("_parsed.xml","")+"_phrase.xml"
events = read_xml_input([inputFile], True)
'''
print(len(events))
for key in events.keys():
	print(len(events[key]['sents']))
	for subkey,v in events[key]['sents'].items():
		print(subkey)
		print(v)
'''
updated_events = extract_actor_code(events)
write_phrases(updated_events,outputFile)

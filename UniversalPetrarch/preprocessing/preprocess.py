# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import sys



def read_doc_input(inputxml,inputparsed,outputfile):
	'''
		input:
			input document xml file and Stanford CoreNLP output
		output:

			1. a new xml file of splitted sentences 
			2. a txt file with one sentence in each line for word segmentation in the later step
	'''

	#read input xml file, store documents in a dictionary.
	#the key of dictionary is the text part of document, the value is the infomartion about the document, e.g date,id
	docdict = {}
	doctexts = []
	output = []

	tree = ET.iterparse(inputxml)
	
	for event, elem in tree:
		if event == "end" and elem.tag == "Sentence":
			story = elem

			# Check to make sure all the proper XML attributes are included
			attribute_check = [key in story.attrib for key in ['date', 'id','sentence', 'source']]
			if not attribute_check:
				print('Need to properly format your XML...')
				break

			entry_id = story.attrib['id'];
			date = story.attrib['date']
			sentence = story.attrib['sentence']
			source = story.attrib['source']

			text = story.find('Text').text
			text = text.replace('\n', ' ').strip()

			if len(text)==0:
				text = "no sentence "+entry_id

			if entry_id in docdict:
				print('id must be unique, this article is in document dictionary :'+entry_id)
				break

			docdict[text] = {'id':entry_id,'date':date,'sentence':sentence,'source':source,'text':text}


			doctexts.append(text)

			elem.clear()

	#read Stanford CoreNLP parsed file		
	parsed = open(inputparsed)
	parsedfile = parsed.readlines()
	parsedlines = []
	#for line in parsedfile:
		#if "Sentence #" in line or "[" in line:
		#	continue
		#else:
			#print(line)
			#parsedlines.append(line.replace("\n"," ").strip())
	i = 0
	'''
	while i <len(parsedfile):
		line = parsedfile[i]
		if "Sentence #" in line:
			i = i+1
			continue
		elif not line.startswith('['):
			temp = line
			i = i+1
			line = parsedfile[i]
			while(not line.startswith('[')):
				temp = temp+line
				i = i+1
				line = parsedfile[i]
			#print(temp)
			parsedlines.append(temp.replace('\n', ' ').strip())
		i = i+1
	'''
	while i<len(parsedfile):
		line = parsedfile[i]
		if "Sentence #" in line:
			i = i+2
			continue
		elif line.startswith('['):
			temp = line.split("] ")
			tokens = []
			for token in temp:
				text = token.split(' ')[0]
				word = text[text.find('=')+1:]
				tokens.append(word)
			parsedlines.append((' ').join(tokens).replace('\n', ' ').strip())
			#raw_input((' ').join(tokens))
		i = i+1




	#match CoreNLP parsed file with input xml file
	sents_dict = {}
	sents = []
	sentidx = 1
	#print(len(doctexts))
	#print(len(parsedlines))
	#raw_input("Press Enter to continue...")

	processed = 0;
	for line in parsedlines:
		doc = doctexts[0]
		#print(doc)
		#print(line+"#")
		#print(isinstance(doc,str))
		#print(isinstance(line,str))
		#print(doc.encode('UTF-8').find(line))
		#break
		#'''
		line = line.replace("&gt;",">").replace("&lt;","<").replace("&amp;","&").replace("-LRB-","(").replace("-RRB-", ")").replace("-LSB-", "[").replace("-RSB-", "]").replace("-LCB-", "{").replace("-RCB-", "}")
		templine = line.replace(" ","")
		tempdoc = doc.replace(" ","")
		if tempdoc.encode('UTF-8').find(templine) ==-1:
			#print(processed)
			#if processed>=33223:
			#	print(line)
			#	print(doc)
			#	raw_input("Press Enter to continue...")
			doctexts.remove(doc)
			sentidx = 1
			doc = doctexts[0]
			tempdoc = doc.replace(" ","")
		
		if tempdoc.encode('UTF-8').find(templine) != -1:
			#print(docdict[doc]['id']+"#"+line)
			key = docdict[doc]['id']+"#"+line
			sents.append(key)
			output.append(line+"\n")
			sents_dict[key] = {}
			sents_dict[key]['sentence_id']=str(sentidx)
			sents_dict[key].update(docdict[doc])
			#print(sents_dict[key]['sentence_id']+":"+key)
			sentidx = sentidx + 1
		
		processed = processed+1
		#'''

	#print(len(parsedlines))
	#print(len(sents))
	#for sent in sents:
		#print(sent)
		#print(sents_dict.get(sent).get('sentence_id'))
		#print(sents_dict[sent]['sentence_id']+":"+key)

	ofile = open(outputfile,'w')
	for line in output:
		ofile.write(line)
	ofile.close()

def create_sentence_xml(sentences,sents_dict,outputxml):
	root = ET.Element("Sentences")

	for s in sentences:
		#print(isinstance(s,unicode))
		sentinfo = sents_dict[s]
		#print(s+" "+sentinfo['id']+"-"+sentinfo['sentence_id'])
		sentence = ET.SubElement(root,"Sentence", {"date":sentinfo['date'],"source":sentinfo['source'],"id":sentinfo['id']+"-"+sentinfo['sentence_id'],"sentence":sentinfo['sentence']})
		ET.SubElement(sentence,"Text").text = s[s.index('#')+1:].decode('UTF-8')

	tree = ET.ElementTree(root)
	tree.write(outputxml,'UTF-8')



inputxml=sys.argv[1]
inputparsed = inputxml+".raw.txt.out"
outputfile = inputxml+".txt"
read_doc_input(inputxml,inputparsed,outputfile)

# -*- coding: utf-8 -*-

import io
import xml.etree.ElementTree as ET
import sys



def read_sentence_input(inputxml,outputfile):
	'''
		input:
			input sentence xml file
		output:

			a txt file with one sentence in each line for word segmentation in the later step
	'''

	#read input xml file, store documents in a dictionary.
	#the key of dictionary is the text part of document, the value is the infomartion about the document, e.g date,id
	docdict = {}
	doctexts = []

	xml_file = io.open(inputxml,'rb')#, encoding='utf-8')
	tree = ET.iterparse(xml_file)
	#tree = ET.fromstring(xml_file)
	
	for event, elem in tree:
		if event == "end" and elem.tag == "Sentence":
	#for elem in tree:
		#if elem.tag == "Sentence":
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

			if entry_id in docdict:
				print('id must be unique, this article is in document dictionary :'+entry_id)
				break

			docdict[text] = {'id':entry_id,'date':date,'sentence':sentence,'source':source,'text':text}

			if len(text)==0:
				text = "no sentence "+entry_id
			doctexts.append(text)

			elem.clear()

	ofile = io.open(outputfile,'w',encoding='utf-8')
	for line in doctexts:
		line = line+u'\n'
		#input(type(line))
		ofile.write(line)
	ofile.close()


def main():
	inputxml=sys.argv[1]
	outputfile = inputxml+".raw.txt"
	read_sentence_input(inputxml,outputfile)


if __name__ == "__main__":
    main()
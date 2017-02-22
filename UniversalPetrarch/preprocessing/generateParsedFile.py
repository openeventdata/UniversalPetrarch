# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import sys

def update_xml_input(inputfile,parsedfile,outputfile):
	
	pfile = open(parsedfile)
	plines = pfile.readlines()
	pfile.close()

	j = 0;

	tree = ET.parse(inputfile)
	root = tree.getroot()

	for elem in root:
		if elem.tag == "Sentence":
			story = elem
			parsed =[]

			# Check to make sure all the proper XML attributes are included
			attribute_check = [key in story.attrib for key in ['date', 'id', 'sentence', 'source']]
			if not attribute_check:
				print('Need to properly format your XML...')
				break

			while not plines[j].isspace():
				parsed.append(plines[j].decode("utf-8"))
				j = j + 1
			j = j+1
			
			parse = ET.SubElement(elem,"Parse")
			parse.text = ''.join(parsed)

	tree.write(outputFile,encoding='utf-8',xml_declaration=True)

inputFile=sys.argv[1]
parsedFile = inputFile+".conll.predpos.pred"
outputFile = inputFile.replace(".xml","")+"_parsed.xml"
update_xml_input(inputFile,parsedFile,outputFile)

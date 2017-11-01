# -*- coding: utf-8 -*-

import io
import xml.etree.ElementTree as ET
import sys

def update_xml_input(inputfile,parsedfile,outputfile):
	
	pfile = io.open(parsedfile,'r',encoding='utf-8')
	plines = pfile.readlines()
	pfile.close()

	j = 0;

	xml_file = io.open(inputfile,'rb')
	#xml_file = io.open(inputfile,'r', encoding='utf-8')

	tree = ET.parse(xml_file)
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

			while j < len(plines) and not plines[j].isspace():
				parsed.append(plines[j])
				j = j + 1
			j = j+1
			
			for oldparse in elem.findall('Parse'):
				elem.remove(oldparse)
			parse = ET.SubElement(elem,"Parse")
			parse.text = ''.join(parsed)

	tree.write(outputFile,encoding='utf-8',xml_declaration=True)

inputFile=sys.argv[1]
parsedFile = inputFile+".conll.predpos.pred"
outputFile = inputFile.replace(".xml","")+"_parsed.xml"
update_xml_input(inputFile,parsedFile,outputFile)

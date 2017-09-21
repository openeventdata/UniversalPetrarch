# -*- coding: utf-8 -*-
import sys
import xml.etree.ElementTree as ET
import codecs


class ProtestDoc:

	def __init__(self):

		self.text = ""
		self.sentences = {}
		self.T={}
		self.R={}


def parse_annotation_file(filename):
	rawtext = codecs.open(filename+".txt","r",encoding='utf8')
	anntext = codecs.open(filename+".ann","r",encoding='utf8')

	doc = ProtestDoc()
	eventsids = []

	lineid = 1
	start = 0
	text= ""
	for line in rawtext:

		text = text+line
		if len(line.replace('\r\n',""))==0:
			start = start +1
			lineid += 1
			continue
		doc.sentences[lineid]={}
		doc.sentences[lineid]['text']=line
		doc.sentences[lineid]['start']=start
		doc.sentences[lineid]['end']=start+len(line)
		start = start+len(line)+1
		lineid += 1

	doc.text = text

	for line in anntext:
		if line.startswith("T"):
			temp = line.split("\t")
			doc.T[temp[0]]={}
			if len(temp)!=3:
				raw_input(filename)
				raw_input(line)

			temp2 = temp[1].split(" ")
			doc.T[temp[0]]['type']=temp2[0]
			doc.T[temp[0]]['start'] = int(temp2[1])
			doc.T[temp[0]]['end'] = int(temp2[-1])

			doc.T[temp[0]]['text'] = temp[-1].replace("\n","")
		elif line.startswith("R"):
			temp = line.replace("\t"," ").split(" ")
			doc.R[temp[0]]={}
			doc.R[temp[0]]['type']=temp[1]
			doc.R[temp[0]]['Arg1']=temp[2].split(":")[1]
			doc.R[temp[0]]['Arg2']=temp[3].split(":")[1]

	print(doc.text)
	for key,value in doc.sentences.items():
		print(key)
		print(value)

	
	for key,Tvalue in doc.T.items():
		if Tvalue['type'] in ['material_conflict','verbal_conflict']:
			for sid,sentence in doc.sentences.items():
				if Tvalue['start']>=sentence['start'] and Tvalue['end']<=sentence['end']:
					print(key+"\t"+Tvalue['text']+"\t"+str(sid))
					eventsids.append(sid)

	return doc,list(set(eventsids))

def generate_event_text(fileDictionary):
	for filename, value in sorted(fileDictionary.items()):
		processed =[]
		doc = value['doc']
		for key, Rvalue in sorted(doc.R.items()):
			Rtype = Rvalue['type']
			event = None
			source = None
			target = None
			if Rtype == 'srcAct':
				source = doc.T[Rvalue['Arg1']]
				event =  doc.T[Rvalue['Arg2']]
			elif Rtype == 'actTar':
				event = doc.T[Rvalue['Arg1']]
				target =  doc.T[Rvalue['Arg2']]
			
			for sid,sentence in doc.sentences.items():
				if event['start']>=sentence['start'] and event['end']<=sentence['end']:
					if 'event' in doc.sentences[sid]:
						doc.sentences[sid]['event'].append((event['text'],source['text'] if source != None else "",target['text'] if target != None else ""))
					else:
						doc.sentences[sid]['event']=[]
						doc.sentences[sid]['event'].append((event['text'],source['text'] if source != None else "",target['text'] if target != None else ""))




def write_sentence_xml(fileDictionary,outputfile):
	root = ET.Element("Sentences")
	outputlines=[]

	for filename, value in sorted(fileDictionary.items()):
		for sid in sorted(value['sids']):
			date = filename.split("_")[-1].split(".")[0]
			source = filename.split("_")[0]
			name = filename.split("/")[-1]
			sentence = ET.SubElement(root, "Sentence", {"date":date,"id":name+"_"+str(sid),"source":source,"sentence":"true"})
			if 'event' in fileDictionary[filename]['doc'].sentences[sid]:
				for event in fileDictionary[filename]['doc'].sentences[sid]['event']:
					ET.SubElement(sentence,"EventText",{"eventtext":event[0],"sourcetext":event[1],"targettext":event[2]})
			ET.SubElement(sentence,"Text").text = fileDictionary[filename]['doc'].sentences[sid]['text']
			outputlines.append(fileDictionary[filename]['doc'].sentences[sid]['text'].replace("."," .").replace(","," ,"))


	tree = ET.ElementTree(root)
	tree.write(outputfile,'UTF-8')

	outfile = codecs.open(outputfile+".txt",'w',encoding='utf8')
	for line in outputlines:
		outfile.write(line)


fileDictionary = {}
filelist = open(sys.argv[1], 'r')

for filename in filelist:
	doc,eventsids = parse_annotation_file("protest_JJ/protest_round_3/"+filename.replace('\n',''))
	print(filename)
	fileDictionary[filename]={}
	fileDictionary[filename]['doc']=doc
	fileDictionary[filename]['sids']=eventsids

generate_event_text(fileDictionary)
write_sentence_xml(fileDictionary,"spanish_protest_event.xml")


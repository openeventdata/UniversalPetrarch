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
		self.location = []

class T:
	def __init__(self,text,start,end,ttype):

		self.text = text
		self.start = start
		self.end = end
		self.type = ttype
		self.sentence_id = None

class R:
	def __init__(self,rtype,arg1,arg2):
		self.type = rtype
		self.arg1 = arg1
		self.arg2 = arg2
		self.sentence_id = None

class Sentence:
	def __init__(self,text,start,end):
		self.text = text
		self.start = start
		self.end = end
		self.location = []
		self.event = []


def parse_annotation_file(filename):
	'''
	read annotation file and return ids of sentences which contain events
	'''
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

		stext=line
		sstart=start
		send=start+len(line)

		doc.sentences[lineid]=Sentence(stext,sstart,send)

		start = start+len(line)+1
		lineid += 1

	doc.text = text

	for line in anntext:
		if line.startswith("T"):
			temp = line.split("\t")
			if len(temp)!=3:
				raw_input(filename)
				raw_input(line)

			temp2 = temp[1].split(" ")
			
			ttype=temp2[0]
			tstart = int(temp2[1])
			tend = int(temp2[-1])
			ttext = temp[-1].replace("\n","")
			doc.T[temp[0]] = T(ttext,tstart,tend,ttype)

		elif line.startswith("R"):
			temp = line.replace("\t"," ").split(" ")
			rtype=temp[1]
			rArg1=temp[2].split(":")[1]
			rArg2=temp[3].split(":")[1]
			doc.R[temp[0]]= R(rtype,rArg1,rArg2)


	#print(doc.text)
	#for key,value in doc.sentences.items():
		#print(key)
		#print(value)

	# find sentences that contain event
	for key,Tvalue in doc.T.items():
		if Tvalue.type in ['material_conflict','verbal_conflict']:
			for sid,sentence in doc.sentences.items():
				if Tvalue.start>=sentence.start and Tvalue.end<=sentence.end:
					print(key+"\t"+Tvalue.text+"\t"+str(sid))
					#raw_input()
					Tvalue.sentence_id = sid
					eventsids.append(sid)

	# find sentences that contain locations
	for key,Tvalue in doc.T.items():
		if Tvalue.type in ['location']:
			for sid,sentence in doc.sentences.items():
				if Tvalue.start>=sentence.start and Tvalue.end<=sentence.end:
					print(key+"\t"+Tvalue.text+"\t"+str(sid))
					if sid in eventsids:
						doc.sentences[sid].location.append(key)
						print("in event sentence")
					else:
						doc.location.append(key)
						print("not in event sentence")
					#raw_input()

	return doc,list(set(eventsids))

def generate_event_text(fileDictionary):
	for filename, value in sorted(fileDictionary.items()):
		processed =[]
		doc = value['doc']
		for key, Rvalue in sorted(doc.R.items()):
			Rtype = Rvalue.type
			event = None
			source = None
			target = None
			if Rtype == 'srcAct':
				source = doc.T[Rvalue.arg1]
				event =  doc.T[Rvalue.arg2]
			elif Rtype == 'actTar':
				event = doc.T[Rvalue.arg1]
				target =  doc.T[Rvalue.arg2]
			
			for sid,sentence in doc.sentences.items():
				if event.start >=sentence.start and event.end<=sentence.end:
					doc.sentences[sid].event.append((event.text,source.text if source != None else "",target.text if target != None else ""))
		
		#find event that doesn't have source or target
		tempevent = {}
		for key,Tvalue in doc.T.items():
			if Tvalue.type in ['material_conflict','verbal_conflict']:
				if Tvalue.sentence_id != None and len(doc.sentences[Tvalue.sentence_id].event) == 0:
					if Tvalue.sentence_id not in tempevent:
						tempevent[Tvalue.sentence_id]=[]
					tempevent[Tvalue.sentence_id].append(Tvalue.text)

		for sid, events in tempevent.items():
			for event in events:
				doc.sentences[sid].event.append((event,"",""))




def write_sentence_xml(fileDictionary,outputfile):
	root = ET.Element("Sentences")
	outputlines=[]

	for filename, value in sorted(fileDictionary.items()):
		for sid in sorted(value['sids']):
			date = filename.split("_")[-1].split(".")[0]
			source = filename.split("_")[0]
			name = filename.split("/")[-1]
			sentence = ET.SubElement(root, "Sentence", {"date":date,"id":name+"_"+str(sid),"source":source,"sentence":"true"})
			for event in fileDictionary[filename]['doc'].sentences[sid].event:
				ET.SubElement(sentence,"EventText",{"eventtext":event[0],"sourcetext":event[1],"targettext":event[2]})
			for location in fileDictionary[filename]['doc'].sentences[sid].location:
				ET.SubElement(sentence,"Location",{"loc_in_sentence":"true"}).text = fileDictionary[filename]['doc'].T[location].text
				#ET.SubElement(sentence,"Location").text = fileDictionary[filename]['doc'].T[location].text
			for location in fileDictionary[filename]['doc'].location:
				ET.SubElement(sentence,"Location",{"loc_in_sentence":"false"}).text = fileDictionary[filename]['doc'].T[location].text
				#ET.SubElement(sentence,"Location").text = fileDictionary[filename]['doc'].T[location].text
			ET.SubElement(sentence,"Text").text = fileDictionary[filename]['doc'].sentences[sid].text
			outputlines.append(fileDictionary[filename]['doc'].sentences[sid].text.replace("."," .").replace(","," ,"))


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
write_sentence_xml(fileDictionary,"spanish_protest_event_test.xml")


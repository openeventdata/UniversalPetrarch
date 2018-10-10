# -*- coding: utf-8 -*-
'''
The script to generate validation file
usage:
	python processGSRCameo.py [brat_folder] [output_xml_name] [udpipe_model_path]

example:
	python processGSRCameo.py Protest_CAMEO_round4_JJ spanish_protest_cameo_4_jj_validation.xml ../preprocessing/udpipe-1.2.0/model/spanish-ancora-ud-2.0-170801.udpipe 

outputs:
	1. an xml file with validation records
	2. a text file with a list of records that has ambigous actors in brat annoation
'''

import sys
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import codecs
import os
import re

sys.path.append('../')

from udpipeparser import UDpipeparser



class ProtestDoc:

	def __init__(self):

		self.text = ""
		self.sentences = {}
		self.T={}
		self.R={}
		self.events = {}
		self.location = []


class T:
	def __init__(self,text,start,end,ttype):

		self.text = text
		self.start = start
		self.end = end
		self.type = ttype
		self.sentence_id = None
		self.code = None

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

class Event:
	def __init__(self,etype,action,source,target):
		self.type = etype
		self.action = action
		self.source = source
		self.target = target
		self.sentence_id = None

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
		lstart=start
		lend=start+len(line)
		
		tempid = 0
		sstart = 0
		
		temps = re.finditer("\\.\s",line)
		count = 0
		for m in temps:
			#print(m.start(0),m.end(0))
			tempid = m.end(0)
			stext = line[sstart:tempid]
			send = tempid 
			doc.sentences[str(lineid)+"."+str(count)] = Sentence(stext,sstart+lstart,send+lstart)
			#print("subline",sstart+lstart,send+lstart,stext)
			sstart = tempid
			count += 1
			#sstart = ss
		if count == 0:
			doc.sentences[str(lineid)] = Sentence(line,lstart,lend)

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
			#print(line)
			temp = line.replace("\t"," ").split(" ")
			rtype=temp[1]
			rArg1=temp[2].split(":")[1]
			rArg2=temp[3].split(":")[1]
			doc.R[temp[0]]= R(rtype,rArg1,rArg2)

		elif line.startswith("E"):
			#print(line)
			temp = line.replace("\t"," ").split(" ")
			etype=temp[1].split(":")[0]
			action = temp[1].split(":")[1]
			source = None
			target = None

			#if len(temp) > 2:
			for i in range(2, len(temp)):
				print(str(len(temp[i]))+"#")
				if i == 2 and len(temp[i])==1:
					break

				if temp[i].startswith("source"):
					source = temp[i].split(":")[1].replace("\n","")
				elif temp[i].startswith("target"):
					target = temp[i].split(":")[1].replace("\n","")
				else:
					raw_input("no source or target:"+ str(i))

			
			doc.events[temp[0]]= Event(etype,action,source,target)


	#print(doc.text)
	#for key,value in doc.sentences.items():
		#print(key)
		#print(value)

	# find sentences that contain event
	for key,Tvalue in doc.T.items():
		if Tvalue.type in ['material_conflict','verbal_conflict','material_cooperation','verbal_cooperation','location']:
			continue

		#print(Tvalue.type)
		for sid,sentence in doc.sentences.items():
			if Tvalue.start>=sentence.start and Tvalue.end<=sentence.end:
				#print(key+"\t"+Tvalue.text+"\t"+str(sid))
				#raw_input()
				Tvalue.sentence_id = sid

				if Tvalue.type not in ['source','target']:
					eventsids.append(sid)
	#raw_input(" ")
	'''
	for eid in doc.events.keys():
		action = doc.events[eid].action
		Tvalue = doc.T[action]
		for sid,sentence in doc.sentences.items():
			if Tvalue.start>=sentence.start and Tvalue.end<=sentence.end:
				print(action+"\t"+Tvalue.text+"\t"+str(sid))
				#raw_input()
				Tvalue.sentence_id = sid
				eventsids.append(sid)
	'''

	# find sentences that contain locations
	for key,Tvalue in doc.T.items():
		if Tvalue.type in ['location']:
			for sid,sentence in doc.sentences.items():
				if Tvalue.start>=sentence.start and Tvalue.end<=sentence.end:
					#print(key+"\t"+Tvalue.text+"\t"+str(sid))
					if sid in eventsids:
						doc.sentences[sid].location.append(key)
						#print("in event sentence")
					else:
						doc.location.append(key)
						#print("not in event sentence")
					#raw_input()

	return doc,list(set(eventsids))


def plover_to_CAMEO(plovercode):
	mapping = {}

	mapping["AGREE"] = "03" # | 03_EXPRESS_INTENT_TO_COOPERATE/AGREE 
	mapping["CONSULT"] = "04" # | 04_CONSULT/CONSULT 
	mapping["SUPPORT"] = "05" # | 05_DIPLOMATIC_COOPERATION/SUPPORT
	mapping["COOPERATE"] =  "06" # | 06_MATERIAL_COOPERATION/COOPERATE
	mapping["AID"] = "07" # | 07_PROCIDE_AID/AID
	mapping["CONCEDE"] = "081-083" # 08_YIELD(081~083)/CONCEDE
	mapping["RETREAT"] = "084-087" # | 08_YIELD(084~087)/RETREAT
	mapping["INVESTIGATE"] = "09" #| 09_INVESTIGATE/INVESTIGATE
	mapping["DEMAND"] = "10" # | 10_DEMAND/DEMAND
	mapping["DISAPPROVE"] = "11" # | 11_DISAPPROVE/DISAPPROVE 
	mapping["ASSAULT"] = "18/19/20" # | [18_ASSAULT/19_FIGHT/20_MASS_VIOLENCE]/ASSAULT
	mapping["REJECT"] = "12" # | 12_REJECT/REJECT
	mapping["THREATEN"] = "13" # | 13_THREATEN/THREATEN
	mapping["PROTEST"] = "14" # | 14_PROTEST/PROTEST
	mapping["MOBILIZE"] = "15" # | 15_EXHIBIT_FORCE_POSTURE/MOBILIZE
	mapping["SACTION"] = "16" # | 16_REDUCE_RELATIONS/SACTION
	mapping["COERCE"] = "17" # | 17_COERCE/COERCE

	if plovercode in mapping:
		return mapping[plovercode]
	else:
		print("mapping not found for:"+plovercode)
		#raw_input()
		input(" ")
		return ""


def generate_event_text_from_E(fileDictionary):
	for filename, value in sorted(fileDictionary.items()):
		processed =[]
		doc = value['doc']

		for eid, event in sorted(doc.events.items()):
			action = doc.T[event.action]
			source = doc.T[event.source] if event.source != None else None
			target = doc.T[event.target] if event.target != None else None
			plovercode = event.type
			cameo = plover_to_CAMEO(plovercode)

			for sid,sentence in doc.sentences.items():
				if action.start >=sentence.start and action.end<=sentence.end:
					doc.sentences[sid].event.append((action.text,source.text if source != None else "",target.text if target != None else "", plovercode, cameo, eid))



def generate_event_text_from_R(fileDictionary):
	conflicts = []
	for filename, value in sorted(fileDictionary.items()):
		print("processing:",filename)
		processed =[]
		doc = value['doc']
		
		SAT_dict = extract_SATs_quad_events(doc)
		#print(len(SAT_dict))

		#find event that coded with CAMEO (it doesn't have source or target)
		tempevent = {}
		for key,Tvalue in doc.T.items():
			if Tvalue.type in ['material_conflict','verbal_conflict','material_cooperation','verbal_cooperation','source','target']:
				continue
			if Tvalue.sentence_id != None and len(doc.sentences[Tvalue.sentence_id].event) == 0:
				if Tvalue.sentence_id not in tempevent:
					tempevent[Tvalue.sentence_id]=[]
				tempevent[Tvalue.sentence_id].append((Tvalue.text, Tvalue.type, Tvalue))

		for sid, events in tempevent.items():
			for eid,event in enumerate(events):
				#print(eid,event)
				if len(SAT_dict) > 0:
					source, target, conflict = extract_actors(event[2],SAT_dict)

					doc.sentences[sid].event.append((event[0],source,target,"",event[1],str(eid)))

					for c in conflict:
						conflicts.append((filename,sid,c))
						
				else:
					sources = []
					targets = []
					foundsource = False
					foundtarget = False
					for item in doc.T.values():
						if item.sentence_id == sid:
							if item.type == 'source':
								sources.append(item.text)
								
							elif item.type == 'target':
								targets.append(item.text)
					
							
					if len(sources)==0 and len(targets)==0:
						doc.sentences[sid].event.append((event[0],"","","",event[1],eventid))
					elif len(sources) > 0 and len(targets)==0:
						count = 0
						for source in sources:
							count += 1
							eventid = str(eid) if count == 1 else (str(eid)+"_"+str(count))
							doc.sentences[sid].event.append((event[0],source,"","",event[1],eventid))
					elif len(sources) == 0 and len(targets)>0:
						count = 0
						for target in targets:
							count += 1
							eventid = str(eid) if count == 1 else (str(eid)+"_"+str(count))
							doc.sentences[sid].event.append((event[0],"",target,"",event[1],eventid))
					else:
						count = 0
						for source in sources:
							for target in targets:
								count += 1
								eventid = str(eid) if count == 1 else (str(eid)+"_"+str(count))
								doc.sentences[sid].event.append((event[0],source,target,"",event[1],eventid))

	return list(set(conflicts))

def extract_SATs_quad_events(doc):
	SAT_dict = {}
	for key, Rvalue in sorted(doc.R.items()):
		Rtype = Rvalue.type
		eventid = ""
		#sourceid = ""
		#targetid = ""
		event = None
		source = None
		target = None
		if Rtype == 'srcAct':
			source = doc.T[Rvalue.arg1]
			event =  doc.T[Rvalue.arg2]
			eventid = Rvalue.arg2
		elif Rtype == 'actTar':
			event = doc.T[Rvalue.arg1]
			target =  doc.T[Rvalue.arg2]
			eventid = Rvalue.arg1

		if eventid not in SAT_dict:
			SAT_dict[eventid] = {}
			SAT_dict[eventid]['event'] = event

		if source != None:
			SAT_dict[eventid]['source'] = source


		if target != None:
			SAT_dict[eventid]['target'] = target

	return SAT_dict


def extract_actors(cameo_event, SAT_dict):
	'''
	Since targets and sources are annotated on quad level events, this function is to map the targets and sources to CAMEO events
	'''
	
	cameo_source = ""
	cameo_target = ""

	temp_source = None
	temp_target = None

	conflicts = []

	foundflag = False
	for eventID, sat in SAT_dict.items():
		if not (sat['event'].end < cameo_event.start or cameo_event.end < sat['event'].start):
			#check if quad event and cameo event are overlapped
			source = sat['source'] if 'source' in sat else ""
			target = sat['target'] if 'target' in sat else ""

			#print("quad event:",eventID,sat['event'].text)
			#print(cameo_event.text,cameo_event.type)
			#print("source:",source.text) if source != "" else print("source:")
			#print("target:",target.text) if target != "" else print("target:")

			#input(" ")
			if temp_source != None and source != temp_source:
				conflicts.append((eventID, cameo_event))
				#print("temp_source:", temp_source.text) if temp_source != "" else print("temp_source:")
				#input("")

			if temp_target != None and target != temp_target:
				conflicts.append((eventID, cameo_event))
				#print("temp_target:", temp_target.text) if temp_target != "" else print("temp_target:")
				#input("")

			temp_source = source
			temp_target = target

			if not foundflag:
				cameo_source = source.text if source != "" else ""
				cameo_target = target.text if target != "" else ""
				foundflag = True


	return cameo_source,cameo_target, conflicts


def write_sentence_xml(fileDictionary,outputfile, udpipemodel):
	udpipe_parser = UDpipeparser(udpipemodel)

	validation_root = ET.Element("Validation")
	environment = ET.SubElement(validation_root,"Environment")
	ET.SubElement(environment,"Verbfile").text = "CAMEO.2.0.txt"
	ET.SubElement(environment,"P1Verbfile").text = "spanish/CAMEO.spanish.verbpatterns.181009.txt"
	ET.SubElement(environment,"Actorfile").text = "spanish/ELBOW_SPANISH_Phoenix_International_actors_UPDATED.txt,spanish/ELBOW_SPANISH_Phoenix_MilNonState_actors_UPDATED.txt,spanish/ELBOW_SPANISH_Phoenix.Countries.actors_UPDATED.txt"
	ET.SubElement(environment,"Agentfile").text = "spanish/Agents_ESP_Bablenet_20171114.txt"
	ET.SubElement(environment,"Discardfile").text = "Phoenix.discards.txt"
	ET.SubElement(environment,"PICOfile").text = "PETR.Internal.Coding.Ontology.txt"
	ET.SubElement(environment,"Include").text = "protest"

	root = ET.SubElement(validation_root,"Sentences")
	#root = ET.Element("Sentences")
	#outputlines=[]

	for filename, value in sorted(fileDictionary.items()):
		print("writing and parsing:",filename)
		for sid in sorted(value['sids']):
			date = filename.split("_")[-1].split(".")[0]
			source = filename.split("_")[0]
			name = filename.split("/")[-1]
			sentence = ET.SubElement(root, "Sentence", {"date":date,"id":name+"_"+str(sid),"category":"protest","evaluate":"true"})
			#sentence = ET.SubElement(root, "Sentence", {"date":date,"id":name+"_"+str(sid),"source":source,"sentence":"true"})
			for event in fileDictionary[filename]['doc'].sentences[sid].event:
				if len(event) == 6:
					ET.SubElement(sentence,"EventText",{"eid":event[5], "eventtext":event[0],"sourcetext":event[1],"targettext":event[2]})
					ET.SubElement(sentence,"EventCoding",{"eid":event[5], "eventcode":event[4],"sourcecode":"","targetcode":"", "plover":event[3]})
				else:
					ET.SubElement(sentence,"EventText",{"eventtext":event[0],"sourcetext":event[1],"targettext":event[2]})
			for location in fileDictionary[filename]['doc'].sentences[sid].location:
				ET.SubElement(sentence,"Location",{"loc_in_sentence":"true"}).text = fileDictionary[filename]['doc'].T[location].text
				#ET.SubElement(sentence,"Location").text = fileDictionary[filename]['doc'].T[location].text
			for location in fileDictionary[filename]['doc'].location:
				ET.SubElement(sentence,"Location",{"loc_in_sentence":"false"}).text = fileDictionary[filename]['doc'].T[location].text
				#ET.SubElement(sentence,"Location").text = fileDictionary[filename]['doc'].T[location].text
			text = fileDictionary[filename]['doc'].sentences[sid].text
			ET.SubElement(sentence,"Text").text = text
			parsed_content = udpipe_parser.udpipe_parse_sent(text)
			parse = ET.SubElement(sentence,"Parse")
			parse.text = "\n"+parsed_content.strip()+"\n"
			#outputlines.append(fileDictionary[filename]['doc'].sentences[sid].text.replace("."," .").replace(","," ,"))



	tree = ET.ElementTree(validation_root)
	#tree.write(outputfile,'UTF-8')

	tree_string = ET.tostring(validation_root,'utf-8')
	new_tree_string = minidom.parseString(tree_string)
	new_tree_string = new_tree_string.toprettyxml(indent = "")
	with open(outputfile,"w") as file:
		file.write(new_tree_string)

	#outfile = codecs.open(outputfile+".txt",'w',encoding='utf8')
	#for line in outputlines:
	#	outfile.write(line)


if __name__ == '__main__':
	output_name = sys.argv[2]
	#mode = sys.argv[3] #normal|validation
	udpipemodel = sys.argv[3]

	fileDictionary = {}
	for root,dirs,files in os.walk(sys.argv[1]):
		for f in files:
			if f.endswith(".ann") and "not_updated" not in root:
				f = os.path.join(root,f)
				filename = f.replace(".ann","")
				#print(f)

				doc,eventsids = parse_annotation_file(filename.replace('\n','')) #spanish_plover/protest_part1/"
				fileDictionary[filename]={}
				fileDictionary[filename]['doc']=doc
				fileDictionary[filename]['sids']=eventsids

	#generate_event_text_from_E(fileDictionary)
	conflicts = generate_event_text_from_R(fileDictionary)
	write_sentence_xml(fileDictionary,output_name,udpipemodel)

	with open(output_name+"_actor_conflicts","w") as file:
		file.write("filename\tsentence_id\tquad_event_id\tcameo_event_text\n")

		for item in conflicts:
			#print(item)
			file.write(item[0]+"\t"+str(item[1])+"\t"+item[2][0]+"\t"+item[2][1].text+"\n")


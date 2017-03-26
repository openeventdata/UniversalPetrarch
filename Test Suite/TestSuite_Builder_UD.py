import sys

#Test Suite builder

fout = open("test_script_ud.py","w") #opens file with name of "test_script.py"

tfuncnum = 1
date=""
id = "" 
category = ""
sentence = ""
eventcode = ""
textflag = 0
parseflag = 0
text = ""
parse=""

    
def check_line(line):
    global tfuncnum, date,id,category,sentence,eventcode,textflag,parseflag,text,parse
    sentence_tag = line.find("<Sentence ")
    eventcode_tag = line.find("<EventCoding ")
    text_tag_start = line.find("<Text>")
    text_tag_end = line.find("</Text>")
    parse_tag_start = line.find("<Parse>")
    parse_tag_end = line.find("</Parse>")
    
    line = line.replace("\n","")
    line = line.replace("\r","")
    
    
    if parse_tag_end != -1:
        parseflag = 0
        eventcode = eventcode.replace("'","\\\"")
        fout.write("\"\"\"\n")
		#fout.write("\"\n")
		# Write other lines
        fout.write("    phrase_dict = parse_parser(parse)\n")
        fout.write("    parsed = utilities._format_ud_parsed_str(parse)\n")
		#	print("#######\n")
		#fout.write("#    print(parse)\n")
		#fout.write("#    print(parsed)\n")
		#	print("#######")
        fout.write("    dict = {u'test"+str(tfuncnum)+"': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},\n")
        fout.write("   		u'meta': {u'date': u'"+date+"'}}}\n")
        
        
        fout.write("    global write_str \n")
        fout.write("    write_str = []\n")
        fout.write("    return_dict = \"\" \n")
        fout.write("    try: \n")
        fout.write("        return_dict = petrarch_ud.do_coding(dict)\n")
        fout.write("    except Exception as e: \n")
        #fout.write("        fout_report.write(text.replace(\"\\n\",\" \") +\"@\"+ parsed.replace(\"\\n\",\" \") +\"@ "+ eventcode + "@ Petrarch Runtime Error \"+ str(e) +\"\\n \" )\n")
        fout.write("        write_str = [text.replace(\"\\n\",\" \") , parsed.replace(\"\\n\",\" \") , \""+eventcode+"\", \"Petrarch Runtime Error \" + str(e)]\n")
		#fout.write("#    print(return_dict)\n")

        functionname = "test"+str(tfuncnum)
        fout.write("    try:\n")
        fout.write("        if 'events' in return_dict['test"+str(tfuncnum)+"']['sents']['0']:\n")
        fout.write("            print(return_dict['test"+str(tfuncnum)+"']['sents']['0']['events'])\n")
		#write report to file
        #fout.write("            fout_report.write(text.replace(\"\\n\",\" \") +\"@\"+ parsed.replace(\"\\n\",\" \") +\"@ "+ eventcode + "@ \" + str(return_dict['"+functionname+"']['sents']['0']['events']) )\n")
        fout.write("            event_out = process_event_output(str(return_dict['"+functionname+"']['sents']['0']['events']))\n")
        #fout.write("            fout_report.write(text.replace(\"\\n\",\" \") +\"@\"+ parsed.replace(\"\\n\",\" \") +\"@ "+ eventcode + "@ \" + event_out )\n")
        fout.write("            write_str = [text.replace(\"\\n\",\" \"),parsed.replace(\"\\n\",\" \"),\""+eventcode+"\",str(return_dict['"+functionname+"']['sents']['0']['events']),event_out]\n")
		#fout.write("#           assert return_dict['test"+str(tfuncnum)+"']['sents']['0']['events'] == ["+eventcode+"]\n")
        fout.write("        else:\n")
        #fout.write("            fout_report.write(text.replace(\"\\n\",\" \") +\"@\"+ parsed.replace(\"\\n\",\" \") +\"@ "+ eventcode + "@ noevent  \" )\n")
        fout.write("            write_str = [text.replace(\"\\n\",\" \"),parsed.replace(\"\\n\",\" \"),\""+eventcode+"\",\"noevent\"]\n")
        fout.write("            print(\"test"+str(tfuncnum)+" Failed\")\n")
        fout.write("    except:\n")
        fout.write("        print(\"test"+str(tfuncnum)+" Failed\")\n")
        fout.write("    #Print the verbs\n")
        fout.write("    if 'verbs' in return_dict['test"+str(tfuncnum)+"']['sents']['0']:\n")        
        fout.write("        verbs=return_dict['test"+str(tfuncnum)+"']['sents']['0']['verbs']\n")
        fout.write("        parse_verb(verbs,phrase_dict,text,parsed)\n")
        fout.write("    if 'nouns' in return_dict['test"+str(tfuncnum)+"']['sents']['0']:\n")        
        fout.write("        #Print the nouns\n")
        fout.write("        nouns=return_dict['test"+str(tfuncnum)+"']['sents']['0']['nouns']\n")
        fout.write("        parse_noun(nouns,phrase_dict,text,parsed)\n")
        fout.write("    if 'triplets' in return_dict['test"+str(tfuncnum)+"']['sents']['0']:\n")
        fout.write("        #Print the nouns\n")
        fout.write("        triplets=return_dict['test"+str(tfuncnum)+"']['sents']['0']['triplets']\n")
        fout.write("        parse_triplets(triplets,phrase_dict)\n")
        
        
        fout.write("    fout_report.writerow(write_str)\n")
		
		
        eventcode = ""
        text=""
        parse=""
	#print("result")
	#print(return_dict['test123']['sents']['0']['events'])
	#assert return_dict['test123']['sents']['0']['events'] == [(u'DEU', u'FRA', u'173')]
	
	
	
    if text_tag_end != -1:
        textflag = 0
        fout.write("\"\"\"\n")
		
    if textflag == 1:
        text = text + line
        fout.write("" + line + "\n")
    elif parseflag == 1:
        parse = parse + line
        fout.write("" + line + "\n")
    elif sentence_tag != -1:
        print("Sentence tag found")
        fout.write("def test"+ str(tfuncnum) +"():\n")
        tfuncnum = tfuncnum + 1
		
		#Find category
        category_tag = line.find("category=\"")
        line = line[category_tag+10:]
        pos = line.find("\"")
        category = line[:pos]
        line = line[pos+1:]
        print("Category="+category)
		#print(line)
		#Find Date
        date_tag = line.find("date=\"")
        line = line[date_tag+6:]
        pos = line.find("\"")
        date = line[:pos]
        line = line[pos+1:]
        print("Date="+date)
		#print(line)
		#Find id
        id_tag = line.find("id=\"")
        line = line[id_tag+4:]
        pos = line.find("\"")
        id = line[:pos]
        line = line[pos+1:]
        print("ID="+id)
		#print(line)
		
		#Find sentence
        sentence_tag = line.find("sentence=\"")
        line = line[sentence_tag+10:]
        pos = line.find("\"")
        sentence = line[:pos]
        line = line[pos+1:]
        print("Sentence="+sentence)
        #print(line)
		
    elif eventcode_tag != -1:
        print("Event Code Found")
		#Check if noevent sentence
        noevent_tag = line.find("noevents=")
        if noevent_tag != -1:
            eventcode = "No Event"
        else:
		    #Find eventcode
            eventcode_tag = line.find("eventcode=")
            line = line[eventcode_tag+11:]
            pos = line.find("\"")
            ecode = line[:pos]
            line = line[pos+1:]
            print("eventcode="+ecode)
		    #Find sourcecode
            sourcecode_tag = line.find("sourcecode=")
            line = line[sourcecode_tag+12:]
            pos = line.find("\"")
            sourcecode = line[:pos]
            line = line[pos+1:]
            print("sourcecode="+sourcecode)
		    #print(line)
		    #Find targetcode
            targetcode_tag = line.find("targetcode=")
            line = line[targetcode_tag+12:]
            pos = line.find("\"")
            targetcode = line[:pos]
            line = line[pos+1:]
            print("targetcode="+targetcode)
		    #print(line)
		    
		    #print(line)
            #if eventcode == "":
            #    eventcode = "(u'"+sourcecode+"', u'"+targetcode+"', u'"+ecode+"')"
            #else:
            #    eventcode = eventcode + ",(u'"+sourcecode+"', u'"+targetcode+"', u'"+ecode+"')"
            #print(eventcode)
            if eventcode == "":
                eventcode = "(["+sourcecode+"],["+targetcode+"],"+ecode+")"
            else:
                eventcode = eventcode + "\\n(["+sourcecode+"],["+targetcode+"],"+ecode+")"
            print(eventcode)
	
    if parse_tag_start != -1:
        parseflag = 1
        fout.write("    parse=\"\"\"")	
	
    if text_tag_start != -1:
        textflag = 1
        fout.write("    text=\"\"\"")
		
def write_header():
    fout.write("#! /usr/bin/env python \n")
    fout.write("# -*- coding: utf-8 -*- \n")
    fout.write("import petrarch_ud, PETRglobals, PETRreader, utilities, codecs, PETRgraph \n\n")
    fout.write("import sys\n")
    fout.write("import csv\n")
    fout.write("# Get the Output File Name\n")
    fout.write("file_out = sys.argv[1]\n")
    fout.write("outfile = open(file_out, 'wb')\n")
    fout.write("fout_report = csv.writer(outfile)\n")
    
    fout.write("config = utilities._get_data('data/config/', 'PETR_config.ini')\n")
    fout.write("print(\"reading config\")\n")
    fout.write("PETRreader.parse_Config(config)\n")
    fout.write("print(\"reading dicts\")\n")
    fout.write("petrarch_ud.read_dictionaries()\n")
    #fout.write("fout_report = codecs.open(\"test_report.txt\",\"w\",encoding='utf8') #opens test report file for writing\n");
    #fout.write("fout_report.write(\"Text@ Parse Tree@ Expected Encoding as per Petrarch@ Result from Petrarch_UD @Verbs @Nouns\\n\")\n")
    fout.write("write_str = [\"Text\", \"Parse Tree\", \"Expected Encoding as per Petrarch\",\"Raw Event Data\",\"Result from Petrarch_UD \",\"Verbs\",\"Nouns\",\"Triplets\"]\n")
    fout.write("fout_report.writerow(write_str)\n")
    

    fout.write("def parse_triplets(triplets, phrase_dict):\n")
    fout.write("    res = \"\"\n")
    fout.write("    for triple in triplets:\n")
    fout.write("        strs = triplets[triple]\n")
    fout.write("        meaning = strs['meaning']\n")
    fout.write("        verbcode = strs['verbcode']\n")
    fout.write("        matched_text = strs['matched_txt']\n")
    fout.write("        codes = str(triple).split(\"#\")\n")
    fout.write("        event = \"(\" + phrase_dict[codes[0]] + \",\" + phrase_dict[codes[1]] + \",\" + phrase_dict[codes[2]] + \")\"\n")
    fout.write("        res = res + str(triple) + event +\": Meaning = \" + str(meaning) + \", VerbCode = \" + str(verbcode) + \", Matched Text = \" + str(matched_text) + \"\\n\"\n")
    fout.write("    write_str.append(res)\n")
    fout.write("    return \n")
    
    fout.write("def parse_parser(parse):\n")
    fout.write("    phrase_dict = {}\n")
    fout.write("    for line in parse.splitlines():\n")
    fout.write("        lines = line.split('\\t')\n")
    fout.write("        num = lines[0].strip()\n")
    fout.write("        str = lines[1].strip()\n")
    fout.write("        phrase_dict[num]=str\n")
    fout.write("        #print(num)\n")
    fout.write("        #print(str)\n")
    fout.write("    phrase_dict['-'] = \" \"\n")
    fout.write("    return phrase_dict	\n")
	
    fout.write("def process_event_output(str):\n")
    fout.write("    str = str.replace(\"{\",\"\")\n")
    fout.write("    str = str.replace(\"}\",\"\")\n")
    fout.write("    res = \"\"\n")
    fout.write("    events = str[str.find(\":\"):].split(\"':\")\n")
    fout.write("    for event in events:\n")
    fout.write("        event = event[0:event.rfind(\"]\")]\n")
    fout.write("        event = event.replace(\" \",\"\")\n")
    fout.write("        event = event.replace(\":\",\"\")\n")
    fout.write("        event = event.replace(\"u\",\"\")\n")
    fout.write("        event = event.replace(\"\\'\",\"\")\n")
    fout.write("        event = event[1:]\n")
    #fout.write("        event = event.replace(\"[\",\"\")\n")
    #fout.write("        event = event.replace(\"]\",\"\")\n")
    fout.write("        event = event.replace(\"~\",\"\")\n")
    fout.write("        res = res+\"\\n(\"+event+\")\"\n")
    fout.write("    return (res[1:])\n")
    

    fout.write("def parse_verb(strs,phrase_dict,text,parsed):\n")
    fout.write("    str_out = \"\"\n")
    fout.write("    str_arr = str(strs).strip(\"{\").split(\",\")\n")
    fout.write("    #print(\"Verb/Noun\") \n")
    fout.write("    for x in str_arr:\n")
    fout.write("        str_num = x.find(\":\")		\n")
    fout.write("        try:        \n")
    fout.write("            sentence = PETRgraph.Sentence(parsed, text, 0000)\n")
    fout.write("            np = sentence.get_verbPhrase(int(x[:str_num].strip()))\n")
    fout.write("            str_out = str_out + x[:str_num].strip() + \" : text = \" + str(np.text) +\", head=\"+ str(np.head) +\", meaning=\"+ str(np.meaning)+\", code=\"+ str(np.code)+\" ,passive=\"+str(np.passive) + \"\\n\"\n")
            
    fout.write("        except Exception as e:\n")
    fout.write("            #write_str.append(str_out)\n")
    fout.write("            print(e)\n")
    fout.write("    write_str.append(str_out)\n")
    fout.write("    return\n")


    fout.write("def parse_noun(strs,phrase_dict,text,parsed):\n")
    fout.write("    str_out = \"\"\n")
    fout.write("    str_arr = str(strs).strip(\"{\").split(\",\")\n")
    fout.write("    for x in str_arr:\n")
    fout.write("        str_num = x.find(\":\")		\n")
    fout.write("        #str_out = str_out + \", \" + phrase_dict[x[:str_num].strip()]\n")
    fout.write("        try:        \n")
    fout.write("            sentence = PETRgraph.Sentence(parsed, text, 0000)\n")
    fout.write("            np = sentence.get_nounPharse(int(x[:str_num].strip()))\n")
    fout.write("            np.get_meaning()\n")
    fout.write("            str_out = str_out + x[:str_num].strip() + \" : head = \" + str(np.head) +\", text=\"+ str(np.text) +\", meaning=\"+str(np.meaning)+\", matched_txt=\"+str(np.matched_txt)+ \"\\n\"\n")
    fout.write("            \n")
    fout.write("        except Exception as e:\n")
    fout.write("            write_str.append(str_out)\n")
    fout.write("            print(e)\n")
    fout.write("    write_str.append(str_out)\n")
    fout.write("    return\n")




	
# ========================== PRIMARY CODING FUNCTIONS ====================== #
# Write the header code to file
write_header()

# Get the Input XML
input_xml = sys.argv[1]

# Read through each line of XML
# Things to parse from the XML File ->
# date, ID, category, sentence, Event Coding, Text and Parse Tree
for line in open(input_xml,'r').readlines():
    #Check the line and decode text
	check_line(line)

	
for x in range(1, tfuncnum):
    fout.write("test"+str(x)+"()\n")

fout.close()	
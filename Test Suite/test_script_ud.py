#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
import petrarch_ud, PETRglobals, PETRreader, utilities, codecs, PETRgraph 

import sys
import csv
# Get the Output File Name
file_out = sys.argv[1]
outfile = open(file_out, 'wb')
fout_report = csv.writer(outfile)
config = utilities._get_data('data/config/', 'PETR_config.ini')
print("reading config")
PETRreader.parse_Config(config)
print("reading dicts")
petrarch_ud.read_dictionaries()
write_str = ["Text", "Parse Tree", "Expected Encoding as per Petrarch","Raw Event Data","Result from Petrarch_UD ","Verbs","Nouns","Triplets"]
fout_report.writerow(write_str)
def parse_triplets(triplets, phrase_dict):
    res = ""
    for triple in triplets:
        strs = triplets[triple]
        meaning = strs['meaning']
        verbcode = strs['verbcode']
        matched_text = strs['matched_txt']
        codes = str(triple).split("#")
        event = "(" + phrase_dict[codes[0]] + "," + phrase_dict[codes[1]] + "," + phrase_dict[codes[2]] + ")"
        res = res + str(triple) + event +": Meaning = " + str(meaning) + ", VerbCode = " + str(verbcode) + ", Matched Text = " + str(matched_text) + "\n"
    write_str.append(res)
    return 
def parse_parser(parse):
    phrase_dict = {}
    for line in parse.splitlines():
        lines = line.split('\t')
        num = lines[0].strip()
        str = lines[1].strip()
        phrase_dict[num]=str
        #print(num)
        #print(str)
    phrase_dict['-'] = " "
    return phrase_dict	
def process_event_output(str):
    str = str.replace("{","")
    str = str.replace("}","")
    res = ""
    events = str[str.find(":"):].split("':")
    for event in events:
        event = event[0:event.rfind("]")]
        event = event.replace(" ","")
        event = event.replace(":","")
        event = event.replace("u","")
        event = event.replace("\'","")
        event = event[1:]
        event = event.replace("~","")
        res = res+"\n("+event+")"
    return (res[1:])
def parse_verb(strs,phrase_dict,text,parsed):
    str_out = ""
    str_arr = str(strs).strip("{").split(",")
    #print("Verb/Noun") 
    for x in str_arr:
        str_num = x.find(":")		
        try:        
            sentence = PETRgraph.Sentence(parsed, text, 0000)
            np = sentence.get_verbPhrase(int(x[:str_num].strip()))
            str_out = str_out + x[:str_num].strip() + " : text = " + str(np.text) +", head="+ str(np.head) +", meaning="+ str(np.meaning)+", code="+ str(np.code)+" ,passive="+str(np.passive) + "\n"
        except Exception as e:
            #write_str.append(str_out)
            print(e)
    write_str.append(str_out)
    return
def parse_noun(strs,phrase_dict,text,parsed):
    str_out = ""
    str_arr = str(strs).strip("{").split(",")
    for x in str_arr:
        str_num = x.find(":")		
        #str_out = str_out + ", " + phrase_dict[x[:str_num].strip()]
        try:        
            sentence = PETRgraph.Sentence(parsed, text, 0000)
            np = sentence.get_nounPharse(int(x[:str_num].strip()))
            np.get_meaning()
            str_out = str_out + x[:str_num].strip() + " : head = " + str(np.head) +", text="+ str(np.text) +", meaning="+str(np.meaning)+", matched_txt="+str(np.matched_txt)+ "\n"
            
        except Exception as e:
            write_str.append(str_out)
            print(e)
    write_str.append(str_out)
    return
def test1():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test2': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test2']['sents']['0']:
            print(return_dict['test2']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test2']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test2']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test2 Failed")
    except:
        print("test2 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test2']['sents']['0']:
        verbs=return_dict['test2']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test2']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test2']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test2']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test2']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test2():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test3': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test3']['sents']['0']:
            print(return_dict['test3']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test3']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test3']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test3 Failed")
    except:
        print("test3 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test3']['sents']['0']:
        verbs=return_dict['test3']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test3']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test3']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test3']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test3']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test3():
    text="""Dagolath's first Deputy Prime Minister Telemar left for 
Minas Tirith on Wednesday for meetings of the joint transport 
committee with Arnor, the Dagolathi news agency reported. 
"""
    parse="""1	Dagolath	Dagolath	PROPN	NNP	Number=Sing	7	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	first	first	ADJ	JJ	Degree=Pos|NumType=Ord	4	amod	_	_
4	Deputy	deputy	NOUN	NN	Number=Sing	6	compound	_	_
5	Prime	Prime	PROPN	NNP	Number=Sing	6	compound	_	_
6	Minister	Minister	PROPN	NNP	Number=Sing	7	compound	_	_
7	Telemar	Telemar	PROPN	NNP	Number=Sing	8	nsubj	_	_
8	left	leave	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	for	for	ADP	IN	_	11	case	_	_
10	Minas	Minas	PROPN	NNP	Number=Sing	11	name	_	_
11	Tirith	Tirith	PROPN	NNP	Number=Sing	8	nmod	_	_
12	on	on	ADP	IN	_	13	case	_	_
13	Wednesday	Wednesday	PROPN	NNP	Number=Sing	8	nmod	_	_
14	for	for	ADP	IN	_	15	case	_	_
15	meetings	meeting	NOUN	NNS	Number=Plur	8	nmod	_	_
16	of	of	ADP	IN	_	20	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	20	det	_	_
18	joint	joint	ADJ	JJ	Degree=Pos	20	amod	_	_
19	transport	transport	NOUN	NN	Number=Sing	20	compound	_	_
20	committee	committee	NOUN	NN	Number=Sing	15	nmod	_	_
21	with	with	ADP	IN	_	22	case	_	_
22	Arnor	Arnor	PROPN	NNP	Number=Sing	20	nmod	_	_
23	,	,	PUNCT	,	_	8	punct	_	_
24	the	the	DET	DT	Definite=Def|PronType=Art	27	det	_	_
25	Dagolathi	Dagolathi	PROPN	NNP	Number=Sing	27	compound	_	_
26	news	news	NOUN	NN	Number=Sing	27	compound	_	_
27	agency	agency	NOUN	NN	Number=Sing	28	nsubj	_	_
28	reported	report	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	8	parataxis	_	_
29	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test4': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([DAGGOV],[GON],040)\n([GON],[DAGGOV],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test4']['sents']['0']:
            print(return_dict['test4']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test4']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DAGGOV],[GON],040)\n([GON],[DAGGOV],040)",str(return_dict['test4']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DAGGOV],[GON],040)\n([GON],[DAGGOV],040)","noevent"]
            print("test4 Failed")
    except:
        print("test4 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test4']['sents']['0']:
        verbs=return_dict['test4']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test4']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test4']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test4']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test4']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test4():
    text="""Caras Galadhon's new mayor left yesterday for Minas Tirith for meetings of 
the joint transport committee with Arnor. 
"""
    parse="""1	Caras	Caras	PROPN	NNP	Number=Sing	2	name	_	_
2	Galadhon	Galadhon	PROPN	NNP	Number=Sing	5	nmod:poss	_	_
3	's	's	PART	POS	_	2	case	_	_
4	new	new	ADJ	JJ	Degree=Pos	5	amod	_	_
5	mayor	mayor	NOUN	NN	Number=Sing	6	nsubj	_	_
6	left	leave	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	yesterday	yesterday	NOUN	NN	Number=Sing	6	nmod:tmod	_	_
8	for	for	ADP	IN	_	10	case	_	_
9	Minas	Minas	PROPN	NNP	Number=Sing	10	compound	_	_
10	Tirith	Tirith	PROPN	NNP	Number=Sing	6	nmod	_	_
11	for	for	ADP	IN	_	12	case	_	_
12	meetings	meeting	NOUN	NNS	Number=Plur	6	nmod	_	_
13	of	of	ADP	IN	_	17	case	_	_
14	the	the	DET	DT	Definite=Def|PronType=Art	17	det	_	_
15	joint	joint	ADJ	JJ	Degree=Pos	17	amod	_	_
16	transport	transport	NOUN	NN	Number=Sing	17	compound	_	_
17	committee	committee	NOUN	NN	Number=Sing	12	nmod	_	_
18	with	with	ADP	IN	_	19	case	_	_
19	Arnor	Arnor	PROPN	NNP	Number=Sing	17	nmod	_	_
20	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test5': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ELF],[GON],040)\n([GON],[ELF],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test5']['sents']['0']:
            print(return_dict['test5']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test5']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ELF],[GON],040)\n([GON],[ELF],040)",str(return_dict['test5']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ELF],[GON],040)\n([GON],[ELF],040)","noevent"]
            print("test5 Failed")
    except:
        print("test5 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test5']['sents']['0']:
        verbs=return_dict['test5']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test5']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test5']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test5']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test5']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test5():
    text="""Arnor is about to restore fxll diplomatic ties with Gondor almost 
five years after volleyball crowds burned down its embassy,  a senior 
official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	fxll	fxll	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	16	case	_	_
15	volleyball	volleyball	NOUN	NN	Number=Sing	16	compound	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
17	burned	burn	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
18	down	down	ADP	RP	_	17	compound:prt	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
21	,	,	PUNCT	,	_	3	punct	_	_
22	a	a	DET	DT	Definite=Ind|PronType=Art	24	det	_	_
23	senior	senior	ADJ	JJ	Degree=Pos	24	amod	_	_
24	official	official	NOUN	NN	Number=Sing	25	nsubj	_	_
25	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
26	on	on	ADP	IN	_	27	case	_	_
27	Saturday	Saturday	PROPN	NNP	Number=Sing	25	nmod	_	_
28	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test6': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test6']['sents']['0']:
            print(return_dict['test6']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test6']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test6']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test6 Failed")
    except:
        print("test6 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test6']['sents']['0']:
        verbs=return_dict['test6']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test6']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test6']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test6']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test6']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test6():
    text="""An Eriadorian was shot dead in Osgiliath, the state's fiercest foe. 
"""
    parse="""1	An	a	DET	DT	Definite=Ind|PronType=Art	2	det	_	_
2	Eriadorian	Eriadorian	NOUN	NN	Number=Sing	4	nsubjpass	_	_
3	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	4	auxpass	_	_
4	shot	shoot	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
5	dead	dead	ADJ	JJ	Degree=Pos	4	xcomp	_	_
6	in	in	ADP	IN	_	7	case	_	_
7	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	5	nmod	_	_
8	,	,	PUNCT	,	_	7	punct	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	state	state	NOUN	NN	Number=Sing	13	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	fiercest	fiercest	NOUN	NN	Number=Sing	13	compound	_	_
13	foe	foe	NOUN	NN	Number=Sing	7	appos	_	_
14	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test7': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([OSG],[ERI],190)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test7']['sents']['0']:
            print(return_dict['test7']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test7']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],190)",str(return_dict['test7']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],190)","noevent"]
            print("test7 Failed")
    except:
        print("test7 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test7']['sents']['0']:
        verbs=return_dict['test7']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test7']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test7']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test7']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test7']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test7():
    text="""The Calenardhon government condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday and promised aid to the affected Ithilen villages. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	name	_	_
3	government	government	NOUN	NN	Number=Sing	4	nsubj	_	_
4	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	attack	attack	NOUN	NN	Number=Sing	4	dobj	_	_
7	by	by	ADP	IN	_	9	case	_	_
8	Osgiliath	Osgiliath	DET	DT	_	9	det	_	_
9	soldiers	soldier	NOUN	NNS	Number=Plur	6	nmod	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	south	south	ADV	RB	_	12	advmod	_	_
12	Ithilen	Ithilen	PROPN	NNP	Number=Sing	9	nmod	_	_
13	on	on	ADP	IN	_	14	case	_	_
14	Thursday	Thursday	PROPN	NNP	Number=Sing	9	nmod	_	_
15	and	and	CONJ	CC	_	14	cc	_	_
16	promised	promise	VERB	VBN	Tense=Past|VerbForm=Part	17	amod	_	_
17	aid	aid	NOUN	NN	Number=Sing	14	conj	_	_
18	to	to	ADP	IN	_	22	case	_	_
19	the	the	DET	DT	Definite=Def|PronType=Art	22	det	_	_
20	affected	affect	VERB	VBN	Tense=Past|VerbForm=Part	22	amod	_	_
21	Ithilen	Ithilen	PROPN	NNP	Number=Sing	22	compound	_	_
22	villages	villag	NOUN	NNS	Number=Plur	9	nmod	_	_
23	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test8': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],033)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test8']['sents']['0']:
            print(return_dict['test8']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test8']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],033)",str(return_dict['test8']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],033)","noevent"]
            print("test8 Failed")
    except:
        print("test8 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test8']['sents']['0']:
        verbs=return_dict['test8']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test8']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test8']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test8']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test8']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test8():
    text="""Arnor believes Dagolath and Osgiliath can cope with a decrease in vital 
water from the mighty Entwash river when a major dam is filled next 
month. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	believes	believe	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
3	Dagolath	Dagolath	PROPN	NNP	Number=Sing	7	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	3	conj	_	_
6	can	can	AUX	MD	VerbForm=Fin	7	aux	_	_
7	cope	cope	VERB	VB	VerbForm=Inf	2	ccomp	_	_
8	with	with	ADP	IN	_	10	case	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	decrease	decrease	NOUN	NN	Number=Sing	7	nmod	_	_
11	in	in	ADP	IN	_	13	case	_	_
12	vital	vital	ADJ	JJ	Degree=Pos	13	amod	_	_
13	water	water	NOUN	NN	Number=Sing	10	nmod	_	_
14	from	from	ADP	IN	_	18	case	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
16	mighty	mighty	NOUN	NN	Number=Sing	18	compound	_	_
17	Entwash	Entwash	NOUN	NN	Number=Sing	18	compound	_	_
18	river	river	NOUN	NN	Number=Sing	10	nmod	_	_
19	when	when	ADV	WRB	PronType=Int	24	mark	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	major	major	ADJ	JJ	Degree=Pos	22	amod	_	_
22	dam	dam	NOUN	NN	Number=Sing	24	nsubjpass	_	_
23	is	be	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	24	auxpass	_	_
24	filled	fill	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	7	advcl	_	_
25	next	next	ADJ	JJ	Degree=Pos	26	amod	_	_
26	month	month	NOUN	NN	Number=Sing	24	nmod:tmod	_	_
27	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test9': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950107'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[DAG],012)\n([ARN],[OSG],012)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test9']['sents']['0']:
            print(return_dict['test9']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test9']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[DAG],012)\n([ARN],[OSG],012)",str(return_dict['test9']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[DAG],012)\n([ARN],[OSG],012)","noevent"]
            print("test9 Failed")
    except:
        print("test9 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test9']['sents']['0']:
        verbs=return_dict['test9']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test9']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test9']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test9']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test9']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test9():
    text="""The ambassadors of Arnor, Osgiliath and Gondor presented 
credentials to Ithilen's president on Wednesday in a further 
show of support to his government by their countries. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	ambassadors	ambassador	NOUN	NNS	Number=Plur	9	nsubj	_	_
3	of	of	ADP	IN	_	4	case	_	_
4	Arnor	Arnor	PROPN	NNP	Number=Sing	2	nmod	_	_
5	,	,	PUNCT	,	_	4	punct	_	_
6	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	4	conj	_	_
7	and	and	CONJ	CC	_	4	cc	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	4	conj	_	_
9	presented	present	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
10	credentials	credential	NOUN	NNS	Number=Plur	9	dobj	_	_
11	to	to	ADP	IN	_	14	case	_	_
12	Ithilen	Ithilen	PROPN	NNP	Number=Sing	14	nmod:poss	_	_
13	's	's	PART	POS	_	12	case	_	_
14	president	president	PROPN	NNP	Number=Sing	9	nmod	_	_
15	on	on	ADP	IN	_	16	case	_	_
16	Wednesday	Wednesday	PROPN	NNP	Number=Sing	9	nmod	_	_
17	in	in	ADP	IN	_	20	case	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	further	further	ADJ	JJ	Degree=Pos	20	amod	_	_
20	show	show	NOUN	NN	Number=Sing	9	nmod	_	_
21	of	of	ADP	IN	_	22	case	_	_
22	support	support	NOUN	NN	Number=Sing	20	nmod	_	_
23	to	to	ADP	IN	_	25	case	_	_
24	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	25	nmod:poss	_	_
25	government	government	NOUN	NN	Number=Sing	20	nmod	_	_
26	by	by	ADP	IN	_	28	case	_	_
27	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	28	nmod:poss	_	_
28	countries	country	NOUN	NNS	Number=Plur	9	nmod	_	_
29	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test10': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950108'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNGOV],[ITHGOV],040)\n([OSGGOV],[ITHGOV],040)\n([GONGOV],[ITHGOV],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test10']['sents']['0']:
            print(return_dict['test10']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test10']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITHGOV],040)\n([OSGGOV],[ITHGOV],040)\n([GONGOV],[ITHGOV],040)",str(return_dict['test10']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITHGOV],040)\n([OSGGOV],[ITHGOV],040)\n([GONGOV],[ITHGOV],040)","noevent"]
            print("test10 Failed")
    except:
        print("test10 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test10']['sents']['0']:
        verbs=return_dict['test10']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test10']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test10']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test10']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test10']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test10():
    text="""Gondor's Prime Minister Falastur noted that Cirith Ungol regretted Eriador's 
refusal to talk to Calenardhon leader Calimehtar. 
"""
    parse="""1	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	Prime	Prime	PROPN	NNP	Number=Sing	4	compound	_	_
4	Minister	Minister	PROPN	NNP	Number=Sing	5	compound	_	_
5	Falastur	Falastur	PROPN	NNP	Number=Sing	6	nsubj	_	_
6	noted	note	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	that	that	SCONJ	IN	_	10	mark	_	_
8	Cirith	Cirith	PROPN	NNP	Number=Sing	9	name	_	_
9	Ungol	Ungol	PROPN	NNP	Number=Sing	10	nsubj	_	_
10	regretted	regrett	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	6	ccomp	_	_
11	Eriador	Eriador	PROPN	NNP	Number=Sing	13	nmod:poss	_	_
12	's	's	PART	POS	_	11	case	_	_
13	refusal	refusal	NOUN	NN	Number=Sing	10	dobj	_	_
14	to	to	PART	TO	_	15	mark	_	_
15	talk	talk	VERB	VB	VerbForm=Inf	13	acl	_	_
16	to	to	ADP	IN	_	19	case	_	_
17	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	18	compound	_	_
18	leader	leader	NOUN	NN	Number=Sing	19	compound	_	_
19	Calimehtar	Calimehtar	PROPN	NNP	Number=Sing	15	nmod	_	_
20	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test11': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950110'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GONGOV],[MORMIL],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test11']['sents']['0']:
            print(return_dict['test11']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test11']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONGOV],[MORMIL],111)",str(return_dict['test11']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONGOV],[MORMIL],111)","noevent"]
            print("test11 Failed")
    except:
        print("test11 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test11']['sents']['0']:
        verbs=return_dict['test11']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test11']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test11']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test11']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test11']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test11():
    text="""Bree Prime Minister Romendacil will meet Eriadori and Calenardhon 
leaders during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	3	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	6	nsubj	_	_
5	will	will	AUX	MD	VerbForm=Fin	6	aux	_	_
6	meet	meet	VERB	VB	VerbForm=Inf	0	root	_	_
7	Eriadori	Eriadori	PROPN	NNP	Number=Sing	10	compound	_	_
8	and	and	CONJ	CC	_	7	cc	_	_
9	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	7	conj	_	_
10	leaders	leader	NOUN	NNS	Number=Plur	6	dobj	_	_
11	during	during	ADP	IN	_	15	case	_	_
12	a	a	DET	DT	Definite=Ind|PronType=Art	15	det	_	_
13	brief	brief	ADJ	JJ	Degree=Pos	15	amod	_	_
14	private	private	ADJ	JJ	Degree=Pos	15	amod	_	_
15	visit	visit	NOUN	NN	Number=Sing	10	nmod	_	_
16	to	to	ADP	IN	_	17	case	_	_
17	Eriador	Eriador	PROPN	NNP	Number=Sing	15	nmod	_	_
18	starting	start	VERB	VBG	VerbForm=Ger	15	acl	_	_
19	on	on	ADP	IN	_	20	case	_	_
20	Sunday	Sunday	PROPN	NNP	Number=Sing	18	nmod	_	_
21	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test12': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],040)\n([ERI],[BREGOV],040)\n([BREGOV],[CAL],040)\n([CAL],[BREGOV],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test12']['sents']['0']:
            print(return_dict['test12']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test12']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],040)\n([ERI],[BREGOV],040)\n([BREGOV],[CAL],040)\n([CAL],[BREGOV],040)",str(return_dict['test12']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],040)\n([ERI],[BREGOV],040)\n([BREGOV],[CAL],040)\n([CAL],[BREGOV],040)","noevent"]
            print("test12 Failed")
    except:
        print("test12 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test12']['sents']['0']:
        verbs=return_dict['test12']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test12']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test12']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test12']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test12']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test12():
    text="""Eriador expressed hopes on Thursday that Osgiliath, the state's 
fiercest foe, could be drawn into the peace process by its resumption 
of diplomatic ties with Gondor. 
"""
    parse="""1	Eriador	Eriador	NOUN	NN	Number=Sing	3	compound	_	_
2	expressed	express	VERB	VBN	Tense=Past|VerbForm=Part	3	amod	_	_
3	hopes	hope	NOUN	NNS	Number=Plur	0	root	_	_
4	on	on	ADP	IN	_	5	case	_	_
5	Thursday	Thursday	PROPN	NNP	Number=Sing	3	nmod	_	_
6	that	that	PRON	WDT	PronType=Rel	17	dobj	_	_
7	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	17	nsubjpass	_	_
8	,	,	PUNCT	,	_	7	punct	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	state	state	NOUN	NN	Number=Sing	13	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	fiercest	fiercest	NOUN	NN	Number=Sing	13	compound	_	_
13	foe	foe	NOUN	NN	Number=Sing	7	appos	_	_
14	,	,	PUNCT	,	_	17	punct	_	_
15	could	could	AUX	MD	VerbForm=Fin	17	aux	_	_
16	be	be	AUX	VB	VerbForm=Inf	17	auxpass	_	_
17	drawn	draw	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	5	acl:relcl	_	_
18	into	into	ADP	IN	_	21	case	_	_
19	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
20	peace	peace	NOUN	NN	Number=Sing	21	compound	_	_
21	process	process	NOUN	NN	Number=Sing	17	nmod	_	_
22	by	by	ADP	IN	_	24	case	_	_
23	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	24	nmod:poss	_	_
24	resumption	resumption	NOUN	NN	Number=Sing	21	nmod	_	_
25	of	of	ADP	IN	_	27	case	_	_
26	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	27	amod	_	_
27	ties	tie	NOUN	NNS	Number=Plur	24	nmod	_	_
28	with	with	ADP	IN	_	29	case	_	_
29	Gondor	Gondor	PROPN	NNP	Number=Sing	27	nmod	_	_
30	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test13': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[OSG],013)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test13']['sents']['0']:
            print(return_dict['test13']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test13']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],013)",str(return_dict['test13']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],013)","noevent"]
            print("test13 Failed")
    except:
        print("test13 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test13']['sents']['0']:
        verbs=return_dict['test13']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test13']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test13']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test13']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test13']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test13():
    text="""Arnor on Thursday signed an 800 million ducat trade protocol
for 1990 with Dagolath, its biggest trading partner, officials said. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	4	nsubj	_	_
2	on	on	ADP	IN	_	3	case	_	_
3	Thursday	Thursday	PROPN	NNP	Number=Sing	1	nmod	_	_
4	signed	sign	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
6	800	800	NUM	CD	NumType=Card	7	compound	_	_
7	million	million	NUM	CD	NumType=Card	8	nummod	_	_
8	ducat	ducat	NOUN	NN	Number=Sing	10	compound	_	_
9	trade	trade	NOUN	NN	Number=Sing	10	compound	_	_
10	protocol	protocol	NOUN	NN	Number=Sing	4	dobj	_	_
11	for	for	ADP	IN	_	12	case	_	_
12	1990	1990	NUM	CD	NumType=Card	10	nmod	_	_
13	with	with	ADP	IN	_	14	case	_	_
14	Dagolath	Dagolath	PROPN	NNP	Number=Sing	12	nmod	_	_
15	,	,	PUNCT	,	_	14	punct	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
17	biggest	biggest	ADJ	JJS	Degree=Sup	19	amod	_	_
18	trading	trading	NOUN	NN	Number=Sing	19	compound	_	_
19	partner	partner	NOUN	NN	Number=Sing	14	appos	_	_
20	,	,	PUNCT	,	_	4	punct	_	_
21	officials	official	NOUN	NNS	Number=Plur	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	parataxis	_	_
23	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test14': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950113'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[DAG],057)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test14']['sents']['0']:
            print(return_dict['test14']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test14']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[DAG],057)",str(return_dict['test14']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[DAG],057)","noevent"]
            print("test14 Failed")
    except:
        print("test14 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test14']['sents']['0']:
        verbs=return_dict['test14']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test14']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test14']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test14']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test14']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test14():
    text="""Ithilen's militia vowed on Thursday to wage war on the Rohans until that 
group yielded ground seized in six days of fighting.
"""
    parse="""1	Ithilen	Ithilen	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	militia	militia	PROPN	NNP	Number=Sing	4	nsubj	_	_
4	vowed	vowe	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	on	on	ADP	IN	_	6	case	_	_
6	Thursday	Thursday	PROPN	NNP	Number=Sing	4	nmod	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	wage	wage	VERB	VB	VerbForm=Inf	4	advcl	_	_
9	war	war	NOUN	NN	Number=Sing	8	dobj	_	_
10	on	on	ADP	IN	_	12	case	_	_
11	the	the	DET	DT	Definite=Def|PronType=Art	12	det	_	_
12	Rohans	Rohans	PROPN	NNPS	Number=Plur	8	nmod	_	_
13	until	until	SCONJ	IN	_	16	mark	_	_
14	that	that	DET	DT	Number=Sing|PronType=Dem	15	det	_	_
15	group	group	NOUN	NN	Number=Sing	16	nsubj	_	_
16	yielded	yield	VERB	VBN	Tense=Past|VerbForm=Part	4	advcl	_	_
17	ground	ground	NOUN	NN	Number=Sing	16	dobj	_	_
18	seized	seize	VERB	VBN	Tense=Past|VerbForm=Part	17	acl	_	_
19	in	in	ADP	IN	_	21	case	_	_
20	six	six	NUM	CD	NumType=Card	21	nummod	_	_
21	days	day	NOUN	NNS	Number=Plur	18	nmod	_	_
22	of	of	ADP	IN	_	23	case	_	_
23	fighting	fighting	NOUN	NN	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test15': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950114'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ITH],[ROH],190)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test15']['sents']['0']:
            print(return_dict['test15']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test15']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[ROH],190)",str(return_dict['test15']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[ROH],190)","noevent"]
            print("test15 Failed")
    except:
        print("test15 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test15']['sents']['0']:
        verbs=return_dict['test15']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test15']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test15']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test15']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test15']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test15():
    text="""Arnor signed an accord on Thursday to supply Gondor with some 
50,000 tonnes of wheat, worth 11.8 million ducats, an Arnorian 
embassy spokesman said.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	signed	sign	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	an	a	DET	DT	Definite=Ind|PronType=Art	4	det	_	_
4	accord	accord	NOUN	NN	Number=Sing	2	dobj	_	_
5	on	on	ADP	IN	_	6	case	_	_
6	Thursday	Thursday	PROPN	NNP	Number=Sing	2	nmod	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	supply	supply	VERB	VB	VerbForm=Inf	2	advcl	_	_
9	Gondor	Gondor	NOUN	NN	Number=Sing	8	dobj	_	_
10	with	with	ADP	IN	_	13	case	_	_
11	some	some	DET	DT	_	13	det	_	_
12	50,000	50,000	NUM	CD	NumType=Card	13	nummod	_	_
13	tonnes	tonne	NOUN	NNS	Number=Plur	8	nmod	_	_
14	of	of	ADP	IN	_	15	case	_	_
15	wheat	wheat	NOUN	NN	Number=Sing	13	nmod	_	_
16	,	,	PUNCT	,	_	2	punct	_	_
17	worth	worth	ADJ	JJ	Degree=Pos	20	amod	_	_
18	11.8	11.8	NUM	CD	NumType=Card	19	compound	_	_
19	million	million	NUM	CD	NumType=Card	20	nummod	_	_
20	ducats	ducat	NOUN	NNS	Number=Plur	2	parataxis	_	_
21	,	,	PUNCT	,	_	2	punct	_	_
22	an	a	DET	DT	Definite=Ind|PronType=Art	25	det	_	_
23	Arnorian	Arnorian	ADJ	JJ	Degree=Pos	25	amod	_	_
24	embassy	embassy	NOUN	NN	Number=Sing	25	compound	_	_
25	spokesman	spokesman	NOUN	NN	Number=Sing	26	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
27	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test16': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950115'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],057)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test16']['sents']['0']:
            print(return_dict['test16']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test16']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],057)",str(return_dict['test16']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],057)","noevent"]
            print("test16 Failed")
    except:
        print("test16 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test16']['sents']['0']:
        verbs=return_dict['test16']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test16']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test16']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test16']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test16']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test16():
    text="""Arnor President Umbardacil has again appealed for peace in Ithilen in 
a message to the spiritial leader of the war-torn nation's influential 
Douzu community.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	2	compound	_	_
2	President	President	PROPN	NNP	Number=Sing	3	compound	_	_
3	Umbardacil	Umbardacil	PROPN	NNP	Number=Sing	6	nsubj	_	_
4	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	aux	_	_
5	again	again	ADV	RB	_	6	advmod	_	_
6	appealed	appeal	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
7	for	for	ADP	IN	_	8	case	_	_
8	peace	peace	NOUN	NN	Number=Sing	6	nmod	_	_
9	in	in	ADP	IN	_	10	case	_	_
10	Ithilen	Ithilen	PROPN	NNP	Number=Sing	6	nmod	_	_
11	in	in	ADP	IN	_	13	case	_	_
12	a	a	DET	DT	Definite=Ind|PronType=Art	13	det	_	_
13	message	message	NOUN	NN	Number=Sing	6	nmod	_	_
14	to	to	ADP	IN	_	17	case	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	17	det	_	_
16	spiritial	spiritial	ADJ	JJ	Degree=Pos	17	amod	_	_
17	leader	leader	NOUN	NN	Number=Sing	13	nmod	_	_
18	of	of	ADP	IN	_	25	case	_	_
19	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
20	war-torn	war-torn	ADJ	JJ	Degree=Pos	21	amod	_	_
21	nation	nation	NOUN	NN	Number=Sing	25	nmod:poss	_	_
22	's	's	PART	POS	_	21	case	_	_
23	influential	influential	ADJ	JJ	Degree=Pos	25	amod	_	_
24	Douzu	Douzu	PROPN	NNP	Number=Sing	25	compound	_	_
25	community	community	NOUN	NN	Number=Sing	17	nmod	_	_
26	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test17': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950116'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNGOV],[ITH],027)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test17']['sents']['0']:
            print(return_dict['test17']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test17']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITH],027)",str(return_dict['test17']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITH],027)","noevent"]
            print("test17 Failed")
    except:
        print("test17 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test17']['sents']['0']:
        verbs=return_dict['test17']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test17']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test17']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test17']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test17']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test17():
    text="""Bree President Romendacil arrived in Gondor on Monday on his first 
official foreign visit since pro-restoration demonstrators 
in Eymn Muil were crushed last June.
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	2	compound	_	_
2	President	President	PROPN	NNP	Number=Sing	3	compound	_	_
3	Romendacil	Romendacil	PROPN	NNP	Number=Sing	4	nsubj	_	_
4	arrived	arrive	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	in	in	ADP	IN	_	6	case	_	_
6	Gondor	Gondor	PROPN	NNP	Number=Sing	4	nmod	_	_
7	on	on	ADP	IN	_	8	case	_	_
8	Monday	Monday	PROPN	NNP	Number=Sing	4	nmod	_	_
9	on	on	ADP	IN	_	12	case	_	_
10	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
11	first	first	ADJ	JJ	Degree=Pos|NumType=Ord	12	amod	_	_
12	official	official	NOUN	NN	Number=Sing	22	nmod	_	_
13	foreign	foreign	ADJ	JJ	Degree=Pos	14	amod	_	_
14	visit	visit	NOUN	NN	Number=Sing	22	nsubjpass	_	_
15	since	since	ADP	IN	_	17	case	_	_
16	pro-restoration	pro-restoration	NOUN	NN	Number=Sing	17	compound	_	_
17	demonstrators	demonstrator	NOUN	NNS	Number=Plur	14	nmod	_	_
18	in	in	ADP	IN	_	20	case	_	_
19	Eymn	Eymn	PROPN	NNP	Number=Sing	20	compound	_	_
20	Muil	Muil	PROPN	NNP	Number=Sing	17	nmod	_	_
21	were	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	22	auxpass	_	_
22	crushed	crush	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	4	advcl	_	_
23	last	last	ADJ	JJ	Degree=Pos	24	amod	_	_
24	June	June	PROPN	NNP	Number=Sing	22	nmod:tmod	_	_
25	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test18': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950117'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[GON],040)\n([GON],[BREGOV],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test18']['sents']['0']:
            print(return_dict['test18']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test18']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[GON],040)\n([GON],[BREGOV],040)",str(return_dict['test18']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[GON],040)\n([GON],[BREGOV],040)","noevent"]
            print("test18 Failed")
    except:
        print("test18 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test18']['sents']['0']:
        verbs=return_dict['test18']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test18']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test18']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test18']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test18']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test18():
    text="""Calenardhon urged Bree on Monday to help win a greater role for 
it in forthcoming peace talks.
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	urged	urge	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	Bree	Bree	PROPN	NNP	Number=Sing	2	dobj	_	_
4	on	on	ADP	IN	_	5	case	_	_
5	Monday	Monday	PROPN	NNP	Number=Sing	2	nmod	_	_
6	to	to	PART	TO	_	7	mark	_	_
7	help	help	VERB	VB	VerbForm=Inf	2	advcl	_	_
8	win	win	VERB	VB	VerbForm=Inf	7	ccomp	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	11	det	_	_
10	greater	greater	ADJ	JJR	Degree=Cmp	11	amod	_	_
11	role	role	NOUN	NN	Number=Sing	8	dobj	_	_
12	for	for	ADP	IN	_	13	case	_	_
13	it	it	PRON	PRP	Case=Acc|Gender=Neut|Number=Sing|Person=3|PronType=Prs	8	nmod	_	_
14	in	in	ADP	IN	_	17	case	_	_
15	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	17	amod	_	_
16	peace	peace	NOUN	NN	Number=Sing	17	compound	_	_
17	talks	talk	NOUN	NNS	Number=Plur	8	nmod	_	_
18	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test19': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],023)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test19']['sents']['0']:
            print(return_dict['test19']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test19']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],023)",str(return_dict['test19']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],023)","noevent"]
            print("test19 Failed")
    except:
        print("test19 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test19']['sents']['0']:
        verbs=return_dict['test19']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test19']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test19']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test19']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test19']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test19():
    text="""Arnor's foreign minister, in remarks published on Monday, urged 
Eriador to respond to Gondor's proposals on elections.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	4	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	foreign	foreign	ADJ	JJ	Degree=Pos	4	amod	_	_
4	minister	minister	NOUN	NN	Number=Sing	12	nsubj	_	_
5	,	,	PUNCT	,	_	7	punct	_	_
6	in	in	ADP	IN	_	7	case	_	_
7	remarks	remark	NOUN	NNS	Number=Plur	4	nmod	_	_
8	published	publish	VERB	VBN	Tense=Past|VerbForm=Part	7	acl	_	_
9	on	on	ADP	IN	_	10	case	_	_
10	Monday	Monday	PROPN	NNP	Number=Sing	8	nmod	_	_
11	,	,	PUNCT	,	_	12	punct	_	_
12	urged	urge	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
13	Eriador	Eriador	PROPN	NNP	Number=Sing	12	dobj	_	_
14	to	to	PART	TO	_	15	mark	_	_
15	respond	respond	VERB	VB	VerbForm=Inf	13	acl	_	_
16	to	to	ADP	IN	_	19	case	_	_
17	Gondor	Gondor	PROPN	NNP	Number=Sing	19	nmod:poss	_	_
18	's	's	PART	POS	_	17	case	_	_
19	proposals	proposal	NOUN	NNS	Number=Plur	15	nmod	_	_
20	on	on	ADP	IN	_	21	case	_	_
21	elections	election	NOUN	NNS	Number=Plur	19	nmod	_	_
22	.	.	PUNCT	.	_	12	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test20': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950119'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNGOVFRM],[ERI],023)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test20']['sents']['0']:
            print(return_dict['test20']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test20']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOVFRM],[ERI],023)",str(return_dict['test20']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOVFRM],[ERI],023)","noevent"]
            print("test20 Failed")
    except:
        print("test20 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test20']['sents']['0']:
        verbs=return_dict['test20']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test20']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test20']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test20']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test20']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test20():
    text="""Eriador's death toll has risen in the dispute with  Osgiliath, the state's 
fiercest foe. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	4	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	death	death	NOUN	NN	Number=Sing	4	compound	_	_
4	toll	toll	NOUN	NN	Number=Sing	6	nsubj	_	_
5	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	aux	_	_
6	risen	rise	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
7	in	in	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	dispute	dispute	NOUN	NN	Number=Sing	6	nmod	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	9	nmod	_	_
12	,	,	PUNCT	,	_	9	punct	_	_
13	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
14	state	state	NOUN	NN	Number=Sing	17	nmod:poss	_	_
15	's	's	PART	POS	_	14	case	_	_
16	fiercest	fiercest	NOUN	NN	Number=Sing	17	compound	_	_
17	foe	foe	NOUN	NN	Number=Sing	9	appos	_	_
18	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test21': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[OSG],190)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test21']['sents']['0']:
            print(return_dict['test21']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test21']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)",str(return_dict['test21']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)","noevent"]
            print("test21 Failed")
    except:
        print("test21 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test21']['sents']['0']:
        verbs=return_dict['test21']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test21']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test21']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test21']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test21']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test21():
    text="""Eriador's death and injury toll has risen in the dispute with Osgiliath, the state's 
fiercest foe. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	death	death	NOUN	NN	Number=Sing	8	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	injury	injury	NOUN	NN	Number=Sing	6	compound	_	_
6	toll	toll	NOUN	NN	Number=Sing	3	conj	_	_
7	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	8	aux	_	_
8	risen	rise	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
9	in	in	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	dispute	dispute	NOUN	NN	Number=Sing	8	nmod	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	11	nmod	_	_
14	,	,	PUNCT	,	_	11	punct	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	16	det	_	_
16	state	state	NOUN	NN	Number=Sing	19	nmod:poss	_	_
17	's	's	PART	POS	_	16	case	_	_
18	fiercest	fiercest	NOUN	NN	Number=Sing	19	compound	_	_
19	foe	foe	NOUN	NN	Number=Sing	11	appos	_	_
20	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test22': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[OSG],190)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test22']['sents']['0']:
            print(return_dict['test22']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test22']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)",str(return_dict['test22']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)","noevent"]
            print("test22 Failed")
    except:
        print("test22 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test22']['sents']['0']:
        verbs=return_dict['test22']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test22']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test22']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test22']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test22']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test22():
    text="""Eriador's death and injury toll has risen in the dispute with Osgiliath, the state's 
fiercest foe. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	death	death	NOUN	NN	Number=Sing	8	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	injury	injury	NOUN	NN	Number=Sing	6	compound	_	_
6	toll	toll	NOUN	NN	Number=Sing	3	conj	_	_
7	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	8	aux	_	_
8	risen	rise	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
9	in	in	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	dispute	dispute	NOUN	NN	Number=Sing	8	nmod	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	11	nmod	_	_
14	,	,	PUNCT	,	_	11	punct	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	16	det	_	_
16	state	state	NOUN	NN	Number=Sing	19	nmod:poss	_	_
17	's	's	PART	POS	_	16	case	_	_
18	fiercest	fiercest	NOUN	NN	Number=Sing	19	compound	_	_
19	foe	foe	NOUN	NN	Number=Sing	11	appos	_	_
20	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test23': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[OSG],190)\n([&quot;INJURY TOLL&quot;],[OSG],190)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test23']['sents']['0']:
            print(return_dict['test23']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test23']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)\n([&quot;INJURY TOLL&quot;],[OSG],190)",str(return_dict['test23']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)\n([&quot;INJURY TOLL&quot;],[OSG],190)","noevent"]
            print("test23 Failed")
    except:
        print("test23 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test23']['sents']['0']:
        verbs=return_dict['test23']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test23']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test23']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test23']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test23']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test23():
    text="""Eriador's death total has risen in the dispute with  Osgiliath, the state's 
fiercest foe. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	4	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	death	death	NOUN	NN	Number=Sing	4	compound	_	_
4	total	total	NOUN	NN	Number=Sing	6	nsubj	_	_
5	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	aux	_	_
6	risen	rise	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
7	in	in	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	dispute	dispute	NOUN	NN	Number=Sing	6	nmod	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	9	nmod	_	_
12	,	,	PUNCT	,	_	9	punct	_	_
13	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
14	state	state	NOUN	NN	Number=Sing	17	nmod:poss	_	_
15	's	's	PART	POS	_	14	case	_	_
16	fiercest	fiercest	NOUN	NN	Number=Sing	17	compound	_	_
17	foe	foe	NOUN	NN	Number=Sing	9	appos	_	_
18	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test24': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[OSG],190)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test24']['sents']['0']:
            print(return_dict['test24']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test24']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)",str(return_dict['test24']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],190)","noevent"]
            print("test24 Failed")
    except:
        print("test24 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test24']['sents']['0']:
        verbs=return_dict['test24']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test24']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test24']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test24']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test24']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test24():
    text="""Eriador's death and injury total has risen in the dispute with Osgiliath, the state's 
fiercest foe. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	death	death	NOUN	NN	Number=Sing	8	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	injury	injury	NOUN	NN	Number=Sing	6	compound	_	_
6	total	total	NOUN	NN	Number=Sing	3	conj	_	_
7	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	8	aux	_	_
8	risen	rise	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
9	in	in	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	dispute	dispute	NOUN	NN	Number=Sing	8	nmod	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	11	nmod	_	_
14	,	,	PUNCT	,	_	11	punct	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	16	det	_	_
16	state	state	NOUN	NN	Number=Sing	19	nmod:poss	_	_
17	's	's	PART	POS	_	16	case	_	_
18	fiercest	fiercest	NOUN	NN	Number=Sing	19	compound	_	_
19	foe	foe	NOUN	NN	Number=Sing	11	appos	_	_
20	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test25': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test25']['sents']['0']:
            print(return_dict['test25']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test25']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test25']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test25 Failed")
    except:
        print("test25 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test25']['sents']['0']:
        verbs=return_dict['test25']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test25']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test25']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test25']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test25']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test25():
    text="""Gondor and Osgiliath have postponed their meeting after a 
hafling was reported on the pass of Cirith Ungol. 
"""
    parse="""1	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	1	conj	_	_
4	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	aux	_	_
5	postponed	postpone	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
6	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
7	meeting	meeting	NOUN	NN	Number=Sing	5	dobj	_	_
8	after	after	ADP	IN	_	12	mark	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	hafling	hafling	NOUN	NN	Number=Sing	12	nsubjpass	_	_
11	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	12	auxpass	_	_
12	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	5	advcl	_	_
13	on	on	ADP	IN	_	15	case	_	_
14	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
15	pass	pass	NOUN	NN	Number=Sing	12	nmod	_	_
16	of	of	ADP	IN	_	18	case	_	_
17	Cirith	Cirith	PROPN	NNP	Number=Sing	18	name	_	_
18	Ungol	Ungol	PROPN	NNP	Number=Sing	15	nmod	_	_
19	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test26': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[MORMIL],120)\n([OSG],[MORMIL],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test26']['sents']['0']:
            print(return_dict['test26']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test26']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[MORMIL],120)\n([OSG],[MORMIL],120)",str(return_dict['test26']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[MORMIL],120)\n([OSG],[MORMIL],120)","noevent"]
            print("test26 Failed")
    except:
        print("test26 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test26']['sents']['0']:
        verbs=return_dict['test26']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test26']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test26']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test26']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test26']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test26():
    text="""Gondor and Osgiliath have delayed their meeting after a 
hafling was reported on the pass of Cirith Ungol. 
"""
    parse="""1	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	1	conj	_	_
4	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	aux	_	_
5	delayed	delay	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
6	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
7	meeting	meeting	NOUN	NN	Number=Sing	5	dobj	_	_
8	after	after	ADP	IN	_	12	mark	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	hafling	hafling	NOUN	NN	Number=Sing	12	nsubjpass	_	_
11	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	12	auxpass	_	_
12	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	5	advcl	_	_
13	on	on	ADP	IN	_	15	case	_	_
14	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
15	pass	pass	NOUN	NN	Number=Sing	12	nmod	_	_
16	of	of	ADP	IN	_	18	case	_	_
17	Cirith	Cirith	PROPN	NNP	Number=Sing	18	name	_	_
18	Ungol	Ungol	PROPN	NNP	Number=Sing	15	nmod	_	_
19	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test27': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[OSG],120)\n([OSG],[GON],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test27']['sents']['0']:
            print(return_dict['test27']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test27']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],120)\n([OSG],[GON],120)",str(return_dict['test27']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],120)\n([OSG],[GON],120)","noevent"]
            print("test27 Failed")
    except:
        print("test27 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test27']['sents']['0']:
        verbs=return_dict['test27']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test27']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test27']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test27']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test27']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test27():
    text="""Gondor and Osgiliath have downplayed their meeting after a 
hafling was reported on the pass of Cirith Ungol. 
"""
    parse="""1	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	1	conj	_	_
4	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	aux	_	_
5	downplayed	downplay	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
6	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
7	meeting	meeting	NOUN	NN	Number=Sing	5	dobj	_	_
8	after	after	ADP	IN	_	12	mark	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	hafling	hafling	NOUN	NN	Number=Sing	12	nsubjpass	_	_
11	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	12	auxpass	_	_
12	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	5	advcl	_	_
13	on	on	ADP	IN	_	15	case	_	_
14	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
15	pass	pass	NOUN	NN	Number=Sing	12	nmod	_	_
16	of	of	ADP	IN	_	18	case	_	_
17	Cirith	Cirith	PROPN	NNP	Number=Sing	18	name	_	_
18	Ungol	Ungol	PROPN	NNP	Number=Sing	15	nmod	_	_
19	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test28': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[OSG],120)\n([OSG],[GON],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test28']['sents']['0']:
            print(return_dict['test28']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test28']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],120)\n([OSG],[GON],120)",str(return_dict['test28']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],120)\n([OSG],[GON],120)","noevent"]
            print("test28 Failed")
    except:
        print("test28 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test28']['sents']['0']:
        verbs=return_dict['test28']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test28']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test28']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test28']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test28']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test28():
    text="""It has been noted that Gondor and Osgiliath have delayed their meeting after a hafling was reported on the pass
"""
    parse="""1	It	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	4	nsubjpass	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
3	been	be	AUX	VBN	Tense=Past|VerbForm=Part	4	auxpass	_	_
4	noted	note	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
5	that	that	SCONJ	IN	_	10	mark	_	_
6	Gondor	Gondor	PROPN	NNP	Number=Sing	10	nsubj	_	_
7	and	and	CONJ	CC	_	6	cc	_	_
8	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	6	conj	_	_
9	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	10	aux	_	_
10	delayed	delay	VERB	VBN	Tense=Past|VerbForm=Part	4	ccomp	_	_
11	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
12	meeting	meeting	NOUN	NN	Number=Sing	10	dobj	_	_
13	after	after	ADP	IN	_	17	mark	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	15	det	_	_
15	hafling	hafling	NOUN	NN	Number=Sing	17	nsubjpass	_	_
16	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	17	auxpass	_	_
17	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	10	advcl	_	_
18	on	on	ADP	IN	_	20	case	_	_
19	the	the	DET	DT	Definite=Def|PronType=Art	20	det	_	_
20	pass	pass	NOUN	NN	Number=Sing	17	nmod	_	_
21	of	of	ADP	IN	_	23	case	_	_
22	Cirith	Cirith	PROPN	NNP	Number=Sing	23	name	_	_
23	Ungol	Ungol	PROPN	NNP	Number=Sing	20	nmod	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test29': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[OSG],120)\n([OSG],[GON],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test29']['sents']['0']:
            print(return_dict['test29']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test29']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],120)\n([OSG],[GON],120)",str(return_dict['test29']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],120)\n([OSG],[GON],120)","noevent"]
            print("test29 Failed")
    except:
        print("test29 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test29']['sents']['0']:
        verbs=return_dict['test29']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test29']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test29']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test29']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test29']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test29():
    text="""Soldiers from Gondor have cordoned off the roads leading into Mordor along the pass 
of Cirith Ungol.
"""
    parse="""1	Soldiers	soldier	NOUN	NNS	Number=Plur	5	nsubj	_	_
2	from	from	ADP	IN	_	3	case	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	1	nmod	_	_
4	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	aux	_	_
5	cordoned	cordon	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
6	off	off	ADP	IN	_	8	case	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	8	det	_	_
8	roads	roads	NOUN	NNS	Number=Plur	5	nmod	_	_
9	leading	lead	VERB	VBG	VerbForm=Ger	8	acl	_	_
10	into	into	ADP	IN	_	11	case	_	_
11	Mordor	Mordor	PROPN	NNP	Number=Sing	9	nmod	_	_
12	along	along	ADP	IN	_	14	case	_	_
13	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
14	pass	pass	NOUN	NN	Number=Sing	9	nmod	_	_
15	of	of	ADP	IN	_	17	case	_	_
16	Cirith	Cirith	PROPN	NNP	Number=Sing	17	name	_	_
17	Ungol	Ungol	PROPN	NNP	Number=Sing	14	nmod	_	_
18	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test30': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GONMIL],[MOR],144)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test30']['sents']['0']:
            print(return_dict['test30']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test30']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],144)",str(return_dict['test30']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],144)","noevent"]
            print("test30 Failed")
    except:
        print("test30 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test30']['sents']['0']:
        verbs=return_dict['test30']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test30']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test30']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test30']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test30']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test30():
    text="""Soldiers from Gondor wire tapped all communication links leading into Mordor along the 
pass of Cirith Ungol.
"""
    parse="""1	Soldiers	soldier	NOUN	NNS	Number=Plur	0	root	_	_
2	from	from	ADP	IN	_	4	case	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	4	name	_	_
4	wire	wire	NOUN	NN	Number=Sing	1	nmod	_	_
5	tapped	tap	VERB	VBN	Tense=Past|VerbForm=Part	1	acl	_	_
6	all	all	DET	DT	_	8	det	_	_
7	communication	communication	NOUN	NN	Number=Sing	8	compound	_	_
8	links	link	NOUN	NNS	Number=Plur	5	dobj	_	_
9	leading	lead	VERB	VBG	VerbForm=Ger	8	acl	_	_
10	into	into	ADP	IN	_	11	case	_	_
11	Mordor	Mordor	PROPN	NNP	Number=Sing	9	nmod	_	_
12	along	along	ADP	IN	_	14	case	_	_
13	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
14	pass	pass	NOUN	NN	Number=Sing	9	nmod	_	_
15	of	of	ADP	IN	_	17	case	_	_
16	Cirith	Cirith	PROPN	NNP	Number=Sing	17	name	_	_
17	Ungol	Ungol	PROPN	NNP	Number=Sing	14	nmod	_	_
18	.	.	PUNCT	.	_	1	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test31': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GONMIL],[MOR],170)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test31']['sents']['0']:
            print(return_dict['test31']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test31']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],170)",str(return_dict['test31']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],170)","noevent"]
            print("test31 Failed")
    except:
        print("test31 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test31']['sents']['0']:
        verbs=return_dict['test31']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test31']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test31']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test31']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test31']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test31():
    text="""Soldiers from Gondor will not wire tap the communication links leading into Mordor along  
the pass of Cirith Ungol.
"""
    parse="""1	Soldiers	soldier	NOUN	NNS	Number=Plur	6	nsubj	_	_
2	from	from	ADP	IN	_	3	case	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	1	nmod	_	_
4	will	will	AUX	MD	VerbForm=Fin	6	aux	_	_
5	not	not	PART	RB	_	6	neg	_	_
6	wire	wire	VERB	VB	VerbForm=Inf	0	root	_	_
7	tap	tap	NOUN	NN	Number=Sing	10	compound	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
9	communication	communication	NOUN	NN	Number=Sing	10	compound	_	_
10	links	link	NOUN	NNS	Number=Plur	6	dobj	_	_
11	leading	lead	VERB	VBG	VerbForm=Ger	10	acl	_	_
12	into	into	ADP	IN	_	13	case	_	_
13	Mordor	Mordor	PROPN	NNP	Number=Sing	11	nmod	_	_
14	along	along	ADP	IN	_	16	case	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	16	det	_	_
16	pass	pass	NOUN	NN	Number=Sing	11	nmod	_	_
17	of	of	ADP	IN	_	19	case	_	_
18	Cirith	Cirith	PROPN	NNP	Number=Sing	19	name	_	_
19	Ungol	Ungol	PROPN	NNP	Number=Sing	16	nmod	_	_
20	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test32': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GONMIL],[MOR],057)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test32']['sents']['0']:
            print(return_dict['test32']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test32']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],057)",str(return_dict['test32']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],057)","noevent"]
            print("test32 Failed")
    except:
        print("test32 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test32']['sents']['0']:
        verbs=return_dict['test32']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test32']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test32']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test32']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test32']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test32():
    text="""Soldiers from Gondor have cordoned off for construction the roads leading into Mordor 
along the pass of Cirith Ungol.
"""
    parse="""1	Soldiers	soldier	NOUN	NNS	Number=Plur	5	nsubj	_	_
2	from	from	ADP	IN	_	3	case	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	1	nmod	_	_
4	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	aux	_	_
5	cordoned	cordon	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
6	off	off	ADP	RP	_	8	case	_	_
7	for	for	ADP	IN	_	8	case	_	_
8	construction	construction	NOUN	NN	Number=Sing	5	nmod	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	roads	road	NOUN	NNS	Number=Plur	5	dobj	_	_
11	leading	lead	VERB	VBG	VerbForm=Ger	10	acl	_	_
12	into	into	ADP	IN	_	13	case	_	_
13	Mordor	Mordor	PROPN	NNP	Number=Sing	11	nmod	_	_
14	along	along	ADP	IN	_	16	case	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	16	det	_	_
16	pass	pass	NOUN	NN	Number=Sing	11	nmod	_	_
17	of	of	ADP	IN	_	19	case	_	_
18	Cirith	Cirith	PROPN	NNP	Number=Sing	19	name	_	_
19	Ungol	Ungol	PROPN	NNP	Number=Sing	16	nmod	_	_
20	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test33': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GONMIL],[MOR],144)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test33']['sents']['0']:
            print(return_dict['test33']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test33']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],144)",str(return_dict['test33']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GONMIL],[MOR],144)","noevent"]
            print("test33 Failed")
    except:
        print("test33 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test33']['sents']['0']:
        verbs=return_dict['test33']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test33']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test33']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test33']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test33']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test33():
    text="""Arnor cleric is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	2	name	_	_
2	cleric	cleric	NOUN	NN	Number=Sing	4	nsubj	_	_
3	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	cop	_	_
4	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
5	to	to	PART	TO	_	6	mark	_	_
6	restore	restore	VERB	VB	VerbForm=Inf	4	xcomp	_	_
7	full	full	ADJ	JJ	Degree=Pos	9	amod	_	_
8	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	9	amod	_	_
9	ties	tie	NOUN	NNS	Number=Plur	6	dobj	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Gondor	Gondor	PROPN	NNP	Number=Sing	6	nmod	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	6	nmod:tmod	_	_
15	after	after	ADP	IN	_	16	case	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	6	nmod	_	_
17	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
18	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
19	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
20	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test34': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNREL],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test34']['sents']['0']:
            print(return_dict['test34']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test34']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNREL],[GON],050)",str(return_dict['test34']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNREL],[GON],050)","noevent"]
            print("test34 Failed")
    except:
        print("test34 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test34']['sents']['0']:
        verbs=return_dict['test34']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test34']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test34']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test34']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test34']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test34():
    text="""MSF Arnor is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	MSF	MSF	PROPN	NNP	Number=Sing	2	name	_	_
2	Arnor	Arnor	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	cop	_	_
4	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
5	to	to	PART	TO	_	6	mark	_	_
6	restore	restore	VERB	VB	VerbForm=Inf	4	xcomp	_	_
7	full	full	ADJ	JJ	Degree=Pos	9	amod	_	_
8	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	9	amod	_	_
9	ties	tie	NOUN	NNS	Number=Plur	6	dobj	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Gondor	Gondor	PROPN	NNP	Number=Sing	6	nmod	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	6	nmod:tmod	_	_
15	after	after	ADP	IN	_	16	case	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	6	nmod	_	_
17	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
18	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
19	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
20	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test35': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([NGOARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test35']['sents']['0']:
            print(return_dict['test35']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test35']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([NGOARN],[GON],050)",str(return_dict['test35']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([NGOARN],[GON],050)","noevent"]
            print("test35 Failed")
    except:
        print("test35 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test35']['sents']['0']:
        verbs=return_dict['test35']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test35']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test35']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test35']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test35']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test35():
    text="""An MSF Arnor diplomat is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	An	a	DET	DT	Definite=Ind|PronType=Art	4	det	_	_
2	MSF	MSF	PROPN	NNP	Number=Sing	3	compound	_	_
3	Arnor	Arnor	PROPN	NNP	Number=Sing	4	compound	_	_
4	diplomat	diplomat	NOUN	NN	Number=Sing	6	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Gondor	Gondor	PROPN	NNP	Number=Sing	8	nmod	_	_
14	almost	almost	ADV	RB	_	15	advmod	_	_
15	five	five	NUM	CD	NumType=Card	16	nummod	_	_
16	years	year	NOUN	NNS	Number=Plur	8	nmod:tmod	_	_
17	after	after	ADP	IN	_	18	case	_	_
18	crowds	crowd	NOUN	NNS	Number=Plur	8	nmod	_	_
19	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	18	acl	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	embassy	embassy	NOUN	NN	Number=Sing	19	dobj	_	_
22	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test36': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([NGOARNGOV],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test36']['sents']['0']:
            print(return_dict['test36']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test36']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([NGOARNGOV],[GON],050)",str(return_dict['test36']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([NGOARNGOV],[GON],050)","noevent"]
            print("test36 Failed")
    except:
        print("test36 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test36']['sents']['0']:
        verbs=return_dict['test36']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test36']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test36']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test36']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test36']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test36():
    text="""Arnor is about to restore full diplomatic ties with the Gondor main opposition group 
almost five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	14	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
11	Gondor	Gondor	PROPN	NNP	Number=Sing	14	compound	_	_
12	main	main	ADJ	JJ	Degree=Pos	14	amod	_	_
13	opposition	opposition	NOUN	NN	Number=Sing	14	compound	_	_
14	group	group	NOUN	NN	Number=Sing	8	nmod	_	_
15	almost	almost	ADV	RB	_	16	advmod	_	_
16	five	five	NUM	CD	NumType=Card	17	nummod	_	_
17	years	year	NOUN	NNS	Number=Plur	19	nmod:npmod	_	_
18	after	after	ADP	IN	_	19	case	_	_
19	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
20	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	19	acl	_	_
21	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
22	embassy	embassy	NOUN	NN	Number=Sing	20	dobj	_	_
23	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test37': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GONMOP],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test37']['sents']['0']:
            print(return_dict['test37']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test37']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONMOP],050)",str(return_dict['test37']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONMOP],050)","noevent"]
            print("test37 Failed")
    except:
        print("test37 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test37']['sents']['0']:
        verbs=return_dict['test37']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test37']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test37']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test37']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test37']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test37():
    text="""Arnor is about to restore full diplomatic ties with Gondor's government 
almost five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	12	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	12	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	government	government	NOUN	NN	Number=Sing	5	nmod	_	_
13	almost	almost	ADV	RB	_	14	advmod	_	_
14	five	five	NUM	CD	NumType=Card	15	nummod	_	_
15	years	year	NOUN	NNS	Number=Plur	17	nmod:npmod	_	_
16	after	after	ADP	IN	_	17	case	_	_
17	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
18	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	17	acl	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	18	dobj	_	_
21	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test38': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GONGOV],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test38']['sents']['0']:
            print(return_dict['test38']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test38']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONGOV],050)",str(return_dict['test38']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONGOV],050)","noevent"]
            print("test38 Failed")
    except:
        print("test38 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test38']['sents']['0']:
        verbs=return_dict['test38']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test38']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test38']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test38']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test38']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test38():
    text="""Arnor is about to restore full diplomatic ties with Gondor's main opposition group 
almost five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	14	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	14	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	main	main	ADJ	JJ	Degree=Pos	14	amod	_	_
13	opposition	opposition	NOUN	NN	Number=Sing	14	compound	_	_
14	group	group	NOUN	NN	Number=Sing	5	nmod	_	_
15	almost	almost	ADV	RB	_	16	advmod	_	_
16	five	five	NUM	CD	NumType=Card	17	nummod	_	_
17	years	year	NOUN	NNS	Number=Plur	19	nmod:npmod	_	_
18	after	after	ADP	IN	_	19	case	_	_
19	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
20	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	19	acl	_	_
21	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
22	embassy	embassy	NOUN	NN	Number=Sing	20	dobj	_	_
23	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test39': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GONMOP],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test39']['sents']['0']:
            print(return_dict['test39']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test39']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONMOP],050)",str(return_dict['test39']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONMOP],050)","noevent"]
            print("test39 Failed")
    except:
        print("test39 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test39']['sents']['0']:
        verbs=return_dict['test39']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test39']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test39']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test39']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test39']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test39():
    text="""Human rights activists in Arnor are about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Human	human	ADJ	JJ	Degree=Pos	3	amod	_	_
2	rights	rights	NOUN	NNS	Number=Plur	3	compound	_	_
3	activists	activist	NOUN	NNS	Number=Plur	7	nsubj	_	_
4	in	in	ADP	IN	_	5	case	_	_
5	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nmod	_	_
6	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	7	cop	_	_
7	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
8	to	to	PART	TO	_	9	mark	_	_
9	restore	restore	VERB	VB	VerbForm=Inf	7	xcomp	_	_
10	full	full	ADJ	JJ	Degree=Pos	12	amod	_	_
11	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	12	amod	_	_
12	ties	tie	NOUN	NNS	Number=Plur	9	dobj	_	_
13	with	with	ADP	IN	_	14	case	_	_
14	Gondor	Gondor	PROPN	NNP	Number=Sing	9	nmod	_	_
15	almost	almost	ADV	RB	_	16	advmod	_	_
16	five	five	NUM	CD	NumType=Card	17	nummod	_	_
17	years	year	NOUN	NNS	Number=Plur	9	nmod:tmod	_	_
18	after	after	ADP	IN	_	19	case	_	_
19	crowds	crowd	NOUN	NNS	Number=Plur	9	nmod	_	_
20	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	19	acl	_	_
21	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
22	embassy	embassy	NOUN	NN	Number=Sing	20	dobj	_	_
23	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test40': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNOPP],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test40']['sents']['0']:
            print(return_dict['test40']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test40']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNOPP],[GON],050)",str(return_dict['test40']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNOPP],[GON],050)","noevent"]
            print("test40 Failed")
    except:
        print("test40 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test40']['sents']['0']:
        verbs=return_dict['test40']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test40']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test40']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test40']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test40']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test40():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test41': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test41']['sents']['0']:
            print(return_dict['test41']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test41']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test41']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test41 Failed")
    except:
        print("test41 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test41']['sents']['0']:
        verbs=return_dict['test41']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test41']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test41']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test41']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test41']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test41():
    text="""The Calenardhon government condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	name	_	_
3	government	government	NOUN	NN	Number=Sing	4	nsubj	_	_
4	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	attack	attack	NOUN	NN	Number=Sing	4	dobj	_	_
7	by	by	ADP	IN	_	9	case	_	_
8	Osgiliath	Osgiliath	DET	DT	_	9	det	_	_
9	soldiers	soldier	NOUN	NNS	Number=Plur	6	nmod	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	south	south	ADV	RB	_	12	advmod	_	_
12	Ithilen	Ithilen	PROPN	NNP	Number=Sing	9	nmod	_	_
13	on	on	ADP	IN	_	14	case	_	_
14	Thursday	Thursday	PROPN	NNP	Number=Sing	9	nmod	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test42': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test42']['sents']['0']:
            print(return_dict['test42']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test42']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)",str(return_dict['test42']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)","noevent"]
            print("test42 Failed")
    except:
        print("test42 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test42']['sents']['0']:
        verbs=return_dict['test42']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test42']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test42']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test42']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test42']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test42():
    text="""Arnor security officials are about to restore full diplomatic 
ties with Gondor police. 
"""
    parse="""1	Arnor	Arnor	ADJ	JJ	Degree=Pos	3	amod	_	_
2	security	security	NOUN	NN	Number=Sing	3	compound	_	_
3	officials	official	NOUN	NNS	Number=Plur	5	nsubj	_	_
4	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	cop	_	_
5	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
6	to	to	PART	TO	_	7	mark	_	_
7	restore	restore	VERB	VB	VerbForm=Inf	5	xcomp	_	_
8	full	full	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	7	dobj	_	_
11	with	with	ADP	IN	_	13	case	_	_
12	Gondor	Gondor	PROPN	NNP	Number=Sing	13	compound	_	_
13	police	police	NOUN	NNS	Number=Plur	10	nmod	_	_
14	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test43': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNGOV],[GONCOP],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test43']['sents']['0']:
            print(return_dict['test43']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test43']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[GONCOP],050)",str(return_dict['test43']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[GONCOP],050)","noevent"]
            print("test43 Failed")
    except:
        print("test43 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test43']['sents']['0']:
        verbs=return_dict['test43']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test43']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test43']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test43']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test43']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test43():
    text="""White House security officials are about to restore full diplomatic 
ties with Minas Tirith border police. 
"""
    parse="""1	White	White	PROPN	NNP	Number=Sing	2	compound	_	_
2	House	House	PROPN	NNP	Number=Sing	4	compound	_	_
3	security	security	NOUN	NN	Number=Sing	4	compound	_	_
4	officials	official	NOUN	NNS	Number=Plur	6	nsubj	_	_
5	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	16	case	_	_
13	Minas	Minas	PROPN	NNP	Number=Sing	16	compound	_	_
14	Tirith	Tirith	PROPN	NNP	Number=Sing	16	compound	_	_
15	border	border	NOUN	NN	Number=Sing	16	compound	_	_
16	police	police	NOUN	NN	Number=Sing	11	nmod	_	_
17	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test44': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAGOV],[GONCOP],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test44']['sents']['0']:
            print(return_dict['test44']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test44']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GONCOP],050)",str(return_dict['test44']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GONCOP],050)","noevent"]
            print("test44 Failed")
    except:
        print("test44 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test44']['sents']['0']:
        verbs=return_dict['test44']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test44']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test44']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test44']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test44']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test44():
    text="""The Calenardhon government condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	name	_	_
3	government	government	NOUN	NN	Number=Sing	4	nsubj	_	_
4	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	attack	attack	NOUN	NN	Number=Sing	4	dobj	_	_
7	by	by	ADP	IN	_	9	case	_	_
8	Osgiliath	Osgiliath	DET	DT	_	9	det	_	_
9	soldiers	soldier	NOUN	NNS	Number=Plur	6	nmod	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	south	south	ADV	RB	_	12	advmod	_	_
12	Ithilen	Ithilen	PROPN	NNP	Number=Sing	9	nmod	_	_
13	on	on	ADP	IN	_	14	case	_	_
14	Thursday	Thursday	PROPN	NNP	Number=Sing	9	nmod	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test45': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test45']['sents']['0']:
            print(return_dict['test45']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test45']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)",str(return_dict['test45']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)","noevent"]
            print("test45 Failed")
    except:
        print("test45 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test45']['sents']['0']:
        verbs=return_dict['test45']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test45']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test45']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test45']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test45']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test45():
    text="""The Calenardhon government condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	name	_	_
3	government	government	NOUN	NN	Number=Sing	4	nsubj	_	_
4	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	attack	attack	NOUN	NN	Number=Sing	4	dobj	_	_
7	by	by	ADP	IN	_	9	case	_	_
8	Osgiliath	Osgiliath	DET	DT	_	9	det	_	_
9	soldiers	soldier	NOUN	NNS	Number=Plur	6	nmod	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	south	south	ADV	RB	_	12	advmod	_	_
12	Ithilen	Ithilen	PROPN	NNP	Number=Sing	9	nmod	_	_
13	on	on	ADP	IN	_	14	case	_	_
14	Thursday	Thursday	PROPN	NNP	Number=Sing	9	nmod	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test46': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test46']['sents']['0']:
            print(return_dict['test46']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test46']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)",str(return_dict['test46']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)","noevent"]
            print("test46 Failed")
    except:
        print("test46 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test46']['sents']['0']:
        verbs=return_dict['test46']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test46']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test46']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test46']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test46']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test46():
    text="""The Calenardhon Ministry of Silly Walks condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	compound	_	_
3	Ministry	Ministry	PROPN	NNP	Number=Sing	7	nsubj	_	_
4	of	of	ADP	IN	_	6	case	_	_
5	Silly	Silly	PROPN	NNP	Number=Sing	6	name	_	_
6	Walks	walks	PROPN	NNP	Number=Sing	3	nmod	_	_
7	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	an	a	DET	DT	Definite=Ind|PronType=Art	9	det	_	_
9	attack	attack	NOUN	NN	Number=Sing	7	dobj	_	_
10	by	by	ADP	IN	_	12	case	_	_
11	Osgiliath	Osgiliath	DET	DT	_	12	det	_	_
12	soldiers	soldier	NOUN	NNS	Number=Plur	9	nmod	_	_
13	in	in	ADP	IN	_	15	case	_	_
14	south	south	ADV	RB	_	15	advmod	_	_
15	Ithilen	Ithilen	PROPN	NNP	Number=Sing	12	nmod	_	_
16	on	on	ADP	IN	_	17	case	_	_
17	Thursday	Thursday	PROPN	NNP	Number=Sing	12	nmod	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test47': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test47']['sents']['0']:
            print(return_dict['test47']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test47']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)",str(return_dict['test47']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)","noevent"]
            print("test47 Failed")
    except:
        print("test47 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test47']['sents']['0']:
        verbs=return_dict['test47']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test47']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test47']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test47']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test47']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test47():
    text="""The Calenardhon Minister of Silly Walks condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	7	nsubj	_	_
4	of	of	ADP	IN	_	6	case	_	_
5	Silly	Silly	PROPN	NNP	Number=Sing	6	name	_	_
6	Walks	walks	PROPN	NNP	Number=Sing	3	nmod	_	_
7	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	an	a	DET	DT	Definite=Ind|PronType=Art	9	det	_	_
9	attack	attack	NOUN	NN	Number=Sing	7	dobj	_	_
10	by	by	ADP	IN	_	12	case	_	_
11	Osgiliath	Osgiliath	DET	DT	_	12	det	_	_
12	soldiers	soldier	NOUN	NNS	Number=Plur	9	nmod	_	_
13	in	in	ADP	IN	_	15	case	_	_
14	south	south	ADV	RB	_	15	advmod	_	_
15	Ithilen	Ithilen	PROPN	NNP	Number=Sing	12	nmod	_	_
16	on	on	ADP	IN	_	17	case	_	_
17	Thursday	Thursday	PROPN	NNP	Number=Sing	12	nmod	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test48': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test48']['sents']['0']:
            print(return_dict['test48']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test48']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)",str(return_dict['test48']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)","noevent"]
            print("test48 Failed")
    except:
        print("test48 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test48']['sents']['0']:
        verbs=return_dict['test48']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test48']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test48']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test48']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test48']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test48():
    text="""The human rights activists of Amnesty International are about to restore 
full diplomatic ties with Gondor. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	human	human	ADJ	JJ	Degree=Pos	4	amod	_	_
3	rights	rights	NOUN	NNS	Number=Plur	4	compound	_	_
4	activists	activist	NOUN	NNS	Number=Plur	9	nsubj	_	_
5	of	of	ADP	IN	_	7	case	_	_
6	Amnesty	Amnesty	PROPN	NNP	Number=Sing	7	compound	_	_
7	International	International	PROPN	NNP	Number=Sing	4	nmod	_	_
8	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	9	cop	_	_
9	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
10	to	to	PART	TO	_	11	mark	_	_
11	restore	restore	VERB	VB	VerbForm=Inf	9	xcomp	_	_
12	full	full	ADJ	JJ	Degree=Pos	14	amod	_	_
13	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	14	amod	_	_
14	ties	tie	NOUN	NNS	Number=Plur	11	dobj	_	_
15	with	with	ADP	IN	_	16	case	_	_
16	Gondor	Gondor	PROPN	NNP	Number=Sing	11	nmod	_	_
17	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test49': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([NGMOPP],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test49']['sents']['0']:
            print(return_dict['test49']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test49']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([NGMOPP],[GON],050)",str(return_dict['test49']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([NGMOPP],[GON],050)","noevent"]
            print("test49 Failed")
    except:
        print("test49 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test49']['sents']['0']:
        verbs=return_dict['test49']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test49']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test49']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test49']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test49']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test49():
    text="""Washington security officials are about to restore full diplomatic 
ties with Gondor. 
"""
    parse="""1	Washington	Washington	PROPN	NNP	Number=Sing	3	compound	_	_
2	security	security	NOUN	NN	Number=Sing	3	compound	_	_
3	officials	official	NOUN	NNS	Number=Plur	5	nsubj	_	_
4	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	cop	_	_
5	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
6	to	to	PART	TO	_	7	mark	_	_
7	restore	restore	VERB	VB	VerbForm=Inf	5	xcomp	_	_
8	full	full	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	7	dobj	_	_
11	with	with	ADP	IN	_	12	case	_	_
12	Gondor	Gondor	PROPN	NNP	Number=Sing	7	nmod	_	_
13	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test50': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAGOV],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test50']['sents']['0']:
            print(return_dict['test50']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test50']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)",str(return_dict['test50']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)","noevent"]
            print("test50 Failed")
    except:
        print("test50 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test50']['sents']['0']:
        verbs=return_dict['test50']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test50']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test50']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test50']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test50']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test50():
    text="""White House security officials are about to restore full diplomatic 
ties with Gondor. 
"""
    parse="""1	White	White	PROPN	NNP	Number=Sing	2	compound	_	_
2	House	House	PROPN	NNP	Number=Sing	4	compound	_	_
3	security	security	NOUN	NN	Number=Sing	4	compound	_	_
4	officials	official	NOUN	NNS	Number=Plur	6	nsubj	_	_
5	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Gondor	Gondor	PROPN	NNP	Number=Sing	8	nmod	_	_
14	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test51': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAGOV],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test51']['sents']['0']:
            print(return_dict['test51']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test51']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)",str(return_dict['test51']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)","noevent"]
            print("test51 Failed")
    except:
        print("test51 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test51']['sents']['0']:
        verbs=return_dict['test51']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test51']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test51']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test51']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test51']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test51():
    text="""The Quibbler government newspaper is about to restore full diplomatic 
ties with Gondor now. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	Quibbler	Quibbler	PROPN	NNP	Number=Sing	4	compound	_	_
3	government	government	NOUN	NN	Number=Sing	4	compound	_	_
4	newspaper	newspaper	NOUN	NN	Number=Sing	6	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Gondor	Gondor	PROPN	NNP	Number=Sing	8	nmod	_	_
14	now	now	ADV	RB	_	8	advmod	_	_
15	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test52': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HGWGOVMED],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test52']['sents']['0']:
            print(return_dict['test52']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test52']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HGWGOVMED],[GON],050)",str(return_dict['test52']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HGWGOVMED],[GON],050)","noevent"]
            print("test52 Failed")
    except:
        print("test52 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test52']['sents']['0']:
        verbs=return_dict['test52']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test52']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test52']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test52']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test52']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test52():
    text="""Arnor is about to restore full diplomatic ties with Gondor's main opposition groups 
almost five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	14	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	14	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	main	main	ADJ	JJ	Degree=Pos	14	amod	_	_
13	opposition	opposition	NOUN	NN	Number=Sing	14	compound	_	_
14	groups	group	NOUN	NNS	Number=Plur	5	nmod	_	_
15	almost	almost	ADV	RB	_	16	advmod	_	_
16	five	five	NUM	CD	NumType=Card	17	nummod	_	_
17	years	year	NOUN	NNS	Number=Plur	19	nmod:npmod	_	_
18	after	after	ADP	IN	_	19	case	_	_
19	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
20	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	19	acl	_	_
21	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
22	embassy	embassy	NOUN	NN	Number=Sing	20	dobj	_	_
23	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test53': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GONMOP],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test53']['sents']['0']:
            print(return_dict['test53']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test53']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONMOP],050)",str(return_dict['test53']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONMOP],050)","noevent"]
            print("test53 Failed")
    except:
        print("test53 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test53']['sents']['0']:
        verbs=return_dict['test53']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test53']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test53']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test53']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test53']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test53():
    text="""Arnor is about to restore full diplomatic ties with Gondor's golden geese 
almost five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	13	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	13	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	golden	golden	ADJ	JJ	Degree=Pos	13	amod	_	_
13	geese	geese	NOUN	NN	Number=Sing	5	nmod	_	_
14	almost	almost	ADV	RB	_	15	advmod	_	_
15	five	five	NUM	CD	NumType=Card	16	nummod	_	_
16	years	year	NOUN	NNS	Number=Plur	18	nmod:npmod	_	_
17	after	after	ADP	IN	_	18	case	_	_
18	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
19	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	18	acl	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	embassy	embassy	NOUN	NN	Number=Sing	19	dobj	_	_
22	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test54': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GONGGS],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test54']['sents']['0']:
            print(return_dict['test54']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test54']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONGGS],050)",str(return_dict['test54']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GONGGS],050)","noevent"]
            print("test54 Failed")
    except:
        print("test54 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test54']['sents']['0']:
        verbs=return_dict['test54']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test54']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test54']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test54']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test54']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test54():
    text="""Arnor is about to restore full diplomatic ties with Gondor's polices 
almost five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	12	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	12	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	polices	polex	NOUN	NNS	Number=Plur	5	nmod	_	_
13	almost	almost	ADV	RB	_	14	advmod	_	_
14	five	five	NUM	CD	NumType=Card	15	nummod	_	_
15	years	year	NOUN	NNS	Number=Plur	17	nmod:npmod	_	_
16	after	after	ADP	IN	_	17	case	_	_
17	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
18	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	17	acl	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	18	dobj	_	_
21	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test55': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test55']['sents']['0']:
            print(return_dict['test55']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test55']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test55']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test55 Failed")
    except:
        print("test55 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test55']['sents']['0']:
        verbs=return_dict['test55']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test55']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test55']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test55']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test55']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test55():
    text="""West German world government activists are about to restore 
full diplomatic ties with human rights activists of Gonzo GMO. 
"""
    parse="""1	West	West	ADJ	JJ	Degree=Pos	5	amod	_	_
2	German	german	ADJ	JJ	Degree=Pos	3	amod	_	_
3	world	world	NOUN	NN	Number=Sing	5	compound	_	_
4	government	government	NOUN	NN	Number=Sing	5	compound	_	_
5	activists	activist	NOUN	NNS	Number=Plur	7	nsubj	_	_
6	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	7	cop	_	_
7	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
8	to	to	PART	TO	_	9	mark	_	_
9	restore	restore	VERB	VB	VerbForm=Inf	7	xcomp	_	_
10	full	full	ADJ	JJ	Degree=Pos	12	amod	_	_
11	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	12	amod	_	_
12	ties	tie	NOUN	NNS	Number=Plur	9	dobj	_	_
13	with	with	ADP	IN	_	16	case	_	_
14	human	human	ADJ	JJ	Degree=Pos	16	amod	_	_
15	rights	rights	NOUN	NNS	Number=Plur	16	compound	_	_
16	activists	activist	NOUN	NNS	Number=Plur	12	nmod	_	_
17	of	of	ADP	IN	_	19	case	_	_
18	Gonzo	Gonzo	PROPN	NNP	Number=Sing	19	name	_	_
19	GMO	GMO	PROPN	NNP	Number=Sing	16	nmod	_	_
20	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test56': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GMWGOVWGO],[GONGMOOPP],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test56']['sents']['0']:
            print(return_dict['test56']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test56']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GMWGOVWGO],[GONGMOOPP],050)",str(return_dict['test56']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GMWGOVWGO],[GONGMOOPP],050)","noevent"]
            print("test56 Failed")
    except:
        print("test56 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test56']['sents']['0']:
        verbs=return_dict['test56']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test56']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test56']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test56']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test56']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test56():
    text="""White House security officials are about to restore full diplomatic 
ties with Gondor and Arnor. 
"""
    parse="""1	White	White	PROPN	NNP	Number=Sing	2	compound	_	_
2	House	House	PROPN	NNP	Number=Sing	4	compound	_	_
3	security	security	NOUN	NN	Number=Sing	4	compound	_	_
4	officials	official	NOUN	NNS	Number=Plur	6	nsubj	_	_
5	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Gondor	Gondor	PROPN	NNP	Number=Sing	11	nmod	_	_
14	and	and	CONJ	CC	_	13	cc	_	_
15	Arnor	Arnor	PROPN	NNP	Number=Sing	13	conj	_	_
16	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test57': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAGOV],[GON],050)\n([USAGOV],[ARN],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test57']['sents']['0']:
            print(return_dict['test57']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test57']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)\n([USAGOV],[ARN],050)",str(return_dict['test57']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)\n([USAGOV],[ARN],050)","noevent"]
            print("test57 Failed")
    except:
        print("test57 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test57']['sents']['0']:
        verbs=return_dict['test57']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test57']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test57']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test57']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test57']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test57():
    text="""Arnor former security officials are about to restore full diplomatic 
ties with former Gondor prosecutors. 
"""
    parse="""1	Arnor	Arnor	ADP	IN	_	4	case	_	_
2	former	former	ADJ	JJ	Degree=Pos	4	amod	_	_
3	security	security	NOUN	NN	Number=Sing	4	compound	_	_
4	officials	official	NOUN	NNS	Number=Plur	6	nsubj	_	_
5	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	15	case	_	_
13	former	former	ADJ	JJ	Degree=Pos	15	amod	_	_
14	Gondor	Gondor	PROPN	NNP	Number=Sing	15	compound	_	_
15	prosecutors	prosecutor	NOUN	NNS	Number=Plur	11	nmod	_	_
16	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test58': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNGOV],[GONJUD],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test58']['sents']['0']:
            print(return_dict['test58']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test58']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[GONJUD],050)",str(return_dict['test58']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[GONJUD],050)","noevent"]
            print("test58 Failed")
    except:
        print("test58 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test58']['sents']['0']:
        verbs=return_dict['test58']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test58']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test58']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test58']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test58']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test58():
    text="""Former security officials in White House are about to restore full 
diplomatic ties with former Minas Tirith border police. 
"""
    parse="""1	Former	former	ADJ	JJ	Degree=Pos	3	amod	_	_
2	security	security	NOUN	NN	Number=Sing	3	compound	_	_
3	officials	official	NOUN	NNS	Number=Plur	8	nsubj	_	_
4	in	in	ADP	IN	_	6	case	_	_
5	White	White	PROPN	NNP	Number=Sing	6	compound	_	_
6	House	House	PROPN	NNP	Number=Sing	3	nmod	_	_
7	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	8	cop	_	_
8	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
9	to	to	PART	TO	_	10	mark	_	_
10	restore	restore	VERB	VB	VerbForm=Inf	8	xcomp	_	_
11	full	full	ADJ	JJ	Degree=Pos	13	amod	_	_
12	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	13	amod	_	_
13	ties	tie	NOUN	NNS	Number=Plur	10	dobj	_	_
14	with	with	ADP	IN	_	19	case	_	_
15	former	former	ADJ	JJ	Degree=Pos	19	amod	_	_
16	Minas	Minas	PROPN	NNP	Number=Sing	19	compound	_	_
17	Tirith	Tirith	PROPN	NNP	Number=Sing	19	compound	_	_
18	border	border	NOUN	NN	Number=Sing	19	compound	_	_
19	police	police	NOUN	NN	Number=Sing	13	nmod	_	_
20	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test59': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAGOV],[GONCOP],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test59']['sents']['0']:
            print(return_dict['test59']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test59']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GONCOP],050)",str(return_dict['test59']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GONCOP],050)","noevent"]
            print("test59 Failed")
    except:
        print("test59 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test59']['sents']['0']:
        verbs=return_dict['test59']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test59']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test59']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test59']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test59']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test59():
    text="""Old foe Gondor and Osgiliath have renewed diplomatic ties after a 
12-year break in a step that holds advantages for both major 
powers. 
"""
    parse="""1	Old	old	PROPN	NNP	Number=Sing	3	compound	_	_
2	foe	foe	PROPN	NNP	Number=Sing	3	compound	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	7	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	3	conj	_	_
6	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	7	aux	_	_
7	renewed	renew	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
8	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	9	amod	_	_
9	ties	tie	NOUN	NNS	Number=Plur	7	dobj	_	_
10	after	after	ADP	IN	_	13	case	_	_
11	a	a	DET	DT	Definite=Ind|PronType=Art	13	det	_	_
12	12-year	12-year	ADJ	JJ	Degree=Pos	13	amod	_	_
13	break	break	NOUN	NN	Number=Sing	7	nmod	_	_
14	in	in	ADP	IN	_	16	case	_	_
15	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
16	step	step	NOUN	NN	Number=Sing	7	nmod	_	_
17	that	that	PRON	WDT	PronType=Rel	18	nsubj	_	_
18	holds	hold	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	16	acl:relcl	_	_
19	advantages	advantage	NOUN	NNS	Number=Plur	18	dobj	_	_
20	for	for	ADP	IN	_	23	case	_	_
21	both	both	DET	DT	_	23	det	_	_
22	major	major	ADJ	JJ	Degree=Pos	23	amod	_	_
23	powers	power	NOUN	NNS	Number=Plur	18	nmod	_	_
24	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test60': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[OSG],050)\n([OSG],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test60']['sents']['0']:
            print(return_dict['test60']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test60']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],050)\n([OSG],[GON],050)",str(return_dict['test60']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],050)\n([OSG],[GON],050)","noevent"]
            print("test60 Failed")
    except:
        print("test60 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test60']['sents']['0']:
        verbs=return_dict['test60']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test60']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test60']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test60']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test60']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test60():
    text="""Mordor, Rohan, Arnor and Bree welcomed their resumption of formal 
diplomatic ties with Osgiliath after a 12-year rift. 
"""
    parse="""1	Mordor	Mordor	PROPN	NNP	Number=Sing	8	nsubj	_	_
2	,	,	PUNCT	,	_	1	punct	_	_
3	Rohan	Rohan	PROPN	NNP	Number=Sing	1	conj	_	_
4	,	,	PUNCT	,	_	1	punct	_	_
5	Arnor	Arnor	PROPN	NNP	Number=Sing	1	conj	_	_
6	and	and	CONJ	CC	_	1	cc	_	_
7	Bree	Bree	PROPN	NNP	Number=Sing	1	conj	_	_
8	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	10	nmod:poss	_	_
10	resumption	resumption	NOUN	NN	Number=Sing	8	dobj	_	_
11	of	of	ADP	IN	_	14	case	_	_
12	formal	formal	ADJ	JJ	Degree=Pos	14	amod	_	_
13	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	14	amod	_	_
14	ties	tie	NOUN	NNS	Number=Plur	10	nmod	_	_
15	with	with	ADP	IN	_	16	case	_	_
16	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	14	nmod	_	_
17	after	after	ADP	IN	_	20	case	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	12-year	12-year	ADJ	JJ	Degree=Pos	20	amod	_	_
20	rift	rift	NOUN	NN	Number=Sing	8	nmod	_	_
21	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test61': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([MOR],[OSG],050)\n([ROH],[OSG],050)\n([ARN],[OSG],050)\n([BRE],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test61']['sents']['0']:
            print(return_dict['test61']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test61']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[OSG],050)\n([ROH],[OSG],050)\n([ARN],[OSG],050)\n([BRE],[OSG],050)",str(return_dict['test61']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[OSG],050)\n([ROH],[OSG],050)\n([ARN],[OSG],050)\n([BRE],[OSG],050)","noevent"]
            print("test61 Failed")
    except:
        print("test61 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test61']['sents']['0']:
        verbs=return_dict['test61']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test61']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test61']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test61']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test61']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test61():
    text="""Arnor and Gondor welcome a resumption of formal diplomatic ties with  
Osgiliath after a 12-year rift, the primary official news agency said 
on Thursday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	4	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	1	conj	_	_
4	welcome	welcome	VERB	VB	VerbForm=Inf	0	root	_	_
5	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	resumption	resumption	NOUN	NN	Number=Sing	4	dobj	_	_
7	of	of	ADP	IN	_	10	case	_	_
8	formal	formal	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	6	nmod	_	_
11	with	with	ADP	IN	_	12	case	_	_
12	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	10	nmod	_	_
13	after	after	ADP	IN	_	16	case	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	12-year	12-year	ADJ	JJ	Degree=Pos	16	amod	_	_
16	rift	rift	NOUN	NN	Number=Sing	4	nmod	_	_
17	,	,	PUNCT	,	_	4	punct	_	_
18	the	the	DET	DT	Definite=Def|PronType=Art	22	det	_	_
19	primary	primary	ADJ	JJ	Degree=Pos	22	amod	_	_
20	official	official	ADJ	JJ	Degree=Pos	22	amod	_	_
21	news	news	NOUN	NN	Number=Sing	22	compound	_	_
22	agency	agency	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Thursday	Thursday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test62': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[OSG],050)\n([GON],[OSG],050)\n([---GOV],[---],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test62']['sents']['0']:
            print(return_dict['test62']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test62']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([GON],[OSG],050)\n([---GOV],[---],010)",str(return_dict['test62']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([GON],[OSG],050)\n([---GOV],[---],010)","noevent"]
            print("test62 Failed")
    except:
        print("test62 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test62']['sents']['0']:
        verbs=return_dict['test62']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test62']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test62']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test62']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test62']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test62():
    text="""Arnor welcomed a resumption of formal diplomatic ties between Gondor 
and Osgiliath after a 12-year rift, the primary official news agency said 
on Thursday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	a	a	DET	DT	Definite=Ind|PronType=Art	4	det	_	_
4	resumption	resumption	NOUN	NN	Number=Sing	2	dobj	_	_
5	of	of	ADP	IN	_	8	case	_	_
6	formal	formal	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	4	nmod	_	_
9	between	between	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	8	nmod	_	_
11	and	and	CONJ	CC	_	10	cc	_	_
12	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	10	conj	_	_
13	after	after	ADP	IN	_	16	case	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	12-year	12-year	ADJ	JJ	Degree=Pos	16	amod	_	_
16	rift	rift	NOUN	NN	Number=Sing	2	nmod	_	_
17	,	,	PUNCT	,	_	2	punct	_	_
18	the	the	DET	DT	Definite=Def|PronType=Art	22	det	_	_
19	primary	primary	ADJ	JJ	Degree=Pos	22	amod	_	_
20	official	official	ADJ	JJ	Degree=Pos	22	amod	_	_
21	news	news	NOUN	NN	Number=Sing	22	compound	_	_
22	agency	agency	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Thursday	Thursday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test63': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)\n([ARN],[OSG],050)\n([---GOV],[---],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test63']['sents']['0']:
            print(return_dict['test63']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test63']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)\n([ARN],[OSG],050)\n([---GOV],[---],010)",str(return_dict['test63']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)\n([ARN],[OSG],050)\n([---GOV],[---],010)","noevent"]
            print("test63 Failed")
    except:
        print("test63 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test63']['sents']['0']:
        verbs=return_dict['test63']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test63']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test63']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test63']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test63']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test63():
    text="""Osgiliath welcomed the resumption of formal  diplomatic ties with 
Mordor, Rohan, Arnor and Bree after a 12-year rift. 
"""
    parse="""1	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcome	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	the	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
4	resumption	resumption	NOUN	NN	Number=Sing	2	dobj	_	_
5	of	of	ADP	IN	_	8	case	_	_
6	formal	formal	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	4	nmod	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Mordor	Mordor	PROPN	NNP	Number=Sing	8	nmod	_	_
11	,	,	PUNCT	,	_	10	punct	_	_
12	Rohan	Rohan	PROPN	NNP	Number=Sing	10	conj	_	_
13	,	,	PUNCT	,	_	10	punct	_	_
14	Arnor	Arnor	PROPN	NNP	Number=Sing	10	conj	_	_
15	and	and	CONJ	CC	_	10	cc	_	_
16	Bree	Bree	PROPN	NNP	Number=Sing	10	conj	_	_
17	after	after	ADP	IN	_	20	case	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	12-year	12-year	ADJ	JJ	Degree=Pos	20	amod	_	_
20	rift	rift	NOUN	NN	Number=Sing	2	nmod	_	_
21	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test64': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([OSG],[MOR],050)\n([OSG],[ROH],050)\n([OSG],[ARN],050)\n([OSG],[BRE],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test64']['sents']['0']:
            print(return_dict['test64']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test64']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[MOR],050)\n([OSG],[ROH],050)\n([OSG],[ARN],050)\n([OSG],[BRE],050)",str(return_dict['test64']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[MOR],050)\n([OSG],[ROH],050)\n([OSG],[ARN],050)\n([OSG],[BRE],050)","noevent"]
            print("test64 Failed")
    except:
        print("test64 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test64']['sents']['0']:
        verbs=return_dict['test64']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test64']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test64']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test64']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test64']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test64():
    text="""Arnor and Gondor welcomed a resumption of formal diplomatic ties
between Eriador and Osgiliath after a 12-year rift, the official news
agency  said on Thursday . 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	4	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	1	conj	_	_
4	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	resumption	resumption	NOUN	NN	Number=Sing	4	dobj	_	_
7	of	of	ADP	IN	_	10	case	_	_
8	formal	formal	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	6	nmod	_	_
11	between	between	ADP	IN	_	12	case	_	_
12	Eriador	Eriador	PROPN	NNP	Number=Sing	10	nmod	_	_
13	and	and	CONJ	CC	_	12	cc	_	_
14	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	12	conj	_	_
15	after	after	ADP	IN	_	18	case	_	_
16	a	a	DET	DT	Definite=Ind|PronType=Art	18	det	_	_
17	12-year	12-year	ADJ	JJ	Degree=Pos	18	amod	_	_
18	rift	rift	NOUN	NN	Number=Sing	4	nmod	_	_
19	,	,	PUNCT	,	_	4	punct	_	_
20	the	the	DET	DT	Definite=Def|PronType=Art	23	det	_	_
21	official	official	ADJ	JJ	Degree=Pos	23	amod	_	_
22	news	news	NOUN	NN	Number=Sing	23	compound	_	_
23	agency	agency	NOUN	NN	Number=Sing	24	nsubj	_	_
24	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	parataxis	_	_
25	on	on	ADP	IN	_	26	case	_	_
26	Thursday	Thursday	PROPN	NNP	Number=Sing	24	nmod	_	_
27	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test65': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[ERI],050)\n([ARN],[OSG],050)\n([GON],[ERI],050)\n([GON],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test65']['sents']['0']:
            print(return_dict['test65']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test65']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[ERI],050)\n([ARN],[OSG],050)\n([GON],[ERI],050)\n([GON],[OSG],050)",str(return_dict['test65']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[ERI],050)\n([ARN],[OSG],050)\n([GON],[ERI],050)\n([GON],[OSG],050)","noevent"]
            print("test65 Failed")
    except:
        print("test65 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test65']['sents']['0']:
        verbs=return_dict['test65']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test65']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test65']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test65']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test65']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test65():
    text="""Mordor, Rohan, Arnor and Bree welcomed a resumption of formal 
diplomatic ties between Gondor and Osgiliath after a 12-year rift, the 
official news agency  said on Thursday . 
"""
    parse="""1	Mordor	Mordor	PROPN	NNP	Number=Sing	8	nsubj	_	_
2	,	,	PUNCT	,	_	1	punct	_	_
3	Rohan	Rohan	PROPN	NNP	Number=Sing	1	conj	_	_
4	,	,	PUNCT	,	_	1	punct	_	_
5	Arnor	Arnor	PROPN	NNP	Number=Sing	1	conj	_	_
6	and	and	CONJ	CC	_	1	cc	_	_
7	Bree	Bree	PROPN	NNP	Number=Sing	1	conj	_	_
8	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	resumption	resumption	NOUN	NN	Number=Sing	8	dobj	_	_
11	of	of	ADP	IN	_	14	case	_	_
12	formal	formal	ADJ	JJ	Degree=Pos	14	amod	_	_
13	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	14	amod	_	_
14	ties	tie	NOUN	NNS	Number=Plur	10	nmod	_	_
15	between	between	ADP	IN	_	16	case	_	_
16	Gondor	Gondor	PROPN	NNP	Number=Sing	14	nmod	_	_
17	and	and	CONJ	CC	_	16	cc	_	_
18	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	16	conj	_	_
19	after	after	ADP	IN	_	22	case	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	12-year	12-year	ADJ	JJ	Degree=Pos	22	amod	_	_
22	rift	rift	NOUN	NN	Number=Sing	8	nmod	_	_
23	,	,	PUNCT	,	_	8	punct	_	_
24	the	the	DET	DT	Definite=Def|PronType=Art	27	det	_	_
25	official	official	ADJ	JJ	Degree=Pos	27	amod	_	_
26	news	news	NOUN	NN	Number=Sing	27	compound	_	_
27	agency	agency	NOUN	NN	Number=Sing	28	nsubj	_	_
28	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	8	parataxis	_	_
29	on	on	ADP	IN	_	30	case	_	_
30	Thursday	Thursday	PROPN	NNP	Number=Sing	28	nmod	_	_
31	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test66': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([MOR],[GON],050)\n([MOR],[OSG],050)\n([ROH],[GON],050)\n([ROH],[OSG],050)\n([ARN],[GON],050)\n([ARN],[OSG],050)\n([BRE],[GON],050)\n([BRE],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test66']['sents']['0']:
            print(return_dict['test66']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test66']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[GON],050)\n([MOR],[OSG],050)\n([ROH],[GON],050)\n([ROH],[OSG],050)\n([ARN],[GON],050)\n([ARN],[OSG],050)\n([BRE],[GON],050)\n([BRE],[OSG],050)",str(return_dict['test66']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[GON],050)\n([MOR],[OSG],050)\n([ROH],[GON],050)\n([ROH],[OSG],050)\n([ARN],[GON],050)\n([ARN],[OSG],050)\n([BRE],[GON],050)\n([BRE],[OSG],050)","noevent"]
            print("test66 Failed")
    except:
        print("test66 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test66']['sents']['0']:
        verbs=return_dict['test66']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test66']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test66']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test66']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test66']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test66():
    text="""Mordor, the Shire, Arnor and Bree welcomed a resumption of formal 
diplomatic ties between Minas Tirith and Osgiliath after a 12-year rift, 
the official news agency  said on Thursday. 
"""
    parse="""1	Mordor	Mordor	PROPN	NNP	Number=Sing	9	nsubj	_	_
2	,	,	PUNCT	,	_	1	punct	_	_
3	the	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
4	Shire	Shire	PROPN	NNP	Number=Sing	1	appos	_	_
5	,	,	PUNCT	,	_	4	punct	_	_
6	Arnor	Arnor	PROPN	NNP	Number=Sing	4	conj	_	_
7	and	and	CONJ	CC	_	4	cc	_	_
8	Bree	Bree	PROPN	NNP	Number=Sing	4	conj	_	_
9	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
10	a	a	DET	DT	Definite=Ind|PronType=Art	11	det	_	_
11	resumption	resumption	NOUN	NN	Number=Sing	9	dobj	_	_
12	of	of	ADP	IN	_	15	case	_	_
13	formal	formal	ADJ	JJ	Degree=Pos	15	amod	_	_
14	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	15	amod	_	_
15	ties	tie	NOUN	NNS	Number=Plur	11	nmod	_	_
16	between	between	ADP	IN	_	18	case	_	_
17	Minas	Minas	PROPN	NNP	Number=Sing	18	name	_	_
18	Tirith	Tirith	PROPN	NNP	Number=Sing	15	nmod	_	_
19	and	and	CONJ	CC	_	18	cc	_	_
20	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	18	conj	_	_
21	after	after	ADP	IN	_	24	case	_	_
22	a	a	DET	DT	Definite=Ind|PronType=Art	24	det	_	_
23	12-year	12-year	ADJ	JJ	Degree=Pos	24	amod	_	_
24	rift	rift	NOUN	NN	Number=Sing	9	nmod	_	_
25	,	,	PUNCT	,	_	9	punct	_	_
26	the	the	DET	DT	Definite=Def|PronType=Art	29	det	_	_
27	official	official	ADJ	JJ	Degree=Pos	29	amod	_	_
28	news	news	NOUN	NN	Number=Sing	29	compound	_	_
29	agency	agency	NOUN	NN	Number=Sing	30	nsubj	_	_
30	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	9	parataxis	_	_
31	on	on	ADP	IN	_	32	case	_	_
32	Thursday	Thursday	PROPN	NNP	Number=Sing	30	nmod	_	_
33	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test67': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([MOR],[GON],050)\n([MOR],[OSG],050)\n([FRO/BIL/SAM],[GON],050)\n([FRO/BIL/SAM],[OSG],050)\n([ARN],[GON],050)\n([ARN],[OSG],050)\n([BRE],[GON],050)\n([BRE],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test67']['sents']['0']:
            print(return_dict['test67']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test67']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[GON],050)\n([MOR],[OSG],050)\n([FRO/BIL/SAM],[GON],050)\n([FRO/BIL/SAM],[OSG],050)\n([ARN],[GON],050)\n([ARN],[OSG],050)\n([BRE],[GON],050)\n([BRE],[OSG],050)",str(return_dict['test67']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[GON],050)\n([MOR],[OSG],050)\n([FRO/BIL/SAM],[GON],050)\n([FRO/BIL/SAM],[OSG],050)\n([ARN],[GON],050)\n([ARN],[OSG],050)\n([BRE],[GON],050)\n([BRE],[OSG],050)","noevent"]
            print("test67 Failed")
    except:
        print("test67 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test67']['sents']['0']:
        verbs=return_dict['test67']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test67']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test67']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test67']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test67']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test67():
    text="""Lawmakers in Arnor and Gondor welcomed a resumption of formal diplomatic ties
with Eriador. 
"""
    parse="""1	Lawmakers	lawmaker	NOUN	NNS	Number=Plur	0	root	_	_
2	in	in	ADP	IN	_	3	case	_	_
3	Arnor	Arnor	PROPN	NNP	Number=Sing	1	nmod	_	_
4	and	and	CONJ	CC	_	1	cc	_	_
5	Gondor	Gondor	PROPN	NNP	Number=Sing	6	nsubj	_	_
6	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	1	conj	_	_
7	a	a	DET	DT	Definite=Ind|PronType=Art	8	det	_	_
8	resumption	resumption	NOUN	NN	Number=Sing	6	dobj	_	_
9	of	of	ADP	IN	_	12	case	_	_
10	formal	formal	ADJ	JJ	Degree=Pos	12	amod	_	_
11	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	12	amod	_	_
12	ties	tie	NOUN	NNS	Number=Plur	8	nmod	_	_
13	with	with	ADP	IN	_	14	case	_	_
14	Eriador	Eriador	PROPN	NNP	Number=Sing	12	nmod	_	_
15	.	.	PUNCT	.	_	1	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test68': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNLEG],[ERI],050)\n([GONLEG],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test68']['sents']['0']:
            print(return_dict['test68']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test68']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNLEG],[ERI],050)\n([GONLEG],[ERI],050)",str(return_dict['test68']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNLEG],[ERI],050)\n([GONLEG],[ERI],050)","noevent"]
            print("test68 Failed")
    except:
        print("test68 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test68']['sents']['0']:
        verbs=return_dict['test68']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test68']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test68']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test68']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test68']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test68():
    text="""Lawmakers and officials in Arnor and Gondor welcomed a resumption of formal diplomatic ties
with Eriador. 
"""
    parse="""1	Lawmakers	lawmaker	NOUN	NNS	Number=Plur	8	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	officials	official	NOUN	NNS	Number=Plur	1	conj	_	_
4	in	in	ADP	IN	_	5	case	_	_
5	Arnor	Arnor	PROPN	NNP	Number=Sing	1	nmod	_	_
6	and	and	CONJ	CC	_	5	cc	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	5	conj	_	_
8	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	resumption	resumption	NOUN	NN	Number=Sing	8	dobj	_	_
11	of	of	ADP	IN	_	14	case	_	_
12	formal	formal	ADJ	JJ	Degree=Pos	14	amod	_	_
13	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	14	amod	_	_
14	ties	tie	NOUN	NNS	Number=Plur	10	nmod	_	_
15	with	with	ADP	IN	_	16	case	_	_
16	Eriador	Eriador	PROPN	NNP	Number=Sing	14	nmod	_	_
17	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test69': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNLEG],[ERI],050)\n([GONLEG],[ERI],050)\n([ARNGOV],[ERI],050)\n([GONGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test69']['sents']['0']:
            print(return_dict['test69']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test69']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNLEG],[ERI],050)\n([GONLEG],[ERI],050)\n([ARNGOV],[ERI],050)\n([GONGOV],[ERI],050)",str(return_dict['test69']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNLEG],[ERI],050)\n([GONLEG],[ERI],050)\n([ARNGOV],[ERI],050)\n([GONGOV],[ERI],050)","noevent"]
            print("test69 Failed")
    except:
        print("test69 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test69']['sents']['0']:
        verbs=return_dict['test69']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test69']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test69']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test69']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test69']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test69():
    text="""The Shire is about to restore full diplomatic ties with Lorien almost 
five years after crowds burned down its embassy. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Shire	Shire	NOUN	NN	Number=Sing	4	nsubj	_	_
3	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	cop	_	_
4	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
5	to	to	PART	TO	_	6	mark	_	_
6	restore	restore	VERB	VB	VerbForm=Inf	4	xcomp	_	_
7	full	full	ADJ	JJ	Degree=Pos	9	amod	_	_
8	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	9	amod	_	_
9	ties	tie	NOUN	NNS	Number=Plur	6	dobj	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Lorien	Lorien	PROPN	NNP	Number=Sing	6	nmod	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	16	nmod:npmod	_	_
15	after	after	ADP	IN	_	16	case	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	6	nmod	_	_
17	burned	burn	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
18	down	down	ADP	RP	_	17	compound:prt	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
21	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test70': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([FRO/BIL/SAM],[ELR/GAL],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test70']['sents']['0']:
            print(return_dict['test70']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test70']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([FRO/BIL/SAM],[ELR/GAL],050)",str(return_dict['test70']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([FRO/BIL/SAM],[ELR/GAL],050)","noevent"]
            print("test70 Failed")
    except:
        print("test70 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test70']['sents']['0']:
        verbs=return_dict['test70']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test70']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test70']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test70']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test70']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test70():
    text="""Arnor and the evil awful Gondor welcomed a resumption of formal diplomatic  
ties with Osgiliath after a 12-year rift, the official news agency  said 
on Thursday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	7	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	the	the	DET	DT	Definite=Def|PronType=Art	6	det	_	_
4	evil	evil	ADJ	JJ	Degree=Pos	6	amod	_	_
5	awful	awful	ADJ	JJ	Degree=Pos	6	amod	_	_
6	Gondor	Gondor	PROPN	NNP	Number=Sing	1	conj	_	_
7	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	a	a	DET	DT	Definite=Ind|PronType=Art	9	det	_	_
9	resumption	resumption	NOUN	NN	Number=Sing	7	dobj	_	_
10	of	of	ADP	IN	_	13	case	_	_
11	formal	formal	ADJ	JJ	Degree=Pos	13	amod	_	_
12	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	13	amod	_	_
13	ties	tie	NOUN	NNS	Number=Plur	9	nmod	_	_
14	with	with	ADP	IN	_	15	case	_	_
15	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	7	nmod	_	_
16	after	after	ADP	IN	_	19	case	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	12-year	12-year	ADJ	JJ	Degree=Pos	19	amod	_	_
19	rift	rift	NOUN	NN	Number=Sing	7	nmod	_	_
20	,	,	PUNCT	,	_	7	punct	_	_
21	the	the	DET	DT	Definite=Def|PronType=Art	24	det	_	_
22	official	official	ADJ	JJ	Degree=Pos	24	amod	_	_
23	news	news	NOUN	NN	Number=Sing	24	compound	_	_
24	agency	agency	NOUN	NN	Number=Sing	25	nsubj	_	_
25	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	7	parataxis	_	_
26	on	on	ADP	IN	_	27	case	_	_
27	Thursday	Thursday	PROPN	NNP	Number=Sing	25	nmod	_	_
28	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test71': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[OSG],050)\n([GON],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test71']['sents']['0']:
            print(return_dict['test71']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test71']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([GON],[OSG],050)",str(return_dict['test71']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([GON],[OSG],050)","noevent"]
            print("test71 Failed")
    except:
        print("test71 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test71']['sents']['0']:
        verbs=return_dict['test71']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test71']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test71']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test71']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test71']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test71():
    text="""Evil Mordor, the awful Arnor, and good Gondor welcomed a resumption of formal   
diplomatic ties with Osgiliath after a 12-year rift, the official news agency  said 
on Thursday. 
"""
    parse="""1	Evil	evil	PROPN	NNP	Number=Sing	2	name	_	_
2	Mordor	Mordor	PROPN	NNP	Number=Sing	11	nsubj	_	_
3	,	,	PUNCT	,	_	2	punct	_	_
4	the	the	DET	DT	Definite=Def|PronType=Art	6	det	_	_
5	awful	awful	ADJ	JJ	Degree=Pos	6	amod	_	_
6	Arnor	Arnor	PROPN	NNP	Number=Sing	2	appos	_	_
7	,	,	PUNCT	,	_	2	punct	_	_
8	and	and	CONJ	CC	_	2	cc	_	_
9	good	good	ADJ	JJ	Degree=Pos	10	amod	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	2	conj	_	_
11	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
12	a	a	DET	DT	Definite=Ind|PronType=Art	13	det	_	_
13	resumption	resumption	NOUN	NN	Number=Sing	11	dobj	_	_
14	of	of	ADP	IN	_	17	case	_	_
15	formal	formal	ADJ	JJ	Degree=Pos	17	amod	_	_
16	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	17	amod	_	_
17	ties	tie	NOUN	NNS	Number=Plur	13	nmod	_	_
18	with	with	ADP	IN	_	19	case	_	_
19	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	11	nmod	_	_
20	after	after	ADP	IN	_	23	case	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
22	12-year	12-year	ADJ	JJ	Degree=Pos	23	amod	_	_
23	rift	rift	NOUN	NN	Number=Sing	11	nmod	_	_
24	,	,	PUNCT	,	_	11	punct	_	_
25	the	the	DET	DT	Definite=Def|PronType=Art	28	det	_	_
26	official	official	ADJ	JJ	Degree=Pos	28	amod	_	_
27	news	news	NOUN	NN	Number=Sing	28	compound	_	_
28	agency	agency	NOUN	NN	Number=Sing	29	nsubj	_	_
29	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	11	parataxis	_	_
30	on	on	ADP	IN	_	31	case	_	_
31	Thursday	Thursday	PROPN	NNP	Number=Sing	29	nmod	_	_
32	.	.	PUNCT	.	_	11	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test72': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([MOR],[OSG],050)\n([ARN],[OSG],050)\n([GON],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test72']['sents']['0']:
            print(return_dict['test72']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test72']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[OSG],050)\n([ARN],[OSG],050)\n([GON],[OSG],050)",str(return_dict['test72']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[OSG],050)\n([ARN],[OSG],050)\n([GON],[OSG],050)","noevent"]
            print("test72 Failed")
    except:
        print("test72 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test72']['sents']['0']:
        verbs=return_dict['test72']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test72']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test72']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test72']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test72']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test72():
    text="""Arnor, Calenardhon and the evil awful Gondor welcomed a resumption of formal diplomatic  
ties with Osgiliath after a 12-year rift, the official news agency  said 
on Thursday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	9	nsubj	_	_
2	,	,	PUNCT	,	_	1	punct	_	_
3	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	1	conj	_	_
4	and	and	CONJ	CC	_	1	cc	_	_
5	the	the	DET	DT	Definite=Def|PronType=Art	8	det	_	_
6	evil	evil	ADJ	JJ	Degree=Pos	8	amod	_	_
7	awful	awful	ADJ	JJ	Degree=Pos	8	amod	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	1	conj	_	_
9	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
10	a	a	DET	DT	Definite=Ind|PronType=Art	11	det	_	_
11	resumption	resumption	NOUN	NN	Number=Sing	9	dobj	_	_
12	of	of	ADP	IN	_	15	case	_	_
13	formal	formal	ADJ	JJ	Degree=Pos	15	amod	_	_
14	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	15	amod	_	_
15	ties	tie	NOUN	NNS	Number=Plur	11	nmod	_	_
16	with	with	ADP	IN	_	17	case	_	_
17	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	9	nmod	_	_
18	after	after	ADP	IN	_	21	case	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	12-year	12-year	ADJ	JJ	Degree=Pos	21	amod	_	_
21	rift	rift	NOUN	NN	Number=Sing	9	nmod	_	_
22	,	,	PUNCT	,	_	9	punct	_	_
23	the	the	DET	DT	Definite=Def|PronType=Art	26	det	_	_
24	official	official	ADJ	JJ	Degree=Pos	26	amod	_	_
25	news	news	NOUN	NN	Number=Sing	26	compound	_	_
26	agency	agency	NOUN	NN	Number=Sing	27	nsubj	_	_
27	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	9	parataxis	_	_
28	on	on	ADP	IN	_	29	case	_	_
29	Thursday	Thursday	PROPN	NNP	Number=Sing	27	nmod	_	_
30	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test73': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[OSG],050)\n([CAL],[OSG],050)\n([GON],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test73']['sents']['0']:
            print(return_dict['test73']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test73']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([CAL],[OSG],050)\n([GON],[OSG],050)",str(return_dict['test73']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([CAL],[OSG],050)\n([GON],[OSG],050)","noevent"]
            print("test73 Failed")
    except:
        print("test73 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test73']['sents']['0']:
        verbs=return_dict['test73']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test73']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test73']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test73']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test73']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test73():
    text="""Calenardhon and the evil Arnor awful Gondor welcomed a resumption of formal diplomatic  
ties with Osgiliath after a 12-year rift, the official news agency  said 
on Thursday. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	8	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	the	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
4	evil	evil	NOUN	NN	Number=Sing	1	conj	_	_
5	Arnor	Arnor	ADP	IN	_	7	case	_	_
6	awful	awful	ADJ	JJ	Degree=Pos	7	amod	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	4	nmod	_	_
8	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	resumption	resumption	NOUN	NN	Number=Sing	8	dobj	_	_
11	of	of	ADP	IN	_	14	case	_	_
12	formal	formal	ADJ	JJ	Degree=Pos	14	amod	_	_
13	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	14	amod	_	_
14	ties	tie	NOUN	NNS	Number=Plur	10	nmod	_	_
15	with	with	ADP	IN	_	16	case	_	_
16	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	10	nmod	_	_
17	after	after	ADP	IN	_	20	case	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	12-year	12-year	ADJ	JJ	Degree=Pos	20	amod	_	_
20	rift	rift	NOUN	NN	Number=Sing	8	nmod	_	_
21	,	,	PUNCT	,	_	8	punct	_	_
22	the	the	DET	DT	Definite=Def|PronType=Art	25	det	_	_
23	official	official	ADJ	JJ	Degree=Pos	25	amod	_	_
24	news	news	NOUN	NN	Number=Sing	25	compound	_	_
25	agency	agency	NOUN	NN	Number=Sing	26	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	8	parataxis	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Thursday	Thursday	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test74': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[OSG],050)\n([ARN],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test74']['sents']['0']:
            print(return_dict['test74']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test74']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[OSG],050)\n([ARN],[OSG],050)",str(return_dict['test74']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[OSG],050)\n([ARN],[OSG],050)","noevent"]
            print("test74 Failed")
    except:
        print("test74 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test74']['sents']['0']:
        verbs=return_dict['test74']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test74']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test74']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test74']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test74']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test74():
    text="""The lions and the evil awful Gondor welcomed a resumption of formal diplomatic  
ties with Osgiliath after a 12-year rift, the primary official news agency  said 
on Thursday. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	lions	lion	NOUN	NNS	Number=Plur	8	nsubj	_	_
3	and	and	CONJ	CC	_	2	cc	_	_
4	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	_
5	evil	evil	ADJ	JJ	Degree=Pos	7	amod	_	_
6	awful	awful	ADJ	JJ	Degree=Pos	7	amod	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	2	conj	_	_
8	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
10	resumption	resumption	NOUN	NN	Number=Sing	8	dobj	_	_
11	of	of	ADP	IN	_	14	case	_	_
12	formal	formal	ADJ	JJ	Degree=Pos	14	amod	_	_
13	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	14	amod	_	_
14	ties	tie	NOUN	NNS	Number=Plur	10	nmod	_	_
15	with	with	ADP	IN	_	16	case	_	_
16	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	8	nmod	_	_
17	after	after	ADP	IN	_	20	case	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	12-year	12-year	ADJ	JJ	Degree=Pos	20	amod	_	_
20	rift	rift	NOUN	NN	Number=Sing	8	nmod	_	_
21	,	,	PUNCT	,	_	8	punct	_	_
22	the	the	DET	DT	Definite=Def|PronType=Art	26	det	_	_
23	primary	primary	ADJ	JJ	Degree=Pos	26	amod	_	_
24	official	official	ADJ	JJ	Degree=Pos	26	amod	_	_
25	news	news	NOUN	NN	Number=Sing	26	compound	_	_
26	agency	agency	NOUN	NN	Number=Sing	27	nsubj	_	_
27	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	8	parataxis	_	_
28	on	on	ADP	IN	_	29	case	_	_
29	Thursday	Thursday	PROPN	NNP	Number=Sing	27	nmod	_	_
30	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test75': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[OSG],050)\n([---GOV],[---],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test75']['sents']['0']:
            print(return_dict['test75']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test75']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],050)\n([---GOV],[---],010)",str(return_dict['test75']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],050)\n([---GOV],[---],010)","noevent"]
            print("test75 Failed")
    except:
        print("test75 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test75']['sents']['0']:
        verbs=return_dict['test75']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test75']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test75']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test75']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test75']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test75():
    text="""Lions, tigers, and Gondor welcomed a resumption of formal diplomatic ties  
with Osgiliath after a 12-year rift, the primary official news agency  said 
on Thursday. 
"""
    parse="""1	Lions	lion	NOUN	NNS	Number=Plur	7	nsubj	_	_
2	,	,	PUNCT	,	_	1	punct	_	_
3	tigers	tiger	NOUN	NNS	Number=Plur	1	conj	_	_
4	,	,	PUNCT	,	_	1	punct	_	_
5	and	and	CONJ	CC	_	1	cc	_	_
6	Gondor	Gondor	PROPN	NNP	Number=Sing	1	conj	_	_
7	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	a	a	DET	DT	Definite=Ind|PronType=Art	9	det	_	_
9	resumption	resumption	NOUN	NN	Number=Sing	7	dobj	_	_
10	of	of	ADP	IN	_	13	case	_	_
11	formal	formal	ADJ	JJ	Degree=Pos	13	amod	_	_
12	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	13	amod	_	_
13	ties	tie	NOUN	NNS	Number=Plur	9	nmod	_	_
14	with	with	ADP	IN	_	15	case	_	_
15	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	7	nmod	_	_
16	after	after	ADP	IN	_	19	case	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	12-year	12-year	ADJ	JJ	Degree=Pos	19	amod	_	_
19	rift	rift	NOUN	NN	Number=Sing	7	nmod	_	_
20	,	,	PUNCT	,	_	7	punct	_	_
21	the	the	DET	DT	Definite=Def|PronType=Art	25	det	_	_
22	primary	primary	ADJ	JJ	Degree=Pos	25	amod	_	_
23	official	official	ADJ	JJ	Degree=Pos	25	amod	_	_
24	news	news	NOUN	NN	Number=Sing	25	compound	_	_
25	agency	agency	NOUN	NN	Number=Sing	26	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	7	parataxis	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Thursday	Thursday	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test76': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[OSG],050)\n([---GOV],[---],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test76']['sents']['0']:
            print(return_dict['test76']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test76']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],050)\n([---GOV],[---],010)",str(return_dict['test76']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],050)\n([---GOV],[---],010)","noevent"]
            print("test76 Failed")
    except:
        print("test76 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test76']['sents']['0']:
        verbs=return_dict['test76']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test76']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test76']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test76']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test76']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test76():
    text="""Ithilen's awful and evil minister Calimehtar warned of the Prince of 
Dol Amroth. 
"""
    parse="""1	Ithilen	Ithilen	PROPN	NNP	Number=Sing	7	nmod:poss	_	_
2	's	be	PART	POS	_	1	case	_	_
3	awful	awful	ADJ	JJ	Degree=Pos	6	amod	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	evil	evil	ADJ	JJ	Degree=Pos	3	conj	_	_
6	minister	minister	NOUN	NN	Number=Sing	7	compound	_	_
7	Calimehtar	Calimehtar	PROPN	NNP	Number=Sing	8	nsubj	_	_
8	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	of	of	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	Prince	Prince	PROPN	NNP	Number=Sing	8	nmod	_	_
12	of	of	ADP	IN	_	14	case	_	_
13	Dol	Dol	PROPN	NNP	Number=Sing	14	name	_	_
14	Amroth	Amroth	PROPN	NNP	Number=Sing	11	nmod	_	_
15	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test77': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ITHGOV],[DOL],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test77']['sents']['0']:
            print(return_dict['test77']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test77']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITHGOV],[DOL],130)",str(return_dict['test77']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITHGOV],[DOL],130)","noevent"]
            print("test77 Failed")
    except:
        print("test77 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test77']['sents']['0']:
        verbs=return_dict['test77']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test77']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test77']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test77']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test77']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test77():
    text="""Arnor and Gondor welcomed a resumption of formal diplomatic ties with  
Osgiliath after a 12-year rift, the official news agency  said 
on Thursday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	4	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	Gondor	Gondor	PROPN	NNP	Number=Sing	1	conj	_	_
4	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	resumption	resumption	NOUN	NN	Number=Sing	4	dobj	_	_
7	of	of	ADP	IN	_	10	case	_	_
8	formal	formal	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	6	nmod	_	_
11	with	with	ADP	IN	_	12	case	_	_
12	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	4	nmod	_	_
13	after	after	ADP	IN	_	16	case	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	12-year	12-year	ADJ	JJ	Degree=Pos	16	amod	_	_
16	rift	rift	NOUN	NN	Number=Sing	4	nmod	_	_
17	,	,	PUNCT	,	_	4	punct	_	_
18	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
19	official	official	ADJ	JJ	Degree=Pos	21	amod	_	_
20	news	news	NOUN	NN	Number=Sing	21	compound	_	_
21	agency	agency	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Thursday	Thursday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test78': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[OSG],050)\n([GON],[OSG],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test78']['sents']['0']:
            print(return_dict['test78']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test78']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([GON],[OSG],050)",str(return_dict['test78']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[OSG],050)\n([GON],[OSG],050)","noevent"]
            print("test78 Failed")
    except:
        print("test78 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test78']['sents']['0']:
        verbs=return_dict['test78']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test78']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test78']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test78']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test78']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test78():
    text="""Ithilen's awful and cool minister Calimehtar warned of the Prince of 
Dol Amroth. 
"""
    parse="""1	Ithilen	Ithilen	PROPN	NNP	Number=Sing	7	nmod:poss	_	_
2	's	be	PART	POS	_	1	case	_	_
3	awful	awful	ADJ	JJ	Degree=Pos	6	amod	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	cool	cool	ADJ	JJ	Degree=Pos	3	conj	_	_
6	minister	minister	NOUN	NN	Number=Sing	7	compound	_	_
7	Calimehtar	Calimehtar	PROPN	NNP	Number=Sing	8	nsubj	_	_
8	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	of	of	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	Prince	Prince	PROPN	NNP	Number=Sing	8	nmod	_	_
12	of	of	ADP	IN	_	14	case	_	_
13	Dol	Dol	PROPN	NNP	Number=Sing	14	name	_	_
14	Amroth	Amroth	PROPN	NNP	Number=Sing	11	nmod	_	_
15	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test79': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ITHGOV],[DOL],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test79']['sents']['0']:
            print(return_dict['test79']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test79']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITHGOV],[DOL],130)",str(return_dict['test79']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITHGOV],[DOL],130)","noevent"]
            print("test79 Failed")
    except:
        print("test79 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test79']['sents']['0']:
        verbs=return_dict['test79']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test79']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test79']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test79']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test79']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test79():
    text="""Ithilen's sheep and goats of Gondor warned of the Prince of Dol Amroth. 
"""
    parse="""1	Ithilen	Ithilen	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	sheep	sheep	NOUN	NNS	Number=Plur	8	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	goats	goat	NOUN	NNS	Number=Plur	3	conj	_	_
6	of	of	ADP	IN	_	7	case	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
8	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
9	of	of	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	Prince	Prince	PROPN	NNP	Number=Sing	8	nmod	_	_
12	of	of	ADP	IN	_	14	case	_	_
13	Dol	Dol	PROPN	NNP	Number=Sing	14	name	_	_
14	Amroth	Amroth	PROPN	NNP	Number=Sing	11	nmod	_	_
15	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test80': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ITH],[DOL],130)\n([GON],[DOL],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test80']['sents']['0']:
            print(return_dict['test80']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test80']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[DOL],130)\n([GON],[DOL],130)",str(return_dict['test80']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[DOL],130)\n([GON],[DOL],130)","noevent"]
            print("test80 Failed")
    except:
        print("test80 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test80']['sents']['0']:
        verbs=return_dict['test80']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test80']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test80']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test80']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test80']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test80():
    text="""Ithilen and the government of Gondor warned their populations about the Prince of Dol Amroth. 
"""
    parse="""1	Ithilen	Ithilen	PROPN	NNP	Number=Sing	7	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	the	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
4	government	government	NOUN	NN	Number=Sing	1	conj	_	_
5	of	of	ADP	IN	_	6	case	_	_
6	Gondor	Gondor	PROPN	NNP	Number=Sing	4	nmod	_	_
7	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	9	nmod:poss	_	_
9	populations	population	NOUN	NNS	Number=Plur	7	dobj	_	_
10	about	about	ADP	IN	_	12	case	_	_
11	the	the	DET	DT	Definite=Def|PronType=Art	12	det	_	_
12	Prince	Prince	PROPN	NNP	Number=Sing	9	nmod	_	_
13	of	of	ADP	IN	_	15	case	_	_
14	Dol	Dol	PROPN	NNP	Number=Sing	15	name	_	_
15	Amroth	Amroth	PROPN	NNP	Number=Sing	12	nmod	_	_
16	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test81': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ITH],[DOL],130)\n([GONGOV],[DOL],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test81']['sents']['0']:
            print(return_dict['test81']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test81']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[DOL],130)\n([GONGOV],[DOL],130)",str(return_dict['test81']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[DOL],130)\n([GONGOV],[DOL],130)","noevent"]
            print("test81 Failed")
    except:
        print("test81 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test81']['sents']['0']:
        verbs=return_dict['test81']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test81']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test81']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test81']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test81']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test81():
    text="""Ithilen and the government of Gondor warned their Ent populations about the Prince of Dol Amroth. 
"""
    parse="""1	Ithilen	Ithilen	PROPN	NNP	Number=Sing	7	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	the	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
4	government	government	NOUN	NN	Number=Sing	1	conj	_	_
5	of	of	ADP	IN	_	6	case	_	_
6	Gondor	Gondor	PROPN	NNP	Number=Sing	4	nmod	_	_
7	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
8	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	10	nmod:poss	_	_
9	Ent	Ent	ADJ	JJ	Degree=Pos	10	amod	_	_
10	populations	population	NOUN	NNS	Number=Plur	7	dobj	_	_
11	about	about	ADP	IN	_	13	case	_	_
12	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
13	Prince	Prince	PROPN	NNP	Number=Sing	10	nmod	_	_
14	of	of	ADP	IN	_	16	case	_	_
15	Dol	Dol	PROPN	NNP	Number=Sing	16	name	_	_
16	Amroth	Amroth	PROPN	NNP	Number=Sing	13	nmod	_	_
17	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test82': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ITH],[DOL],130)\n([GONGOV],[DOL],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test82']['sents']['0']:
            print(return_dict['test82']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test82']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[DOL],130)\n([GONGOV],[DOL],130)",str(return_dict['test82']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ITH],[DOL],130)\n([GONGOV],[DOL],130)","noevent"]
            print("test82 Failed")
    except:
        print("test82 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test82']['sents']['0']:
        verbs=return_dict['test82']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test82']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test82']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test82']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test82']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test82():
    text="""Neither Galadriel nor Gollum boycotted the parade supporting Gondor 
on Saturday. 
"""
    parse="""1	Neither	neither	CONJ	CC	_	5	cc	_	_
2	Galadriel	Galadriel	PROPN	NNP	Number=Sing	5	nsubj	_	_
3	nor	nor	CONJ	CC	_	2	cc	_	_
4	Gollum	Gollum	PROPN	NNP	Number=Sing	2	conj	_	_
5	boycotted	boycot	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
6	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	_
7	parade	parade	NOUN	NN	Number=Sing	5	dobj	_	_
8	supporting	support	VERB	VBG	VerbForm=Ger	7	acl	_	_
9	Gondor	Gondor	PROPN	NNP	Number=Sing	8	dobj	_	_
10	on	on	ADP	IN	_	11	case	_	_
11	Saturday	Saturday	PROPN	NNP	Number=Sing	8	nmod	_	_
12	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test83': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ELF],[GON],163)\n([HOB],[GON],163)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test83']['sents']['0']:
            print(return_dict['test83']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test83']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ELF],[GON],163)\n([HOB],[GON],163)",str(return_dict['test83']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ELF],[GON],163)\n([HOB],[GON],163)","noevent"]
            print("test83 Failed")
    except:
        print("test83 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test83']['sents']['0']:
        verbs=return_dict['test83']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test83']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test83']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test83']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test83']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test83():
    text="""The Calenardhon government condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday and promised aid to the affected Ithilen villages. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	name	_	_
3	government	government	NOUN	NN	Number=Sing	4	nsubj	_	_
4	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	attack	attack	NOUN	NN	Number=Sing	4	dobj	_	_
7	by	by	ADP	IN	_	9	case	_	_
8	Osgiliath	Osgiliath	DET	DT	_	9	det	_	_
9	soldiers	soldier	NOUN	NNS	Number=Plur	6	nmod	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	south	south	ADV	RB	_	12	advmod	_	_
12	Ithilen	Ithilen	PROPN	NNP	Number=Sing	9	nmod	_	_
13	on	on	ADP	IN	_	14	case	_	_
14	Thursday	Thursday	PROPN	NNP	Number=Sing	9	nmod	_	_
15	and	and	CONJ	CC	_	14	cc	_	_
16	promised	promise	VERB	VBN	Tense=Past|VerbForm=Part	17	amod	_	_
17	aid	aid	NOUN	NN	Number=Sing	14	conj	_	_
18	to	to	ADP	IN	_	22	case	_	_
19	the	the	DET	DT	Definite=Def|PronType=Art	22	det	_	_
20	affected	affect	VERB	VBN	Tense=Past|VerbForm=Part	22	amod	_	_
21	Ithilen	Ithilen	PROPN	NNP	Number=Sing	22	compound	_	_
22	villages	villag	NOUN	NNS	Number=Plur	9	nmod	_	_
23	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test84': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],033)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test84']['sents']['0']:
            print(return_dict['test84']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test84']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],033)",str(return_dict['test84']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],033)","noevent"]
            print("test84 Failed")
    except:
        print("test84 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test84']['sents']['0']:
        verbs=return_dict['test84']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test84']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test84']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test84']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test84']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test84():
    text="""Danish media and government warned at the Gondor of the Prince of Dol Amroth. 
"""
    parse="""1	Danish	Danish	ADJ	JJ	Degree=Pos	2	amod	_	_
2	media	media	NOUN	NN	Number=Sing	0	root	_	_
3	and	and	CONJ	CC	_	2	cc	_	_
4	government	government	NOUN	NN	Number=Sing	2	conj	_	_
5	warned	warn	VERB	VBN	Tense=Past|VerbForm=Part	2	acl	_	_
6	at	at	ADP	IN	_	8	case	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	8	det	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
9	of	of	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	Prince	Prince	PROPN	NNP	Number=Sing	8	nmod	_	_
12	of	of	ADP	IN	_	14	case	_	_
13	Dol	Dol	PROPN	NNP	Number=Sing	14	name	_	_
14	Amroth	Amroth	PROPN	NNP	Number=Sing	11	nmod	_	_
15	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test85': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([DNKMED],[DOL],130)\n([DNKGOV],[DOL],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test85']['sents']['0']:
            print(return_dict['test85']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test85']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DNKMED],[DOL],130)\n([DNKGOV],[DOL],130)",str(return_dict['test85']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DNKMED],[DOL],130)\n([DNKGOV],[DOL],130)","noevent"]
            print("test85 Failed")
    except:
        print("test85 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test85']['sents']['0']:
        verbs=return_dict['test85']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test85']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test85']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test85']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test85']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test85():
    text=""""""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Danish	Danish	ADJ	JJ	Degree=Pos	3	amod	_	_
3	media	media	NOUN	NN	Number=Sing	6	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	government	government	NOUN	NN	Number=Sing	3	conj	_	_
6	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	8	det	_	_
8	population	population	NOUN	NN	Number=Sing	6	dobj	_	_
9	of	of	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	8	nmod	_	_
11	of	of	ADP	IN	_	13	case	_	_
12	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
13	Prince	Prince	PROPN	NNP	Number=Sing	10	nmod	_	_
14	of	of	ADP	IN	_	16	case	_	_
15	Dol	Dol	PROPN	NNP	Number=Sing	16	name	_	_
16	Amroth	Amroth	PROPN	NNP	Number=Sing	13	nmod	_	_
17	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test86': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([DNKMED],[GON],130)\n([---GOV],[GON],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test86']['sents']['0']:
            print(return_dict['test86']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test86']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DNKMED],[GON],130)\n([---GOV],[GON],130)",str(return_dict['test86']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DNKMED],[GON],130)\n([---GOV],[GON],130)","noevent"]
            print("test86 Failed")
    except:
        print("test86 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test86']['sents']['0']:
        verbs=return_dict['test86']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test86']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test86']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test86']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test86']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test86():
    text="""The Danish Islamist media and government warned at the Gondor of the Prince of Dol Amroth. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	Danish	Danish	PROPN	NNP	Number=Sing	3	compound	_	_
3	Islamist	Islamist	PROPN	NNP	Number=Sing	4	compound	_	_
4	media	media	NOUN	NN	Number=Sing	0	root	_	_
5	and	and	CONJ	CC	_	4	cc	_	_
6	government	government	NOUN	NN	Number=Sing	4	conj	_	_
7	warned	warn	VERB	VBN	Tense=Past|VerbForm=Part	4	acl	_	_
8	at	at	ADP	IN	_	10	case	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	7	nmod	_	_
11	of	of	ADP	IN	_	13	case	_	_
12	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
13	Prince	Prince	PROPN	NNP	Number=Sing	10	nmod	_	_
14	of	of	ADP	IN	_	16	case	_	_
15	Dol	Dol	PROPN	NNP	Number=Sing	16	name	_	_
16	Amroth	Amroth	PROPN	NNP	Number=Sing	13	nmod	_	_
17	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test87': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990809'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([DNKMUSMED],[GON],130)\n([DNKMUSGOV],[GON],130)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test87']['sents']['0']:
            print(return_dict['test87']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test87']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DNKMUSMED],[GON],130)\n([DNKMUSGOV],[GON],130)",str(return_dict['test87']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([DNKMUSMED],[GON],130)\n([DNKMUSGOV],[GON],130)","noevent"]
            print("test87 Failed")
    except:
        print("test87 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test87']['sents']['0']:
        verbs=return_dict['test87']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test87']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test87']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test87']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test87']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test87():
    text="""Frodo said he has deep satisfaction toward Gondor and Arnor's Elrond, 
and Gondor's dramatic cooperation and its eye-catching development are of 
great significance to the region and even the entire world, he noted. 
"""
    parse="""1	Frodo	Frodo	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	2	aux	_	_
2	said	say	VERB	VBN	Tense=Past|VerbForm=Part	37	ccomp	_	_
3	he	he	PRON	PRP	Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs	5	nsubj	_	_
4	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	5	aux	_	_
5	deep	deep	VERB	VBN	Tense=Past|VerbForm=Part	2	ccomp	_	_
6	satisfaction	satisfaction	NOUN	NN	Number=Sing	5	dobj	_	_
7	toward	toward	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
9	and	and	CONJ	CC	_	8	cc	_	_
10	Arnor	Arnor	PROPN	NNP	Number=Sing	12	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	Elrond	Elrond	PROPN	NNP	Number=Sing	8	conj	_	_
13	,	,	PUNCT	,	_	5	punct	_	_
14	and	and	CONJ	CC	_	5	cc	_	_
15	Gondor	Gondor	PROPN	NNP	Number=Sing	18	nmod:poss	_	_
16	's	's	PART	POS	_	15	case	_	_
17	dramatic	dramatic	ADJ	JJ	Degree=Pos	18	amod	_	_
18	cooperation	cooperation	NOUN	NN	Number=Sing	5	conj	_	_
19	and	and	CONJ	CC	_	18	cc	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
21	eye-catching	eye-catching	ADJ	JJ	Degree=Pos	22	amod	_	_
22	development	development	NOUN	NN	Number=Sing	18	conj	_	_
23	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	26	cop	_	_
24	of	of	ADP	IN	_	26	case	_	_
25	great	great	ADJ	JJ	Degree=Pos	26	amod	_	_
26	significance	significance	NOUN	NN	Number=Sing	37	ccomp	_	_
27	to	to	ADP	IN	_	29	case	_	_
28	the	the	DET	DT	Definite=Def|PronType=Art	29	det	_	_
29	region	region	NOUN	NN	Number=Sing	26	nmod	_	_
30	and	and	CONJ	CC	_	26	cc	_	_
31	even	even	ADV	RB	_	34	advmod	_	_
32	the	the	DET	DT	Definite=Def|PronType=Art	34	det	_	_
33	entire	entire	ADJ	JJ	Degree=Pos	34	amod	_	_
34	world	world	NOUN	NN	Number=Sing	26	conj	_	_
35	,	,	PUNCT	,	_	37	punct	_	_
36	he	he	PRON	PRP	Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs	37	nsubj	_	_
37	noted	not	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
38	.	.	PUNCT	.	_	37	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test88': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20000423'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],010)\n([HOB],[ARN],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test88']['sents']['0']:
            print(return_dict['test88']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test88']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],010)\n([HOB],[ARN],010)",str(return_dict['test88']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],010)\n([HOB],[ARN],010)","noevent"]
            print("test88 Failed")
    except:
        print("test88 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test88']['sents']['0']:
        verbs=return_dict['test88']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test88']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test88']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test88']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test88']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test88():
    text="""The Calenardhon government issue condemned an attack by Osgiliath soldiers 
in south Ithilen on Thursday and promised raids to the affected Ithilen villages. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	4	compound	_	_
3	government	government	NOUN	NN	Number=Sing	4	compound	_	_
4	issue	issue	NOUN	NN	Number=Sing	5	nsubj	_	_
5	condemned	condemn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
6	an	a	DET	DT	Definite=Ind|PronType=Art	7	det	_	_
7	attack	attack	NOUN	NN	Number=Sing	5	dobj	_	_
8	by	by	ADP	IN	_	10	case	_	_
9	Osgiliath	Osgiliath	DET	DT	_	10	det	_	_
10	soldiers	soldier	NOUN	NNS	Number=Plur	7	nmod	_	_
11	in	in	ADP	IN	_	13	case	_	_
12	south	south	ADV	RB	_	13	advmod	_	_
13	Ithilen	Ithilen	PROPN	NNP	Number=Sing	10	nmod	_	_
14	on	on	ADP	IN	_	15	case	_	_
15	Thursday	Thursday	PROPN	NNP	Number=Sing	5	nmod	_	_
16	and	and	CONJ	CC	_	15	cc	_	_
17	promised	promise	VERB	VBN	Tense=Past|VerbForm=Part	18	amod	_	_
18	raids	raid	NOUN	NNS	Number=Plur	15	conj	_	_
19	to	to	ADP	IN	_	23	case	_	_
20	the	the	DET	DT	Definite=Def|PronType=Art	23	det	_	_
21	affected	affect	VERB	VBN	Tense=Past|VerbForm=Part	23	amod	_	_
22	Ithilen	Ithilen	PROPN	NNP	Number=Sing	23	compound	_	_
23	villages	villag	NOUN	NNS	Number=Plur	5	nmod	_	_
24	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test89': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],138)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test89']['sents']['0']:
            print(return_dict['test89']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test89']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],138)",str(return_dict['test89']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],138)","noevent"]
            print("test89 Failed")
    except:
        print("test89 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test89']['sents']['0']:
        verbs=return_dict['test89']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test89']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test89']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test89']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test89']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test89():
    text="""The Calenardhon government chided an attack by Osgiliath soldiers 
in south Ithilen on Thursday and ousted the affected Ithilen villages. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	3	name	_	_
3	government	government	NOUN	NN	Number=Sing	4	nsubj	_	_
4	chided	chide	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	attack	attack	NOUN	NN	Number=Sing	4	dobj	_	_
7	by	by	ADP	IN	_	9	case	_	_
8	Osgiliath	Osgiliath	DET	DT	_	9	det	_	_
9	soldiers	soldier	NOUN	NNS	Number=Plur	6	nmod	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	south	south	ADV	RB	_	12	advmod	_	_
12	Ithilen	Ithilen	PROPN	NNP	Number=Sing	9	nmod	_	_
13	on	on	ADP	IN	_	14	case	_	_
14	Thursday	Thursday	PROPN	NNP	Number=Sing	9	nmod	_	_
15	and	and	CONJ	CC	_	4	cc	_	_
16	ousted	oust	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	conj	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	20	det	_	_
18	affected	affect	VERB	VBN	Tense=Past|VerbForm=Part	20	amod	_	_
19	Ithilen	Ithilen	PROPN	NNP	Number=Sing	20	compound	_	_
20	villages	villag	NOUN	NNS	Number=Plur	16	dobj	_	_
21	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test90': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],174)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test90']['sents']['0']:
            print(return_dict['test90']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test90']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],174)",str(return_dict['test90']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CALGOV],[OSGMIL],111)\n([CALGOV],[ITH],174)","noevent"]
            print("test90 Failed")
    except:
        print("test90 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test90']['sents']['0']:
        verbs=return_dict['test90']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test90']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test90']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test90']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test90']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test90():
    text="""And Eriador has called for a boycott against Osgiliath, the state's fiercest foe. 
"""
    parse="""1	And	and	CONJ	CC	_	4	cc	_	_
2	Eriador	Eriador	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	called	call	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	for	for	ADP	IN	_	7	case	_	_
6	a	a	DET	DT	Definite=Ind|PronType=Art	7	det	_	_
7	boycott	boycott	NOUN	NN	Number=Sing	4	nmod	_	_
8	against	against	ADP	IN	_	9	case	_	_
9	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	7	nmod	_	_
10	,	,	PUNCT	,	_	4	punct	_	_
11	the	the	DET	DT	Definite=Def|PronType=Art	12	det	_	_
12	state	state	NOUN	NN	Number=Sing	15	nmod:poss	_	_
13	's	's	PART	POS	_	12	case	_	_
14	fiercest	fiercest	NOUN	NN	Number=Sing	15	compound	_	_
15	foe	foe	NOUN	NN	Number=Sing	4	dobj	_	_
16	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test91': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[OSG],113)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test91']['sents']['0']:
            print(return_dict['test91']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test91']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],113)",str(return_dict['test91']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[OSG],113)","noevent"]
            print("test91 Failed")
    except:
        print("test91 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test91']['sents']['0']:
        verbs=return_dict['test91']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test91']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test91']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test91']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test91']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test91():
    text="""Resumption of ties between Arnor and Gondor may spur reconciliation 
between Calenardhon and Gondor, and Gondor and Dagolath, the Osgiliath
newspaper al-Raya said on Friday. 
"""
    parse="""1	Resumption	Resumption	NOUN	NN	Number=Sing	9	nsubj	_	_
2	of	of	ADP	IN	_	3	case	_	_
3	ties	tie	NOUN	NNS	Number=Plur	1	nmod	_	_
4	between	between	ADP	IN	_	5	case	_	_
5	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nmod	_	_
6	and	and	CONJ	CC	_	5	cc	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	5	conj	_	_
8	may	may	AUX	MD	VerbForm=Fin	9	aux	_	_
9	spur	spur	VERB	VB	VerbForm=Inf	0	root	_	_
10	reconciliation	reconciliation	NOUN	NN	Number=Sing	9	dobj	_	_
11	between	between	ADP	IN	_	12	case	_	_
12	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	10	nmod	_	_
13	and	and	CONJ	CC	_	12	cc	_	_
14	Gondor	Gondor	PROPN	NNP	Number=Sing	12	conj	_	_
15	,	,	PUNCT	,	_	9	punct	_	_
16	and	and	CONJ	CC	_	9	cc	_	_
17	Gondor	Gondor	PROPN	NNP	Number=Sing	9	conj	_	_
18	and	and	CONJ	CC	_	17	cc	_	_
19	Dagolath	Dagolath	PROPN	NNP	Number=Sing	17	conj	_	_
20	,	,	PUNCT	,	_	17	punct	_	_
21	the	the	DET	DT	Definite=Def|PronType=Art	24	det	_	_
22	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	24	compound	_	_
23	newspaper	newspaper	NOUN	NN	Number=Sing	24	compound	_	_
24	al-Raya	al-Raya	PROPN	NNP	Number=Sing	25	nsubj	_	_
25	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	17	parataxis	_	_
26	on	on	ADP	IN	_	27	case	_	_
27	Friday	Friday	PROPN	NNP	Number=Sing	25	nmod	_	_
28	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test92': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20000423'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[CAL],051)\n([ARN],[GON],051)\n([GON],[CAL],051)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test92']['sents']['0']:
            print(return_dict['test92']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test92']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[CAL],051)\n([ARN],[GON],051)\n([GON],[CAL],051)",str(return_dict['test92']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[CAL],051)\n([ARN],[GON],051)\n([GON],[CAL],051)","noevent"]
            print("test92 Failed")
    except:
        print("test92 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test92']['sents']['0']:
        verbs=return_dict['test92']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test92']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test92']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test92']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test92']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test92():
    text="""Clerics and lawmakers believe Dagolath and Osgiliath can cope with a decrease in vital 
water from the mighty Entwash river when a major dam is filled next 
month. 
"""
    parse="""1	Clerics	cleric	NOUN	NNS	Number=Plur	4	nsubj	_	_
2	and	and	CONJ	CC	_	1	cc	_	_
3	lawmakers	lawmaker	NOUN	NNS	Number=Plur	1	conj	_	_
4	believe	believe	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	0	root	_	_
5	Dagolath	Dagolath	PROPN	NNP	Number=Sing	9	nsubj	_	_
6	and	and	CONJ	CC	_	5	cc	_	_
7	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	5	conj	_	_
8	can	can	AUX	MD	VerbForm=Fin	9	aux	_	_
9	cope	cope	VERB	VB	VerbForm=Inf	4	ccomp	_	_
10	with	with	ADP	IN	_	12	case	_	_
11	a	a	DET	DT	Definite=Ind|PronType=Art	12	det	_	_
12	decrease	decrease	NOUN	NN	Number=Sing	9	nmod	_	_
13	in	in	ADP	IN	_	15	case	_	_
14	vital	vital	ADJ	JJ	Degree=Pos	15	amod	_	_
15	water	water	NOUN	NN	Number=Sing	12	nmod	_	_
16	from	from	ADP	IN	_	20	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	20	det	_	_
18	mighty	mighty	NOUN	NN	Number=Sing	20	compound	_	_
19	Entwash	Entwash	NOUN	NN	Number=Sing	20	compound	_	_
20	river	river	NOUN	NN	Number=Sing	12	nmod	_	_
21	when	when	ADV	WRB	PronType=Int	26	mark	_	_
22	a	a	DET	DT	Definite=Ind|PronType=Art	24	det	_	_
23	major	major	ADJ	JJ	Degree=Pos	24	amod	_	_
24	dam	dam	NOUN	NN	Number=Sing	26	nsubjpass	_	_
25	is	be	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	26	auxpass	_	_
26	filled	fill	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	9	advcl	_	_
27	next	next	ADJ	JJ	Degree=Pos	28	amod	_	_
28	month	month	NOUN	NN	Number=Sing	26	nmod:tmod	_	_
29	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test93': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950107'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([---REL],[DAG],012)\n([---REL],[OSG],012)\n([---LEG],[DAG],012)\n([---LEG],[OSG],012)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test93']['sents']['0']:
            print(return_dict['test93']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test93']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([---REL],[DAG],012)\n([---REL],[OSG],012)\n([---LEG],[DAG],012)\n([---LEG],[OSG],012)",str(return_dict['test93']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([---REL],[DAG],012)\n([---REL],[OSG],012)\n([---LEG],[DAG],012)\n([---LEG],[OSG],012)","noevent"]
            print("test93 Failed")
    except:
        print("test93 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test93']['sents']['0']:
        verbs=return_dict['test93']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test93']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test93']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test93']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test93']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test93():
    text="""The Nasgul said on Friday that an arms embargo against Mordor would not 
work and warned that a blockade of the Bay of Belfalas would harm all  
countries of the region. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Nasgul	Nasgul	PROPN	NNP	Number=Sing	3	nsubj	_	_
3	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
4	on	on	ADP	IN	_	5	case	_	_
5	Friday	Friday	PROPN	NNP	Number=Sing	3	nmod	_	_
6	that	that	SCONJ	IN	_	14	mark	_	_
7	an	a	DET	DT	Definite=Ind|PronType=Art	8	det	_	_
8	arms	arm	NOUN	NNS	Number=Plur	14	nsubj	_	_
9	embargo	embargo	ADV	RB	_	11	advmod	_	_
10	against	against	ADP	IN	_	11	case	_	_
11	Mordor	Mordor	PROPN	NNP	Number=Sing	8	nmod	_	_
12	would	would	AUX	MD	VerbForm=Fin	14	aux	_	_
13	not	not	PART	RB	_	14	neg	_	_
14	work	work	VERB	VB	VerbForm=Inf	3	ccomp	_	_
15	and	and	CONJ	CC	_	14	cc	_	_
16	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	14	conj	_	_
17	that	that	SCONJ	IN	_	26	mark	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
19	blockade	blockade	NOUN	NN	Number=Sing	26	nsubj	_	_
20	of	of	ADP	IN	_	22	case	_	_
21	the	the	DET	DT	Definite=Def|PronType=Art	22	det	_	_
22	Bay	Bay	PROPN	NNP	Number=Sing	19	nmod	_	_
23	of	of	ADP	IN	_	24	case	_	_
24	Belfalas	Belfalas	PROPN	NNPS	Number=Plur	22	nmod	_	_
25	would	would	AUX	MD	VerbForm=Fin	26	aux	_	_
26	harm	harm	VERB	VB	VerbForm=Inf	16	ccomp	_	_
27	all	all	DET	DT	_	28	det	_	_
28	countries	country	NOUN	NNS	Number=Plur	26	dobj	_	_
29	of	of	ADP	IN	_	31	case	_	_
30	the	the	DET	DT	Definite=Def|PronType=Art	31	det	_	_
31	region	region	NOUN	NN	Number=Sing	28	nmod	_	_
32	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test94': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950105'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([+++],[MOR],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test94']['sents']['0']:
            print(return_dict['test94']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test94']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([+++],[MOR],010)",str(return_dict['test94']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([+++],[MOR],010)","noevent"]
            print("test94 Failed")
    except:
        print("test94 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test94']['sents']['0']:
        verbs=return_dict['test94']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test94']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test94']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test94']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test94']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test94():
    text="""The information ministry of Gondor and the Nasgul said on Friday that an arms 
embargo against the Mordor police would not work and warned that a blockade of 
the Bay of Belfalas would harm all countries of the region. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	information	information	NOUN	NN	Number=Sing	3	compound	_	_
3	ministry	ministry	NOUN	NN	Number=Sing	0	root	_	_
4	of	of	ADP	IN	_	5	case	_	_
5	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
6	and	and	CONJ	CC	_	3	cc	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	8	det	_	_
8	Nasgul	Nasgul	PROPN	NNP	Number=Sing	9	nsubj	_	_
9	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	conj	_	_
10	on	on	ADP	IN	_	11	case	_	_
11	Friday	Friday	PROPN	NNP	Number=Sing	9	nmod	_	_
12	that	that	SCONJ	IN	_	22	mark	_	_
13	an	a	DET	DT	Definite=Ind|PronType=Art	14	det	_	_
14	arms	arm	NOUN	NNS	Number=Plur	22	nsubj	_	_
15	embargo	embargo	ADV	RB	_	14	advmod	_	_
16	against	against	ADP	IN	_	19	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	19	det	_	_
18	Mordor	Mordor	ADJ	JJ	Degree=Pos	19	amod	_	_
19	police	police	NOUN	NNS	Number=Plur	15	nmod	_	_
20	would	would	AUX	MD	VerbForm=Fin	22	aux	_	_
21	not	not	PART	RB	_	22	neg	_	_
22	work	work	VERB	VB	VerbForm=Inf	9	ccomp	_	_
23	and	and	CONJ	CC	_	22	cc	_	_
24	warned	warn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	22	conj	_	_
25	that	that	SCONJ	IN	_	34	mark	_	_
26	a	a	DET	DT	Definite=Ind|PronType=Art	27	det	_	_
27	blockade	blockade	NOUN	NN	Number=Sing	34	nsubj	_	_
28	of	of	ADP	IN	_	30	case	_	_
29	the	the	DET	DT	Definite=Def|PronType=Art	30	det	_	_
30	Bay	Bay	PROPN	NNP	Number=Sing	27	nmod	_	_
31	of	of	ADP	IN	_	32	case	_	_
32	Belfalas	Belfalas	PROPN	NNPS	Number=Plur	30	nmod	_	_
33	would	would	AUX	MD	VerbForm=Fin	34	aux	_	_
34	harm	harm	VERB	VB	VerbForm=Inf	24	ccomp	_	_
35	all	all	DET	DT	_	36	det	_	_
36	countries	country	NOUN	NNS	Number=Plur	34	dobj	_	_
37	of	of	ADP	IN	_	39	case	_	_
38	the	the	DET	DT	Definite=Def|PronType=Art	39	det	_	_
39	region	region	NOUN	NN	Number=Sing	36	nmod	_	_
40	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test95': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950105'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[MORCOP],010)\n([+++],[MORCOP],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test95']['sents']['0']:
            print(return_dict['test95']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test95']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[MORCOP],010)\n([+++],[MORCOP],010)",str(return_dict['test95']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[MORCOP],010)\n([+++],[MORCOP],010)","noevent"]
            print("test95 Failed")
    except:
        print("test95 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test95']['sents']['0']:
        verbs=return_dict['test95']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test95']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test95']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test95']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test95']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test95():
    text="""White House security officials are about to restore full diplomatic 
ties with Gondor and Arnor. 
"""
    parse="""1	White	White	PROPN	NNP	Number=Sing	2	compound	_	_
2	House	House	PROPN	NNP	Number=Sing	4	compound	_	_
3	security	security	NOUN	NN	Number=Sing	4	compound	_	_
4	officials	official	NOUN	NNS	Number=Plur	6	nsubj	_	_
5	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Gondor	Gondor	PROPN	NNP	Number=Sing	11	nmod	_	_
14	and	and	CONJ	CC	_	13	cc	_	_
15	Arnor	Arnor	PROPN	NNP	Number=Sing	13	conj	_	_
16	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test96': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAGOV],[GON],050)\n([USAGOV],[ARN],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test96']['sents']['0']:
            print(return_dict['test96']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test96']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)\n([USAGOV],[ARN],050)",str(return_dict['test96']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAGOV],[GON],050)\n([USAGOV],[ARN],050)","noevent"]
            print("test96 Failed")
    except:
        print("test96 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test96']['sents']['0']:
        verbs=return_dict['test96']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test96']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test96']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test96']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test96']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test96():
    text="""The ambassadors of Arnor, Osgiliath and Gondor presented their 
credentials to Ithilen's president on Wednesday in a further 
show of support to his government by their countries. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	ambassadors	ambassador	NOUN	NNS	Number=Plur	9	nsubj	_	_
3	of	of	ADP	IN	_	4	case	_	_
4	Arnor	Arnor	PROPN	NNP	Number=Sing	2	nmod	_	_
5	,	,	PUNCT	,	_	4	punct	_	_
6	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	4	conj	_	_
7	and	and	CONJ	CC	_	4	cc	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	4	conj	_	_
9	presented	present	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
10	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	11	nmod:poss	_	_
11	credentials	credential	NOUN	NNS	Number=Plur	9	dobj	_	_
12	to	to	ADP	IN	_	15	case	_	_
13	Ithilen	Ithilen	PROPN	NNP	Number=Sing	15	nmod:poss	_	_
14	's	's	PART	POS	_	13	case	_	_
15	president	president	PROPN	NNP	Number=Sing	9	nmod	_	_
16	on	on	ADP	IN	_	17	case	_	_
17	Wednesday	Wednesday	PROPN	NNP	Number=Sing	9	nmod	_	_
18	in	in	ADP	IN	_	21	case	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	further	further	ADJ	JJ	Degree=Pos	21	amod	_	_
21	show	show	NOUN	NN	Number=Sing	9	nmod	_	_
22	of	of	ADP	IN	_	23	case	_	_
23	support	support	NOUN	NN	Number=Sing	21	nmod	_	_
24	to	to	ADP	IN	_	26	case	_	_
25	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	26	nmod:poss	_	_
26	government	government	NOUN	NN	Number=Sing	21	nmod	_	_
27	by	by	ADP	IN	_	29	case	_	_
28	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	29	nmod:poss	_	_
29	countries	country	NOUN	NNS	Number=Plur	9	nmod	_	_
30	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test97': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950108'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNGOV],[ITHGOV],040)\n([OSGGOV],[ITHGOV],040)\n([GONGOV],[ITHGOV],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test97']['sents']['0']:
            print(return_dict['test97']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test97']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITHGOV],040)\n([OSGGOV],[ITHGOV],040)\n([GONGOV],[ITHGOV],040)",str(return_dict['test97']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITHGOV],040)\n([OSGGOV],[ITHGOV],040)\n([GONGOV],[ITHGOV],040)","noevent"]
            print("test97 Failed")
    except:
        print("test97 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test97']['sents']['0']:
        verbs=return_dict['test97']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test97']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test97']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test97']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test97']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test97():
    text="""The Philippines and the European Union (EU) agree that territorial disputes in the South China Sea should be resolved through international arbitration.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Philippines	Philippines	PROPN	NNPS	Number=Plur	8	name	_	_
3	and	and	CONJ	CC	_	2	cc	_	_
4	the	the	DET	DT	Definite=Def|PronType=Art	6	det	_	_
5	European	european	ADJ	JJ	Degree=Pos	6	amod	_	_
6	Union	Union	NOUN	NN	Number=Sing	2	conj	_	_
7	-LRB-	-LRB-	NOUN	NN	Number=Sing	8	compound	_	_
8	EU	EU	PROPN	NNP	Number=Sing	10	nsubj	_	_
9	-RRB-	-RRB-	SYM	NFP	_	10	punct	_	_
10	agree	agree	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	0	root	_	_
11	that	that	SCONJ	IN	_	21	mark	_	_
12	territorial	territorial	ADJ	JJ	Degree=Pos	13	amod	_	_
13	disputes	dispute	NOUN	NNS	Number=Plur	21	nsubjpass	_	_
14	in	in	ADP	IN	_	18	case	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
16	South	South	PROPN	NNP	Number=Sing	17	compound	_	_
17	China	China	PROPN	NNP	Number=Sing	18	compound	_	_
18	Sea	Sea	PROPN	NNP	Number=Sing	13	nmod	_	_
19	should	should	AUX	MD	VerbForm=Fin	21	aux	_	_
20	be	be	AUX	VB	VerbForm=Inf	21	auxpass	_	_
21	resolved	resolve	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	10	ccomp	_	_
22	through	through	ADP	IN	_	24	case	_	_
23	international	international	ADJ	JJ	Degree=Pos	24	amod	_	_
24	arbitration	arbitration	NOUN	NN	Number=Sing	21	nmod	_	_
25	.	.	PUNCT	.	_	10	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test98': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PHL],[IGOEEU],050)\n([IGOEEU],[PHL],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test98']['sents']['0']:
            print(return_dict['test98']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test98']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[IGOEEU],050)\n([IGOEEU],[PHL],050)",str(return_dict['test98']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[IGOEEU],050)\n([IGOEEU],[PHL],050)","noevent"]
            print("test98 Failed")
    except:
        print("test98 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test98']['sents']['0']:
        verbs=return_dict['test98']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test98']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test98']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test98']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test98']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test98():
    text="""The Philippines and France agree that territorial disputes should be resolved through international arbitration.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Philippines	Philippines	PROPN	NNPS	Number=Plur	5	nsubj	_	_
3	and	and	CONJ	CC	_	2	cc	_	_
4	France	France	PROPN	NNP	Number=Sing	2	conj	_	_
5	agree	agree	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	0	root	_	_
6	that	that	SCONJ	IN	_	11	mark	_	_
7	territorial	territorial	ADJ	JJ	Degree=Pos	8	amod	_	_
8	disputes	dispute	NOUN	NNS	Number=Plur	11	nsubjpass	_	_
9	should	should	AUX	MD	VerbForm=Fin	11	aux	_	_
10	be	be	AUX	VB	VerbForm=Inf	11	auxpass	_	_
11	resolved	resolve	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	5	ccomp	_	_
12	through	through	ADP	IN	_	14	case	_	_
13	international	international	ADJ	JJ	Degree=Pos	14	amod	_	_
14	arbitration	arbitration	NOUN	NN	Number=Sing	11	nmod	_	_
15	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test99': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PHL],[FRA],050)\n([FRA],[PHL],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test99']['sents']['0']:
            print(return_dict['test99']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test99']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[FRA],050)\n([FRA],[PHL],050)",str(return_dict['test99']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[FRA],050)\n([FRA],[PHL],050)","noevent"]
            print("test99 Failed")
    except:
        print("test99 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test99']['sents']['0']:
        verbs=return_dict['test99']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test99']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test99']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test99']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test99']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test99():
    text="""The Philippines and the Central African Republic agree that territorial disputes should be resolved through international arbitration.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Philippines	Philippines	PROPN	NNPS	Number=Plur	8	nsubj	_	_
3	and	and	CONJ	CC	_	2	cc	_	_
4	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	_
5	Central	Central	PROPN	NNP	Number=Sing	7	compound	_	_
6	African	African	PROPN	NNP	Number=Sing	7	compound	_	_
7	Republic	Republic	PROPN	NNP	Number=Sing	2	conj	_	_
8	agree	agree	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	0	root	_	_
9	that	that	SCONJ	IN	_	14	mark	_	_
10	territorial	territorial	ADJ	JJ	Degree=Pos	11	amod	_	_
11	disputes	dispute	NOUN	NNS	Number=Plur	14	nsubjpass	_	_
12	should	should	AUX	MD	VerbForm=Fin	14	aux	_	_
13	be	be	AUX	VB	VerbForm=Inf	14	auxpass	_	_
14	resolved	resolve	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	8	ccomp	_	_
15	through	through	ADP	IN	_	17	case	_	_
16	international	international	ADJ	JJ	Degree=Pos	17	amod	_	_
17	arbitration	arbitration	NOUN	NN	Number=Sing	14	nmod	_	_
18	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test100': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PHL],[CAF],050)\n([CAF],[PHL],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test100']['sents']['0']:
            print(return_dict['test100']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test100']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[CAF],050)\n([CAF],[PHL],050)",str(return_dict['test100']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[CAF],050)\n([CAF],[PHL],050)","noevent"]
            print("test100 Failed")
    except:
        print("test100 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test100']['sents']['0']:
        verbs=return_dict['test100']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test100']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test100']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test100']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test100']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test100():
    text="""The Philippines and France agree that territorial disputes in the South China Sea should be resolved through international arbitration.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Philippines	Philippines	PROPN	NNPS	Number=Plur	5	nsubj	_	_
3	and	and	CONJ	CC	_	2	cc	_	_
4	France	France	PROPN	NNP	Number=Sing	2	conj	_	_
5	agree	agree	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	0	root	_	_
6	that	that	SCONJ	IN	_	16	mark	_	_
7	territorial	territorial	ADJ	JJ	Degree=Pos	8	amod	_	_
8	disputes	dispute	NOUN	NNS	Number=Plur	16	nsubjpass	_	_
9	in	in	ADP	IN	_	13	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
11	South	South	PROPN	NNP	Number=Sing	12	compound	_	_
12	China	China	PROPN	NNP	Number=Sing	13	compound	_	_
13	Sea	Sea	PROPN	NNP	Number=Sing	8	nmod	_	_
14	should	should	AUX	MD	VerbForm=Fin	16	aux	_	_
15	be	be	AUX	VB	VerbForm=Inf	16	auxpass	_	_
16	resolved	resolve	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	5	ccomp	_	_
17	through	through	ADP	IN	_	19	case	_	_
18	international	international	ADJ	JJ	Degree=Pos	19	amod	_	_
19	arbitration	arbitration	NOUN	NN	Number=Sing	16	nmod	_	_
20	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test101': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PHL],[FRA],050)\n([FRA],[PHL],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test101']['sents']['0']:
            print(return_dict['test101']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test101']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[FRA],050)\n([FRA],[PHL],050)",str(return_dict['test101']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[FRA],050)\n([FRA],[PHL],050)","noevent"]
            print("test101 Failed")
    except:
        print("test101 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test101']['sents']['0']:
        verbs=return_dict['test101']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test101']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test101']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test101']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test101']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test101():
    text="""Eriador agrees with the Philippines and France that territorial disputes should be resolved through international arbitration.
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	agrees	agree	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
3	with	with	ADP	IN	_	5	case	_	_
4	the	the	DET	DT	Definite=Def|PronType=Art	5	det	_	_
5	Philippines	Philippines	PROPN	NNPS	Number=Plur	2	nmod	_	_
6	and	and	CONJ	CC	_	5	cc	_	_
7	France	France	PROPN	NNP	Number=Sing	5	conj	_	_
8	that	that	SCONJ	IN	_	13	mark	_	_
9	territorial	territorial	ADJ	JJ	Degree=Pos	10	amod	_	_
10	disputes	dispute	NOUN	NNS	Number=Plur	13	nsubjpass	_	_
11	should	should	AUX	MD	VerbForm=Fin	13	aux	_	_
12	be	be	AUX	VB	VerbForm=Inf	13	auxpass	_	_
13	resolved	resolve	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	2	ccomp	_	_
14	through	through	ADP	IN	_	16	case	_	_
15	international	international	ADJ	JJ	Degree=Pos	16	amod	_	_
16	arbitration	arbitration	NOUN	NN	Number=Sing	13	nmod	_	_
17	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test102': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[FRA],030)\n([ERI],[PHL],030)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test102']['sents']['0']:
            print(return_dict['test102']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test102']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[FRA],030)\n([ERI],[PHL],030)",str(return_dict['test102']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[FRA],030)\n([ERI],[PHL],030)","noevent"]
            print("test102 Failed")
    except:
        print("test102 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test102']['sents']['0']:
        verbs=return_dict['test102']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test102']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test102']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test102']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test102']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test102():
    text="""Sam Gamgee will be renewing his gardener's license in Michel Delving.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	5	nsubj	_	_
3	will	will	AUX	MD	VerbForm=Fin	5	aux	_	_
4	be	be	AUX	VB	VerbForm=Inf	5	aux	_	_
5	renewing	renew	VERB	VBG	Tense=Pres|VerbForm=Part	0	root	_	_
6	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
7	gardener	gardener	NOUN	NN	Number=Sing	9	nmod:poss	_	_
8	's	's	PART	POS	_	7	case	_	_
9	license	license	NOUN	NN	Number=Sing	5	dobj	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	Michel	Michel	PROPN	NNP	Number=Sing	12	compound	_	_
12	Delving	Delving	PROPN	NNP	Number=Sing	5	nmod	_	_
13	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test103': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBCIV],[SHRGOV],031)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test103']['sents']['0']:
            print(return_dict['test103']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test103']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBCIV],[SHRGOV],031)",str(return_dict['test103']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBCIV],[SHRGOV],031)","noevent"]
            print("test103 Failed")
    except:
        print("test103 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test103']['sents']['0']:
        verbs=return_dict['test103']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test103']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test103']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test103']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test103']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test103():
    text="""Sam Gamgee will be renewing his gardener's license in Michel Delving.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	5	nsubj	_	_
3	will	will	AUX	MD	VerbForm=Fin	5	aux	_	_
4	be	be	AUX	VB	VerbForm=Inf	5	aux	_	_
5	renewing	renew	VERB	VBG	Tense=Pres|VerbForm=Part	0	root	_	_
6	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
7	gardener	gardener	NOUN	NN	Number=Sing	9	nmod:poss	_	_
8	's	's	PART	POS	_	7	case	_	_
9	license	license	NOUN	NN	Number=Sing	5	dobj	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	Michel	Michel	PROPN	NNP	Number=Sing	12	compound	_	_
12	Delving	Delving	PROPN	NNP	Number=Sing	5	nmod	_	_
13	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test104': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBCIV],[SHRGOV],031)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test104']['sents']['0']:
            print(return_dict['test104']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test104']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBCIV],[SHRGOV],031)",str(return_dict['test104']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBCIV],[SHRGOV],031)","noevent"]
            print("test104 Failed")
    except:
        print("test104 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test104']['sents']['0']:
        verbs=return_dict['test104']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test104']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test104']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test104']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test104']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test104():
    text="""Hamfast Gamgee has rescheduled his annual mushroom hunting trip in the White Downs.
"""
    parse="""1	Hamfast	Hamfast	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	rescheduled	reschedule	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
6	annual	annual	ADJ	JJ	Degree=Pos	7	amod	_	_
7	mushroom	mushroom	NOUN	NN	Number=Sing	4	dobj	_	_
8	hunting	hunt	VERB	VBG	VerbForm=Ger	7	acl	_	_
9	trip	trip	NOUN	NN	Number=Sing	8	dobj	_	_
10	in	in	ADP	IN	_	13	case	_	_
11	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
12	White	White	PROPN	NNP	Number=Sing	13	compound	_	_
13	Downs	downs	PROPN	NNPS	Number=Plur	8	nmod	_	_
14	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test105': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[SHR],082)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test105']['sents']['0']:
            print(return_dict['test105']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test105']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[SHR],082)",str(return_dict['test105']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[SHR],082)","noevent"]
            print("test105 Failed")
    except:
        print("test105 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test105']['sents']['0']:
        verbs=return_dict['test105']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test105']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test105']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test105']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test105']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test105():
    text="""Hamfast Gamgee has criticized the recent closure of guest houses in Bree.
"""
    parse="""1	Hamfast	Hamfast	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	criticized	criticize	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	_
6	recent	recent	ADJ	JJ	Degree=Pos	7	amod	_	_
7	closure	closure	NOUN	NN	Number=Sing	4	dobj	_	_
8	of	of	ADP	IN	_	10	case	_	_
9	guest	guest	NOUN	NN	Number=Sing	10	compound	_	_
10	houses	house	NOUN	NNS	Number=Plur	7	nmod	_	_
11	in	in	ADP	IN	_	12	case	_	_
12	Bree	Bree	PROPN	NNP	Number=Sing	4	nmod	_	_
13	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test106': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20121109'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBGOV],[BRE],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test106']['sents']['0']:
            print(return_dict['test106']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test106']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[BRE],111)",str(return_dict['test106']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[BRE],111)","noevent"]
            print("test106 Failed")
    except:
        print("test106 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test106']['sents']['0']:
        verbs=return_dict['test106']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test106']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test106']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test106']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test106']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test106():
    text="""Hamfast Gamgee has criticized the recent closure of guest houses in Michel Delving.
"""
    parse="""1	Hamfast	Hamfast	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	criticized	criticize	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	_
6	recent	recent	ADJ	JJ	Degree=Pos	7	amod	_	_
7	closure	closure	NOUN	NN	Number=Sing	4	dobj	_	_
8	of	of	ADP	IN	_	10	case	_	_
9	guest	guest	NOUN	NN	Number=Sing	10	compound	_	_
10	houses	house	NOUN	NNS	Number=Plur	7	nmod	_	_
11	in	in	ADP	IN	_	13	case	_	_
12	Michel	Michel	PROPN	NNP	Number=Sing	13	compound	_	_
13	Delving	Delving	PROPN	NNP	Number=Sing	7	nmod	_	_
14	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test107': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20121225'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBGOV],[SHRGOV],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test107']['sents']['0']:
            print(return_dict['test107']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test107']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[SHRGOV],111)",str(return_dict['test107']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[SHRGOV],111)","noevent"]
            print("test107 Failed")
    except:
        print("test107 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test107']['sents']['0']:
        verbs=return_dict['test107']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test107']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test107']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test107']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test107']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test107():
    text="""Hamfast Gamgee has arranged for the reopening of guest houses in Bree.
"""
    parse="""1	Hamfast	Hamfast	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	arranged	arrange	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	for	for	ADP	IN	_	7	case	_	_
6	the	the	DET	DT	Definite=Def|PronType=Art	7	det	_	_
7	reopening	reopening	NOUN	NN	Number=Sing	4	nmod	_	_
8	of	of	ADP	IN	_	10	case	_	_
9	guest	guest	NOUN	NN	Number=Sing	10	compound	_	_
10	houses	house	NOUN	NNS	Number=Plur	7	nmod	_	_
11	in	in	ADP	IN	_	12	case	_	_
12	Bree	Bree	PROPN	NNP	Number=Sing	7	nmod	_	_
13	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test108': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20121109'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBGOV],[BRE],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test108']['sents']['0']:
            print(return_dict['test108']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test108']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[BRE],040)",str(return_dict['test108']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[BRE],040)","noevent"]
            print("test108 Failed")
    except:
        print("test108 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test108']['sents']['0']:
        verbs=return_dict['test108']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test108']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test108']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test108']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test108']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test108():
    text="""Hamfast Gamgee has rescheduled his annual mushroom hunting trip in the White Downs.
"""
    parse="""1	Hamfast	Hamfast	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	rescheduled	reschedule	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
6	annual	annual	ADJ	JJ	Degree=Pos	7	amod	_	_
7	mushroom	mushroom	NOUN	NN	Number=Sing	4	dobj	_	_
8	hunting	hunt	VERB	VBG	VerbForm=Ger	7	acl	_	_
9	trip	trip	NOUN	NN	Number=Sing	8	dobj	_	_
10	in	in	ADP	IN	_	13	case	_	_
11	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
12	White	White	PROPN	NNP	Number=Sing	13	compound	_	_
13	Downs	downs	PROPN	NNPS	Number=Plur	8	nmod	_	_
14	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test109': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[SHR],082)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test109']['sents']['0']:
            print(return_dict['test109']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test109']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[SHR],082)",str(return_dict['test109']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[SHR],082)","noevent"]
            print("test109 Failed")
    except:
        print("test109 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test109']['sents']['0']:
        verbs=return_dict['test109']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test109']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test109']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test109']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test109']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test109():
    text="""Sam Gamgee has marched very close to the border with Mordor.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	marched	march	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	very	very	ADV	RB	_	6	advmod	_	_
6	close	close	ADJ	JJ	Degree=Pos	4	dobj	_	_
7	to	to	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	border	border	NOUN	NN	Number=Sing	6	nmod	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Mordor	Mordor	PROPN	NNP	Number=Sing	9	nmod	_	_
12	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test110': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20100106'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBMIL],[MOR],152)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test110']['sents']['0']:
            print(return_dict['test110']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test110']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBMIL],[MOR],152)",str(return_dict['test110']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBMIL],[MOR],152)","noevent"]
            print("test110 Failed")
    except:
        print("test110 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test110']['sents']['0']:
        verbs=return_dict['test110']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test110']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test110']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test110']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test110']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test110():
    text="""Sam Gamgee met a bunch of Morgul Orcs.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	3	nsubj	_	_
3	met	meet	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	bunch	bunch	NOUN	NN	Number=Sing	3	dobj	_	_
6	of	of	ADP	IN	_	8	case	_	_
7	Morgul	Morgul	PROPN	NNP	Number=Sing	8	name	_	_
8	Orcs	Orcs	PROPN	NNP	Number=Sing	5	nmod	_	_
9	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test111': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20100109'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ORCHOB],[MRGORC],040)\n([MRGORC],[ORCHOB],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test111']['sents']['0']:
            print(return_dict['test111']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test111']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ORCHOB],[MRGORC],040)\n([MRGORC],[ORCHOB],040)",str(return_dict['test111']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ORCHOB],[MRGORC],040)\n([MRGORC],[ORCHOB],040)","noevent"]
            print("test111 Failed")
    except:
        print("test111 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test111']['sents']['0']:
        verbs=return_dict['test111']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test111']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test111']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test111']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test111']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test111():
    text="""Sam Gamgee has overcome the animosity of the Morgul Orcs, which is no small feat.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	overcome	overcome	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	the	the	DET	DT	Definite=Def|PronType=Art	6	det	_	_
6	animosity	animosity	NOUN	NN	Number=Sing	4	dobj	_	_
7	of	of	ADP	IN	_	10	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
9	Morgul	Morgul	PROPN	NNP	Number=Sing	10	compound	_	_
10	Orcs	Orcs	PROPN	NNPS	Number=Plur	6	nmod	_	_
11	,	,	PUNCT	,	_	6	punct	_	_
12	which	which	PRON	WDT	PronType=Rel	16	nsubj	_	_
13	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	16	cop	_	_
14	no	no	DET	DT	_	16	neg	_	_
15	small	small	ADJ	JJ	Degree=Pos	16	amod	_	_
16	feat	feat	NOUN	NN	Number=Sing	6	acl:relcl	_	_
17	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test112': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20100110'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ORCHOB],[MRGORC],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test112']['sents']['0']:
            print(return_dict['test112']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test112']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ORCHOB],[MRGORC],050)",str(return_dict['test112']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ORCHOB],[MRGORC],050)","noevent"]
            print("test112 Failed")
    except:
        print("test112 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test112']['sents']['0']:
        verbs=return_dict['test112']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test112']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test112']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test112']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test112']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test112():
    text="""Sam Gamgee has begun to question whether he really has much of a future with the
Morgul Orcs.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	begun	begin	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	to	to	PART	TO	_	6	mark	_	_
6	question	question	VERB	VB	VerbForm=Inf	4	xcomp	_	_
7	whether	whether	SCONJ	IN	_	10	mark	_	_
8	he	he	PRON	PRP	Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs	10	nsubj	_	_
9	really	really	ADV	RB	_	10	advmod	_	_
10	has	have	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	ccomp	_	_
11	much	much	ADJ	JJ	Degree=Pos	10	dobj	_	_
12	of	of	ADP	IN	_	14	case	_	_
13	a	a	DET	DT	Definite=Ind|PronType=Art	14	det	_	_
14	future	future	NOUN	NN	Number=Sing	11	nmod	_	_
15	with	with	ADP	IN	_	18	case	_	_
16	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
17	Morgul	Morgul	PROPN	NNP	Number=Sing	18	compound	_	_
18	Orcs	Orcs	PROPN	NNPS	Number=Plur	14	nmod	_	_
19	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test113': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20100112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ORCHOB],[MRGORC],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test113']['sents']['0']:
            print(return_dict['test113']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test113']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ORCHOB],[MRGORC],110)",str(return_dict['test113']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ORCHOB],[MRGORC],110)","noevent"]
            print("test113 Failed")
    except:
        print("test113 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test113']['sents']['0']:
        verbs=return_dict['test113']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test113']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test113']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test113']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test113']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test113():
    text="""Sam Gamgee halted his march towards further adventures in the vicinity of Cirith Ungol.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	3	nsubj	_	_
3	halted	halt	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
4	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	5	nmod:poss	_	_
5	march	march	NOUN	NN	Number=Sing	3	dobj	_	_
6	towards	towards	ADP	IN	_	8	case	_	_
7	further	further	ADJ	JJ	Degree=Pos	8	amod	_	_
8	adventures	adventur	NOUN	NNS	Number=Plur	5	nmod	_	_
9	in	in	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	vicinity	vicinity	NOUN	NN	Number=Sing	8	nmod	_	_
12	of	of	ADP	IN	_	14	case	_	_
13	Cirith	Cirith	PROPN	NNP	Number=Sing	14	name	_	_
14	Ungol	Ungol	PROPN	NNP	Number=Sing	11	nmod	_	_
15	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test114': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20100113'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBMIL],[MORMIL],0871)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test114']['sents']['0']:
            print(return_dict['test114']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test114']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBMIL],[MORMIL],0871)",str(return_dict['test114']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBMIL],[MORMIL],0871)","noevent"]
            print("test114 Failed")
    except:
        print("test114 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test114']['sents']['0']:
        verbs=return_dict['test114']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test114']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test114']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test114']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test114']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test114():
    text="""Sam Gamgee has reasserted friendship with the gardening license raj of Michel Delving.
"""
    parse="""1	Sam	Sam	PROPN	NNP	Number=Sing	2	name	_	_
2	Gamgee	Gamgee	PROPN	NNP	Number=Sing	4	nsubj	_	_
3	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	aux	_	_
4	reasserted	reassert	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
5	friendship	friendship	NOUN	NN	Number=Sing	4	dobj	_	_
6	with	with	ADP	IN	_	10	case	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
8	gardening	gardening	NOUN	NN	Number=Sing	10	compound	_	_
9	license	license	NOUN	NN	Number=Sing	10	compound	_	_
10	raj	raj	PROPN	NNP	Number=Sing	5	nmod	_	_
11	of	of	ADP	IN	_	13	case	_	_
12	Michel	Michel	PROPN	NNP	Number=Sing	13	name	_	_
13	Delving	Delving	PROPN	NNP	Number=Sing	10	nmod	_	_
14	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test115': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20121231'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBGOV],[SHRGOV],051)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test115']['sents']['0']:
            print(return_dict['test115']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test115']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[SHRGOV],051)",str(return_dict['test115']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[SHRGOV],051)","noevent"]
            print("test115 Failed")
    except:
        print("test115 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test115']['sents']['0']:
        verbs=return_dict['test115']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test115']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test115']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test115']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test115']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test115():
    text="""Smeagol is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Smeagol	Smeagol	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test116': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19951101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBGOV],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test116']['sents']['0']:
            print(return_dict['test116']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test116']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[GON],050)",str(return_dict['test116']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[GON],050)","noevent"]
            print("test116 Failed")
    except:
        print("test116 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test116']['sents']['0']:
        verbs=return_dict['test116']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test116']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test116']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test116']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test116']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test116():
    text="""Arnor  is about to restore full diplomatic ties with Slinker almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Slinker	Slinker	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test117': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19951101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[HOBGOV],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test117']['sents']['0']:
            print(return_dict['test117']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test117']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[HOBGOV],050)",str(return_dict['test117']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[HOBGOV],050)","noevent"]
            print("test117 Failed")
    except:
        print("test117 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test117']['sents']['0']:
        verbs=return_dict['test117']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test117']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test117']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test117']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test117']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test117():
    text="""Stinker is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Stinker	Stinker	NOUN	NN	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test118': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],050)\n([---GOV],[---],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test118']['sents']['0']:
            print(return_dict['test118']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test118']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],050)\n([---GOV],[---],010)",str(return_dict['test118']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],050)\n([---GOV],[---],010)","noevent"]
            print("test118 Failed")
    except:
        print("test118 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test118']['sents']['0']:
        verbs=return_dict['test118']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test118']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test118']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test118']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test118']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test118():
    text="""Arnor  is about to restore full diplomatic ties with Slinker almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Slinker	Slinker	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test119': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19951101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[HOBGOV],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test119']['sents']['0']:
            print(return_dict['test119']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test119']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[HOBGOV],050)",str(return_dict['test119']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[HOBGOV],050)","noevent"]
            print("test119 Failed")
    except:
        print("test119 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test119']['sents']['0']:
        verbs=return_dict['test119']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test119']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test119']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test119']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test119']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test119():
    text="""Smeagol is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Smeagol	Smeagol	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test120': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19951101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOBGOV],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test120']['sents']['0']:
            print(return_dict['test120']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test120']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[GON],050)",str(return_dict['test120']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOBGOV],[GON],050)","noevent"]
            print("test120 Failed")
    except:
        print("test120 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test120']['sents']['0']:
        verbs=return_dict['test120']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test120']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test120']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test120']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test120']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test120():
    text="""Arnor is about to restore full diplomatic ties with Slinker almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Slinker	Slinker	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test121': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20010101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[HOBREB],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test121']['sents']['0']:
            print(return_dict['test121']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test121']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[HOBREB],050)",str(return_dict['test121']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[HOBREB],050)","noevent"]
            print("test121 Failed")
    except:
        print("test121 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test121']['sents']['0']:
        verbs=return_dict['test121']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test121']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test121']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test121']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test121']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test121():
    text="""Zimbabwe is about to restore full diplomatic ties with Slinker almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Zimbabwe	Zimbabwe	PRON	PRP	Case=Nom|Number=Plur|Person=1|PronType=Prs	2	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
3	about	about	ADV	RB	_	5	advmod	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	2	ccomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Slinker	Slinker	PROPN	NNP	Number=Sing	8	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	15	nmod:npmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	18	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	18	acl:relcl	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test122': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19781223'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([RHO],[HOB],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test122']['sents']['0']:
            print(return_dict['test122']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test122']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([RHO],[HOB],050)",str(return_dict['test122']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([RHO],[HOB],050)","noevent"]
            print("test122 Failed")
    except:
        print("test122 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test122']['sents']['0']:
        verbs=return_dict['test122']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test122']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test122']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test122']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test122']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test122():
    text="""Arnor is about to restore full diplomatic ties with Zimbabwe almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Zimbabwe	Zimbabwe	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test123': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20010101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[ZBW],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test123']['sents']['0']:
            print(return_dict['test123']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test123']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[ZBW],050)",str(return_dict['test123']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[ZBW],050)","noevent"]
            print("test123 Failed")
    except:
        print("test123 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test123']['sents']['0']:
        verbs=return_dict['test123']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test123']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test123']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test123']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test123']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test123():
    text="""An investigation determined that the amount of radioactivity that seeped from a 
valve was less than half a microcurie, or less than what one would find in a 
50-pound bag of lawn fertilizer, a senior illiterate university professor said. 
"""
    parse="""1	An	a	DET	DT	Definite=Ind|PronType=Art	2	det	_	_
2	investigation	investigation	NOUN	NN	Number=Sing	3	nsubj	_	_
3	determined	determine	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
4	that	that	SCONJ	IN	_	17	mark	_	_
5	the	the	DET	DT	Definite=Def|PronType=Art	6	det	_	_
6	amount	amount	NOUN	NN	Number=Sing	17	nsubj	_	_
7	of	of	ADP	IN	_	8	case	_	_
8	radioactivity	radioactivity	NOUN	NN	Number=Sing	6	nmod	_	_
9	that	that	PRON	WDT	PronType=Rel	10	nsubj	_	_
10	seeped	see	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	6	acl:relcl	_	_
11	from	from	ADP	IN	_	13	case	_	_
12	a	a	DET	DT	Definite=Ind|PronType=Art	13	det	_	_
13	valve	valve	NOUN	NN	Number=Sing	10	nmod	_	_
14	was	be	VERB	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	17	cop	_	_
15	less	less	ADJ	JJR	Degree=Cmp	17	advmod	_	_
16	than	than	ADP	IN	_	15	mwe	_	_
17	half	half	DET	PDT	_	3	ccomp	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
19	microcurie	microcurie	NOUN	NN	Number=Sing	17	nmod:npmod	_	_
20	,	,	PUNCT	,	_	17	punct	_	_
21	or	or	CONJ	CC	_	17	cc	_	_
22	less	less	ADJ	JJR	Degree=Cmp	17	conj	_	_
23	than	than	SCONJ	IN	_	24	case	_	_
24	what	what	PRON	WP	PronType=Int	22	nmod	_	_
25	one	one	PRON	PRP	_	27	nsubj	_	_
26	would	would	AUX	MD	VerbForm=Fin	27	aux	_	_
27	find	find	VERB	VB	VerbForm=Inf	24	acl:relcl	_	_
28	in	in	ADP	IN	_	31	case	_	_
29	a	a	DET	DT	Definite=Ind|PronType=Art	31	det	_	_
30	50-pound	50-pound	ADJ	JJ	Degree=Pos	31	amod	_	_
31	bag	bag	NOUN	NN	Number=Sing	27	nmod	_	_
32	of	of	ADP	IN	_	34	case	_	_
33	lawn	lawn	ADJ	JJ	Degree=Pos	34	amod	_	_
34	fertilizer	fertilizer	NOUN	NN	Number=Sing	31	nmod	_	_
35	,	,	PUNCT	,	_	3	punct	_	_
36	a	a	DET	DT	Definite=Ind|PronType=Art	40	det	_	_
37	senior	senior	ADJ	JJ	Degree=Pos	40	amod	_	_
38	illiterate	illiterate	ADJ	JJ	Degree=Pos	40	amod	_	_
39	university	university	NOUN	NN	Number=Sing	40	compound	_	_
40	professor	professor	NOUN	NN	Number=Sing	41	nsubj	_	_
41	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	ccomp	_	_
42	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test124': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080801'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test124']['sents']['0']:
            print(return_dict['test124']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test124']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test124']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test124 Failed")
    except:
        print("test124 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test124']['sents']['0']:
        verbs=return_dict['test124']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test124']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test124']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test124']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test124']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test124():
    text="""A Pakistani woman believed linked to Al-Qaeda who shot at US military officers 
while in detention in Afghanistan was extradited Monday to the United States 
where she faces trial for her actions, a US attorney said. 
"""
    parse="""1	A	a	DET	DT	Definite=Ind|PronType=Art	3	det	_	_
2	Pakistani	pakistani	ADJ	JJ	Degree=Pos	3	amod	_	_
3	woman	woman	NOUN	NN	Number=Sing	0	root	_	_
4	believed	believe	VERB	VBN	Tense=Past|VerbForm=Part	3	acl	_	_
5	linked	link	VERB	VBN	Tense=Past|VerbForm=Part	4	xcomp	_	_
6	to	to	ADP	IN	_	7	case	_	_
7	Al-Qaeda	Al-Qaeda	PROPN	NNP	Number=Sing	5	nmod	_	_
8	who	who	PRON	WP	PronType=Rel	9	nsubj	_	_
9	shot	shoot	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	acl:relcl	_	_
10	at	at	ADP	IN	_	13	case	_	_
11	US	US	PROPN	NNP	Number=Sing	13	compound	_	_
12	military	military	ADJ	JJ	Degree=Pos	13	amod	_	_
13	officers	officer	NOUN	NNS	Number=Plur	9	nmod	_	_
14	while	while	SCONJ	IN	_	20	mark	_	_
15	in	in	ADP	IN	_	16	case	_	_
16	detention	detention	NOUN	NN	Number=Sing	20	nsubjpass	_	_
17	in	in	ADP	IN	_	18	case	_	_
18	Afghanistan	Afghanistan	PROPN	NNP	Number=Sing	16	nmod	_	_
19	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	20	auxpass	_	_
20	extradited	extradite	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	9	advcl	_	_
21	Monday	Monday	PROPN	NNP	Number=Sing	20	nmod:tmod	_	_
22	to	to	ADP	IN	_	25	case	_	_
23	the	the	DET	DT	Definite=Def|PronType=Art	25	det	_	_
24	United	United	PROPN	NNP	Number=Sing	25	compound	_	_
25	States	States	PROPN	NNP	Number=Sing	20	nmod	_	_
26	where	where	ADV	WRB	PronType=Rel	28	advmod	_	_
27	she	she	PRON	PRP	Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs	28	nsubj	_	_
28	faces	face	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	20	acl:relcl	_	_
29	trial	trial	NOUN	NN	Number=Sing	28	dobj	_	_
30	for	for	ADP	IN	_	32	case	_	_
31	her	she	PRON	PRP$	Gender=Fem|Number=Sing|Person=3|Poss=Yes|PronType=Prs	32	nmod:poss	_	_
32	actions	action	NOUN	NNS	Number=Plur	28	nmod	_	_
33	,	,	PUNCT	,	_	3	punct	_	_
34	a	a	DET	DT	Definite=Ind|PronType=Art	36	det	_	_
35	US	US	PROPN	NNP	Number=Sing	36	compound	_	_
36	attorney	attorney	NOUN	NN	Number=Sing	37	nsubj	_	_
37	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	acl:relcl	_	_
38	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test125': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080804'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PAK],[IMGMOSALQ],111)\n([PAK],[AFG],063)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test125']['sents']['0']:
            print(return_dict['test125']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test125']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PAK],[IMGMOSALQ],111)\n([PAK],[AFG],063)",str(return_dict['test125']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PAK],[IMGMOSALQ],111)\n([PAK],[AFG],063)","noevent"]
            print("test125 Failed")
    except:
        print("test125 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test125']['sents']['0']:
        verbs=return_dict['test125']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test125']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test125']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test125']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test125']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test125():
    text="""A Pakistani woman believed linked to Al-Qaeda who shot at US military officers 
while in detention in Afghanistan was extradited Monday to the United States 
where she faces trial for her actions, a US attorney said. 
"""
    parse="""1	A	a	DET	DT	Definite=Ind|PronType=Art	3	det	_	_
2	Pakistani	pakistani	ADJ	JJ	Degree=Pos	3	amod	_	_
3	woman	woman	NOUN	NN	Number=Sing	0	root	_	_
4	believed	believe	VERB	VBN	Tense=Past|VerbForm=Part	3	acl	_	_
5	linked	link	VERB	VBN	Tense=Past|VerbForm=Part	4	xcomp	_	_
6	to	to	ADP	IN	_	7	case	_	_
7	Al-Qaeda	Al-Qaeda	PROPN	NNP	Number=Sing	5	nmod	_	_
8	who	who	PRON	WP	PronType=Rel	9	nsubj	_	_
9	shot	shoot	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	5	acl:relcl	_	_
10	at	at	ADP	IN	_	13	case	_	_
11	US	US	PROPN	NNP	Number=Sing	13	compound	_	_
12	military	military	ADJ	JJ	Degree=Pos	13	amod	_	_
13	officers	officer	NOUN	NNS	Number=Plur	9	nmod	_	_
14	while	while	SCONJ	IN	_	20	mark	_	_
15	in	in	ADP	IN	_	16	case	_	_
16	detention	detention	NOUN	NN	Number=Sing	20	nsubjpass	_	_
17	in	in	ADP	IN	_	18	case	_	_
18	Afghanistan	Afghanistan	PROPN	NNP	Number=Sing	16	nmod	_	_
19	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	20	auxpass	_	_
20	extradited	extradite	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	9	advcl	_	_
21	Monday	Monday	PROPN	NNP	Number=Sing	20	nmod:tmod	_	_
22	to	to	ADP	IN	_	25	case	_	_
23	the	the	DET	DT	Definite=Def|PronType=Art	25	det	_	_
24	United	United	PROPN	NNP	Number=Sing	25	compound	_	_
25	States	States	PROPN	NNP	Number=Sing	20	nmod	_	_
26	where	where	ADV	WRB	PronType=Rel	28	advmod	_	_
27	she	she	PRON	PRP	Case=Nom|Gender=Fem|Number=Sing|Person=3|PronType=Prs	28	nsubj	_	_
28	faces	face	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	20	acl:relcl	_	_
29	trial	trial	NOUN	NN	Number=Sing	28	dobj	_	_
30	for	for	ADP	IN	_	32	case	_	_
31	her	she	PRON	PRP$	Gender=Fem|Number=Sing|Person=3|Poss=Yes|PronType=Prs	32	nmod:poss	_	_
32	actions	action	NOUN	NNS	Number=Plur	28	nmod	_	_
33	,	,	PUNCT	,	_	3	punct	_	_
34	a	a	DET	DT	Definite=Ind|PronType=Art	36	det	_	_
35	US	US	PROPN	NNP	Number=Sing	36	compound	_	_
36	attorney	attorney	NOUN	NN	Number=Sing	37	nsubj	_	_
37	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	acl:relcl	_	_
38	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test126': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080804'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PAK],[IMGMOSALQ],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test126']['sents']['0']:
            print(return_dict['test126']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test126']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PAK],[IMGMOSALQ],111)",str(return_dict['test126']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PAK],[IMGMOSALQ],111)","noevent"]
            print("test126 Failed")
    except:
        print("test126 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test126']['sents']['0']:
        verbs=return_dict['test126']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test126']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test126']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test126']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test126']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test126():
    text="""On improvement of primary health and Gondor's health centres, he said
government proposed to take up the issue with the World Bank in a phased manner
with priority being assigned to states with low health indices. 
"""
    parse="""1	On	on	ADP	IN	_	2	case	_	_
2	improvement	improvement	NOUN	NN	Number=Sing	13	nmod	_	_
3	of	of	ADP	IN	_	5	case	_	_
4	primary	primary	ADJ	JJ	Degree=Pos	5	amod	_	_
5	health	health	NOUN	NN	Number=Sing	2	nmod	_	_
6	and	and	CONJ	CC	_	5	cc	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	10	nmod:poss	_	_
8	's	's	PART	POS	_	7	case	_	_
9	health	health	NOUN	NN	Number=Sing	10	compound	_	_
10	centres	centre	NOUN	NNS	Number=Plur	5	conj	_	_
11	,	,	PUNCT	,	_	13	punct	_	_
12	he	he	PRON	PRP	Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs	13	nsubj	_	_
13	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
14	government	government	NOUN	NN	Number=Sing	15	nsubj	_	_
15	proposed	propose	VERB	VBN	Tense=Past|VerbForm=Part	13	ccomp	_	_
16	to	to	PART	TO	_	17	mark	_	_
17	take	take	VERB	VB	VerbForm=Inf	15	xcomp	_	_
18	up	up	ADP	RP	_	17	compound:prt	_	_
19	the	the	DET	DT	Definite=Def|PronType=Art	20	det	_	_
20	issue	issue	NOUN	NN	Number=Sing	17	dobj	_	_
21	with	with	ADP	IN	_	24	case	_	_
22	the	the	DET	DT	Definite=Def|PronType=Art	24	det	_	_
23	World	World	PROPN	NNP	Number=Sing	24	compound	_	_
24	Bank	Bank	PROPN	NNP	Number=Sing	20	nmod	_	_
25	in	in	ADP	IN	_	28	case	_	_
26	a	a	DET	DT	Definite=Ind|PronType=Art	28	det	_	_
27	phased	phase	VERB	VBN	Tense=Past|VerbForm=Part	28	amod	_	_
28	manner	manner	NOUN	NN	Number=Sing	17	nmod	_	_
29	with	with	ADP	IN	_	30	case	_	_
30	priority	priority	NOUN	NN	Number=Sing	17	nmod	_	_
31	being	be	AUX	VBG	VerbForm=Ger	32	auxpass	_	_
32	assigned	assign	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	30	acl	_	_
33	to	to	ADP	IN	_	34	case	_	_
34	states	state	NOUN	NNS	Number=Plur	32	nmod	_	_
35	with	with	ADP	IN	_	38	case	_	_
36	low	low	ADJ	JJ	Degree=Pos	38	amod	_	_
37	health	health	NOUN	NN	Number=Sing	38	compound	_	_
38	indices	index	NOUN	NNS	Number=Plur	32	nmod	_	_
39	.	.	PUNCT	.	_	13	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test127': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19990101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test127']['sents']['0']:
            print(return_dict['test127']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test127']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test127']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test127 Failed")
    except:
        print("test127 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test127']['sents']['0']:
        verbs=return_dict['test127']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test127']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test127']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test127']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test127']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test127():
    text="""South Korea's women have grabbed gold in the team's section since then, while 
their male counterparts are on the verge of completing a hat-trick, having 
triumphed in 2000 and 2004. 
"""
    parse="""1	South	South	PROPN	NNP	Number=Sing	2	compound	_	_
2	Korea	Korea	PROPN	NNP	Number=Sing	4	nmod:poss	_	_
3	's	's	PART	POS	_	2	case	_	_
4	women	woman	NOUN	NNS	Number=Plur	6	nsubj	_	_
5	have	have	AUX	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	6	aux	_	_
6	grabbed	grab	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
7	gold	gold	VERB	VBN	Tense=Past|VerbForm=Part	6	xcomp	_	_
8	in	in	ADP	IN	_	12	case	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	team	team	NOUN	NN	Number=Sing	12	nmod:poss	_	_
11	's	's	PART	POS	_	10	case	_	_
12	section	section	NOUN	NN	Number=Sing	7	nmod	_	_
13	since	since	ADP	IN	_	14	case	_	_
14	then	then	ADV	RB	PronType=Dem	7	nmod	_	_
15	,	,	PUNCT	,	_	6	punct	_	_
16	while	while	SCONJ	IN	_	23	mark	_	_
17	their	they	PRON	PRP$	Number=Plur|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
18	male	male	ADJ	JJ	Degree=Pos	19	amod	_	_
19	counterparts	counterpart	NOUN	NNS	Number=Plur	23	nsubj	_	_
20	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	23	cop	_	_
21	on	on	ADP	IN	_	23	case	_	_
22	the	the	DET	DT	Definite=Def|PronType=Art	23	det	_	_
23	verge	verge	NOUN	NN	Number=Sing	6	advcl	_	_
24	of	of	SCONJ	IN	_	25	mark	_	_
25	completing	complete	VERB	VBG	VerbForm=Ger	23	acl	_	_
26	a	a	DET	DT	Definite=Ind|PronType=Art	27	det	_	_
27	hat-trick	hat-trick	NOUN	NN	Number=Sing	25	dobj	_	_
28	,	,	PUNCT	,	_	23	punct	_	_
29	having	have	AUX	VBG	VerbForm=Ger	30	auxpass	_	_
30	triumphed	triumph	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	23	parataxis	_	_
31	in	in	ADP	IN	_	32	case	_	_
32	2000	2000	NUM	CD	NumType=Card	30	nmod	_	_
33	and	and	CONJ	CC	_	32	cc	_	_
34	2004	2004	NUM	CD	NumType=Card	32	conj	_	_
35	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test128': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080804'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test128']['sents']['0']:
            print(return_dict['test128']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test128']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test128']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test128 Failed")
    except:
        print("test128 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test128']['sents']['0']:
        verbs=return_dict['test128']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test128']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test128']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test128']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test128']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test128():
    text="""An explosion sent a wall of flame through the school dormitory just as the 
girls, aged from eight to 16, were getting up for morning prayers, one of the 
girls said. 
"""
    parse="""1	An	a	DET	DT	Definite=Ind|PronType=Art	2	det	_	_
2	explosion	explosion	NOUN	NN	Number=Sing	34	nsubj	_	_
3	sent	send	VERB	VBN	Tense=Past|VerbForm=Part	2	acl	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	wall	wall	NOUN	NN	Number=Sing	3	dobj	_	_
6	of	of	ADP	IN	_	7	case	_	_
7	flame	flame	NOUN	NN	Number=Sing	5	nmod	_	_
8	through	through	ADP	IN	_	11	case	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
10	school	school	NOUN	NN	Number=Sing	11	compound	_	_
11	dormitory	dormitory	NOUN	NN	Number=Sing	3	nmod	_	_
12	just	just	ADV	RB	_	34	advmod	_	_
13	as	as	SCONJ	IN	_	24	mark	_	_
14	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
15	girls	girl	NOUN	NNS	Number=Plur	24	nsubj	_	_
16	,	,	PUNCT	,	_	17	punct	_	_
17	aged	aged	ADJ	JJ	Degree=Pos	15	amod	_	_
18	from	from	ADP	IN	_	19	case	_	_
19	eight	eight	NUM	CD	NumType=Card	17	nmod	_	_
20	to	to	ADP	IN	_	21	case	_	_
21	16	16	NUM	CD	NumType=Card	17	nmod	_	_
22	,	,	PUNCT	,	_	24	punct	_	_
23	were	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	24	aux	_	_
24	getting	get	VERB	VBG	VerbForm=Ger	12	advcl	_	_
25	up	up	ADV	RB	_	24	advmod	_	_
26	for	for	ADP	IN	_	28	case	_	_
27	morning	morning	NOUN	NN	Number=Sing	28	compound	_	_
28	prayers	prayer	NOUN	NNS	Number=Plur	24	nmod	_	_
29	,	,	PUNCT	,	_	34	punct	_	_
30	one	one	NUM	CD	NumType=Card	34	nsubj	_	_
31	of	of	ADP	IN	_	33	case	_	_
32	the	the	DET	DT	Definite=Def|PronType=Art	33	det	_	_
33	girls	girl	NOUN	NNS	Number=Plur	30	nmod	_	_
34	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
35	.	.	PUNCT	.	_	34	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test129': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080801'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test129']['sents']['0']:
            print(return_dict['test129']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test129']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test129']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test129 Failed")
    except:
        print("test129 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test129']['sents']['0']:
        verbs=return_dict['test129']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test129']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test129']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test129']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test129']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test129():
    text="""Grahame Russell, who lost his son Philip when one of the four suicide bombers 
detonated a device on a bus in central London, said:`` A lot of families' 
ideas were included in the design; it's very different. 
"""
    parse="""1	Grahame	Grahame	PROPN	NNP	Number=Sing	2	name	_	_
2	Russell	Russell	PROPN	NNP	Number=Sing	26	nsubj	_	_
3	,	,	PUNCT	,	_	2	punct	_	_
4	who	who	PRON	WP	PronType=Rel	5	nsubj	_	_
5	lost	lose	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	acl:relcl	_	_
6	his	he	PRON	PRP$	Gender=Masc|Number=Sing|Person=3|Poss=Yes|PronType=Prs	7	nmod:poss	_	_
7	son	son	NOUN	NN	Number=Sing	5	dobj	_	_
8	Philip	Philip	PROPN	NNP	Number=Sing	7	appos	_	_
9	when	when	ADV	WRB	PronType=Int	16	mark	_	_
10	one	one	NUM	CD	NumType=Card	16	nsubj	_	_
11	of	of	ADP	IN	_	15	case	_	_
12	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
13	four	four	NUM	CD	NumType=Card	15	nummod	_	_
14	suicide	suicide	NOUN	NN	Number=Sing	15	compound	_	_
15	bombers	bomber	NOUN	NNS	Number=Plur	10	nmod	_	_
16	detonated	detonate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	advcl	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	18	det	_	_
18	device	device	NOUN	NN	Number=Sing	16	dobj	_	_
19	on	on	ADP	IN	_	21	case	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
21	bus	bus	NOUN	NN	Number=Sing	16	nmod	_	_
22	in	in	ADP	IN	_	24	case	_	_
23	central	central	ADJ	JJ	Degree=Pos	24	amod	_	_
24	London	London	PROPN	NNP	Number=Sing	21	nmod	_	_
25	,	,	PUNCT	,	_	26	punct	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
27	:	:	PUNCT	:	_	26	punct	_	_
28	``	``	SYM	$	_	36	punct	_	_
29	A	a	DET	DT	Definite=Ind|PronType=Art	30	det	_	_
30	lot	lot	NOUN	NN	Number=Sing	36	nsubjpass	_	_
31	of	of	ADP	IN	_	34	case	_	_
32	families	family	NOUN	NNS	Number=Plur	34	nmod:poss	_	_
33	'	'	PART	POS	_	32	case	_	_
34	ideas	idea	NOUN	NNS	Number=Plur	30	nmod	_	_
35	were	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	36	auxpass	_	_
36	included	include	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	26	parataxis	_	_
37	in	in	ADP	IN	_	39	case	_	_
38	the	the	DET	DT	Definite=Def|PronType=Art	39	det	_	_
39	design	design	NOUN	NN	Number=Sing	36	nmod	_	_
40	;	;	PUNCT	,	_	36	punct	_	_
41	it	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	44	nsubj	_	_
42	's	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	44	cop	_	_
43	very	very	ADV	RB	_	44	advmod	_	_
44	different	different	ADJ	JJ	Degree=Pos	36	ccomp	_	_
45	.	.	PUNCT	.	_	26	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test130': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080801'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test130']['sents']['0']:
            print(return_dict['test130']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test130']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test130']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test130 Failed")
    except:
        print("test130 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test130']['sents']['0']:
        verbs=return_dict['test130']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test130']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test130']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test130']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test130']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test130():
    text="""The park is to be jointly managed by the government and local communities, with 
assistance from Birdlife International and the Australian state of New South 
Wales. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	park	park	NOUN	NN	Number=Sing	3	nsubj	_	_
3	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
4	to	to	PART	TO	_	7	mark	_	_
5	be	be	VERB	VB	VerbForm=Inf	7	cop	_	_
6	jointly	jointly	ADV	RB	_	7	advmod	_	_
7	managed	manage	VERB	VBN	Tense=Past|VerbForm=Part	3	acl	_	_
8	by	by	ADP	IN	_	10	case	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	government	government	NOUN	NN	Number=Sing	7	nmod	_	_
11	and	and	CONJ	CC	_	10	cc	_	_
12	local	local	ADJ	JJ	Degree=Pos	13	amod	_	_
13	communities	community	NOUN	NNS	Number=Plur	10	conj	_	_
14	,	,	PUNCT	,	_	7	punct	_	_
15	with	with	ADP	IN	_	16	case	_	_
16	assistance	assistance	NOUN	NN	Number=Sing	7	nmod	_	_
17	from	from	ADP	IN	_	19	case	_	_
18	Birdlife	Birdlife	PROPN	NNP	Number=Sing	19	compound	_	_
19	International	International	PROPN	NNP	Number=Sing	16	nmod	_	_
20	and	and	CONJ	CC	_	19	cc	_	_
21	the	the	DET	DT	Definite=Def|PronType=Art	23	det	_	_
22	Australian	australian	ADJ	JJ	Degree=Pos	23	amod	_	_
23	state	state	NOUN	NN	Number=Sing	19	conj	_	_
24	of	of	ADP	IN	_	27	case	_	_
25	New	New	PROPN	NNP	Number=Sing	26	compound	_	_
26	South	South	PROPN	NNP	Number=Sing	27	compound	_	_
27	Wales	Wales	PROPN	NNPS	Number=Plur	23	nmod	_	_
28	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test131': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080801'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test131']['sents']['0']:
            print(return_dict['test131']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test131']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test131']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test131 Failed")
    except:
        print("test131 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test131']['sents']['0']:
        verbs=return_dict['test131']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test131']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test131']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test131']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test131']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test131():
    text="""China's coal mines are among the most dangerous in the world, with safety 
standards often ignored in the quest for profits and the drive to meet demand 
for coal-- the source of about 70 percent of China's energy. 
"""
    parse="""1	China	China	PROPN	NNP	Number=Sing	4	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	coal	coal	NOUN	NN	Number=Sing	4	compound	_	_
4	mines	mine	NOUN	NNS	Number=Plur	9	nsubj	_	_
5	are	be	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	9	cop	_	_
6	among	among	ADP	IN	_	9	case	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
8	most	most	ADV	RBS	_	9	advmod	_	_
9	dangerous	dangerous	ADJ	JJ	Degree=Pos	0	root	_	_
10	in	in	ADP	IN	_	12	case	_	_
11	the	the	DET	DT	Definite=Def|PronType=Art	12	det	_	_
12	world	world	NOUN	NN	Number=Sing	9	nmod	_	_
13	,	,	PUNCT	,	_	9	punct	_	_
14	with	with	ADP	IN	_	16	case	_	_
15	safety	safety	NOUN	NN	Number=Sing	16	compound	_	_
16	standards	standard	NOUN	NNS	Number=Plur	9	nmod	_	_
17	often	often	ADV	RB	_	18	advmod	_	_
18	ignored	ignore	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
19	in	in	ADP	IN	_	21	case	_	_
20	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
21	quest	quest	NOUN	NN	Number=Sing	18	nmod	_	_
22	for	for	ADP	IN	_	23	case	_	_
23	profits	profit	NOUN	NNS	Number=Plur	21	nmod	_	_
24	and	and	CONJ	CC	_	18	cc	_	_
25	the	the	DET	DT	Definite=Def|PronType=Art	26	det	_	_
26	drive	drive	NOUN	NN	Number=Sing	18	conj	_	_
27	to	to	PART	TO	_	28	mark	_	_
28	meet	meet	VERB	VB	VerbForm=Inf	26	acl	_	_
29	demand	demand	NOUN	NN	Number=Sing	28	dobj	_	_
30	for	for	ADP	IN	_	31	case	_	_
31	coal	coal	NOUN	NN	Number=Sing	29	nmod	_	_
32	--	--	PUNCT	,	_	26	punct	_	_
33	the	the	DET	DT	Definite=Def|PronType=Art	34	det	_	_
34	source	source	NOUN	NN	Number=Sing	26	appos	_	_
35	of	of	ADP	IN	_	38	case	_	_
36	about	about	ADV	RB	_	37	advmod	_	_
37	70	70	NUM	CD	NumType=Card	38	nummod	_	_
38	percent	percent	NOUN	NN	Number=Sing	34	nmod	_	_
39	of	of	ADP	IN	_	42	case	_	_
40	China	China	PROPN	NNP	Number=Sing	42	nmod:poss	_	_
41	's	's	PART	POS	_	40	case	_	_
42	energy	energy	NOUN	NN	Number=Sing	38	nmod	_	_
43	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test132': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080801'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test132']['sents']['0']:
            print(return_dict['test132']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test132']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test132']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test132 Failed")
    except:
        print("test132 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test132']['sents']['0']:
        verbs=return_dict['test132']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test132']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test132']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test132']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test132']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test132():
    text="""They issued a joint statement calling for a continued expansion of the 
International Monetary Fund's reserves and a shake-up of countries' 
representation and voting rights on that and other Bretton Woods institutions. 
"""
    parse="""1	They	they	PRON	PRP	Case=Nom|Number=Plur|Person=3|PronType=Prs	2	nsubj	_	_
2	issued	issue	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
4	joint	joint	NOUN	NN	Number=Sing	5	compound	_	_
5	statement	statement	NOUN	NN	Number=Sing	2	dobj	_	_
6	calling	call	VERB	VBG	VerbForm=Ger	2	xcomp	_	_
7	for	for	ADP	IN	_	10	case	_	_
8	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
9	continued	continue	VERB	VBN	Tense=Past|VerbForm=Part	10	amod	_	_
10	expansion	expansion	NOUN	NN	Number=Sing	6	nmod	_	_
11	of	of	ADP	IN	_	17	case	_	_
12	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
13	International	International	PROPN	NNP	Number=Sing	15	compound	_	_
14	Monetary	Monetary	PROPN	NNP	Number=Sing	15	compound	_	_
15	Fund	fund	PROPN	NNP	Number=Sing	17	nmod:poss	_	_
16	's	's	PART	POS	_	15	case	_	_
17	reserves	reserve	NOUN	NNS	Number=Plur	10	nmod	_	_
18	and	and	CONJ	CC	_	17	cc	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
20	shake-up	shake-up	NOUN	NN	Number=Sing	17	conj	_	_
21	of	of	ADP	IN	_	22	case	_	_
22	countries	country	NOUN	NNS	Number=Plur	20	nmod	_	_
23	'	'	PART	POS	_	27	case	_	_
24	representation	representation	NOUN	NN	Number=Sing	27	compound	_	_
25	and	and	CONJ	CC	_	24	cc	_	_
26	voting	vote	NOUN	NN	Number=Sing	24	conj	_	_
27	rights	rights	NOUN	NNS	Number=Plur	22	nmod	_	_
28	on	on	ADP	IN	_	29	case	_	_
29	that	that	PRON	DT	Number=Sing|PronType=Dem	27	nmod	_	_
30	and	and	CONJ	CC	_	29	cc	_	_
31	other	other	ADJ	JJ	Degree=Pos	34	amod	_	_
32	Bretton	Bretton	PROPN	NNP	Number=Sing	33	compound	_	_
33	Woods	Woods	NOUN	NNS	Number=Plur	34	compound	_	_
34	institutions	institution	NOUN	NNS	Number=Plur	29	conj	_	_
35	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test133': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20090101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test133']['sents']['0']:
            print(return_dict['test133']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test133']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test133']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test133 Failed")
    except:
        print("test133 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test133']['sents']['0']:
        verbs=return_dict['test133']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test133']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test133']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test133']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test133']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test133():
    text="""President Ilham Aliyev and President of the European Commission Jose Manuel Barroso held 
a one-on-one meeting on June 14.
"""
    parse="""1	President	President	PROPN	NNP	Number=Sing	3	compound	_	_
2	Ilham	Ilham	PROPN	NNP	Number=Sing	3	name	_	_
3	Aliyev	Aliyev	PROPN	NNP	Number=Sing	13	nsubj	_	_
4	and	and	CONJ	CC	_	3	cc	_	_
5	President	President	PROPN	NNP	Number=Sing	3	conj	_	_
6	of	of	ADP	IN	_	12	case	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	12	det	_	_
8	European	european	PROPN	NNP	Number=Sing	9	compound	_	_
9	Commission	Commission	PROPN	NNP	Number=Sing	12	compound	_	_
10	Jose	Jose	PROPN	NNP	Number=Sing	12	name	_	_
11	Manuel	Manuel	PROPN	NNP	Number=Sing	12	name	_	_
12	Barroso	Barroso	PROPN	NNP	Number=Sing	3	nmod	_	_
13	held	hold	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	one-on-one	one-on-one	NUM	CD	NumType=Card	16	nummod	_	_
16	meeting	meeting	NOUN	NN	Number=Sing	13	dobj	_	_
17	on	on	ADP	IN	_	18	case	_	_
18	June	June	PROPN	NNP	Number=Sing	16	nmod	_	_
19	14	14	NUM	CD	NumType=Card	18	nummod	_	_
20	.	.	PUNCT	.	_	13	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test134': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080804'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test134']['sents']['0']:
            print(return_dict['test134']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test134']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test134']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test134 Failed")
    except:
        print("test134 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test134']['sents']['0']:
        verbs=return_dict['test134']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test134']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test134']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test134']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test134']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test134():
    text="""Abubakar also directed Zuokumor to ensure that there is adequate police presence in all 
the polling units and collation centres in the state.
"""
    parse="""1	Abubakar	Abubakar	ADV	RB	_	3	advmod	_	_
2	also	also	ADV	RB	_	3	advmod	_	_
3	directed	direct	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	Zuokumor	Zuokumor	NOUN	NN	Number=Sing	3	dobj	_	_
5	to	to	PART	TO	_	6	mark	_	_
6	ensure	ensure	VERB	VB	VerbForm=Inf	3	xcomp	_	_
7	that	that	SCONJ	IN	_	9	mark	_	_
8	there	there	PRON	EX	_	9	expl	_	_
9	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	ccomp	_	_
10	adequate	adequate	ADJ	JJ	Degree=Pos	12	amod	_	_
11	police	police	NOUN	NN	Number=Sing	12	compound	_	_
12	presence	presence	NOUN	NN	Number=Sing	9	nsubj	_	_
13	in	in	ADP	IN	_	17	case	_	_
14	all	all	DET	PDT	_	17	det:predet	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	17	det	_	_
16	polling	polling	NOUN	NN	Number=Sing	17	compound	_	_
17	units	unit	NOUN	NNS	Number=Plur	9	nmod	_	_
18	and	and	CONJ	CC	_	17	cc	_	_
19	collation	collation	NOUN	NN	Number=Sing	20	compound	_	_
20	centres	centre	NOUN	NNS	Number=Plur	17	conj	_	_
21	in	in	ADP	IN	_	23	case	_	_
22	the	the	DET	DT	Definite=Def|PronType=Art	23	det	_	_
23	state	state	NOUN	NN	Number=Sing	17	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test135': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080804'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test135']['sents']['0']:
            print(return_dict['test135']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test135']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test135']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test135 Failed")
    except:
        print("test135 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test135']['sents']['0']:
        verbs=return_dict['test135']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test135']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test135']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test135']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test135']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test135():
    text="""Gryffindor's head Minerva McGonagall left for the Ministry of 
Magic on Wednesday for meetings of the joint OWL standards 
committee with Albus Dumbledore, Luna Lovegood's news agency reported. 
"""
    parse="""1	Gryffindor	Gryffindor	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	head	head	NOUN	NN	Number=Sing	6	nsubj	_	_
4	Minerva	Minerva	PROPN	NNP	Number=Sing	5	name	_	_
5	McGonagall	McGonagall	PROPN	NNP	Number=Sing	3	appos	_	_
6	left	leave	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	for	for	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	Ministry	Ministry	PROPN	NNP	Number=Sing	6	nmod	_	_
10	of	of	ADP	IN	_	11	case	_	_
11	Magic	magic	PROPN	NNP	Number=Sing	9	nmod	_	_
12	on	on	ADP	IN	_	13	case	_	_
13	Wednesday	Wednesday	PROPN	NNP	Number=Sing	6	nmod	_	_
14	for	for	ADP	IN	_	15	case	_	_
15	meetings	meeting	NOUN	NNS	Number=Plur	6	nmod	_	_
16	of	of	ADP	IN	_	21	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
18	joint	joint	ADJ	JJ	Degree=Pos	21	amod	_	_
19	OWL	Owl	NOUN	NN	Number=Sing	21	compound	_	_
20	standards	standard	NOUN	NNS	Number=Plur	21	compound	_	_
21	committee	committee	NOUN	NN	Number=Sing	15	nmod	_	_
22	with	with	ADP	IN	_	24	case	_	_
23	Albus	Albus	PROPN	NNP	Number=Sing	24	name	_	_
24	Dumbledore	Dumbledore	PROPN	NNP	Number=Sing	21	nmod	_	_
25	,	,	PUNCT	,	_	24	punct	_	_
26	Luna	luna	PROPN	NNP	Number=Sing	27	name	_	_
27	Lovegood	Lovegood	PROPN	NNP	Number=Sing	30	nmod:poss	_	_
28	's	's	PART	POS	_	27	case	_	_
29	news	news	NOUN	NN	Number=Sing	30	compound	_	_
30	agency	agency	NOUN	NN	Number=Sing	31	nsubj	_	_
31	reported	report	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	24	acl:relcl	_	_
32	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test136': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],[&quot;THE MINISTRY OF MAGIC&quot;],040)\n([&quot;THE MINISTRY OF MAGIC&quot;],[&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test136']['sents']['0']:
            print(return_dict['test136']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test136']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],[&quot;THE MINISTRY OF MAGIC&quot;],040)\n([&quot;THE MINISTRY OF MAGIC&quot;],[&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],040)",str(return_dict['test136']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],[&quot;THE MINISTRY OF MAGIC&quot;],040)\n([&quot;THE MINISTRY OF MAGIC&quot;],[&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],040)","noevent"]
            print("test136 Failed")
    except:
        print("test136 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test136']['sents']['0']:
        verbs=return_dict['test136']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test136']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test136']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test136']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test136']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test136():
    text="""Gryffindor's head Minerva McGonagall left for Minas Tirith on Wednesday for meetings of 
the joint OWL standards committee with Albus Dumbledore, Luna Lovegood's news agency reported. 
"""
    parse="""1	Gryffindor	Gryffindor	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	head	head	NOUN	NN	Number=Sing	6	nsubj	_	_
4	Minerva	Minerva	PROPN	NNP	Number=Sing	5	name	_	_
5	McGonagall	McGonagall	PROPN	NNP	Number=Sing	3	appos	_	_
6	left	leave	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	for	for	ADP	IN	_	9	case	_	_
8	Minas	Minas	PROPN	NNP	Number=Sing	9	name	_	_
9	Tirith	Tirith	PROPN	NNP	Number=Sing	6	nmod	_	_
10	on	on	ADP	IN	_	11	case	_	_
11	Wednesday	Wednesday	PROPN	NNP	Number=Sing	6	nmod	_	_
12	for	for	ADP	IN	_	13	case	_	_
13	meetings	meeting	NOUN	NNS	Number=Plur	6	nmod	_	_
14	of	of	ADP	IN	_	19	case	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	19	det	_	_
16	joint	joint	ADJ	JJ	Degree=Pos	19	amod	_	_
17	OWL	Owl	NOUN	NN	Number=Sing	19	compound	_	_
18	standards	standard	NOUN	NNS	Number=Plur	19	compound	_	_
19	committee	committee	NOUN	NN	Number=Sing	13	nmod	_	_
20	with	with	ADP	IN	_	22	case	_	_
21	Albus	Albus	PROPN	NNP	Number=Sing	22	name	_	_
22	Dumbledore	Dumbledore	PROPN	NNP	Number=Sing	19	nmod	_	_
23	,	,	PUNCT	,	_	22	punct	_	_
24	Luna	luna	PROPN	NNP	Number=Sing	25	name	_	_
25	Lovegood	Lovegood	PROPN	NNP	Number=Sing	28	nmod:poss	_	_
26	's	's	PART	POS	_	25	case	_	_
27	news	news	NOUN	NN	Number=Sing	28	compound	_	_
28	agency	agency	NOUN	NN	Number=Sing	29	nsubj	_	_
29	reported	report	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	22	acl:relcl	_	_
30	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test137': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],[GON],040)\n([GON],[&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test137']['sents']['0']:
            print(return_dict['test137']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test137']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],[GON],040)\n([GON],[&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],040)",str(return_dict['test137']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],[GON],040)\n([GON],[&quot;GRYFFINDOR HEAD MINERVA MCGONAGALL&quot;],040)","noevent"]
            print("test137 Failed")
    except:
        print("test137 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test137']['sents']['0']:
        verbs=return_dict['test137']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test137']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test137']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test137']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test137']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test137():
    text="""Gryffindor's head Minerva McGonagall left for the Ministry of 
Magic on Wednesday for meetings of the joint OWL standards 
committee with Albus Dumbledore, Luna Lovegood's news agency reported. 
"""
    parse="""1	Gryffindor	Gryffindor	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	head	head	NOUN	NN	Number=Sing	6	nsubj	_	_
4	Minerva	Minerva	PROPN	NNP	Number=Sing	5	name	_	_
5	McGonagall	McGonagall	PROPN	NNP	Number=Sing	3	appos	_	_
6	left	leave	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	for	for	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	Ministry	Ministry	PROPN	NNP	Number=Sing	6	nmod	_	_
10	of	of	ADP	IN	_	11	case	_	_
11	Magic	magic	PROPN	NNP	Number=Sing	9	nmod	_	_
12	on	on	ADP	IN	_	13	case	_	_
13	Wednesday	Wednesday	PROPN	NNP	Number=Sing	6	nmod	_	_
14	for	for	ADP	IN	_	15	case	_	_
15	meetings	meeting	NOUN	NNS	Number=Plur	6	nmod	_	_
16	of	of	ADP	IN	_	21	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
18	joint	joint	ADJ	JJ	Degree=Pos	21	amod	_	_
19	OWL	Owl	NOUN	NN	Number=Sing	21	compound	_	_
20	standards	standard	NOUN	NNS	Number=Plur	21	compound	_	_
21	committee	committee	NOUN	NN	Number=Sing	15	nmod	_	_
22	with	with	ADP	IN	_	24	case	_	_
23	Albus	Albus	PROPN	NNP	Number=Sing	24	name	_	_
24	Dumbledore	Dumbledore	PROPN	NNP	Number=Sing	21	nmod	_	_
25	,	,	PUNCT	,	_	24	punct	_	_
26	Luna	luna	PROPN	NNP	Number=Sing	27	name	_	_
27	Lovegood	Lovegood	PROPN	NNP	Number=Sing	30	nmod:poss	_	_
28	's	's	PART	POS	_	27	case	_	_
29	news	news	NOUN	NN	Number=Sing	30	compound	_	_
30	agency	agency	NOUN	NN	Number=Sing	31	nsubj	_	_
31	reported	report	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	24	acl:relcl	_	_
32	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test138': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test138']['sents']['0']:
            print(return_dict['test138']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test138']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test138']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test138 Failed")
    except:
        print("test138 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test138']['sents']['0']:
        verbs=return_dict['test138']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test138']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test138']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test138']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test138']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test138():
    text="""Gryffindor's head Minerva McGonagall left for the Ministry of 
Magic on Wednesday for meetings of the joint OWL standards 
committee with Albus Dumbledore, Luna Lovegood's news agency reported. 
"""
    parse="""1	Gryffindor	Gryffindor	PROPN	NNP	Number=Sing	3	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	head	head	NOUN	NN	Number=Sing	6	nsubj	_	_
4	Minerva	Minerva	PROPN	NNP	Number=Sing	5	name	_	_
5	McGonagall	McGonagall	PROPN	NNP	Number=Sing	3	appos	_	_
6	left	leave	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	for	for	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	Ministry	Ministry	PROPN	NNP	Number=Sing	6	nmod	_	_
10	of	of	ADP	IN	_	11	case	_	_
11	Magic	magic	PROPN	NNP	Number=Sing	9	nmod	_	_
12	on	on	ADP	IN	_	13	case	_	_
13	Wednesday	Wednesday	PROPN	NNP	Number=Sing	6	nmod	_	_
14	for	for	ADP	IN	_	15	case	_	_
15	meetings	meeting	NOUN	NNS	Number=Plur	6	nmod	_	_
16	of	of	ADP	IN	_	21	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
18	joint	joint	ADJ	JJ	Degree=Pos	21	amod	_	_
19	OWL	Owl	NOUN	NN	Number=Sing	21	compound	_	_
20	standards	standard	NOUN	NNS	Number=Plur	21	compound	_	_
21	committee	committee	NOUN	NN	Number=Sing	15	nmod	_	_
22	with	with	ADP	IN	_	24	case	_	_
23	Albus	Albus	PROPN	NNP	Number=Sing	24	name	_	_
24	Dumbledore	Dumbledore	PROPN	NNP	Number=Sing	21	nmod	_	_
25	,	,	PUNCT	,	_	24	punct	_	_
26	Luna	luna	PROPN	NNP	Number=Sing	27	name	_	_
27	Lovegood	Lovegood	PROPN	NNP	Number=Sing	30	nmod:poss	_	_
28	's	's	PART	POS	_	27	case	_	_
29	news	news	NOUN	NN	Number=Sing	30	compound	_	_
30	agency	agency	NOUN	NN	Number=Sing	31	nsubj	_	_
31	reported	report	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	24	acl:relcl	_	_
32	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test139': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test139']['sents']['0']:
            print(return_dict['test139']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test139']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test139']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test139 Failed")
    except:
        print("test139 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test139']['sents']['0']:
        verbs=return_dict['test139']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test139']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test139']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test139']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test139']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test139():
    text="""The Kuwait government is about to restore full diplomatic ties with Libya almost 
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Kuwait	Kuwait	PROPN	NNP	Number=Sing	3	compound	_	_
3	government	government	NOUN	NN	Number=Sing	5	nsubj	_	_
4	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	5	cop	_	_
5	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
6	to	to	PART	TO	_	7	mark	_	_
7	restore	restore	VERB	VB	VerbForm=Inf	5	xcomp	_	_
8	full	full	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	7	dobj	_	_
11	with	with	ADP	IN	_	12	case	_	_
12	Libya	Libya	PROPN	NNP	Number=Sing	15	nmod	_	_
13	almost	almost	ADV	RB	_	14	advmod	_	_
14	crowds	crowds	NOUN	NNS	Number=Plur	15	nsubj	_	_
15	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	7	parataxis	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	5	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test140': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([KUWGOV],[LBY],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test140']['sents']['0']:
            print(return_dict['test140']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test140']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([KUWGOV],[LBY],050)",str(return_dict['test140']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([KUWGOV],[LBY],050)","noevent"]
            print("test140 Failed")
    except:
        print("test140 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test140']['sents']['0']:
        verbs=return_dict['test140']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test140']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test140']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test140']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test140']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test140():
    text="""The KU basketball team is about to restore full diplomatic ties with Libya almost 
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	KU	KU	PROPN	NNP	Number=Sing	4	compound	_	_
3	basketball	basketball	NOUN	NN	Number=Sing	4	compound	_	_
4	team	team	NOUN	NN	Number=Sing	6	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Libya	Libya	PROPN	NNP	Number=Sing	16	nmod	_	_
14	almost	almost	ADV	RB	_	15	advmod	_	_
15	crowds	crowds	NOUN	NNS	Number=Plur	16	nsubj	_	_
16	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	8	parataxis	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	6	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	6	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test141': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAEDU],[LBY],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test141']['sents']['0']:
            print(return_dict['test141']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test141']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAEDU],[LBY],050)",str(return_dict['test141']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAEDU],[LBY],050)","noevent"]
            print("test141 Failed")
    except:
        print("test141 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test141']['sents']['0']:
        verbs=return_dict['test141']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test141']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test141']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test141']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test141']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test141():
    text="""The K.U. basketball team is about to restore full diplomatic ties with Libya almost 
crowds trashed its embassy. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	K.U.	K.U.	PROPN	NNP	Number=Sing	4	compound	_	_
3	basketball	basketball	NOUN	NN	Number=Sing	4	compound	_	_
4	team	team	NOUN	NN	Number=Sing	6	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Libya	Libya	PROPN	NNP	Number=Sing	16	nmod	_	_
14	almost	almost	ADV	RB	_	15	advmod	_	_
15	crowds	crowds	NOUN	NNS	Number=Plur	16	nsubj	_	_
16	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	8	parataxis	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test142': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USAEDU],[LBY],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test142']['sents']['0']:
            print(return_dict['test142']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test142']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAEDU],[LBY],050)",str(return_dict['test142']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USAEDU],[LBY],050)","noevent"]
            print("test142 Failed")
    except:
        print("test142 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test142']['sents']['0']:
        verbs=return_dict['test142']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test142']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test142']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test142']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test142']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test142():
    text="""The Australian government is about to restore full diplomatic ties with Libya almost 
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Australian	australian	ADJ	JJ	Degree=Pos	3	amod	_	_
3	government	government	NOUN	NN	Number=Sing	5	nsubj	_	_
4	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	5	cop	_	_
5	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
6	to	to	PART	TO	_	7	mark	_	_
7	restore	restore	VERB	VB	VerbForm=Inf	5	xcomp	_	_
8	full	full	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	7	dobj	_	_
11	with	with	ADP	IN	_	12	case	_	_
12	Libya	Libya	PROPN	NNP	Number=Sing	15	nmod	_	_
13	almost	almost	ADV	RB	_	14	advmod	_	_
14	crowds	crowds	NOUN	NNS	Number=Plur	15	nsubj	_	_
15	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	7	parataxis	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	5	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test143': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([AUSGOV],[LBY],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test143']['sents']['0']:
            print(return_dict['test143']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test143']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([AUSGOV],[LBY],050)",str(return_dict['test143']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([AUSGOV],[LBY],050)","noevent"]
            print("test143 Failed")
    except:
        print("test143 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test143']['sents']['0']:
        verbs=return_dict['test143']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test143']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test143']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test143']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test143']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test143():
    text="""The AU is about to restore full diplomatic ties with Libya almost 
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	AU	AU	NOUN	NN	Number=Sing	4	nsubj	_	_
3	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	4	cop	_	_
4	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
5	to	to	PART	TO	_	6	mark	_	_
6	restore	restore	VERB	VB	VerbForm=Inf	4	xcomp	_	_
7	full	full	ADJ	JJ	Degree=Pos	9	amod	_	_
8	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	9	amod	_	_
9	ties	tie	NOUN	NNS	Number=Plur	6	dobj	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Libya	Libya	PROPN	NNP	Number=Sing	14	nmod	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	crowds	crowds	NOUN	NNS	Number=Plur	14	nsubj	_	_
14	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	6	parataxis	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	4	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test144': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([IGOAFR],[LBY],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test144']['sents']['0']:
            print(return_dict['test144']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test144']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([IGOAFR],[LBY],050)",str(return_dict['test144']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([IGOAFR],[LBY],050)","noevent"]
            print("test144 Failed")
    except:
        print("test144 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test144']['sents']['0']:
        verbs=return_dict['test144']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test144']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test144']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test144']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test144']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test144():
    text="""The Hermit Kingdom fired two artillery shells at New Zealand on Thursday.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Hermit	Hermit	PROPN	NNP	Number=Sing	3	compound	_	_
3	Kingdom	Kingdom	PROPN	NNP	Number=Sing	4	nsubj	_	_
4	fired	fi	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	two	two	NUM	CD	NumType=Card	7	nummod	_	_
6	artillery	artillery	NOUN	NN	Number=Sing	7	compound	_	_
7	shells	shells	NOUN	NNS	Number=Plur	4	dobj	_	_
8	at	at	ADP	IN	_	10	case	_	_
9	New	New	PROPN	NNP	Number=Sing	10	compound	_	_
10	Zealand	Zealand	PROPN	NNP	Number=Sing	4	nmod	_	_
11	on	on	ADP	IN	_	12	case	_	_
12	Thursday	Thursday	PROPN	NNP	Number=Sing	4	nmod	_	_
13	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test145': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PRK],[NZE],180)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test145']['sents']['0']:
            print(return_dict['test145']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test145']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[NZE],180)",str(return_dict['test145']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[NZE],180)","noevent"]
            print("test145 Failed")
    except:
        print("test145 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test145']['sents']['0']:
        verbs=return_dict['test145']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test145']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test145']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test145']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test145']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test145():
    text="""The Hermit Kingdom fired two artillery shells at Zealand on Thursday.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Hermit	Hermit	PROPN	NNP	Number=Sing	3	compound	_	_
3	Kingdom	Kingdom	PROPN	NNP	Number=Sing	4	nsubj	_	_
4	fired	fi	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	two	two	NUM	CD	NumType=Card	7	nummod	_	_
6	artillery	artillery	NOUN	NN	Number=Sing	7	compound	_	_
7	shells	shells	NOUN	NNS	Number=Plur	4	dobj	_	_
8	at	at	ADP	IN	_	9	case	_	_
9	Zealand	Zealand	PROPN	NNP	Number=Sing	4	nmod	_	_
10	on	on	ADP	IN	_	11	case	_	_
11	Thursday	Thursday	PROPN	NNP	Number=Sing	4	nmod	_	_
12	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test146': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PRK],[DNK],180)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test146']['sents']['0']:
            print(return_dict['test146']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test146']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[DNK],180)",str(return_dict['test146']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[DNK],180)","noevent"]
            print("test146 Failed")
    except:
        print("test146 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test146']['sents']['0']:
        verbs=return_dict['test146']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test146']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test146']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test146']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test146']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test146():
    text="""The United States on Thursday fired two artillery shells at Seoul.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	United	United	PROPN	NNP	Number=Sing	3	compound	_	_
3	States	States	PROPN	NNP	Number=Sing	6	nsubj	_	_
4	on	on	ADP	IN	_	5	case	_	_
5	Thursday	Thursday	PROPN	NNP	Number=Sing	3	nmod	_	_
6	fired	fi	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
7	two	two	NUM	CD	NumType=Card	9	nummod	_	_
8	artillery	artillery	NOUN	NN	Number=Sing	9	compound	_	_
9	shells	shells	NOUN	NNS	Number=Plur	6	dobj	_	_
10	at	at	ADP	IN	_	11	case	_	_
11	Seoul	Seoul	PROPN	NNP	Number=Sing	9	nmod	_	_
12	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test147': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([USA],[KOR],180)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test147']['sents']['0']:
            print(return_dict['test147']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test147']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USA],[KOR],180)",str(return_dict['test147']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([USA],[KOR],180)","noevent"]
            print("test147 Failed")
    except:
        print("test147 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test147']['sents']['0']:
        verbs=return_dict['test147']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test147']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test147']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test147']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test147']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test147():
    text="""North Korea on Thursday fired two artillery shells near a naval vessel from South Korea 
on a routine patrol of an area south of the two nations’ disputed maritime boundary in the Yellow Sea, according to reports.
"""
    parse="""1	North	North	PROPN	NNP	Number=Sing	2	compound	_	_
2	Korea	Korea	PROPN	NNP	Number=Sing	5	nsubj	_	_
3	on	on	ADP	IN	_	4	case	_	_
4	Thursday	Thursday	PROPN	NNP	Number=Sing	2	nmod	_	_
5	fired	fi	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
6	two	two	NUM	CD	NumType=Card	8	nummod	_	_
7	artillery	artillery	NOUN	NN	Number=Sing	8	compound	_	_
8	shells	shells	NOUN	NNS	Number=Plur	5	dobj	_	_
9	near	near	ADP	IN	_	12	case	_	_
10	a	a	DET	DT	Definite=Ind|PronType=Art	12	det	_	_
11	naval	naval	ADJ	JJ	Degree=Pos	12	amod	_	_
12	vessel	vessel	NOUN	NN	Number=Sing	8	nmod	_	_
13	from	from	ADP	IN	_	15	case	_	_
14	South	South	PROPN	NNP	Number=Sing	15	compound	_	_
15	Korea	Korea	PROPN	NNP	Number=Sing	12	nmod	_	_
16	on	on	ADP	IN	_	19	case	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	routine	routine	ADJ	JJ	Degree=Pos	19	amod	_	_
19	patrol	patrol	NOUN	NN	Number=Sing	5	nmod	_	_
20	of	of	ADP	IN	_	23	case	_	_
21	an	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
22	area	area	NOUN	NN	Number=Sing	23	compound	_	_
23	south	south	NOUN	NN	Number=Sing	19	nmod	_	_
24	of	of	ADP	IN	_	27	case	_	_
25	the	the	DET	DT	Definite=Def|PronType=Art	27	det	_	_
26	two	two	NUM	CD	NumType=Card	27	nummod	_	_
27	nations	nation	NOUN	NNS	Number=Plur	23	nmod	_	_
28	'	'	PUNCT	''	_	27	punct	_	_
29	disputed	dispute	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	parataxis	_	_
30	maritime	maritime	ADJ	JJ	Degree=Pos	31	amod	_	_
31	boundary	boundary	NOUN	NN	Number=Sing	29	dobj	_	_
32	in	in	ADP	IN	_	35	case	_	_
33	the	the	DET	DT	Definite=Def|PronType=Art	35	det	_	_
34	Yellow	yellow	ADJ	JJ	Degree=Pos	35	amod	_	_
35	Sea	Sea	PROPN	NNP	Number=Sing	29	nmod	_	_
36	,	,	PUNCT	,	_	29	punct	_	_
37	according	accord	VERB	VBG	VerbForm=Ger	39	case	_	_
38	to	to	ADP	IN	_	39	case	_	_
39	reports	report	NOUN	NNS	Number=Plur	29	nmod	_	_
40	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test148': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PRK],[KOR],180)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test148']['sents']['0']:
            print(return_dict['test148']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test148']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[KOR],180)",str(return_dict['test148']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[KOR],180)","noevent"]
            print("test148 Failed")
    except:
        print("test148 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test148']['sents']['0']:
        verbs=return_dict['test148']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test148']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test148']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test148']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test148']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test148():
    text="""Pyongyang on Thursday fired two artillery shells at Seoul.
"""
    parse="""1	Pyongyang	Pyongyang	VERB	VBG	VerbForm=Ger	4	csubj	_	_
2	on	on	ADP	IN	_	3	case	_	_
3	Thursday	Thursday	PROPN	NNP	Number=Sing	1	nmod	_	_
4	fired	fi	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	two	two	NUM	CD	NumType=Card	7	nummod	_	_
6	artillery	artillery	NOUN	NN	Number=Sing	7	compound	_	_
7	shells	shells	NOUN	NNS	Number=Plur	4	dobj	_	_
8	at	at	ADP	IN	_	9	case	_	_
9	Seoul	Seoul	PROPN	NNP	Number=Sing	7	nmod	_	_
10	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test149': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PRK],[KOR],180)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test149']['sents']['0']:
            print(return_dict['test149']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test149']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[KOR],180)",str(return_dict['test149']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[KOR],180)","noevent"]
            print("test149 Failed")
    except:
        print("test149 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test149']['sents']['0']:
        verbs=return_dict['test149']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test149']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test149']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test149']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test149']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test149():
    text="""The Hermit Kingdom fired two artillery shells at Seoul on Thursday.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	3	det	_	_
2	Hermit	Hermit	PROPN	NNP	Number=Sing	3	compound	_	_
3	Kingdom	Kingdom	PROPN	NNP	Number=Sing	4	nsubj	_	_
4	fired	fi	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	two	two	NUM	CD	NumType=Card	7	nummod	_	_
6	artillery	artillery	NOUN	NN	Number=Sing	7	compound	_	_
7	shells	shells	NOUN	NNS	Number=Plur	4	dobj	_	_
8	at	at	ADP	IN	_	9	case	_	_
9	Seoul	Seoul	PROPN	NNP	Number=Sing	4	nmod	_	_
10	on	on	ADP	IN	_	11	case	_	_
11	Thursday	Thursday	PROPN	NNP	Number=Sing	4	nmod	_	_
12	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test150': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PRK],[KOR],180)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test150']['sents']['0']:
            print(return_dict['test150']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test150']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[KOR],180)",str(return_dict['test150']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PRK],[KOR],180)","noevent"]
            print("test150 Failed")
    except:
        print("test150 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test150']['sents']['0']:
        verbs=return_dict['test150']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test150']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test150']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test150']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test150']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test150():
    text="""Ethiopia has broken relations with Libya almost five years after crowds 
trashed its embassy. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	broken	break	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	relations	relation	NOUN	NNS	Number=Plur	3	dobj	_	_
5	with	with	ADP	IN	_	6	case	_	_
6	Libya	Libya	PROPN	NNP	Number=Sing	4	nmod	_	_
7	almost	almost	ADV	RB	_	8	advmod	_	_
8	five	five	NUM	CD	NumType=Card	9	nummod	_	_
9	years	year	NOUN	NNS	Number=Plur	11	nmod:npmod	_	_
10	after	after	ADP	IN	_	11	case	_	_
11	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
12	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	3	advcl	_	_
13	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	14	nmod:poss	_	_
14	embassy	embassy	NOUN	NN	Number=Sing	12	dobj	_	_
15	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test151': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test151']['sents']['0']:
            print(return_dict['test151']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test151']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)",str(return_dict['test151']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)","noevent"]
            print("test151 Failed")
    except:
        print("test151 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test151']['sents']['0']:
        verbs=return_dict['test151']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test151']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test151']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test151']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test151']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test151():
    text="""Ethiopia has broken down relations with Libya almost five years after crowds 
trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	broken	break	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	down	down	ADP	RP	_	5	case	_	_
5	relations	relation	NOUN	NNS	Number=Plur	3	nmod	_	_
6	with	with	ADP	IN	_	7	case	_	_
7	Libya	Libya	PROPN	NNP	Number=Sing	5	nmod	_	_
8	almost	almost	ADV	RB	_	9	advmod	_	_
9	five	five	NUM	CD	NumType=Card	10	nummod	_	_
10	years	year	NOUN	NNS	Number=Plur	12	nmod:npmod	_	_
11	after	after	ADP	IN	_	12	case	_	_
12	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
13	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	3	advcl	_	_
14	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	15	nmod:poss	_	_
15	embassy	embassy	NOUN	NN	Number=Sing	13	dobj	_	_
16	,	,	PUNCT	,	_	3	punct	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	senior	senior	ADJ	JJ	Degree=Pos	19	amod	_	_
19	official	official	NOUN	NN	Number=Sing	20	nsubj	_	_
20	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
21	on	on	ADP	IN	_	22	case	_	_
22	Saturday	Saturday	PROPN	NNP	Number=Sing	20	nmod	_	_
23	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test152': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test152']['sents']['0']:
            print(return_dict['test152']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test152']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)",str(return_dict['test152']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)","noevent"]
            print("test152 Failed")
    except:
        print("test152 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test152']['sents']['0']:
        verbs=return_dict['test152']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test152']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test152']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test152']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test152']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test152():
    text="""Ethiopia will break relations with Libya almost five years after crowds 
trashed its embassy.
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	break	break	VERB	VB	VerbForm=Inf	0	root	_	_
4	relations	relation	NOUN	NNS	Number=Plur	3	dobj	_	_
5	with	with	ADP	IN	_	6	case	_	_
6	Libya	Libya	PROPN	NNP	Number=Sing	3	nmod	_	_
7	almost	almost	ADV	RB	_	8	advmod	_	_
8	five	five	NUM	CD	NumType=Card	9	nummod	_	_
9	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
10	after	after	ADP	IN	_	11	case	_	_
11	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
12	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	11	acl	_	_
13	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	14	nmod:poss	_	_
14	embassy	embassy	NOUN	NN	Number=Sing	12	dobj	_	_
15	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test153': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test153']['sents']['0']:
            print(return_dict['test153']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test153']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)",str(return_dict['test153']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)","noevent"]
            print("test153 Failed")
    except:
        print("test153 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test153']['sents']['0']:
        verbs=return_dict['test153']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test153']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test153']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test153']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test153']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test153():
    text="""Ethiopia broken down a treaty with Libya's  almost five years after 
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	broken	break	VERB	VB	VerbForm=Inf	0	root	_	_
3	down	down	ADP	RP	_	2	compound:prt	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	treaty	treaty	NOUN	NN	Number=Sing	2	dobj	_	_
6	with	with	ADP	IN	_	13	case	_	_
7	Libya	Libya	PROPN	NNP	Number=Sing	13	nmod:poss	_	_
8	's	's	PART	POS	_	7	case	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	13	nmod:npmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	5	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test154': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],1246)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test154']['sents']['0']:
            print(return_dict['test154']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test154']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1246)",str(return_dict['test154']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1246)","noevent"]
            print("test154 Failed")
    except:
        print("test154 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test154']['sents']['0']:
        verbs=return_dict['test154']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test154']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test154']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test154']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test154']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test154():
    text="""Ethiopia broken down a treaty with Libya's  almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	broken	break	VERB	VB	VerbForm=Inf	0	root	_	_
3	down	down	ADP	RP	_	2	compound:prt	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	treaty	treaty	NOUN	NN	Number=Sing	2	dobj	_	_
6	with	with	ADP	IN	_	13	case	_	_
7	Libya	Libya	PROPN	NNP	Number=Sing	13	nmod:poss	_	_
8	's	's	PART	POS	_	7	case	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	13	nmod:npmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	5	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test155': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],1246)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test155']['sents']['0']:
            print(return_dict['test155']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test155']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1246)",str(return_dict['test155']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1246)","noevent"]
            print("test155 Failed")
    except:
        print("test155 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test155']['sents']['0']:
        verbs=return_dict['test155']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test155']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test155']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test155']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test155']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test155():
    text="""Ethiopia is acting strangely with Libya almost five years after  
crowds trashed its embassy. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	acting	act	VERB	VBG	Tense=Pres|VerbForm=Part	0	root	_	_
4	strangely	strangely	ADV	RB	_	8	advmod	_	_
5	with	with	ADP	IN	_	6	case	_	_
6	Libya	Libya	PROPN	NNP	Number=Sing	4	nmod	_	_
7	almost	almost	ADV	RB	_	8	advmod	_	_
8	five	five	NUM	CD	NumType=Card	9	nummod	_	_
9	years	year	NOUN	NNS	Number=Plur	11	nmod:npmod	_	_
10	after	after	ADP	IN	_	11	case	_	_
11	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
12	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	11	acl	_	_
13	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	14	nmod:poss	_	_
14	embassy	embassy	NOUN	NN	Number=Sing	12	dobj	_	_
15	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test156': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],100)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test156']['sents']['0']:
            print(return_dict['test156']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test156']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],100)",str(return_dict['test156']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],100)","noevent"]
            print("test156 Failed")
    except:
        print("test156 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test156']['sents']['0']:
        verbs=return_dict['test156']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test156']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test156']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test156']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test156']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test156():
    text="""Ethiopia has acted oddly with respect to Libya almost five years after  
crowds trashed its embassy
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	acted	act	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	oddly	oddly	ADV	RB	_	3	advmod	_	_
5	with	with	ADP	IN	_	6	case	_	_
6	respect	respect	NOUN	NN	Number=Sing	3	nmod	_	_
7	to	to	ADP	IN	_	8	case	_	_
8	Libya	Libya	PROPN	NNP	Number=Sing	6	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	13	nmod:npmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test157': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],100)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test157']['sents']['0']:
            print(return_dict['test157']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test157']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],100)",str(return_dict['test157']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],100)","noevent"]
            print("test157 Failed")
    except:
        print("test157 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test157']['sents']['0']:
        verbs=return_dict['test157']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test157']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test157']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test157']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test157']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test157():
    text="""Ethiopia indicated it would act now with Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	indicated	indicate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	it	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	5	nsubj	_	_
4	would	would	AUX	MD	VerbForm=Fin	5	aux	_	_
5	act	act	VERB	VB	VerbForm=Inf	2	ccomp	_	_
6	now	now	ADV	RB	_	5	advmod	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Libya	Libya	PROPN	NNP	Number=Sing	5	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	13	nmod:npmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	2	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test158': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],1010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test158']['sents']['0']:
            print(return_dict['test158']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test158']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1010)",str(return_dict['test158']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1010)","noevent"]
            print("test158 Failed")
    except:
        print("test158 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test158']['sents']['0']:
        verbs=return_dict['test158']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test158']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test158']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test158']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test158']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test158():
    text="""Ethiopia indicated it would acting now  with Libya's  almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	indicated	indicate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	it	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	5	nsubj	_	_
4	would	would	AUX	MD	VerbForm=Fin	5	aux	_	_
5	acting	act	VERB	VBG	VerbForm=Ger	2	ccomp	_	_
6	now	now	ADV	RB	_	5	advmod	_	_
7	with	with	ADP	IN	_	14	case	_	_
8	Libya	Libya	PROPN	NNP	Number=Sing	14	nmod:poss	_	_
9	's	's	PART	POS	_	8	case	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	14	nmod:npmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	2	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test159': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],1010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test159']['sents']['0']:
            print(return_dict['test159']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test159']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1010)",str(return_dict['test159']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1010)","noevent"]
            print("test159 Failed")
    except:
        print("test159 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test159']['sents']['0']:
        verbs=return_dict['test159']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test159']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test159']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test159']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test159']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test159():
    text="""Ethiopia indicated it should have acted against Libya almost five years after  
crowds trashed its embassy. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	indicated	indicate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	it	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	6	nsubj	_	_
4	should	should	AUX	MD	VerbForm=Fin	6	aux	_	_
5	have	have	AUX	VB	VerbForm=Inf	6	aux	_	_
6	acted	act	VERB	VBN	Tense=Past|VerbForm=Part	2	ccomp	_	_
7	against	against	ADP	IN	_	8	case	_	_
8	Libya	Libya	PROPN	NNP	Number=Sing	6	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	6	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	6	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test160': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],1011)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test160']['sents']['0']:
            print(return_dict['test160']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test160']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1011)",str(return_dict['test160']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],1011)","noevent"]
            print("test160 Failed")
    except:
        print("test160 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test160']['sents']['0']:
        verbs=return_dict['test160']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test160']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test160']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test160']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test160']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test160():
    text="""Ethiopia act on a resolution  with Libya's  almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	compound	_	_
2	act	act	NOUN	NN	Number=Sing	0	root	_	_
3	on	on	ADP	IN	_	5	case	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	resolution	resolution	NOUN	NN	Number=Sing	2	nmod	_	_
6	with	with	ADP	IN	_	13	case	_	_
7	Libya	Libya	PROPN	NNP	Number=Sing	13	nmod:poss	_	_
8	's	's	PART	POS	_	7	case	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	13	nmod:npmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	2	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test161': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test161']['sents']['0']:
            print(return_dict['test161']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test161']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],010)",str(return_dict['test161']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],010)","noevent"]
            print("test161 Failed")
    except:
        print("test161 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test161']['sents']['0']:
        verbs=return_dict['test161']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test161']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test161']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test161']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test161']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test161():
    text="""Ethiopia is acting on a resolution with Libya's  almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	acting	act	VERB	VBG	Tense=Pres|VerbForm=Part	0	root	_	_
4	on	on	ADP	IN	_	6	case	_	_
5	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
6	resolution	resolution	NOUN	NN	Number=Sing	3	nmod	_	_
7	with	with	ADP	IN	_	12	case	_	_
8	Libya	Libya	PROPN	NNP	Number=Sing	12	nmod:poss	_	_
9	's	's	PART	POS	_	8	case	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	6	nmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	12	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	12	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	17	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	17	acl:relcl	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test162': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test162']['sents']['0']:
            print(return_dict['test162']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test162']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],010)",str(return_dict['test162']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],010)","noevent"]
            print("test162 Failed")
    except:
        print("test162 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test162']['sents']['0']:
        verbs=return_dict['test162']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test162']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test162']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test162']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test162']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test162():
    text="""Ethiopia acted on a resolution against Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	acted	act	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	on	on	ADP	IN	_	5	case	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	resolution	resolution	NOUN	NN	Number=Sing	2	nmod	_	_
6	against	against	ADP	IN	_	7	case	_	_
7	Libya	Libya	PROPN	NNP	Number=Sing	5	nmod	_	_
8	almost	almost	ADV	RB	_	9	advmod	_	_
9	five	five	NUM	CD	NumType=Card	10	nummod	_	_
10	years	year	NOUN	NNS	Number=Plur	12	nmod:npmod	_	_
11	after	after	ADP	IN	_	12	case	_	_
12	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
13	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	conj	_	_
14	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	15	nmod:poss	_	_
15	embassy	embassy	NOUN	NN	Number=Sing	13	dobj	_	_
16	,	,	PUNCT	,	_	15	punct	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	senior	senior	ADJ	JJ	Degree=Pos	19	amod	_	_
19	official	official	NOUN	NN	Number=Sing	20	nsubj	_	_
20	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	15	acl:relcl	_	_
21	on	on	ADP	IN	_	22	case	_	_
22	Saturday	Saturday	PROPN	NNP	Number=Sing	20	nmod	_	_
23	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test163': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test163']['sents']['0']:
            print(return_dict['test163']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test163']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],010)",str(return_dict['test163']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],010)","noevent"]
            print("test163 Failed")
    except:
        print("test163 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test163']['sents']['0']:
        verbs=return_dict['test163']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test163']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test163']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test163']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test163']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test163():
    text="""Ethiopia will act on some programs with Libya  almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	act	act	VERB	VB	VerbForm=Inf	0	root	_	_
4	on	on	ADP	IN	_	6	case	_	_
5	some	some	DET	DT	_	6	det	_	_
6	programs	program	NOUN	NNS	Number=Plur	3	nmod	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Libya	Libya	PROPN	NNP	Number=Sing	6	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	13	nmod:npmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	16	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	16	acl:relcl	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test164': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],051)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test164']['sents']['0']:
            print(return_dict['test164']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test164']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],051)",str(return_dict['test164']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],051)","noevent"]
            print("test164 Failed")
    except:
        print("test164 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test164']['sents']['0']:
        verbs=return_dict['test164']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test164']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test164']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test164']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test164']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test164():
    text="""Ethiopia acted on some programs with Libya almost five years after  
crowds trashed its embassy. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	acted	act	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	on	on	ADP	IN	_	5	case	_	_
4	some	some	DET	DT	_	5	det	_	_
5	programs	program	NOUN	NNS	Number=Plur	2	nmod	_	_
6	with	with	ADP	IN	_	7	case	_	_
7	Libya	Libya	PROPN	NNP	Number=Sing	5	nmod	_	_
8	almost	almost	ADV	RB	_	9	advmod	_	_
9	five	five	NUM	CD	NumType=Card	10	nummod	_	_
10	years	year	NOUN	NNS	Number=Plur	12	nmod:npmod	_	_
11	after	after	ADP	IN	_	12	case	_	_
12	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
13	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	conj	_	_
14	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	15	nmod:poss	_	_
15	embassy	embassy	NOUN	NN	Number=Sing	13	dobj	_	_
16	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test165': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],051)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test165']['sents']['0']:
            print(return_dict['test165']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test165']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],051)",str(return_dict['test165']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],051)","noevent"]
            print("test165 Failed")
    except:
        print("test165 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test165']['sents']['0']:
        verbs=return_dict['test165']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test165']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test165']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test165']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test165']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test165():
    text="""Ethiopia broken down with Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	broken	break	VERB	VB	VerbForm=Inf	0	root	_	_
3	down	down	ADV	RB	_	2	advmod	_	_
4	with	with	ADP	IN	_	5	case	_	_
5	Libya	Libya	PROPN	NNP	Number=Sing	2	nmod	_	_
6	almost	almost	ADV	RB	_	7	advmod	_	_
7	five	five	NUM	CD	NumType=Card	8	nummod	_	_
8	years	year	NOUN	NNS	Number=Plur	2	nmod:tmod	_	_
9	after	after	ADP	IN	_	10	case	_	_
10	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
11	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	10	acl	_	_
12	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	13	nmod:poss	_	_
13	embassy	embassy	NOUN	NN	Number=Sing	11	dobj	_	_
14	,	,	PUNCT	,	_	2	punct	_	_
15	a	a	DET	DT	Definite=Ind|PronType=Art	17	det	_	_
16	senior	senior	ADJ	JJ	Degree=Pos	17	amod	_	_
17	official	official	NOUN	NN	Number=Sing	18	nsubj	_	_
18	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
19	on	on	ADP	IN	_	20	case	_	_
20	Saturday	Saturday	PROPN	NNP	Number=Sing	18	nmod	_	_
21	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test166': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test166']['sents']['0']:
            print(return_dict['test166']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test166']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)",str(return_dict['test166']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],120)","noevent"]
            print("test166 Failed")
    except:
        print("test166 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test166']['sents']['0']:
        verbs=return_dict['test166']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test166']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test166']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test166']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test166']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test166():
    text="""Ethiopia is about to depart from Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	depart	depart	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	from	from	ADP	IN	_	7	case	_	_
7	Libya	Libya	PROPN	NNP	Number=Sing	5	nmod	_	_
8	almost	almost	ADV	RB	_	9	advmod	_	_
9	five	five	NUM	CD	NumType=Card	10	nummod	_	_
10	years	year	NOUN	NNS	Number=Plur	12	nmod:npmod	_	_
11	after	after	ADP	IN	_	12	case	_	_
12	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
13	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	12	acl	_	_
14	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	15	nmod:poss	_	_
15	embassy	embassy	NOUN	NN	Number=Sing	13	dobj	_	_
16	,	,	PUNCT	,	_	3	punct	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	senior	senior	ADJ	JJ	Degree=Pos	19	amod	_	_
19	official	official	NOUN	NN	Number=Sing	20	nsubj	_	_
20	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
21	on	on	ADP	IN	_	22	case	_	_
22	Saturday	Saturday	PROPN	NNP	Number=Sing	20	nmod	_	_
23	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test167': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test167']['sents']['0']:
            print(return_dict['test167']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test167']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],040)",str(return_dict['test167']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],040)","noevent"]
            print("test167 Failed")
    except:
        print("test167 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test167']['sents']['0']:
        verbs=return_dict['test167']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test167']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test167']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test167']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test167']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test167():
    text="""Ethiopia departs from Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	compound	_	_
2	departs	depart	NOUN	NNS	Number=Plur	0	root	_	_
3	from	from	ADP	IN	_	4	case	_	_
4	Libya	Libya	PROPN	NNP	Number=Sing	2	nmod	_	_
5	almost	almost	ADV	RB	_	6	advmod	_	_
6	five	five	NUM	CD	NumType=Card	7	nummod	_	_
7	years	year	NOUN	NNS	Number=Plur	9	nmod:npmod	_	_
8	after	after	ADP	IN	_	9	case	_	_
9	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
10	trashed	trashed	VERB	VBN	Tense=Past|VerbForm=Part	2	acl	_	_
11	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
12	embassy	embassy	NOUN	NN	Number=Sing	10	dobj	_	_
13	,	,	PUNCT	,	_	2	punct	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	senior	senior	ADJ	JJ	Degree=Pos	16	amod	_	_
16	official	official	NOUN	NN	Number=Sing	17	nsubj	_	_
17	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
18	on	on	ADP	IN	_	19	case	_	_
19	Saturday	Saturday	PROPN	NNP	Number=Sing	17	nmod	_	_
20	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test168': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test168']['sents']['0']:
            print(return_dict['test168']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test168']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],040)",str(return_dict['test168']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],040)","noevent"]
            print("test168 Failed")
    except:
        print("test168 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test168']['sents']['0']:
        verbs=return_dict['test168']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test168']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test168']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test168']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test168']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test168():
    text="""Ethiopia departed from Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	departed	depart	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	from	from	ADP	IN	_	4	case	_	_
4	Libya	Libya	PROPN	NNP	Number=Sing	2	nmod	_	_
5	almost	almost	ADV	RB	_	6	advmod	_	_
6	five	five	NUM	CD	NumType=Card	7	nummod	_	_
7	years	year	NOUN	NNS	Number=Plur	9	nmod:npmod	_	_
8	after	after	ADP	IN	_	9	case	_	_
9	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
10	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	advcl	_	_
11	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
12	embassy	embassy	NOUN	NN	Number=Sing	10	dobj	_	_
13	,	,	PUNCT	,	_	12	punct	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	senior	senior	ADJ	JJ	Degree=Pos	16	amod	_	_
16	official	official	NOUN	NN	Number=Sing	17	nsubj	_	_
17	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	12	acl:relcl	_	_
18	on	on	ADP	IN	_	19	case	_	_
19	Saturday	Saturday	PROPN	NNP	Number=Sing	17	nmod	_	_
20	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test169': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],040)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test169']['sents']['0']:
            print(return_dict['test169']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test169']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],040)",str(return_dict['test169']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],040)","noevent"]
            print("test169 Failed")
    except:
        print("test169 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test169']['sents']['0']:
        verbs=return_dict['test169']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test169']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test169']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test169']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test169']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test169():
    text="""Ethiopia departx from Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	name	_	_
2	departx	departx	NOUN	NN	Number=Sing	0	root	_	_
3	from	from	ADP	IN	_	4	case	_	_
4	Libya	Libya	PROPN	NNP	Number=Sing	2	nmod	_	_
5	almost	almost	ADV	RB	_	6	advmod	_	_
6	five	five	NUM	CD	NumType=Card	7	nummod	_	_
7	years	year	NOUN	NNS	Number=Plur	9	nmod:npmod	_	_
8	after	after	ADP	IN	_	9	case	_	_
9	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
10	trashed	trashed	VERB	VBN	Tense=Past|VerbForm=Part	9	acl	_	_
11	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
12	embassy	embassy	NOUN	NN	Number=Sing	10	dobj	_	_
13	,	,	PUNCT	,	_	2	punct	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	senior	senior	ADJ	JJ	Degree=Pos	16	amod	_	_
16	official	official	NOUN	NN	Number=Sing	17	nsubj	_	_
17	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	parataxis	_	_
18	on	on	ADP	IN	_	19	case	_	_
19	Saturday	Saturday	PROPN	NNP	Number=Sing	17	nmod	_	_
20	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test170': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test170']['sents']['0']:
            print(return_dict['test170']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test170']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test170']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test170 Failed")
    except:
        print("test170 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test170']['sents']['0']:
        verbs=return_dict['test170']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test170']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test170']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test170']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test170']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test170():
    text="""Ethiopia departes from Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	departes	depart	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	0	root	_	_
3	from	from	ADP	IN	_	4	case	_	_
4	Libya	Libya	PROPN	NNP	Number=Sing	2	nmod	_	_
5	almost	almost	ADV	RB	_	6	advmod	_	_
6	five	five	NUM	CD	NumType=Card	7	nummod	_	_
7	years	year	NOUN	NNS	Number=Plur	9	nmod:npmod	_	_
8	after	after	ADP	IN	_	9	case	_	_
9	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
10	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	2	advcl	_	_
11	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
12	embassy	embassy	NOUN	NN	Number=Sing	10	dobj	_	_
13	,	,	PUNCT	,	_	12	punct	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	senior	senior	ADJ	JJ	Degree=Pos	16	amod	_	_
16	official	official	NOUN	NN	Number=Sing	17	nsubj	_	_
17	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	12	acl:relcl	_	_
18	on	on	ADP	IN	_	19	case	_	_
19	Saturday	Saturday	PROPN	NNP	Number=Sing	17	nmod	_	_
20	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test171': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test171']['sents']['0']:
            print(return_dict['test171']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test171']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test171']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test171 Failed")
    except:
        print("test171 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test171']['sents']['0']:
        verbs=return_dict['test171']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test171']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test171']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test171']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test171']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test171():
    text="""Ethiopia deplored from Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	deplored	deplor	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	from	from	ADP	IN	_	4	case	_	_
4	Libya	Libya	PROPN	NNP	Number=Sing	2	nmod	_	_
5	almost	almost	ADV	RB	_	6	advmod	_	_
6	five	five	NUM	CD	NumType=Card	7	nummod	_	_
7	years	year	NOUN	NNS	Number=Plur	9	nmod:npmod	_	_
8	after	after	ADP	IN	_	9	case	_	_
9	crowds	crowd	NOUN	NNS	Number=Plur	2	nmod	_	_
10	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	advcl	_	_
11	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
12	embassy	embassy	NOUN	NN	Number=Sing	10	dobj	_	_
13	,	,	PUNCT	,	_	12	punct	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	senior	senior	ADJ	JJ	Degree=Pos	16	amod	_	_
16	official	official	NOUN	NN	Number=Sing	17	nsubj	_	_
17	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	12	acl:relcl	_	_
18	on	on	ADP	IN	_	19	case	_	_
19	Saturday	Saturday	PROPN	NNP	Number=Sing	17	nmod	_	_
20	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test172': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test172']['sents']['0']:
            print(return_dict['test172']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test172']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],111)",str(return_dict['test172']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],111)","noevent"]
            print("test172 Failed")
    except:
        print("test172 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test172']['sents']['0']:
        verbs=return_dict['test172']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test172']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test172']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test172']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test172']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test172():
    text="""Ethiopia indicated it deplored Libya almost five years after  
crowds trashed its embassy, a senior official said on Saturday. 
"""
    parse="""1	Ethiopia	Ethiopia	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	indicated	indicate	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	it	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	4	nsubj	_	_
4	deplored	deplor	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	ccomp	_	_
5	Libya	Libya	PROPN	NNP	Number=Sing	4	dobj	_	_
6	almost	almost	ADV	RB	_	7	advmod	_	_
7	five	five	NUM	CD	NumType=Card	8	nummod	_	_
8	years	year	NOUN	NNS	Number=Plur	10	nmod:npmod	_	_
9	after	after	ADP	IN	_	10	case	_	_
10	crowds	crowd	NOUN	NNS	Number=Plur	4	nmod	_	_
11	trashed	trash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	advcl	_	_
12	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	13	nmod:poss	_	_
13	embassy	embassy	NOUN	NN	Number=Sing	11	dobj	_	_
14	,	,	PUNCT	,	_	13	punct	_	_
15	a	a	DET	DT	Definite=Ind|PronType=Art	17	det	_	_
16	senior	senior	ADJ	JJ	Degree=Pos	17	amod	_	_
17	official	official	NOUN	NN	Number=Sing	18	nsubj	_	_
18	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	13	acl:relcl	_	_
19	on	on	ADP	IN	_	20	case	_	_
20	Saturday	Saturday	PROPN	NNP	Number=Sing	18	nmod	_	_
21	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test173': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ETH],[LBY],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test173']['sents']['0']:
            print(return_dict['test173']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test173']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],111)",str(return_dict['test173']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ETH],[LBY],111)","noevent"]
            print("test173 Failed")
    except:
        print("test173 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test173']['sents']['0']:
        verbs=return_dict['test173']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test173']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test173']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test173']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test173']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test173():
    text="""Gollum was seen to break into an anti- Gondor parade on Saturday. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	3	nsubjpass	_	_
2	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	3	auxpass	_	_
3	seen	see	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	break	break	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	into	into	ADP	IN	_	10	case	_	_
7	an	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
8	anti-	anti-	SYM	SYM	_	10	punct	_	_
9	Gondor	Gondor	NOUN	NN	Number=Sing	10	compound	_	_
10	parade	parade	NOUN	NN	Number=Sing	5	nmod	_	_
11	on	on	ADP	IN	_	12	case	_	_
12	Saturday	Saturday	PROPN	NNP	Number=Sing	10	nmod	_	_
13	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test174': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test174']['sents']['0']:
            print(return_dict['test174']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test174']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],120)",str(return_dict['test174']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],120)","noevent"]
            print("test174 Failed")
    except:
        print("test174 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test174']['sents']['0']:
        verbs=return_dict['test174']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test174']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test174']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test174']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test174']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test174():
    text="""Gollum abandoned an anti- Gondor parade on Saturday. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	abandoned	abandon	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	an	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
4	anti-	anti-	SYM	NFP	_	6	punct	_	_
5	Gondor	Gondor	NOUN	NN	Number=Sing	6	compound	_	_
6	parade	parade	NOUN	NN	Number=Sing	2	dobj	_	_
7	on	on	ADP	IN	_	8	case	_	_
8	Saturday	Saturday	PROPN	NNP	Number=Sing	6	nmod	_	_
9	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test175': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],345)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test175']['sents']['0']:
            print(return_dict['test175']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test175']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],345)",str(return_dict['test175']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],345)","noevent"]
            print("test175 Failed")
    except:
        print("test175 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test175']['sents']['0']:
        verbs=return_dict['test175']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test175']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test175']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test175']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test175']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test175():
    text="""Gollum will bargain for asylum in Gondor, AFP reported. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	bargain	bargain	VERB	VB	VerbForm=Inf	0	root	_	_
4	for	for	ADP	IN	_	5	case	_	_
5	asylum	asylum	NOUN	NN	Number=Sing	3	nmod	_	_
6	in	in	ADP	IN	_	7	case	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
8	,	,	PUNCT	,	_	3	punct	_	_
9	AFP	AFP	PROPN	NNP	Number=Sing	10	nsubj	_	_
10	reported	report	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
11	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test176': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],063K)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test176']['sents']['0']:
            print(return_dict['test176']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test176']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],063K)",str(return_dict['test176']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],063K)","noevent"]
            print("test176 Failed")
    except:
        print("test176 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test176']['sents']['0']:
        verbs=return_dict['test176']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test176']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test176']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test176']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test176']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test176():
    text="""Gollum will bargain foreign asylum in Gondor, AFP reported. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	bargain	bargain	VERB	VB	VerbForm=Inf	0	root	_	_
4	foreign	foreign	ADJ	JJ	Degree=Pos	5	amod	_	_
5	asylum	asylum	NOUN	NN	Number=Sing	3	dobj	_	_
6	in	in	ADP	IN	_	7	case	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
8	,	,	PUNCT	,	_	3	punct	_	_
9	AFP	AFP	PROPN	NNP	Number=Sing	10	nsubj	_	_
10	reported	report	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
11	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test177': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],063L)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test177']['sents']['0']:
            print(return_dict['test177']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test177']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],063L)",str(return_dict['test177']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],063L)","noevent"]
            print("test177 Failed")
    except:
        print("test177 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test177']['sents']['0']:
        verbs=return_dict['test177']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test177']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test177']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test177']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test177']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test177():
    text="""Gollum was known to break into an anti- Gondor parade on Saturday. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	3	nsubjpass	_	_
2	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	3	auxpass	_	_
3	known	know	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	break	break	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	into	into	ADP	IN	_	10	case	_	_
7	an	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
8	anti-	anti-	SYM	SYM	_	10	punct	_	_
9	Gondor	Gondor	NOUN	NN	Number=Sing	10	compound	_	_
10	parade	parade	NOUN	NN	Number=Sing	5	nmod	_	_
11	on	on	ADP	IN	_	12	case	_	_
12	Saturday	Saturday	PROPN	NNP	Number=Sing	5	nmod	_	_
13	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test178': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],120)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test178']['sents']['0']:
            print(return_dict['test178']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test178']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],120)",str(return_dict['test178']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],120)","noevent"]
            print("test178 Failed")
    except:
        print("test178 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test178']['sents']['0']:
        verbs=return_dict['test178']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test178']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test178']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test178']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test178']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test178():
    text="""Gollum was in an accord with an anti- Gondor parade on Saturday. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	5	nsubj	_	_
2	was	be	VERB	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	5	cop	_	_
3	in	in	ADP	IN	_	5	case	_	_
4	an	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	accord	accord	NOUN	NN	Number=Sing	0	root	_	_
6	with	with	ADP	IN	_	10	case	_	_
7	an	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
8	anti-	anti-	SYM	SYM	_	10	punct	_	_
9	Gondor	Gondor	ADJ	JJ	Degree=Pos	10	amod	_	_
10	parade	parade	NOUN	NN	Number=Sing	5	nmod	_	_
11	on	on	ADP	IN	_	12	case	_	_
12	Saturday	Saturday	PROPN	NNP	Number=Sing	10	nmod	_	_
13	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test179': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test179']['sents']['0']:
            print(return_dict['test179']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test179']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"",str(return_dict['test179']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"","noevent"]
            print("test179 Failed")
    except:
        print("test179 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test179']['sents']['0']:
        verbs=return_dict['test179']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test179']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test179']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test179']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test179']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test179():
    text="""Ithilen's palace guard militia was freed from Barad-dur after that 
group yielded ground seized in six days of fighting.
"""
    parse="""1	Ithilen	Ithilen	PROPN	NNP	Number=Sing	5	nmod:poss	_	_
2	's	's	PART	POS	_	1	case	_	_
3	palace	palace	NOUN	NN	Number=Sing	4	compound	_	_
4	guard	guard	NOUN	NN	Number=Sing	5	compound	_	_
5	militia	militia	NOUN	NN	Number=Sing	7	nsubjpass	_	_
6	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	7	auxpass	_	_
7	freed	free	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
8	from	from	ADP	IN	_	9	case	_	_
9	Barad-dur	Barad-dur	PROPN	NNP	Number=Sing	7	nmod	_	_
10	after	after	ADP	IN	_	14	case	_	_
11	that	that	DET	DT	Number=Sing|PronType=Dem	14	det	_	_
12	group	group	NOUN	NN	Number=Sing	14	compound	_	_
13	yielded	yield	VERB	VBN	Tense=Past|VerbForm=Part	14	amod	_	_
14	ground	ground	NOUN	NN	Number=Sing	7	nmod	_	_
15	seized	seize	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	in	in	ADP	IN	_	18	case	_	_
17	six	six	NUM	CD	NumType=Card	18	nummod	_	_
18	days	day	NOUN	NNS	Number=Plur	15	nmod	_	_
19	of	of	ADP	IN	_	20	case	_	_
20	fighting	fighting	NOUN	NN	Number=Sing	18	nmod	_	_
21	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test180': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950114'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([MOR],[ITH],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test180']['sents']['0']:
            print(return_dict['test180']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test180']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[ITH],080)",str(return_dict['test180']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MOR],[ITH],080)","noevent"]
            print("test180 Failed")
    except:
        print("test180 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test180']['sents']['0']:
        verbs=return_dict['test180']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test180']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test180']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test180']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test180']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test180():
    text="""Arnor President Umbardacil has again appealed for peace in Ithilen state-run television in 
a message to the spiritual leader of the war-torn nation's influential 
Douzu community
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	2	compound	_	_
2	President	President	PROPN	NNP	Number=Sing	3	compound	_	_
3	Umbardacil	Umbardacil	PROPN	NNP	Number=Sing	6	nsubj	_	_
4	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	aux	_	_
5	again	again	ADV	RB	_	6	advmod	_	_
6	appealed	appeal	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
7	for	for	ADP	IN	_	8	case	_	_
8	peace	peace	NOUN	NN	Number=Sing	6	nmod	_	_
9	in	in	ADP	IN	_	12	case	_	_
10	Ithilen	Ithilen	PROPN	NNP	Number=Sing	12	compound	_	_
11	state-run	state-run	NOUN	NN	Number=Sing	12	compound	_	_
12	television	television	NOUN	NN	Number=Sing	6	nmod	_	_
13	in	in	ADP	IN	_	15	case	_	_
14	a	a	DET	DT	Definite=Ind|PronType=Art	15	det	_	_
15	message	message	NOUN	NN	Number=Sing	6	nmod	_	_
16	to	to	ADP	IN	_	19	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	19	det	_	_
18	spiritual	spiritual	ADJ	JJ	Degree=Pos	19	amod	_	_
19	leader	leader	NOUN	NN	Number=Sing	15	nmod	_	_
20	of	of	ADP	IN	_	27	case	_	_
21	the	the	DET	DT	Definite=Def|PronType=Art	23	det	_	_
22	war-torn	war-torn	ADJ	JJ	Degree=Pos	23	amod	_	_
23	nation	nation	NOUN	NN	Number=Sing	27	nmod:poss	_	_
24	's	's	PART	POS	_	23	case	_	_
25	influential	influential	ADJ	JJ	Degree=Pos	27	amod	_	_
26	Douzu	Douzu	PROPN	NNP	Number=Sing	27	compound	_	_
27	community	community	NOUN	NN	Number=Sing	19	nmod	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test181': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950116'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARNGOV],[ITHTV],027)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test181']['sents']['0']:
            print(return_dict['test181']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test181']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITHTV],027)",str(return_dict['test181']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARNGOV],[ITHTV],027)","noevent"]
            print("test181 Failed")
    except:
        print("test181 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test181']['sents']['0']:
        verbs=return_dict['test181']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test181']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test181']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test181']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test181']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test181():
    text="""Gollum was seen to break in an anti- Gondor parade on Saturday. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	3	nsubjpass	_	_
2	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	3	auxpass	_	_
3	seen	see	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	break	break	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	in	in	ADP	IN	_	5	compound:prt	_	_
7	an	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
8	anti-	anti-	SYM	SYM	_	10	punct	_	_
9	Gondor	Gondor	NOUN	NN	Number=Sing	10	compound	_	_
10	parade	parade	NOUN	NN	Number=Sing	5	dobj	_	_
11	on	on	ADP	IN	_	12	case	_	_
12	Saturday	Saturday	PROPN	NNP	Number=Sing	5	nmod	_	_
13	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test182': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[HOB],075)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test182']['sents']['0']:
            print(return_dict['test182']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test182']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[HOB],075)",str(return_dict['test182']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[HOB],075)","noevent"]
            print("test182 Failed")
    except:
        print("test182 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test182']['sents']['0']:
        verbs=return_dict['test182']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test182']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test182']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test182']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test182']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test182():
    text="""Gollum abandoned efforts to stop an anti- Gondor parade on Saturday. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	abandoned	abandon	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	efforts	effort	NOUN	NNS	Number=Plur	2	dobj	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	stop	stop	VERB	VB	VerbForm=Inf	3	acl	_	_
6	an	a	DET	DT	Definite=Ind|PronType=Art	9	det	_	_
7	anti-	anti-	SYM	SYM	_	9	punct	_	_
8	Gondor	Gondor	ADJ	JJ	Degree=Pos	9	amod	_	_
9	parade	parade	NOUN	NN	Number=Sing	5	dobj	_	_
10	on	on	ADP	IN	_	11	case	_	_
11	Saturday	Saturday	PROPN	NNP	Number=Sing	5	nmod	_	_
12	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test183': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],345)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test183']['sents']['0']:
            print(return_dict['test183']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test183']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],345)",str(return_dict['test183']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],345)","noevent"]
            print("test183 Failed")
    except:
        print("test183 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test183']['sents']['0']:
        verbs=return_dict['test183']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test183']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test183']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test183']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test183']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test183():
    text="""Gollum allowed that Mordor isn't a really pleasant place to visit. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	allowed	allow	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	that	that	SCONJ	IN	_	10	mark	_	_
4	Mordor	Mordor	PROPN	NNP	Number=Sing	10	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	10	cop	_	_
6	n't	not	PART	RB	_	10	neg	_	_
7	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
8	really	really	ADV	RB	_	9	advmod	_	_
9	pleasant	pleasant	ADJ	JJ	Degree=Pos	10	amod	_	_
10	place	place	NOUN	NN	Number=Sing	2	ccomp	_	_
11	to	to	PART	TO	_	12	mark	_	_
12	visit	visit	VERB	VB	VerbForm=Inf	10	acl	_	_
13	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test184': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[MOR],013)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test184']['sents']['0']:
            print(return_dict['test184']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test184']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],013)",str(return_dict['test184']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],013)","noevent"]
            print("test184 Failed")
    except:
        print("test184 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test184']['sents']['0']:
        verbs=return_dict['test184']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test184']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test184']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test184']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test184']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test184():
    text="""Gollum allowed that Mordor isn't a real pleasant place to visit. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	allowed	allow	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	that	that	SCONJ	IN	_	10	mark	_	_
4	Mordor	Mordor	PROPN	NNP	Number=Sing	10	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	10	cop	_	_
6	n't	not	PART	RB	_	10	neg	_	_
7	a	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
8	real	real	ADJ	JJ	Degree=Pos	10	amod	_	_
9	pleasant	pleasant	ADJ	JJ	Degree=Pos	10	amod	_	_
10	place	place	NOUN	NN	Number=Sing	2	ccomp	_	_
11	to	to	PART	TO	_	12	mark	_	_
12	visit	visit	VERB	VB	VerbForm=Inf	10	advcl	_	_
13	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test185': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[MOR],013)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test185']['sents']['0']:
            print(return_dict['test185']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test185']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],013)",str(return_dict['test185']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],013)","noevent"]
            print("test185 Failed")
    except:
        print("test185 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test185']['sents']['0']:
        verbs=return_dict['test185']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test185']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test185']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test185']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test185']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test185():
    text="""Gollum allowed that Mordor isn't a real easy or pleasant place to visit. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	allowed	allow	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	that	that	SCONJ	IN	_	12	mark	_	_
4	Mordor	Mordor	PROPN	NNP	Number=Sing	12	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	12	cop	_	_
6	n't	not	PART	RB	_	12	neg	_	_
7	a	a	DET	DT	Definite=Ind|PronType=Art	12	det	_	_
8	real	real	ADJ	JJ	Degree=Pos	12	amod	_	_
9	easy	easy	ADJ	JJ	Degree=Pos	12	amod	_	_
10	or	or	CONJ	CC	_	9	cc	_	_
11	pleasant	pleasant	ADJ	JJ	Degree=Pos	9	conj	_	_
12	place	place	NOUN	NN	Number=Sing	2	ccomp	_	_
13	to	to	PART	TO	_	14	mark	_	_
14	visit	visit	VERB	VB	VerbForm=Inf	12	advcl	_	_
15	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test186': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[MOR],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test186']['sents']['0']:
            print(return_dict['test186']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test186']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],080)",str(return_dict['test186']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],080)","noevent"]
            print("test186 Failed")
    except:
        print("test186 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test186']['sents']['0']:
        verbs=return_dict['test186']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test186']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test186']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test186']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test186']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test186():
    text="""Gollum recently allowed that Mordor isn't a such neat place to visit. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	recently	recently	ADV	RB	_	3	advmod	_	_
3	allowed	allow	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
4	that	that	SCONJ	IN	_	11	mark	_	_
5	Mordor	Mordor	PROPN	NNP	Number=Sing	11	nsubj	_	_
6	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	11	cop	_	_
7	n't	not	PART	RB	_	11	neg	_	_
8	a	a	DET	DT	Definite=Ind|PronType=Art	11	det	_	_
9	such	such	ADJ	JJ	Degree=Pos	11	amod	_	_
10	neat	neat	ADJ	JJ	Degree=Pos	11	amod	_	_
11	place	place	NOUN	NN	Number=Sing	3	ccomp	_	_
12	to	to	PART	TO	_	13	mark	_	_
13	visit	visit	VERB	VB	VerbForm=Inf	11	advcl	_	_
14	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test187': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[MOR],025)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test187']['sents']['0']:
            print(return_dict['test187']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test187']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],025)",str(return_dict['test187']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],025)","noevent"]
            print("test187 Failed")
    except:
        print("test187 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test187']['sents']['0']:
        verbs=return_dict['test187']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test187']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test187']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test187']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test187']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test187():
    text="""Gollum recently did allow that Mordor isn't a such neat place to visit. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	4	nsubj	_	_
2	recently	recently	ADV	RB	_	4	advmod	_	_
3	did	do	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	aux	_	_
4	allow	allow	VERB	VB	VerbForm=Inf	0	root	_	_
5	that	that	SCONJ	IN	_	12	mark	_	_
6	Mordor	Mordor	PROPN	NNP	Number=Sing	12	nsubj	_	_
7	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	12	cop	_	_
8	n't	not	PART	RB	_	12	neg	_	_
9	a	a	DET	DT	Definite=Ind|PronType=Art	12	det	_	_
10	such	such	ADJ	JJ	Degree=Pos	12	amod	_	_
11	neat	neat	ADJ	JJ	Degree=Pos	12	amod	_	_
12	place	place	NOUN	NN	Number=Sing	4	ccomp	_	_
13	to	to	PART	TO	_	14	mark	_	_
14	visit	visit	VERB	VB	VerbForm=Inf	12	advcl	_	_
15	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test188': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[MOR],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test188']['sents']['0']:
            print(return_dict['test188']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test188']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],080)",str(return_dict['test188']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],080)","noevent"]
            print("test188 Failed")
    except:
        print("test188 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test188']['sents']['0']:
        verbs=return_dict['test188']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test188']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test188']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test188']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test188']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test188():
    text="""Gollum allowed that Mordor isn't the neatest place to visit. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	allowed	allow	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	that	that	SCONJ	IN	_	9	mark	_	_
4	Mordor	Mordor	PROPN	NNP	Number=Sing	9	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	9	cop	_	_
6	n't	not	PART	RB	_	9	neg	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
8	neatest	neatest	ADJ	JJS	Degree=Sup	9	amod	_	_
9	place	place	NOUN	NN	Number=Sing	2	ccomp	_	_
10	to	to	PART	TO	_	11	mark	_	_
11	visit	visit	VERB	VB	VerbForm=Inf	9	acl	_	_
12	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test189': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[MOR],027)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test189']['sents']['0']:
            print(return_dict['test189']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test189']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],027)",str(return_dict['test189']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],027)","noevent"]
            print("test189 Failed")
    except:
        print("test189 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test189']['sents']['0']:
        verbs=return_dict['test189']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test189']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test189']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test189']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test189']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test189():
    text="""Gollum in recent days did allow that Mordor isn't the neat or cool place to visit. 
"""
    parse="""1	Gollum	Gollum	VERB	VB	Mood=Imp|VerbForm=Fin	6	nsubj	_	_
2	in	in	ADP	IN	_	4	case	_	_
3	recent	recent	ADJ	JJ	Degree=Pos	4	amod	_	_
4	days	day	NOUN	NNS	Number=Plur	1	nmod	_	_
5	did	do	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	6	aux	_	_
6	allow	allow	VERB	VB	VerbForm=Inf	0	root	_	_
7	that	that	SCONJ	IN	_	15	mark	_	_
8	Mordor	Mordor	PROPN	NNP	Number=Sing	15	nsubj	_	_
9	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	15	cop	_	_
10	n't	not	PART	RB	_	15	neg	_	_
11	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
12	neat	neat	ADJ	JJ	Degree=Pos	15	amod	_	_
13	or	or	CONJ	CC	_	12	cc	_	_
14	cool	cool	ADJ	JJ	Degree=Pos	12	conj	_	_
15	place	place	NOUN	NN	Number=Sing	6	ccomp	_	_
16	to	to	PART	TO	_	17	mark	_	_
17	visit	visit	VERB	VB	VerbForm=Inf	15	acl	_	_
18	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test190': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[MOR],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test190']['sents']['0']:
            print(return_dict['test190']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test190']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],080)",str(return_dict['test190']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[MOR],080)","noevent"]
            print("test190 Failed")
    except:
        print("test190 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test190']['sents']['0']:
        verbs=return_dict['test190']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test190']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test190']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test190']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test190']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test190():
    text="""Gollum centre of a diplomatic row between Radagast the Brown called on 
Gondor late Sunday to be allowed to leave Lorien by elves. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	name	_	_
2	centre	centre	NOUN	NN	Number=Sing	0	root	_	_
3	of	of	ADP	IN	_	6	case	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	row	row	NOUN	NN	Number=Sing	2	nmod	_	_
7	between	between	ADP	IN	_	8	case	_	_
8	Radagast	Radagast	PROPN	NNP	Number=Sing	6	nmod	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	Brown	brown	PROPN	NNP	Number=Sing	11	nsubj	_	_
11	called	call	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	acl:relcl	_	_
12	on	on	ADP	IN	_	13	case	_	_
13	Gondor	Gondor	PROPN	NNP	Number=Sing	11	nmod	_	_
14	late	late	ADJ	JJ	Degree=Pos	15	amod	_	_
15	Sunday	Sunday	PROPN	NNP	Number=Sing	11	nmod:tmod	_	_
16	to	to	PART	TO	_	18	mark	_	_
17	be	be	AUX	VB	VerbForm=Inf	18	auxpass	_	_
18	allowed	allow	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	11	xcomp	_	_
19	to	to	PART	TO	_	20	mark	_	_
20	leave	leave	VERB	VB	VerbForm=Inf	18	advcl	_	_
21	Lorien	Lorien	VERB	VBN	Tense=Past|VerbForm=Part	20	xcomp	_	_
22	by	by	ADP	IN	_	23	case	_	_
23	elves	elves	NOUN	NNS	Number=Plur	21	nmod	_	_
24	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test191': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],027)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test191']['sents']['0']:
            print(return_dict['test191']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test191']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],027)",str(return_dict['test191']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],027)","noevent"]
            print("test191 Failed")
    except:
        print("test191 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test191']['sents']['0']:
        verbs=return_dict['test191']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test191']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test191']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test191']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test191']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test191():
    text="""Gollum centre of a diplomatic row between Radagast the Brown called immediately for  
Gondor late Sunday to be allowed to leave Lorien by elves. 
"""
    parse="""1	Gollum	Gollum	PROPN	NNP	Number=Sing	2	name	_	_
2	centre	centre	NOUN	NN	Number=Sing	0	root	_	_
3	of	of	ADP	IN	_	6	case	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	row	row	NOUN	NN	Number=Sing	2	nmod	_	_
7	between	between	ADP	IN	_	8	case	_	_
8	Radagast	Radagast	PROPN	NNP	Number=Sing	6	nmod	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	Brown	brown	PROPN	NNP	Number=Sing	11	nsubj	_	_
11	called	call	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	acl:relcl	_	_
12	immediately	immediately	ADV	RB	_	11	advmod	_	_
13	for	for	ADP	IN	_	14	case	_	_
14	Gondor	Gondor	PROPN	NNP	Number=Sing	11	nmod	_	_
15	late	late	ADJ	JJ	Degree=Pos	16	amod	_	_
16	Sunday	Sunday	PROPN	NNP	Number=Sing	11	nmod:tmod	_	_
17	to	to	PART	TO	_	19	mark	_	_
18	be	be	AUX	VB	VerbForm=Inf	19	auxpass	_	_
19	allowed	allow	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	11	xcomp	_	_
20	to	to	PART	TO	_	21	mark	_	_
21	leave	leave	VERB	VB	VerbForm=Inf	19	advcl	_	_
22	Lorien	Lorien	VERB	VBN	Tense=Past|VerbForm=Part	21	xcomp	_	_
23	by	by	ADP	IN	_	24	case	_	_
24	elves	elves	NOUN	NNS	Number=Plur	22	nmod	_	_
25	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test192': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19920102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([HOB],[GON],113)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test192']['sents']['0']:
            print(return_dict['test192']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test192']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],113)",str(return_dict['test192']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([HOB],[GON],113)","noevent"]
            print("test192 Failed")
    except:
        print("test192 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test192']['sents']['0']:
        verbs=return_dict['test192']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test192']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test192']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test192']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test192']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test192():
    text="""Mordor will be hosting Osgiliath to celebrate Tabaski with Eriador
next week at Cirith Ungol. 
"""
    parse="""1	Mordor	Mordor	NOUN	NN	Number=Sing	4	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	4	aux	_	_
3	be	be	AUX	VB	VerbForm=Inf	4	aux	_	_
4	hosting	host	VERB	VBG	VerbForm=Ger	0	root	_	_
5	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	4	dobj	_	_
6	to	to	PART	TO	_	7	mark	_	_
7	celebrate	celebrate	VERB	VB	VerbForm=Inf	4	xcomp	_	_
8	Tabaski	Tabaski	PROPN	NNP	Number=Sing	7	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Eriador	Eriador	PROPN	NNP	Number=Sing	7	nmod	_	_
11	next	next	ADJ	JJ	Degree=Pos	12	amod	_	_
12	week	week	NOUN	NN	Number=Sing	7	nmod:tmod	_	_
13	at	at	ADP	IN	_	15	case	_	_
14	Cirith	Cirith	PROPN	NNP	Number=Sing	15	compound	_	_
15	Ungol	Ungol	PROPN	NNP	Number=Sing	7	nmod	_	_
16	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test193': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([MORMIL],[MOR],051)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test193']['sents']['0']:
            print(return_dict['test193']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test193']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MORMIL],[MOR],051)",str(return_dict['test193']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([MORMIL],[MOR],051)","noevent"]
            print("test193 Failed")
    except:
        print("test193 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test193']['sents']['0']:
        verbs=return_dict['test193']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test193']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test193']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test193']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test193']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test193():
    text="""Mordor will be hosting Osgiliath to celebrate May Day with Eriador
next week at Cirith Ungol. 
"""
    parse="""1	Mordor	Mordor	NOUN	NN	Number=Sing	4	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	4	aux	_	_
3	be	be	AUX	VB	VerbForm=Inf	4	aux	_	_
4	hosting	host	VERB	VBG	VerbForm=Ger	0	root	_	_
5	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	4	dobj	_	_
6	to	to	PART	TO	_	7	mark	_	_
7	celebrate	celebrate	VERB	VB	VerbForm=Inf	4	xcomp	_	_
8	May	May	PROPN	NNP	Number=Sing	9	compound	_	_
9	Day	Day	PROPN	NNP	Number=Sing	7	dobj	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Eriador	Eriador	PROPN	NNP	Number=Sing	7	nmod	_	_
12	next	next	ADJ	JJ	Degree=Pos	13	amod	_	_
13	week	week	NOUN	NN	Number=Sing	7	nmod:tmod	_	_
14	at	at	ADP	IN	_	16	case	_	_
15	Cirith	Cirith	PROPN	NNP	Number=Sing	16	compound	_	_
16	Ungol	Ungol	PROPN	NNP	Number=Sing	7	nmod	_	_
17	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test194': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ERI],[MOR],017)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test194']['sents']['0']:
            print(return_dict['test194']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test194']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[MOR],017)",str(return_dict['test194']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ERI],[MOR],017)","noevent"]
            print("test194 Failed")
    except:
        print("test194 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test194']['sents']['0']:
        verbs=return_dict['test194']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test194']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test194']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test194']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test194']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test194():
    text="""Arnor has celebrated Eid at Osgiliath with Gondor after a 
hafling was reported on the pass of Cirith Ungol. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	celebrated	celebrate	VERB	VBN	Tense=Past|VerbForm=Part	13	nsubjpass	_	_
4	Eid	Eid	NOUN	NN	Number=Sing	3	dobj	_	_
5	at	at	ADP	IN	_	6	case	_	_
6	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	3	nmod	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	after	after	ADP	IN	_	11	case	_	_
10	a	a	DET	DT	Definite=Ind|PronType=Art	11	det	_	_
11	hafling	hafling	NOUN	NN	Number=Sing	3	nmod	_	_
12	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	13	auxpass	_	_
13	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
14	on	on	ADP	IN	_	16	case	_	_
15	the	the	DET	DT	Definite=Def|PronType=Art	16	det	_	_
16	pass	pass	NOUN	NN	Number=Sing	13	nmod	_	_
17	of	of	ADP	IN	_	19	case	_	_
18	Cirith	Cirith	PROPN	NNP	Number=Sing	19	name	_	_
19	Ungol	Ungol	PROPN	NNP	Number=Sing	16	nmod	_	_
20	.	.	PUNCT	.	_	13	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test195': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],017)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test195']['sents']['0']:
            print(return_dict['test195']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test195']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],017)",str(return_dict['test195']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],017)","noevent"]
            print("test195 Failed")
    except:
        print("test195 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test195']['sents']['0']:
        verbs=return_dict['test195']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test195']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test195']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test195']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test195']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test195():
    text="""Arnor has celebrated Iftar in Osgiliath with the leaders of Gondor after leaving Eriador 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	celebrated	celebrate	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	Iftar	Iftar	PROPN	NNP	Number=Sing	3	dobj	_	_
5	in	in	ADP	IN	_	6	case	_	_
6	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	3	nmod	_	_
7	with	with	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	leaders	leader	NOUN	NNS	Number=Plur	3	nmod	_	_
10	of	of	ADP	IN	_	11	case	_	_
11	Gondor	Gondor	PROPN	NNP	Number=Sing	9	nmod	_	_
12	after	after	SCONJ	IN	_	13	mark	_	_
13	leaving	leave	VERB	VBG	VerbForm=Ger	3	advcl	_	_
14	Eriador	Eriador	PROPN	NNP	Number=Sing	13	dobj	_	_
15	when	when	ADV	WRB	PronType=Int	19	mark	_	_
16	a	a	DET	DT	Definite=Ind|PronType=Art	17	det	_	_
17	hafling	hafling	NOUN	NN	Number=Sing	19	nsubjpass	_	_
18	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	19	auxpass	_	_
19	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	13	advcl	_	_
20	on	on	ADP	IN	_	22	case	_	_
21	the	the	DET	DT	Definite=Def|PronType=Art	22	det	_	_
22	pass	pass	NOUN	NN	Number=Sing	19	nmod	_	_
23	of	of	ADP	IN	_	25	case	_	_
24	Cirith	Cirith	PROPN	NNP	Number=Sing	25	name	_	_
25	Ungol	Ungol	PROPN	NNP	Number=Sing	22	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test196': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],045)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test196']['sents']['0']:
            print(return_dict['test196']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test196']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],045)",str(return_dict['test196']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],045)","noevent"]
            print("test196 Failed")
    except:
        print("test196 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test196']['sents']['0']:
        verbs=return_dict['test196']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test196']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test196']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test196']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test196']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test196():
    text="""Arnor has celebrated Iftar at Osgiliath with the parliament of Gondor in Eriador 
after a hafling was reported on the pass of Cirith Ungol. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	celebrated	celebrate	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	Iftar	Iftar	PROPN	NNP	Number=Sing	3	dobj	_	_
5	at	at	ADP	IN	_	6	case	_	_
6	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	3	nmod	_	_
7	with	with	ADP	IN	_	9	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	parliament	parliament	NOUN	NN	Number=Sing	3	nmod	_	_
10	of	of	ADP	IN	_	11	case	_	_
11	Gondor	Gondor	PROPN	NNP	Number=Sing	9	nmod	_	_
12	in	in	ADP	IN	_	13	case	_	_
13	Eriador	Eriador	PROPN	NNP	Number=Sing	3	nmod	_	_
14	after	after	ADP	IN	_	18	mark	_	_
15	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
16	hafling	hafling	NOUN	NN	Number=Sing	18	nsubjpass	_	_
17	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	18	auxpass	_	_
18	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	3	advcl	_	_
19	on	on	ADP	IN	_	21	case	_	_
20	the	the	DET	DT	Definite=Def|PronType=Art	21	det	_	_
21	pass	pass	NOUN	NN	Number=Sing	18	nmod	_	_
22	of	of	ADP	IN	_	24	case	_	_
23	Cirith	Cirith	PROPN	NNP	Number=Sing	24	name	_	_
24	Ungol	Ungol	PROPN	NNP	Number=Sing	21	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test197': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],044)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test197']['sents']['0']:
            print(return_dict['test197']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test197']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],044)",str(return_dict['test197']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],044)","noevent"]
            print("test197 Failed")
    except:
        print("test197 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test197']['sents']['0']:
        verbs=return_dict['test197']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test197']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test197']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test197']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test197']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test197():
    text="""Arnor has celebrated Eid at United Arab Emirates with Gondor after a 
hafling was reported on the pass of Cirith Ungol. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	celebrated	celebrate	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	Eid	Eid	NOUN	NN	Number=Sing	3	dobj	_	_
5	at	at	ADP	IN	_	8	case	_	_
6	United	United	PROPN	NNP	Number=Sing	8	compound	_	_
7	Arab	Arab	PROPN	NNP	Number=Sing	8	compound	_	_
8	Emirates	Emirates	PROPN	NNP	Number=Sing	4	nmod	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	4	nmod	_	_
11	after	after	ADP	IN	_	15	mark	_	_
12	a	a	DET	DT	Definite=Ind|PronType=Art	13	det	_	_
13	hafling	hafling	NOUN	NN	Number=Sing	15	nsubjpass	_	_
14	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	15	auxpass	_	_
15	reported	report	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	3	advcl	_	_
16	on	on	ADP	IN	_	18	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
18	pass	pass	NOUN	NN	Number=Sing	15	nmod	_	_
19	of	of	ADP	IN	_	21	case	_	_
20	Cirith	Cirith	PROPN	NNP	Number=Sing	21	name	_	_
21	Ungol	Ungol	PROPN	NNP	Number=Sing	18	nmod	_	_
22	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test198': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950102'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],017)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test198']['sents']['0']:
            print(return_dict['test198']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test198']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],017)",str(return_dict['test198']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],017)","noevent"]
            print("test198 Failed")
    except:
        print("test198 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test198']['sents']['0']:
        verbs=return_dict['test198']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test198']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test198']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test198']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test198']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test198():
    text="""Gondor launched a new bombing and shelling offensive against besieged 
Osgiliath during the night following daylight raids in which 
Arnor spokesmen said 54 civilians were killed or injured. 
"""
    parse="""1	Gondor	Gondor	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	launched	launch	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
4	new	new	ADJ	JJ	Degree=Pos	5	amod	_	_
5	bombing	bombing	NOUN	NN	Number=Sing	2	dobj	_	_
6	and	and	CONJ	CC	_	5	cc	_	_
7	shelling	shell	NOUN	NN	Number=Sing	8	compound	_	_
8	offensive	offensive	NOUN	NN	Number=Sing	5	conj	_	_
9	against	against	ADP	IN	_	10	case	_	_
10	besieged	besieged	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	2	nmod	_	_
11	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	10	dobj	_	_
12	during	during	ADP	IN	_	14	case	_	_
13	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
14	night	night	NOUN	NN	Number=Sing	10	nmod	_	_
15	following	follow	VERB	VBG	VerbForm=Ger	17	case	_	_
16	daylight	daylight	NOUN	NN	Number=Sing	17	compound	_	_
17	raids	raid	NOUN	NNS	Number=Plur	14	nmod	_	_
18	in	in	ADP	IN	_	21	case	_	_
19	which	which	DET	WDT	PronType=Int	21	det	_	_
20	Arnor	Arnor	PROPN	NNP	Number=Sing	21	name	_	_
21	spokesmen	spokesman	NOUN	NN	Number=Sing	17	nmod	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	21	root	_	_
23	54	54	NUM	CD	NumType=Card	24	nummod	_	_
24	civilians	civilian	NOUN	NNS	Number=Plur	26	nsubjpass	_	_
25	were	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	26	auxpass	_	_
26	killed	kill	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	22	ccomp	_	_
27	or	or	CONJ	CC	_	26	cc	_	_
28	injured	injure	VERB	VBN	Tense=Past|VerbForm=Part	26	conj	_	_
29	.	.	PUNCT	.	_	22	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test199': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19820727'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[OSG],190)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test199']['sents']['0']:
            print(return_dict['test199']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test199']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],190)",str(return_dict['test199']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[OSG],190)","noevent"]
            print("test199 Failed")
    except:
        print("test199 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test199']['sents']['0']:
        verbs=return_dict['test199']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test199']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test199']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test199']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test199']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test199():
    text="""The Philippines was criticized over its territorial dispute with Eriador.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Philippines	Philippines	PROPN	NNPS	Number=Plur	4	nsubjpass	_	_
3	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	4	auxpass	_	_
4	criticized	criticize	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
5	over	over	ADP	IN	_	8	case	_	_
6	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	8	nmod:poss	_	_
7	territorial	territorial	ADJ	JJ	Degree=Pos	8	amod	_	_
8	dispute	dispute	NOUN	NN	Number=Sing	4	nmod	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Eriador	Eriador	PROPN	NNP	Number=Sing	8	nmod	_	_
11	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test200': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PHL],[ERI],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test200']['sents']['0']:
            print(return_dict['test200']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test200']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[ERI],111)",str(return_dict['test200']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[ERI],111)","noevent"]
            print("test200 Failed")
    except:
        print("test200 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test200']['sents']['0']:
        verbs=return_dict['test200']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test200']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test200']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test200']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test200']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test200():
    text="""The Philippines was heavily and unjustly criticized over its territorial dispute with Eriador.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Philippines	Philippines	PROPN	NNPS	Number=Plur	4	nsubj	_	_
3	was	be	VERB	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	4	cop	_	_
4	heavily	heavily	ADV	RB	_	0	root	_	_
5	and	and	CONJ	CC	_	4	cc	_	_
6	unjustly	unjustly	ADV	RB	_	7	advmod	_	_
7	criticized	criticize	VERB	VBN	Tense=Past|VerbForm=Part	4	conj	_	_
8	over	over	ADP	IN	_	11	case	_	_
9	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	11	nmod:poss	_	_
10	territorial	territorial	ADJ	JJ	Degree=Pos	11	amod	_	_
11	dispute	dispute	NOUN	NN	Number=Sing	7	nmod	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Eriador	Eriador	PROPN	NNP	Number=Sing	11	nmod	_	_
14	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test201': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PHL],[ERI],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test201']['sents']['0']:
            print(return_dict['test201']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test201']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[ERI],111)",str(return_dict['test201']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[ERI],111)","noevent"]
            print("test201 Failed")
    except:
        print("test201 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test201']['sents']['0']:
        verbs=return_dict['test201']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test201']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test201']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test201']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test201']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test201():
    text="""The Philippines was heavily criticized over its territorial dispute with Eriador.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	2	det	_	_
2	Philippines	Philippines	PROPN	NNPS	Number=Plur	5	nsubjpass	_	_
3	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	5	auxpass	_	_
4	heavily	heavily	ADV	RB	_	5	advmod	_	_
5	criticized	criticize	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
6	over	over	ADP	IN	_	9	case	_	_
7	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	9	nmod:poss	_	_
8	territorial	territorial	ADJ	JJ	Degree=Pos	9	amod	_	_
9	dispute	dispute	NOUN	NN	Number=Sing	5	nmod	_	_
10	with	with	ADP	IN	_	11	case	_	_
11	Eriador	Eriador	PROPN	NNP	Number=Sing	9	nmod	_	_
12	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test202': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950103'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([PHL],[ERI],111)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test202']['sents']['0']:
            print(return_dict['test202']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test202']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[ERI],111)",str(return_dict['test202']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([PHL],[ERI],111)","noevent"]
            print("test202 Failed")
    except:
        print("test202 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test202']['sents']['0']:
        verbs=return_dict['test202']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test202']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test202']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test202']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test202']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test202():
    text="""Eriador was opposed by Osgiliath, the state's fiercest foe, 
in being drawn into the peace process by its resumption 
of diplomatic ties with Gondor. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	3	nsubjpass	_	_
2	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	3	auxpass	_	_
3	opposed	oppose	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	by	by	ADP	IN	_	5	case	_	_
5	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	3	nmod	_	_
6	,	,	PUNCT	,	_	3	punct	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	8	det	_	_
8	state	state	NOUN	NN	Number=Sing	11	nmod:poss	_	_
9	's	's	PART	POS	_	8	case	_	_
10	fiercest	fiercest	NOUN	NN	Number=Sing	11	compound	_	_
11	foe	foe	NOUN	NN	Number=Sing	3	dobj	_	_
12	,	,	PUNCT	,	_	11	punct	_	_
13	in	in	SCONJ	IN	_	15	mark	_	_
14	being	be	AUX	VBG	VerbForm=Ger	15	auxpass	_	_
15	drawn	draw	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	11	acl	_	_
16	into	into	ADP	IN	_	19	case	_	_
17	the	the	DET	DT	Definite=Def|PronType=Art	19	det	_	_
18	peace	peace	NOUN	NN	Number=Sing	19	compound	_	_
19	process	process	NOUN	NN	Number=Sing	15	nmod	_	_
20	by	by	ADP	IN	_	22	case	_	_
21	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
22	resumption	resumption	NOUN	NN	Number=Sing	19	nmod	_	_
23	of	of	ADP	IN	_	25	case	_	_
24	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	25	amod	_	_
25	ties	tie	NOUN	NNS	Number=Plur	22	nmod	_	_
26	with	with	ADP	IN	_	27	case	_	_
27	Gondor	Gondor	PROPN	NNP	Number=Sing	25	nmod	_	_
28	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test203': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([OSG],[ERI],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test203']['sents']['0']:
            print(return_dict['test203']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test203']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],110)",str(return_dict['test203']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],110)","noevent"]
            print("test203 Failed")
    except:
        print("test203 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test203']['sents']['0']:
        verbs=return_dict['test203']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test203']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test203']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test203']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test203']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test203():
    text="""Eriador was fiercely opposed by Osgiliath, the state's fiercest foe, 
in being drawn into the peace process by its resumption 
of diplomatic ties with Gondor. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	4	nsubjpass	_	_
2	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	4	auxpass	_	_
3	fiercely	fiercely	ADV	RB	_	4	advmod	_	_
4	opposed	oppose	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
5	by	by	ADP	IN	_	6	case	_	_
6	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	4	nmod	_	_
7	,	,	PUNCT	,	_	4	punct	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	state	state	NOUN	NN	Number=Sing	12	nmod:poss	_	_
10	's	's	PART	POS	_	9	case	_	_
11	fiercest	fiercest	NOUN	NN	Number=Sing	12	compound	_	_
12	foe	foe	NOUN	NN	Number=Sing	4	dobj	_	_
13	,	,	PUNCT	,	_	12	punct	_	_
14	in	in	SCONJ	IN	_	16	mark	_	_
15	being	be	AUX	VBG	VerbForm=Ger	16	auxpass	_	_
16	drawn	draw	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	12	acl	_	_
17	into	into	ADP	IN	_	20	case	_	_
18	the	the	DET	DT	Definite=Def|PronType=Art	20	det	_	_
19	peace	peace	NOUN	NN	Number=Sing	20	compound	_	_
20	process	process	NOUN	NN	Number=Sing	16	nmod	_	_
21	by	by	ADP	IN	_	23	case	_	_
22	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	23	nmod:poss	_	_
23	resumption	resumption	NOUN	NN	Number=Sing	20	nmod	_	_
24	of	of	ADP	IN	_	26	case	_	_
25	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	26	amod	_	_
26	ties	tie	NOUN	NNS	Number=Plur	23	nmod	_	_
27	with	with	ADP	IN	_	28	case	_	_
28	Gondor	Gondor	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test204': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([OSG],[ERI],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test204']['sents']['0']:
            print(return_dict['test204']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test204']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],110)",str(return_dict['test204']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],110)","noevent"]
            print("test204 Failed")
    except:
        print("test204 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test204']['sents']['0']:
        verbs=return_dict['test204']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test204']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test204']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test204']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test204']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test204():
    text="""Eriador has received by courier money from Osgiliath, the state's 
fiercest foe, to be drawn into the peace process by its resumption 
of diplomatic ties with Gondor. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	has	have	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	received	receive	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	by	by	ADP	IN	_	6	case	_	_
5	courier	courier	NOUN	NN	Number=Sing	6	compound	_	_
6	money	money	NOUN	NN	Number=Sing	3	nmod	_	_
7	from	from	ADP	IN	_	8	case	_	_
8	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	6	nmod	_	_
9	,	,	PUNCT	,	_	3	punct	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	state	state	NOUN	NN	Number=Sing	14	nmod:poss	_	_
12	's	's	PART	POS	_	11	case	_	_
13	fiercest	fiercest	NOUN	NN	Number=Sing	14	compound	_	_
14	foe	foe	NOUN	NN	Number=Sing	3	dobj	_	_
15	,	,	PUNCT	,	_	14	punct	_	_
16	to	to	PART	TO	_	18	mark	_	_
17	be	be	AUX	VB	VerbForm=Inf	18	auxpass	_	_
18	drawn	draw	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	14	acl	_	_
19	into	into	ADP	IN	_	22	case	_	_
20	the	the	DET	DT	Definite=Def|PronType=Art	22	det	_	_
21	peace	peace	NOUN	NN	Number=Sing	22	compound	_	_
22	process	process	NOUN	NN	Number=Sing	18	nmod	_	_
23	by	by	ADP	IN	_	25	case	_	_
24	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	25	nmod:poss	_	_
25	resumption	resumption	NOUN	NN	Number=Sing	22	nmod	_	_
26	of	of	ADP	IN	_	28	case	_	_
27	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	28	amod	_	_
28	ties	tie	NOUN	NNS	Number=Plur	25	nmod	_	_
29	with	with	ADP	IN	_	30	case	_	_
30	Gondor	Gondor	PROPN	NNP	Number=Sing	28	nmod	_	_
31	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test205': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([OSG],[ERI],144)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test205']['sents']['0']:
            print(return_dict['test205']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test205']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],144)",str(return_dict['test205']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],144)","noevent"]
            print("test205 Failed")
    except:
        print("test205 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test205']['sents']['0']:
        verbs=return_dict['test205']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test205']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test205']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test205']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test205']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test205():
    text="""Eriador was opposed earlier by Osgiliath, the state's fiercest foe, 
in being drawn into the peace process by its resumption 
of diplomatic ties with Gondor. 
"""
    parse="""1	Eriador	Eriador	PROPN	NNP	Number=Sing	3	nsubjpass	_	_
2	was	be	AUX	VBD	Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin	3	auxpass	_	_
3	opposed	oppose	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	earlier	earlier	ADV	RBR	Degree=Cmp	3	advmod	_	_
5	by	by	ADP	IN	_	6	case	_	_
6	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	4	nmod	_	_
7	,	,	PUNCT	,	_	3	punct	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
9	state	state	NOUN	NN	Number=Sing	12	nmod:poss	_	_
10	's	's	PART	POS	_	9	case	_	_
11	fiercest	fiercest	NOUN	NN	Number=Sing	12	compound	_	_
12	foe	foe	NOUN	NN	Number=Sing	3	dobj	_	_
13	,	,	PUNCT	,	_	12	punct	_	_
14	in	in	SCONJ	IN	_	16	mark	_	_
15	being	be	AUX	VBG	VerbForm=Ger	16	auxpass	_	_
16	drawn	draw	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	12	acl	_	_
17	into	into	ADP	IN	_	20	case	_	_
18	the	the	DET	DT	Definite=Def|PronType=Art	20	det	_	_
19	peace	peace	NOUN	NN	Number=Sing	20	compound	_	_
20	process	process	NOUN	NN	Number=Sing	16	nmod	_	_
21	by	by	ADP	IN	_	23	case	_	_
22	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	23	nmod:poss	_	_
23	resumption	resumption	NOUN	NN	Number=Sing	20	nmod	_	_
24	of	of	ADP	IN	_	26	case	_	_
25	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	26	amod	_	_
26	ties	tie	NOUN	NNS	Number=Plur	23	nmod	_	_
27	with	with	ADP	IN	_	28	case	_	_
28	Gondor	Gondor	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test206': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([OSG],[ERI],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test206']['sents']['0']:
            print(return_dict['test206']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test206']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],110)",str(return_dict['test206']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([OSG],[ERI],110)","noevent"]
            print("test206 Failed")
    except:
        print("test206 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test206']['sents']['0']:
        verbs=return_dict['test206']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test206']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test206']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test206']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test206']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test206():
    text="""Rebuked by Eriador, the state's fiercest foe, 
Osgiliath is being drawn into the peace process by its resumption 
of diplomatic ties with Gondor. 
"""
    parse="""1	Rebuked	Rebuk	VERB	VBN	Tense=Past|VerbForm=Part	14	advcl	_	_
2	by	by	ADP	IN	_	3	case	_	_
3	Eriador	Eriador	PROPN	NNP	Number=Sing	1	nmod	_	_
4	,	,	PUNCT	,	_	14	punct	_	_
5	the	the	DET	DT	Definite=Def|PronType=Art	6	det	_	_
6	state	state	NOUN	NN	Number=Sing	9	nmod:poss	_	_
7	's	's	PART	POS	_	6	case	_	_
8	fiercest	fiercest	NOUN	NN	Number=Sing	9	compound	_	_
9	foe	foe	NOUN	NN	Number=Sing	14	nsubjpass	_	_
10	,	,	PUNCT	,	_	9	punct	_	_
11	Osgiliath	Osgiliath	PROPN	NNP	Number=Sing	9	appos	_	_
12	is	be	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	14	aux	_	_
13	being	be	AUX	VBG	VerbForm=Ger	14	auxpass	_	_
14	drawn	draw	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
15	into	into	ADP	IN	_	18	case	_	_
16	the	the	DET	DT	Definite=Def|PronType=Art	18	det	_	_
17	peace	peace	NOUN	NN	Number=Sing	18	compound	_	_
18	process	process	NOUN	NN	Number=Sing	14	nmod	_	_
19	by	by	ADP	IN	_	21	case	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	resumption	resumption	NOUN	NN	Number=Sing	18	nmod	_	_
22	of	of	ADP	IN	_	24	case	_	_
23	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	24	amod	_	_
24	ties	tie	NOUN	NNS	Number=Plur	21	nmod	_	_
25	with	with	ADP	IN	_	26	case	_	_
26	Gondor	Gondor	PROPN	NNP	Number=Sing	24	nmod	_	_
27	.	.	PUNCT	.	_	14	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test207': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950112'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test207']['sents']['0']:
            print(return_dict['test207']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test207']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test207']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test207 Failed")
    except:
        print("test207 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test207']['sents']['0']:
        verbs=return_dict['test207']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test207']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test207']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test207']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test207']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test207():
    text="""Arnor is about to restore full diplomatic ties with Gondor, 
five years after crowds burned down its embassy,  a very senior 
Bree official said on Saturday night. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	,	,	PUNCT	,	_	3	punct	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	15	nmod:npmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
16	burned	burn	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	down	down	ADP	RP	_	16	compound:prt	_	_
18	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
19	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
20	,	,	PUNCT	,	_	15	punct	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	25	det	_	_
22	very	very	ADV	RB	_	23	advmod	_	_
23	senior	senior	ADJ	JJ	Degree=Pos	25	amod	_	_
24	Bree	Bree	PROPN	NNP	Number=Sing	25	compound	_	_
25	official	official	NOUN	NN	Number=Sing	26	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	15	acl:relcl	_	_
27	on	on	ADP	IN	_	29	case	_	_
28	Saturday	Saturday	PROPN	NNP	Number=Sing	29	compound	_	_
29	night	night	NOUN	NN	Number=Sing	26	nmod	_	_
30	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test208': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test208']['sents']['0']:
            print(return_dict['test208']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test208']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test208']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test208 Failed")
    except:
        print("test208 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test208']['sents']['0']:
        verbs=return_dict['test208']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test208']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test208']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test208']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test208']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test208():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost 
five years after Calenardhon crowds burned down its embassy,  a senior 
Bree official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	16	nmod:npmod	_	_
14	after	after	ADP	IN	_	16	case	_	_
15	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	16	compound	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	10	nmod	_	_
17	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	conj	_	_
18	down	down	ADP	RP	_	17	compound:prt	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
21	,	,	PUNCT	,	_	17	punct	_	_
22	a	a	DET	DT	Definite=Ind|PronType=Art	25	det	_	_
23	senior	senior	ADJ	JJ	Degree=Pos	25	amod	_	_
24	Bree	Bree	PROPN	NNP	Number=Sing	25	compound	_	_
25	official	official	NOUN	NN	Number=Sing	28	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	28	cop	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Saturday	Saturday	PROPN	NNP	Number=Sing	17	conj	_	_
29	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test209': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test209']['sents']['0']:
            print(return_dict['test209']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test209']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test209']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test209 Failed")
    except:
        print("test209 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test209']['sents']['0']:
        verbs=return_dict['test209']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test209']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test209']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test209']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test209']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test209():
    text="""Arnor is about to restore full diplomatic ties with Gondor, 
five years after crowds burned down its embassy,  a senior 
official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	,	,	PUNCT	,	_	3	punct	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	15	nmod:npmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
16	burned	burn	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	down	down	ADP	RP	_	16	compound:prt	_	_
18	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
19	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
20	,	,	PUNCT	,	_	16	punct	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
22	senior	senior	ADJ	JJ	Degree=Pos	23	amod	_	_
23	official	official	NOUN	NN	Number=Sing	26	nsubj	_	_
24	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	26	cop	_	_
25	on	on	ADP	IN	_	26	case	_	_
26	Saturday	Saturday	PROPN	NNP	Number=Sing	16	conj	_	_
27	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test210': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test210']['sents']['0']:
            print(return_dict['test210']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test210']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test210']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test210 Failed")
    except:
        print("test210 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test210']['sents']['0']:
        verbs=return_dict['test210']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test210']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test210']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test210']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test210']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test210():
    text="""Arnor is about to restore complete, full diplomatic ties with Gondor almost 
five years after Cxlenardhon crowds burned down its embassy,  a senior 
Bree official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	complete	complete	ADJ	JJ	Degree=Pos	10	amod	_	_
7	,	,	PUNCT	,	_	6	punct	_	_
8	full	full	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
11	with	with	ADP	IN	_	12	case	_	_
12	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
13	almost	almost	ADV	RB	_	14	advmod	_	_
14	five	five	NUM	CD	NumType=Card	15	nummod	_	_
15	years	year	NOUN	NNS	Number=Plur	18	nmod:npmod	_	_
16	after	after	ADP	IN	_	18	case	_	_
17	Cxlenardhon	Cxlenardhon	PROPN	NNP	Number=Sing	18	compound	_	_
18	crowds	crowd	NOUN	NNS	Number=Plur	12	nmod	_	_
19	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	conj	_	_
20	down	down	ADP	RP	_	19	compound:prt	_	_
21	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
22	embassy	embassy	NOUN	NN	Number=Sing	19	dobj	_	_
23	,	,	PUNCT	,	_	19	punct	_	_
24	a	a	DET	DT	Definite=Ind|PronType=Art	27	det	_	_
25	senior	senior	ADJ	JJ	Degree=Pos	27	amod	_	_
26	Bree	Bree	PROPN	NNP	Number=Sing	27	compound	_	_
27	official	official	NOUN	NN	Number=Sing	30	nsubj	_	_
28	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	30	cop	_	_
29	on	on	ADP	IN	_	30	case	_	_
30	Saturday	Saturday	PROPN	NNP	Number=Sing	19	conj	_	_
31	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test211': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test211']['sents']['0']:
            print(return_dict['test211']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test211']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test211']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test211 Failed")
    except:
        print("test211 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test211']['sents']['0']:
        verbs=return_dict['test211']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test211']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test211']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test211']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test211']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test211():
    text="""Arnor is about to restore full diplomatic ties with Gxndor, almost 
five years after Calenardhon crowds burned down its embassy,  a senior 
official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gxndor	Gxndor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	,	,	PUNCT	,	_	10	punct	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	17	nmod:npmod	_	_
15	after	after	ADP	IN	_	17	case	_	_
16	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	17	compound	_	_
17	crowds	crowd	NOUN	NNS	Number=Plur	18	nmod	_	_
18	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	conj	_	_
19	down	down	ADP	RP	_	21	case	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	embassy	embassy	NOUN	NN	Number=Sing	18	nmod	_	_
22	,	,	PUNCT	,	_	10	punct	_	_
23	a	a	DET	DT	Definite=Ind|PronType=Art	25	det	_	_
24	senior	senior	ADJ	JJ	Degree=Pos	25	amod	_	_
25	official	official	NOUN	NN	Number=Sing	26	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	conj	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Saturday	Saturday	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test212': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[CAL],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test212']['sents']['0']:
            print(return_dict['test212']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test212']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[CAL],050)",str(return_dict['test212']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[CAL],050)","noevent"]
            print("test212 Failed")
    except:
        print("test212 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test212']['sents']['0']:
        verbs=return_dict['test212']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test212']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test212']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test212']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test212']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test212():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost five years after 
Calenardhon crowds burned down its embassy,  a clearly inebriated Bree official said today. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	16	case	_	_
15	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	16	compound	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
17	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	16	acl	_	_
18	down	down	ADP	RP	_	17	compound:prt	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
21	,	,	PUNCT	,	_	3	punct	_	_
22	a	a	DET	DT	Definite=Ind|PronType=Art	26	det	_	_
23	clearly	clearly	ADV	RB	_	24	advmod	_	_
24	inebriated	inebriate	VERB	VBN	Tense=Past|VerbForm=Part	26	amod	_	_
25	Bree	Bree	PROPN	NNP	Number=Sing	26	compound	_	_
26	official	official	NOUN	NN	Number=Sing	27	nsubj	_	_
27	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
28	today	today	NOUN	NN	Number=Sing	27	nmod:tmod	_	_
29	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test213': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test213']['sents']['0']:
            print(return_dict['test213']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test213']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)",str(return_dict['test213']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)","noevent"]
            print("test213 Failed")
    except:
        print("test213 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test213']['sents']['0']:
        verbs=return_dict['test213']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test213']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test213']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test213']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test213']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test213():
    text="""Arnor is about to restore, it seems, complete, full diplomatic ties with Gondor almost 
five years after Calenardhon crowds burned down its embassy,  a senior 
Bree official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	ccomp	_	_
6	,	,	PUNCT	,	_	3	punct	_	_
7	it	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	8	nsubj	_	_
8	seems	seem	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	parataxis	_	_
9	,	,	PUNCT	,	_	8	punct	_	_
10	complete	complete	ADJ	JJ	Degree=Pos	8	conj	_	_
11	,	,	PUNCT	,	_	8	punct	_	_
12	full	full	ADJ	JJ	Degree=Pos	14	amod	_	_
13	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	14	amod	_	_
14	ties	tie	NOUN	NNS	Number=Plur	23	nsubj	_	_
15	with	with	ADP	IN	_	16	case	_	_
16	Gondor	Gondor	PROPN	NNP	Number=Sing	14	nmod	_	_
17	almost	almost	ADV	RB	_	18	advmod	_	_
18	five	five	NUM	CD	NumType=Card	19	nummod	_	_
19	years	year	NOUN	NNS	Number=Plur	22	nmod:npmod	_	_
20	after	after	ADP	IN	_	22	case	_	_
21	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	22	compound	_	_
22	crowds	crowd	NOUN	NNS	Number=Plur	14	nmod	_	_
23	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	8	conj	_	_
24	down	down	ADP	RP	_	23	compound:prt	_	_
25	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	26	nmod:poss	_	_
26	embassy	embassy	NOUN	NN	Number=Sing	23	dobj	_	_
27	,	,	PUNCT	,	_	8	punct	_	_
28	a	a	DET	DT	Definite=Ind|PronType=Art	31	det	_	_
29	senior	senior	ADJ	JJ	Degree=Pos	31	amod	_	_
30	Bree	Bree	PROPN	NNP	Number=Sing	31	compound	_	_
31	official	official	NOUN	NN	Number=Sing	34	nsubj	_	_
32	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	34	cop	_	_
33	on	on	ADP	IN	_	34	case	_	_
34	Saturday	Saturday	PROPN	NNP	Number=Sing	8	conj	_	_
35	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test214': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([GON],[---],222)\n([BREGOV],[---],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test214']['sents']['0']:
            print(return_dict['test214']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test214']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[---],222)\n([BREGOV],[---],010)",str(return_dict['test214']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([GON],[---],222)\n([BREGOV],[---],010)","noevent"]
            print("test214 Failed")
    except:
        print("test214 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test214']['sents']['0']:
        verbs=return_dict['test214']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test214']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test214']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test214']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test214']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test214():
    text="""Arnor is about to restore complete, full diplomatic ties with Gondor almost 
five years after Calenardhon crowds burned down its embassy,  a senior 
Bree official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	complete	complete	ADJ	JJ	Degree=Pos	10	amod	_	_
7	,	,	PUNCT	,	_	6	punct	_	_
8	full	full	ADJ	JJ	Degree=Pos	10	amod	_	_
9	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	10	amod	_	_
10	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
11	with	with	ADP	IN	_	12	case	_	_
12	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
13	almost	almost	ADV	RB	_	14	advmod	_	_
14	five	five	NUM	CD	NumType=Card	15	nummod	_	_
15	years	year	NOUN	NNS	Number=Plur	18	nmod:npmod	_	_
16	after	after	ADP	IN	_	18	case	_	_
17	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	18	compound	_	_
18	crowds	crowd	NOUN	NNS	Number=Plur	12	nmod	_	_
19	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	conj	_	_
20	down	down	ADP	RP	_	19	compound:prt	_	_
21	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	22	nmod:poss	_	_
22	embassy	embassy	NOUN	NN	Number=Sing	19	dobj	_	_
23	,	,	PUNCT	,	_	19	punct	_	_
24	a	a	DET	DT	Definite=Ind|PronType=Art	27	det	_	_
25	senior	senior	ADJ	JJ	Degree=Pos	27	amod	_	_
26	Bree	Bree	PROPN	NNP	Number=Sing	27	compound	_	_
27	official	official	NOUN	NN	Number=Sing	30	nsubj	_	_
28	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	30	cop	_	_
29	on	on	ADP	IN	_	30	case	_	_
30	Saturday	Saturday	PROPN	NNP	Number=Sing	19	conj	_	_
31	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test215': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)\n([BREGOV],[---],010)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test215']['sents']['0']:
            print(return_dict['test215']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test215']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)\n([BREGOV],[---],010)",str(return_dict['test215']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)\n([BREGOV],[---],010)","noevent"]
            print("test215 Failed")
    except:
        print("test215 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test215']['sents']['0']:
        verbs=return_dict['test215']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test215']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test215']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test215']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test215']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test215():
    text="""Arnor is said to be about to restore, it seems, complete, full diplomatic ties with
Gondor almost five years after Calenardhon crowds burned down its embassy, a senior Bree 
official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubjpass	_	_
2	is	be	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	auxpass	_	_
3	said	say	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
4	to	to	PART	TO	_	8	mark	_	_
5	be	be	VERB	VB	VerbForm=Inf	8	cop	_	_
6	about	about	ADV	RB	_	8	advmod	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
9	,	,	PUNCT	,	_	3	punct	_	_
10	it	it	PRON	PRP	Case=Nom|Gender=Neut|Number=Sing|Person=3|PronType=Prs	11	nsubj	_	_
11	seems	seem	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	parataxis	_	_
12	,	,	PUNCT	,	_	11	punct	_	_
13	complete	complete	ADJ	JJ	Degree=Pos	17	amod	_	_
14	,	,	PUNCT	,	_	13	punct	_	_
15	full	full	ADJ	JJ	Degree=Pos	17	amod	_	_
16	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	17	amod	_	_
17	ties	tie	NOUN	NNS	Number=Plur	11	dobj	_	_
18	with	with	ADP	IN	_	19	case	_	_
19	Gondor	Gondor	PROPN	NNP	Number=Sing	17	nmod	_	_
20	almost	almost	ADV	RB	_	21	advmod	_	_
21	five	five	NUM	CD	NumType=Card	22	nummod	_	_
22	years	year	NOUN	NNS	Number=Plur	25	nmod:npmod	_	_
23	after	after	ADP	IN	_	25	case	_	_
24	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	25	compound	_	_
25	crowds	crowd	NOUN	NNS	Number=Plur	26	nmod	_	_
26	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	11	conj	_	_
27	down	down	ADP	RP	_	26	compound:prt	_	_
28	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	29	nmod:poss	_	_
29	embassy	embassy	NOUN	NN	Number=Sing	26	dobj	_	_
30	,	,	PUNCT	,	_	29	punct	_	_
31	a	a	DET	DT	Definite=Ind|PronType=Art	34	det	_	_
32	senior	senior	ADJ	JJ	Degree=Pos	34	amod	_	_
33	Bree	Bree	PROPN	NNP	Number=Sing	34	compound	_	_
34	official	official	NOUN	NN	Number=Sing	35	nsubj	_	_
35	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	29	acl:relcl	_	_
36	on	on	ADP	IN	_	37	case	_	_
37	Saturday	Saturday	PROPN	NNP	Number=Sing	35	nmod	_	_
38	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test216': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],012)\n([BREGOV],[---],012)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test216']['sents']['0']:
            print(return_dict['test216']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test216']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],012)\n([BREGOV],[---],012)",str(return_dict['test216']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],012)\n([BREGOV],[---],012)","noevent"]
            print("test216 Failed")
    except:
        print("test216 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test216']['sents']['0']:
        verbs=return_dict['test216']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test216']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test216']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test216']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test216']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test216():
    text="""Arnor is about to restore full diplomatic ties with Gondor, almost 
five years after Calenardhon crowds burned down its embassy,  a senior 
official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	,	,	PUNCT	,	_	10	punct	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	17	nmod:npmod	_	_
15	after	after	ADP	IN	_	17	case	_	_
16	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	17	compound	_	_
17	crowds	crowd	NOUN	NNS	Number=Plur	18	nmod	_	_
18	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	conj	_	_
19	down	down	ADP	RP	_	21	case	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	embassy	embassy	NOUN	NN	Number=Sing	18	nmod	_	_
22	,	,	PUNCT	,	_	10	punct	_	_
23	a	a	DET	DT	Definite=Ind|PronType=Art	25	det	_	_
24	senior	senior	ADJ	JJ	Degree=Pos	25	amod	_	_
25	official	official	NOUN	NN	Number=Sing	26	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	conj	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Saturday	Saturday	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test217': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],050)\n([---GOV],[---],012)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test217']['sents']['0']:
            print(return_dict['test217']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test217']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)\n([---GOV],[---],012)",str(return_dict['test217']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],050)\n([---GOV],[---],012)","noevent"]
            print("test217 Failed")
    except:
        print("test217 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test217']['sents']['0']:
        verbs=return_dict['test217']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test217']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test217']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test217']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test217']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test217():
    text="""Arnor is about to improve full diplomatic ties with Gondor, almost 
five years after Calenardhon crowds burned down its embassy,  a 
clearly inebriated Bree official said today.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	improve	improve	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	,	,	PUNCT	,	_	10	punct	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	17	nmod:npmod	_	_
15	after	after	ADP	IN	_	17	case	_	_
16	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	17	compound	_	_
17	crowds	crowd	NOUN	NNS	Number=Plur	10	nmod	_	_
18	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	17	root	_	_
19	down	down	ADP	RP	_	18	compound:prt	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	embassy	embassy	NOUN	NN	Number=Sing	18	dobj	_	_
22	,	,	PUNCT	,	_	18	punct	_	_
23	a	a	DET	DT	Definite=Ind|PronType=Art	27	det	_	_
24	clearly	clearly	ADV	RB	_	25	advmod	_	_
25	inebriated	inebriate	VERB	VBN	Tense=Past|VerbForm=Part	27	amod	_	_
26	Bree	Bree	PROPN	NNP	Number=Sing	27	compound	_	_
27	official	official	NOUN	NN	Number=Sing	28	nsubj	_	_
28	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	18	conj	_	_
29	today	today	NOUN	NN	Number=Sing	28	nmod:tmod	_	_
30	.	.	PUNCT	.	_	18	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test218': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[---],222)\n([---GOV],[---],012)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test218']['sents']['0']:
            print(return_dict['test218']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test218']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[---],222)\n([---GOV],[---],012)",str(return_dict['test218']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[---],222)\n([---GOV],[---],012)","noevent"]
            print("test218 Failed")
    except:
        print("test218 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test218']['sents']['0']:
        verbs=return_dict['test218']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test218']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test218']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test218']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test218']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test218():
    text="""Arnor is about to improve full diplomatic ties with Gondor, almost 
five years after Calenardhon crowds burned down its embassy,  a 
senior Bree official said today. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	improve	improve	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	,	,	PUNCT	,	_	10	punct	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	17	nmod:npmod	_	_
15	after	after	ADP	IN	_	17	case	_	_
16	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	17	compound	_	_
17	crowds	crowd	NOUN	NNS	Number=Plur	18	nmod	_	_
18	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	conj	_	_
19	down	down	ADP	RP	_	21	case	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	embassy	embassy	NOUN	NN	Number=Sing	18	nmod	_	_
22	,	,	PUNCT	,	_	10	punct	_	_
23	a	a	DET	DT	Definite=Ind|PronType=Art	26	det	_	_
24	senior	senior	ADJ	JJ	Degree=Pos	26	amod	_	_
25	Bree	Bree	PROPN	NNP	Number=Sing	26	compound	_	_
26	official	official	NOUN	NN	Number=Sing	27	nsubj	_	_
27	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	parataxis	_	_
28	today	today	NOUN	NN	Number=Sing	27	nmod:tmod	_	_
29	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test219': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[---],222)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test219']['sents']['0']:
            print(return_dict['test219']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test219']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[---],222)",str(return_dict['test219']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[---],222)","noevent"]
            print("test219 Failed")
    except:
        print("test219 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test219']['sents']['0']:
        verbs=return_dict['test219']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test219']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test219']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test219']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test219']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test219():
    text="""Arnor on Thursday signed an 800 million ducat trade protocol
for 1990 with Dagolath, its biggest trading partner, officials said. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	4	nsubj	_	_
2	on	on	ADP	IN	_	3	case	_	_
3	Thursday	Thursday	PROPN	NNP	Number=Sing	1	nmod	_	_
4	signed	sign	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
5	an	a	DET	DT	Definite=Ind|PronType=Art	10	det	_	_
6	800	800	NUM	CD	NumType=Card	7	compound	_	_
7	million	million	NUM	CD	NumType=Card	8	nummod	_	_
8	ducat	ducat	NOUN	NN	Number=Sing	10	compound	_	_
9	trade	trade	NOUN	NN	Number=Sing	10	compound	_	_
10	protocol	protocol	NOUN	NN	Number=Sing	4	dobj	_	_
11	for	for	ADP	IN	_	12	case	_	_
12	1990	1990	NUM	CD	NumType=Card	10	nmod	_	_
13	with	with	ADP	IN	_	14	case	_	_
14	Dagolath	Dagolath	PROPN	NNP	Number=Sing	12	nmod	_	_
15	,	,	PUNCT	,	_	14	punct	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
17	biggest	biggest	ADJ	JJS	Degree=Sup	19	amod	_	_
18	trading	trading	NOUN	NN	Number=Sing	19	compound	_	_
19	partner	partner	NOUN	NN	Number=Sing	14	appos	_	_
20	,	,	PUNCT	,	_	4	punct	_	_
21	officials	official	NOUN	NNS	Number=Plur	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	parataxis	_	_
23	.	.	PUNCT	.	_	4	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test220': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950113'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[DAG],057)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test220']['sents']['0']:
            print(return_dict['test220']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test220']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[DAG],057)",str(return_dict['test220']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[DAG],057)","noevent"]
            print("test220 Failed")
    except:
        print("test220 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test220']['sents']['0']:
        verbs=return_dict['test220']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test220']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test220']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test220']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test220']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test220():
    text="""Arnor is about to restore full diplomatic ties with Gxndor, several 
years after Calenardhon crowds burned down its embassy,  a senior 
official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gxndor	Gxndor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	,	,	PUNCT	,	_	3	punct	_	_
12	several	several	ADJ	JJ	Degree=Pos	13	amod	_	_
13	years	year	NOUN	NNS	Number=Plur	16	nmod:npmod	_	_
14	after	after	ADP	IN	_	16	case	_	_
15	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	16	compound	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	17	nsubj	_	_
17	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
18	down	down	ADP	RP	_	17	compound:prt	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
21	,	,	PUNCT	,	_	17	punct	_	_
22	a	a	DET	DT	Definite=Ind|PronType=Art	24	det	_	_
23	senior	senior	ADJ	JJ	Degree=Pos	24	amod	_	_
24	official	official	NOUN	NN	Number=Sing	25	nsubj	_	_
25	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	17	conj	_	_
26	on	on	ADP	IN	_	27	case	_	_
27	Saturday	Saturday	PROPN	NNP	Number=Sing	25	nmod	_	_
28	.	.	PUNCT	.	_	17	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test221': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test221']['sents']['0']:
            print(return_dict['test221']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test221']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test221']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test221 Failed")
    except:
        print("test221 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test221']['sents']['0']:
        verbs=return_dict['test221']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test221']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test221']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test221']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test221']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test221():
    text="""Arnor is about to restore full diplomatic ties with Gxndor almost 
five years after Cxlenardhon crowds burned down its embassy,  a senior 
Bree official said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gxndor	Gxndor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	16	nmod:npmod	_	_
14	after	after	ADP	IN	_	16	case	_	_
15	Cxlenardhon	Cxlenardhon	PROPN	NNP	Number=Sing	16	compound	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	10	nmod	_	_
17	burned	burn	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	conj	_	_
18	down	down	ADP	RP	_	17	compound:prt	_	_
19	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	20	nmod:poss	_	_
20	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
21	,	,	PUNCT	,	_	17	punct	_	_
22	a	a	DET	DT	Definite=Ind|PronType=Art	25	det	_	_
23	senior	senior	ADJ	JJ	Degree=Pos	25	amod	_	_
24	Bree	Bree	PROPN	NNP	Number=Sing	25	compound	_	_
25	official	official	NOUN	NN	Number=Sing	28	nsubj	_	_
26	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	28	cop	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Saturday	Saturday	PROPN	NNP	Number=Sing	17	conj	_	_
29	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test222': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test222']['sents']['0']:
            print(return_dict['test222']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test222']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test222']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test222 Failed")
    except:
        print("test222 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test222']['sents']['0']:
        verbs=return_dict['test222']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test222']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test222']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test222']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test222']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test222():
    text="""Arnor will abandon full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	full	full	ADJ	JJ	Degree=Pos	6	amod	_	_
5	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	ties	tie	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test223': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test223']['sents']['0']:
            print(return_dict['test223']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test223']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)",str(return_dict['test223']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)","noevent"]
            print("test223 Failed")
    except:
        print("test223 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test223']['sents']['0']:
        verbs=return_dict['test223']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test223']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test223']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test223']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test223']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test223():
    text="""Arnor will abandon full &amp;TIETYPE ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	full	full	ADJ	JJ	Degree=Pos	7	amod	_	_
5	&amp;	&amp;	CONJ	CC	_	4	cc	_	_
6	TIETYPE	Tietype	ADJ	JJ	Degree=Pos	4	conj	_	_
7	ties	tie	NOUN	NNS	Number=Plur	3	dobj	_	_
8	with	with	ADP	IN	_	9	case	_	_
9	Gondor	Gondor	PROPN	NNP	Number=Sing	7	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test224': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],345)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test224']['sents']['0']:
            print(return_dict['test224']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test224']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)",str(return_dict['test224']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)","noevent"]
            print("test224 Failed")
    except:
        print("test224 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test224']['sents']['0']:
        verbs=return_dict['test224']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test224']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test224']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test224']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test224']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test224():
    text="""Arnor will abandon full economic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	full	full	ADJ	JJ	Degree=Pos	6	amod	_	_
5	economic	economic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	ties	tie	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test225': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test225']['sents']['0']:
            print(return_dict['test225']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test225']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)",str(return_dict['test225']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)","noevent"]
            print("test225 Failed")
    except:
        print("test225 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test225']['sents']['0']:
        verbs=return_dict['test225']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test225']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test225']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test225']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test225']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test225():
    text="""Arnor will abandon full cultural ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	full	full	ADJ	JJ	Degree=Pos	6	amod	_	_
5	cultural	cultural	ADJ	JJ	Degree=Pos	6	amod	_	_
6	ties	tie	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test226': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test226']['sents']['0']:
            print(return_dict['test226']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test226']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)",str(return_dict['test226']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)","noevent"]
            print("test226 Failed")
    except:
        print("test226 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test226']['sents']['0']:
        verbs=return_dict['test226']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test226']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test226']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test226']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test226']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test226():
    text="""Arnor will abandon full military ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	full	full	ADJ	JJ	Degree=Pos	6	amod	_	_
5	military	military	ADJ	JJ	Degree=Pos	6	amod	_	_
6	ties	tie	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test227': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],080)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test227']['sents']['0']:
            print(return_dict['test227']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test227']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)",str(return_dict['test227']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],080)","noevent"]
            print("test227 Failed")
    except:
        print("test227 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test227']['sents']['0']:
        verbs=return_dict['test227']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test227']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test227']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test227']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test227']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test227():
    text="""Arnor will abandon full military txes with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	full	full	ADJ	JJ	Degree=Pos	6	amod	_	_
5	military	military	ADJ	JJ	Degree=Pos	6	amod	_	_
6	txes	tx	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test228': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],345)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test228']['sents']['0']:
            print(return_dict['test228']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test228']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)",str(return_dict['test228']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)","noevent"]
            print("test228 Failed")
    except:
        print("test228 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test228']['sents']['0']:
        verbs=return_dict['test228']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test228']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test228']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test228']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test228']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test228():
    text="""Arnor will abandon full symbolic ties with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	full	full	ADJ	JJ	Degree=Pos	6	amod	_	_
5	symbolic	symbolic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	ties	tie	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	6	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test229': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],345)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test229']['sents']['0']:
            print(return_dict['test229']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test229']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)",str(return_dict['test229']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)","noevent"]
            print("test229 Failed")
    except:
        print("test229 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test229']['sents']['0']:
        verbs=return_dict['test229']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test229']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test229']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test229']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test229']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test229():
    text="""Arnor will contribute a million rupees to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	million	million	NUM	CD	NumType=Card	6	nummod	_	_
6	rupees	rupee	NOUN	NNS	Number=Plur	3	dobj	_	_
7	to	to	ADP	IN	_	8	case	_	_
8	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test230': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test230']['sents']['0']:
            print(return_dict['test230']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test230']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test230']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test230 Failed")
    except:
        print("test230 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test230']['sents']['0']:
        verbs=return_dict['test230']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test230']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test230']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test230']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test230']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test230():
    text="""Arnor will contribute a million dollars to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	million	million	NUM	CD	NumType=Card	6	nummod	_	_
6	dollars	dollar	NOUN	NNS	Number=Plur	3	dobj	_	_
7	to	to	ADP	IN	_	8	case	_	_
8	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test231': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test231']['sents']['0']:
            print(return_dict['test231']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test231']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test231']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test231 Failed")
    except:
        print("test231 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test231']['sents']['0']:
        verbs=return_dict['test231']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test231']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test231']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test231']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test231']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test231():
    text="""Arnor will contribute a million euros to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	million	million	NUM	CD	NumType=Card	6	nummod	_	_
6	euros	euro	NOUN	NNS	Number=Plur	3	dobj	_	_
7	to	to	ADP	IN	_	8	case	_	_
8	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test232': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test232']['sents']['0']:
            print(return_dict['test232']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test232']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test232']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test232 Failed")
    except:
        print("test232 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test232']['sents']['0']:
        verbs=return_dict['test232']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test232']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test232']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test232']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test232']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test232():
    text="""Arnor will contribute a million kroner to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	million	million	NUM	CD	NumType=Card	6	nummod	_	_
6	kroner	kroner	NOUN	NN	Number=Sing	3	dobj	_	_
7	to	to	ADP	IN	_	8	case	_	_
8	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test233': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test233']['sents']['0']:
            print(return_dict['test233']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test233']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test233']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test233 Failed")
    except:
        print("test233 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test233']['sents']['0']:
        verbs=return_dict['test233']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test233']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test233']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test233']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test233']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test233():
    text="""Arnor will contribute a million swiss francs to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	7	det	_	_
5	million	million	NUM	CD	NumType=Card	6	nummod	_	_
6	swiss	swiss	NOUN	NN	Number=Sing	7	compound	_	_
7	francs	franc	NOUN	NNS	Number=Plur	3	dobj	_	_
8	to	to	ADP	IN	_	9	case	_	_
9	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test234': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test234']['sents']['0']:
            print(return_dict['test234']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test234']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test234']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test234 Failed")
    except:
        print("test234 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test234']['sents']['0']:
        verbs=return_dict['test234']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test234']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test234']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test234']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test234']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test234():
    text="""Arnor will contribute a million golden goblin galleons to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	8	det	_	_
5	million	million	NUM	CD	NumType=Card	8	nummod	_	_
6	golden	golden	ADJ	JJ	Degree=Pos	8	amod	_	_
7	goblin	goblin	NOUN	NN	Number=Sing	8	compound	_	_
8	galleons	galleon	NOUN	NNS	Number=Plur	3	dobj	_	_
9	to	to	ADP	IN	_	10	case	_	_
10	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test235': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test235']['sents']['0']:
            print(return_dict['test235']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test235']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test235']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test235 Failed")
    except:
        print("test235 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test235']['sents']['0']:
        verbs=return_dict['test235']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test235']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test235']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test235']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test235']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test235():
    text="""Arnor will contribute a million goblin galleons to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	7	det	_	_
5	million	million	NUM	CD	NumType=Card	6	nummod	_	_
6	goblin	goblin	NOUN	NN	Number=Sing	7	compound	_	_
7	galleons	galleon	NOUN	NNS	Number=Plur	3	dobj	_	_
8	to	to	ADP	IN	_	9	case	_	_
9	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test236': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test236']['sents']['0']:
            print(return_dict['test236']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test236']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test236']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test236 Failed")
    except:
        print("test236 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test236']['sents']['0']:
        verbs=return_dict['test236']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test236']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test236']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test236']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test236']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test236():
    text="""Arnor will contribute a million golden galleons to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	million	million	NUM	CD	NumType=Card	7	nummod	_	_
6	golden	golden	ADJ	JJ	Degree=Pos	7	amod	_	_
7	galleons	galleon	NOUN	NNS	Number=Plur	3	dobj	_	_
8	to	to	ADP	IN	_	9	case	_	_
9	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test237': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test237']['sents']['0']:
            print(return_dict['test237']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test237']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test237']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test237 Failed")
    except:
        print("test237 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test237']['sents']['0']:
        verbs=return_dict['test237']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test237']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test237']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test237']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test237']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test237():
    text="""Bree Prime Minister Romendacil clashed over the efforts of Eriadori to deal 
with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	5	nsubj	_	_
5	clashed	clash	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
6	over	over	ADP	IN	_	8	case	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	8	det	_	_
8	efforts	effort	NOUN	NNS	Number=Plur	5	nmod	_	_
9	of	of	ADP	IN	_	10	case	_	_
10	Eriadori	Eriadori	PROPN	NNP	Number=Sing	8	nmod	_	_
11	to	to	PART	TO	_	12	mark	_	_
12	deal	deal	VERB	VB	VerbForm=Inf	5	xcomp	_	_
13	with	with	ADP	IN	_	16	case	_	_
14	an	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
15	orc	orc	ADJ	JJ	Degree=Pos	16	amod	_	_
16	infestation	infestation	NOUN	NN	Number=Sing	12	nmod	_	_
17	during	during	ADP	IN	_	21	case	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
19	brief	brief	ADJ	JJ	Degree=Pos	21	amod	_	_
20	private	private	ADJ	JJ	Degree=Pos	21	amod	_	_
21	visit	visit	NOUN	NN	Number=Sing	12	nmod	_	_
22	to	to	ADP	IN	_	23	case	_	_
23	Eriador	Eriador	PROPN	NNP	Number=Sing	21	nmod	_	_
24	starting	start	VERB	VBG	VerbForm=Ger	21	acl	_	_
25	on	on	ADP	IN	_	26	case	_	_
26	Sunday	Sunday	PROPN	NNP	Number=Sing	24	nmod	_	_
27	.	.	PUNCT	.	_	5	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test238': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test238']['sents']['0']:
            print(return_dict['test238']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test238']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],110)",str(return_dict['test238']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],110)","noevent"]
            print("test238 Failed")
    except:
        print("test238 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test238']['sents']['0']:
        verbs=return_dict['test238']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test238']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test238']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test238']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test238']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test238():
    text="""Bree Prime Minister Romendacil didn't clash over the efforts of Eriadori to deal 
with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	3	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	7	nsubj	_	_
5	did	do	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	7	aux	_	_
6	n't	not	PART	RB	_	7	neg	_	_
7	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
8	over	over	ADP	IN	_	10	case	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	efforts	effort	NOUN	NNS	Number=Plur	7	nmod	_	_
11	of	of	ADP	IN	_	12	case	_	_
12	Eriadori	Eriadori	PROPN	NNP	Number=Sing	10	nmod	_	_
13	to	to	PART	TO	_	14	mark	_	_
14	deal	deal	VERB	VB	VerbForm=Inf	7	xcomp	_	_
15	with	with	ADP	IN	_	18	case	_	_
16	an	a	DET	DT	Definite=Ind|PronType=Art	18	det	_	_
17	orc	orc	ADJ	JJ	Degree=Pos	18	amod	_	_
18	infestation	infestation	NOUN	NN	Number=Sing	14	nmod	_	_
19	during	during	ADP	IN	_	23	case	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
21	brief	brief	ADJ	JJ	Degree=Pos	23	amod	_	_
22	private	private	ADJ	JJ	Degree=Pos	23	amod	_	_
23	visit	visit	NOUN	NN	Number=Sing	14	nmod	_	_
24	to	to	ADP	IN	_	25	case	_	_
25	Eriador	Eriador	PROPN	NNP	Number=Sing	23	nmod	_	_
26	starting	start	VERB	VBG	VerbForm=Ger	23	acl	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Sunday	Sunday	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test239': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test239']['sents']['0']:
            print(return_dict['test239']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test239']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test239']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test239 Failed")
    except:
        print("test239 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test239']['sents']['0']:
        verbs=return_dict['test239']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test239']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test239']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test239']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test239']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test239():
    text="""Bree Prime Minister Romendacil will not clash over the efforts of Eriadori to deal 
with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	3	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	7	nsubj	_	_
5	will	will	AUX	MD	VerbForm=Fin	7	aux	_	_
6	not	not	PART	RB	_	7	neg	_	_
7	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
8	over	over	ADP	IN	_	10	case	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	efforts	effort	NOUN	NNS	Number=Plur	7	nmod	_	_
11	of	of	ADP	IN	_	12	case	_	_
12	Eriadori	Eriadori	PROPN	NNP	Number=Sing	10	nmod	_	_
13	to	to	PART	TO	_	14	mark	_	_
14	deal	deal	VERB	VB	VerbForm=Inf	7	xcomp	_	_
15	with	with	ADP	IN	_	18	case	_	_
16	an	a	DET	DT	Definite=Ind|PronType=Art	18	det	_	_
17	orc	orc	ADJ	JJ	Degree=Pos	18	amod	_	_
18	infestation	infestation	NOUN	NN	Number=Sing	14	nmod	_	_
19	during	during	ADP	IN	_	23	case	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
21	brief	brief	ADJ	JJ	Degree=Pos	23	amod	_	_
22	private	private	ADJ	JJ	Degree=Pos	23	amod	_	_
23	visit	visit	NOUN	NN	Number=Sing	18	nmod	_	_
24	to	to	ADP	IN	_	25	case	_	_
25	Eriador	Eriador	PROPN	NNP	Number=Sing	23	nmod	_	_
26	starting	start	VERB	VBG	VerbForm=Ger	14	advcl	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Sunday	Sunday	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test240': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test240']['sents']['0']:
            print(return_dict['test240']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test240']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test240']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test240 Failed")
    except:
        print("test240 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test240']['sents']['0']:
        verbs=return_dict['test240']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test240']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test240']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test240']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test240']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test240():
    text="""Bree Prime Minister Romendacil will not ever clash over the efforts of Eriadori to deal 
with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	3	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	8	nsubj	_	_
5	will	will	AUX	MD	VerbForm=Fin	8	aux	_	_
6	not	not	PART	RB	_	8	neg	_	_
7	ever	ever	ADV	RB	_	8	advmod	_	_
8	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
9	over	over	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	efforts	effort	NOUN	NNS	Number=Plur	8	nmod	_	_
12	of	of	ADP	IN	_	13	case	_	_
13	Eriadori	Eriadori	PROPN	NNP	Number=Sing	11	nmod	_	_
14	to	to	PART	TO	_	15	mark	_	_
15	deal	deal	VERB	VB	VerbForm=Inf	8	xcomp	_	_
16	with	with	ADP	IN	_	19	case	_	_
17	an	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	orc	orc	ADJ	JJ	Degree=Pos	19	amod	_	_
19	infestation	infestation	NOUN	NN	Number=Sing	15	nmod	_	_
20	during	during	ADP	IN	_	24	case	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	24	det	_	_
22	brief	brief	ADJ	JJ	Degree=Pos	24	amod	_	_
23	private	private	ADJ	JJ	Degree=Pos	24	amod	_	_
24	visit	visit	NOUN	NN	Number=Sing	15	nmod	_	_
25	to	to	ADP	IN	_	26	case	_	_
26	Eriador	Eriador	PROPN	NNP	Number=Sing	24	nmod	_	_
27	starting	start	VERB	VBG	VerbForm=Ger	24	acl	_	_
28	on	on	ADP	IN	_	29	case	_	_
29	Sunday	Sunday	PROPN	NNP	Number=Sing	27	nmod	_	_
30	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test241': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test241']['sents']['0']:
            print(return_dict['test241']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test241']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test241']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test241 Failed")
    except:
        print("test241 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test241']['sents']['0']:
        verbs=return_dict['test241']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test241']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test241']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test241']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test241']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test241():
    text="""Bree Prime Minister Romendacil can't ever clash over the efforts of Eriadori to deal 
with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	8	nsubj	_	_
5	ca	can	AUX	MD	VerbForm=Fin	8	aux	_	_
6	n't	not	PART	RB	_	8	neg	_	_
7	ever	ever	ADV	RB	_	8	advmod	_	_
8	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
9	over	over	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	efforts	effort	NOUN	NNS	Number=Plur	8	nmod	_	_
12	of	of	ADP	IN	_	13	case	_	_
13	Eriadori	Eriadori	PROPN	NNP	Number=Sing	11	nmod	_	_
14	to	to	PART	TO	_	15	mark	_	_
15	deal	deal	VERB	VB	VerbForm=Inf	8	advcl	_	_
16	with	with	ADP	IN	_	19	case	_	_
17	an	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	orc	orc	ADJ	JJ	Degree=Pos	19	amod	_	_
19	infestation	infestation	NOUN	NN	Number=Sing	15	nmod	_	_
20	during	during	ADP	IN	_	24	case	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	24	det	_	_
22	brief	brief	ADJ	JJ	Degree=Pos	24	amod	_	_
23	private	private	ADJ	JJ	Degree=Pos	24	amod	_	_
24	visit	visit	NOUN	NN	Number=Sing	15	nmod	_	_
25	to	to	ADP	IN	_	26	case	_	_
26	Eriador	Eriador	PROPN	NNP	Number=Sing	24	nmod	_	_
27	starting	start	VERB	VBG	VerbForm=Ger	24	acl	_	_
28	on	on	ADP	IN	_	29	case	_	_
29	Sunday	Sunday	PROPN	NNP	Number=Sing	27	nmod	_	_
30	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test242': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test242']['sents']['0']:
            print(return_dict['test242']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test242']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test242']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test242 Failed")
    except:
        print("test242 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test242']['sents']['0']:
        verbs=return_dict['test242']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test242']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test242']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test242']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test242']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test242():
    text="""Bree Prime Minister Romendacil unexpectedly won't clash over the efforts of Eriadori to deal 
with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	8	nsubj	_	_
5	unexpectedly	unexpectedly	ADV	RB	_	8	advmod	_	_
6	wo	will	AUX	MD	VerbForm=Fin	8	aux	_	_
7	n't	not	PART	RB	_	8	neg	_	_
8	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
9	over	over	ADP	IN	_	11	case	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	efforts	effort	NOUN	NNS	Number=Plur	8	nmod	_	_
12	of	of	ADP	IN	_	13	case	_	_
13	Eriadori	Eriadori	PROPN	NNP	Number=Sing	11	nmod	_	_
14	to	to	PART	TO	_	15	mark	_	_
15	deal	deal	VERB	VB	VerbForm=Inf	8	xcomp	_	_
16	with	with	ADP	IN	_	19	case	_	_
17	an	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	orc	orc	ADJ	JJ	Degree=Pos	19	amod	_	_
19	infestation	infestation	NOUN	NN	Number=Sing	15	nmod	_	_
20	during	during	ADP	IN	_	24	case	_	_
21	a	a	DET	DT	Definite=Ind|PronType=Art	24	det	_	_
22	brief	brief	ADJ	JJ	Degree=Pos	24	amod	_	_
23	private	private	ADJ	JJ	Degree=Pos	24	amod	_	_
24	visit	visit	NOUN	NN	Number=Sing	15	nmod	_	_
25	to	to	ADP	IN	_	26	case	_	_
26	Eriador	Eriador	PROPN	NNP	Number=Sing	24	nmod	_	_
27	starting	start	VERB	VBG	VerbForm=Ger	24	acl	_	_
28	on	on	ADP	IN	_	29	case	_	_
29	Sunday	Sunday	PROPN	NNP	Number=Sing	27	nmod	_	_
30	.	.	PUNCT	.	_	8	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test243': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test243']['sents']['0']:
            print(return_dict['test243']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test243']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test243']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test243 Failed")
    except:
        print("test243 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test243']['sents']['0']:
        verbs=return_dict['test243']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test243']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test243']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test243']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test243']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test243():
    text="""Bree Prime Minister Romendacil most certainly really did not clash over the efforts of Eriadori  
to deal with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	10	nsubj	_	_
5	most	most	ADV	RBS	_	6	advmod	_	_
6	certainly	certainly	ADV	RB	_	10	advmod	_	_
7	really	really	ADV	RB	_	10	advmod	_	_
8	did	do	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	aux	_	_
9	not	not	PART	RB	_	10	neg	_	_
10	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
11	over	over	ADP	IN	_	13	case	_	_
12	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
13	efforts	effort	NOUN	NNS	Number=Plur	10	nmod	_	_
14	of	of	ADP	IN	_	15	case	_	_
15	Eriadori	Eriadori	PROPN	NNP	Number=Sing	13	nmod	_	_
16	to	to	PART	TO	_	17	mark	_	_
17	deal	deal	VERB	VB	VerbForm=Inf	10	xcomp	_	_
18	with	with	ADP	IN	_	21	case	_	_
19	an	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	orc	orc	ADJ	JJ	Degree=Pos	21	amod	_	_
21	infestation	infestation	NOUN	NN	Number=Sing	17	nmod	_	_
22	during	during	ADP	IN	_	26	case	_	_
23	a	a	DET	DT	Definite=Ind|PronType=Art	26	det	_	_
24	brief	brief	ADJ	JJ	Degree=Pos	26	amod	_	_
25	private	private	ADJ	JJ	Degree=Pos	26	amod	_	_
26	visit	visit	NOUN	NN	Number=Sing	17	nmod	_	_
27	to	to	ADP	IN	_	28	case	_	_
28	Eriador	Eriador	PROPN	NNP	Number=Sing	26	nmod	_	_
29	starting	start	VERB	VBG	VerbForm=Ger	26	acl	_	_
30	on	on	ADP	IN	_	31	case	_	_
31	Sunday	Sunday	PROPN	NNP	Number=Sing	29	nmod	_	_
32	.	.	PUNCT	.	_	10	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test244': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test244']['sents']['0']:
            print(return_dict['test244']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test244']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test244']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test244 Failed")
    except:
        print("test244 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test244']['sents']['0']:
        verbs=return_dict['test244']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test244']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test244']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test244']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test244']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test244():
    text="""Bree Prime Minister Romendacil didn't clash over the efforts of Eriadori to deal 
with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	3	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	7	nsubj	_	_
5	did	do	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	7	aux	_	_
6	n't	not	PART	RB	_	7	neg	_	_
7	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
8	over	over	ADP	IN	_	10	case	_	_
9	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
10	efforts	effort	NOUN	NNS	Number=Plur	7	nmod	_	_
11	of	of	ADP	IN	_	12	case	_	_
12	Eriadori	Eriadori	PROPN	NNP	Number=Sing	10	nmod	_	_
13	to	to	PART	TO	_	14	mark	_	_
14	deal	deal	VERB	VB	VerbForm=Inf	7	xcomp	_	_
15	with	with	ADP	IN	_	18	case	_	_
16	an	a	DET	DT	Definite=Ind|PronType=Art	18	det	_	_
17	orc	orc	ADJ	JJ	Degree=Pos	18	amod	_	_
18	infestation	infestation	NOUN	NN	Number=Sing	14	nmod	_	_
19	during	during	ADP	IN	_	23	case	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
21	brief	brief	ADJ	JJ	Degree=Pos	23	amod	_	_
22	private	private	ADJ	JJ	Degree=Pos	23	amod	_	_
23	visit	visit	NOUN	NN	Number=Sing	14	nmod	_	_
24	to	to	ADP	IN	_	25	case	_	_
25	Eriador	Eriador	PROPN	NNP	Number=Sing	23	nmod	_	_
26	starting	start	VERB	VBG	VerbForm=Ger	23	acl	_	_
27	on	on	ADP	IN	_	28	case	_	_
28	Sunday	Sunday	PROPN	NNP	Number=Sing	26	nmod	_	_
29	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test245': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test245']['sents']['0']:
            print(return_dict['test245']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test245']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test245']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test245 Failed")
    except:
        print("test245 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test245']['sents']['0']:
        verbs=return_dict['test245']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test245']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test245']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test245']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test245']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test245():
    text="""Arnor will contribute a million yum yennyen to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	million	million	NUM	CD	NumType=Card	6	nummod	_	_
6	yum	yum	NOUN	NN	Number=Sing	3	dobj	_	_
7	yennyen	yennyen	ADV	RB	_	3	advmod	_	_
8	to	to	ADP	IN	_	9	case	_	_
9	Australia	Australia	PROPN	NNP	Number=Sing	7	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	14	nmod:npmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	17	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	17	acl:relcl	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test246': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test246']['sents']['0']:
            print(return_dict['test246']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test246']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test246']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test246 Failed")
    except:
        print("test246 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test246']['sents']['0']:
        verbs=return_dict['test246']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test246']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test246']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test246']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test246']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test246():
    text="""Arnor will contribute a million austrian florin to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	million	million	NUM	CD	NumType=Card	7	nummod	_	_
6	austrian	austrian	ADJ	JJ	Degree=Pos	7	amod	_	_
7	florin	florin	NOUN	NN	Number=Sing	3	dobj	_	_
8	to	to	ADP	IN	_	9	case	_	_
9	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test247': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],070)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test247']['sents']['0']:
            print(return_dict['test247']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test247']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)",str(return_dict['test247']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],070)","noevent"]
            print("test247 Failed")
    except:
        print("test247 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test247']['sents']['0']:
        verbs=return_dict['test247']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test247']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test247']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test247']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test247']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test247():
    text="""Arnor will contribute a million austrian gold florin to Australia almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	contribute	contribute	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	8	det	_	_
5	million	million	NUM	CD	NumType=Card	8	nummod	_	_
6	austrian	austrian	ADJ	JJ	Degree=Pos	8	amod	_	_
7	gold	gold	NOUN	NN	Number=Sing	8	compound	_	_
8	florin	florin	NOUN	NN	Number=Sing	3	dobj	_	_
9	to	to	ADP	IN	_	10	case	_	_
10	Australia	Australia	PROPN	NNP	Number=Sing	3	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test248': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[AUS],904)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test248']['sents']['0']:
            print(return_dict['test248']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test248']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],904)",str(return_dict['test248']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[AUS],904)","noevent"]
            print("test248 Failed")
    except:
        print("test248 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test248']['sents']['0']:
        verbs=return_dict['test248']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test248']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test248']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test248']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test248']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test248():
    text="""Arnor will adopt a resolution with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	adopt	adopt	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	resolution	resolution	NOUN	NN	Number=Sing	3	dobj	_	_
6	with	with	ADP	IN	_	7	case	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
8	almost	almost	ADV	RB	_	9	advmod	_	_
9	five	five	NUM	CD	NumType=Card	10	nummod	_	_
10	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
11	after	after	ADP	IN	_	12	case	_	_
12	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
13	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	12	acl	_	_
14	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	15	nmod:poss	_	_
15	embassy	embassy	NOUN	NN	Number=Sing	13	dobj	_	_
16	,	,	PUNCT	,	_	3	punct	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	senior	senior	ADJ	JJ	Degree=Pos	19	amod	_	_
19	official	official	NOUN	NN	Number=Sing	20	nsubj	_	_
20	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
21	on	on	ADP	IN	_	22	case	_	_
22	Saturday	Saturday	PROPN	NNP	Number=Sing	20	nmod	_	_
23	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test249': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],057)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test249']['sents']['0']:
            print(return_dict['test249']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test249']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],057)",str(return_dict['test249']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],057)","noevent"]
            print("test249 Failed")
    except:
        print("test249 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test249']['sents']['0']:
        verbs=return_dict['test249']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test249']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test249']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test249']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test249']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test249():
    text="""Arnor will adopt a set of resolutions with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	adopt	adopt	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	set	set	NOUN	NN	Number=Sing	3	dobj	_	_
6	of	of	ADP	IN	_	7	case	_	_
7	resolutions	resolution	NOUN	NNS	Number=Plur	5	nmod	_	_
8	with	with	ADP	IN	_	9	case	_	_
9	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test250': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],057)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test250']['sents']['0']:
            print(return_dict['test250']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test250']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],057)",str(return_dict['test250']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],057)","noevent"]
            print("test250 Failed")
    except:
        print("test250 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test250']['sents']['0']:
        verbs=return_dict['test250']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test250']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test250']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test250']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test250']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test250():
    text="""Arnor will adopt a revolution with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	adopt	adopt	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
5	revolution	revolution	NOUN	NN	Number=Sing	3	dobj	_	_
6	with	with	ADP	IN	_	7	case	_	_
7	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
8	almost	almost	ADV	RB	_	9	advmod	_	_
9	five	five	NUM	CD	NumType=Card	10	nummod	_	_
10	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
11	after	after	ADP	IN	_	12	case	_	_
12	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
13	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	12	acl	_	_
14	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	15	nmod:poss	_	_
15	embassy	embassy	NOUN	NN	Number=Sing	13	dobj	_	_
16	,	,	PUNCT	,	_	3	punct	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	senior	senior	ADJ	JJ	Degree=Pos	19	amod	_	_
19	official	official	NOUN	NN	Number=Sing	20	nsubj	_	_
20	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
21	on	on	ADP	IN	_	22	case	_	_
22	Saturday	Saturday	PROPN	NNP	Number=Sing	20	nmod	_	_
23	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test251': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],802)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test251']['sents']['0']:
            print(return_dict['test251']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test251']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],802)",str(return_dict['test251']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],802)","noevent"]
            print("test251 Failed")
    except:
        print("test251 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test251']['sents']['0']:
        verbs=return_dict['test251']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test251']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test251']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test251']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test251']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test251():
    text="""Arnor will adopt a revolutionary manifesto with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	adopt	adopt	VERB	VB	VerbForm=Inf	0	root	_	_
4	a	a	DET	DT	Definite=Ind|PronType=Art	6	det	_	_
5	revolutionary	revolutionary	ADJ	JJ	Degree=Pos	6	amod	_	_
6	manifesto	manifesto	NOUN	NN	Number=Sing	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test252': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],802)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test252']['sents']['0']:
            print(return_dict['test252']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test252']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],802)",str(return_dict['test252']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],802)","noevent"]
            print("test252 Failed")
    except:
        print("test252 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test252']['sents']['0']:
        verbs=return_dict['test252']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test252']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test252']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test252']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test252']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test252():
    text="""Arnor will abandon new economic relations with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	new	new	ADJ	JJ	Degree=Pos	6	amod	_	_
5	economic	economic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	relations	relation	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test253': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],903)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test253']['sents']['0']:
            print(return_dict['test253']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test253']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],903)",str(return_dict['test253']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],903)","noevent"]
            print("test253 Failed")
    except:
        print("test253 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test253']['sents']['0']:
        verbs=return_dict['test253']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test253']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test253']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test253']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test253']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test253():
    text="""Arnor will abandon new global economic relations with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	new	new	ADJ	JJ	Degree=Pos	7	amod	_	_
5	global	global	ADJ	JJ	Degree=Pos	7	amod	_	_
6	economic	economic	ADJ	JJ	Degree=Pos	7	amod	_	_
7	relations	relation	NOUN	NNS	Number=Plur	3	dobj	_	_
8	with	with	ADP	IN	_	9	case	_	_
9	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test254': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],345)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test254']['sents']['0']:
            print(return_dict['test254']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test254']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)",str(return_dict['test254']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)","noevent"]
            print("test254 Failed")
    except:
        print("test254 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test254']['sents']['0']:
        verbs=return_dict['test254']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test254']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test254']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test254']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test254']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test254():
    text="""Arnor will abandon new global economic trade relations with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	new	new	ADJ	JJ	Degree=Pos	8	amod	_	_
5	global	global	ADJ	JJ	Degree=Pos	8	amod	_	_
6	economic	economic	ADJ	JJ	Degree=Pos	8	amod	_	_
7	trade	trade	NOUN	NN	Number=Sing	8	compound	_	_
8	relations	relation	NOUN	NNS	Number=Plur	3	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	,	,	PUNCT	,	_	3	punct	_	_
20	a	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	senior	senior	ADJ	JJ	Degree=Pos	22	amod	_	_
22	official	official	NOUN	NN	Number=Sing	23	nsubj	_	_
23	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
24	on	on	ADP	IN	_	25	case	_	_
25	Saturday	Saturday	PROPN	NNP	Number=Sing	23	nmod	_	_
26	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test255': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],345)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test255']['sents']['0']:
            print(return_dict['test255']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test255']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)",str(return_dict['test255']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],345)","noevent"]
            print("test255 Failed")
    except:
        print("test255 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test255']['sents']['0']:
        verbs=return_dict['test255']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test255']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test255']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test255']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test255']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test255():
    text="""Arnor will abandon improved economic relations with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	improved	improve	VERB	VBN	Tense=Past|VerbForm=Part	6	amod	_	_
5	economic	economic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	relations	relation	NOUN	NNS	Number=Plur	3	dobj	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	6	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	13	acl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	3	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test256': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],904)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test256']['sents']['0']:
            print(return_dict['test256']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test256']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],904)",str(return_dict['test256']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],904)","noevent"]
            print("test256 Failed")
    except:
        print("test256 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test256']['sents']['0']:
        verbs=return_dict['test256']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test256']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test256']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test256']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test256']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test256():
    text="""Arnor will abandon improved global economic relations with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	will	will	AUX	MD	VerbForm=Fin	3	aux	_	_
3	abandon	abandon	VERB	VB	VerbForm=Inf	0	root	_	_
4	improved	improve	VERB	VBN	Tense=Past|VerbForm=Part	7	amod	_	_
5	global	global	ADJ	JJ	Degree=Pos	7	amod	_	_
6	economic	economic	ADJ	JJ	Degree=Pos	7	amod	_	_
7	relations	relation	NOUN	NNS	Number=Plur	3	dobj	_	_
8	with	with	ADP	IN	_	9	case	_	_
9	Gondor	Gondor	PROPN	NNP	Number=Sing	3	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	3	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	3	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	,	,	PUNCT	,	_	3	punct	_	_
19	a	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	senior	senior	ADJ	JJ	Degree=Pos	21	amod	_	_
21	official	official	NOUN	NN	Number=Sing	22	nsubj	_	_
22	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	3	parataxis	_	_
23	on	on	ADP	IN	_	24	case	_	_
24	Saturday	Saturday	PROPN	NNP	Number=Sing	22	nmod	_	_
25	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test257': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],904)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test257']['sents']['0']:
            print(return_dict['test257']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test257']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],904)",str(return_dict['test257']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],904)","noevent"]
            print("test257 Failed")
    except:
        print("test257 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test257']['sents']['0']:
        verbs=return_dict['test257']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test257']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test257']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test257']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test257']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test257():
    text="""Bree Prime Minister Romendacil unexpectedly now won't try to clash over the efforts of Eriadori to deal 
with an orc infestation during a brief private trip to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	4	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	9	nsubj	_	_
5	unexpectedly	unexpectedly	ADV	RB	_	4	advmod	_	_
6	now	now	ADV	RB	_	9	advmod	_	_
7	wo	will	AUX	MD	VerbForm=Fin	9	aux	_	_
8	n't	not	PART	RB	_	9	neg	_	_
9	try	try	VERB	VB	VerbForm=Inf	0	root	_	_
10	to	to	PART	TO	_	11	mark	_	_
11	clash	clash	VERB	VB	VerbForm=Inf	9	xcomp	_	_
12	over	over	ADP	IN	_	14	case	_	_
13	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
14	efforts	effort	NOUN	NNS	Number=Plur	11	nmod	_	_
15	of	of	ADP	IN	_	16	case	_	_
16	Eriadori	Eriadori	PROPN	NNP	Number=Sing	14	nmod	_	_
17	to	to	PART	TO	_	18	mark	_	_
18	deal	deal	VERB	VB	VerbForm=Inf	11	xcomp	_	_
19	with	with	ADP	IN	_	22	case	_	_
20	an	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	orc	orc	ADJ	JJ	Degree=Pos	22	amod	_	_
22	infestation	infestation	NOUN	NN	Number=Sing	18	nmod	_	_
23	during	during	ADP	IN	_	27	case	_	_
24	a	a	DET	DT	Definite=Ind|PronType=Art	27	det	_	_
25	brief	brief	ADJ	JJ	Degree=Pos	27	amod	_	_
26	private	private	ADJ	JJ	Degree=Pos	27	amod	_	_
27	trip	trip	NOUN	NN	Number=Sing	22	nmod	_	_
28	to	to	ADP	IN	_	29	case	_	_
29	Eriador	Eriador	PROPN	NNP	Number=Sing	27	nmod	_	_
30	starting	start	VERB	VBG	VerbForm=Ger	18	advcl	_	_
31	on	on	ADP	IN	_	32	case	_	_
32	Sunday	Sunday	PROPN	NNP	Number=Sing	30	nmod	_	_
33	.	.	PUNCT	.	_	9	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test258': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test258']['sents']['0']:
            print(return_dict['test258']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test258']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],110)",str(return_dict['test258']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],110)","noevent"]
            print("test258 Failed")
    except:
        print("test258 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test258']['sents']['0']:
        verbs=return_dict['test258']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test258']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test258']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test258']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test258']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test258():
    text="""Bree Prime Minister Romendacil most certainly won't ever clash over the efforts of Eriadori  
to deal with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	10	nsubj	_	_
5	most	most	ADV	RBS	_	6	advmod	_	_
6	certainly	certainly	ADV	RB	_	10	advmod	_	_
7	wo	will	AUX	MD	VerbForm=Fin	10	aux	_	_
8	n't	not	PART	RB	_	10	neg	_	_
9	ever	ever	ADV	RB	_	10	advmod	_	_
10	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
11	over	over	ADP	IN	_	13	case	_	_
12	the	the	DET	DT	Definite=Def|PronType=Art	13	det	_	_
13	efforts	effort	NOUN	NNS	Number=Plur	10	nmod	_	_
14	of	of	ADP	IN	_	15	case	_	_
15	Eriadori	Eriadori	PROPN	NNP	Number=Sing	13	nmod	_	_
16	to	to	PART	TO	_	17	mark	_	_
17	deal	deal	VERB	VB	VerbForm=Inf	10	xcomp	_	_
18	with	with	ADP	IN	_	21	case	_	_
19	an	a	DET	DT	Definite=Ind|PronType=Art	21	det	_	_
20	orc	orc	ADJ	JJ	Degree=Pos	21	amod	_	_
21	infestation	infestation	NOUN	NN	Number=Sing	17	nmod	_	_
22	during	during	ADP	IN	_	26	case	_	_
23	a	a	DET	DT	Definite=Ind|PronType=Art	26	det	_	_
24	brief	brief	ADJ	JJ	Degree=Pos	26	amod	_	_
25	private	private	ADJ	JJ	Degree=Pos	26	amod	_	_
26	visit	visit	NOUN	NN	Number=Sing	17	nmod	_	_
27	to	to	ADP	IN	_	28	case	_	_
28	Eriador	Eriador	PROPN	NNP	Number=Sing	26	nmod	_	_
29	starting	start	VERB	VBG	VerbForm=Ger	26	acl	_	_
30	on	on	ADP	IN	_	31	case	_	_
31	Sunday	Sunday	PROPN	NNP	Number=Sing	29	nmod	_	_
32	.	.	PUNCT	.	_	10	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test259': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test259']['sents']['0']:
            print(return_dict['test259']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test259']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test259']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test259 Failed")
    except:
        print("test259 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test259']['sents']['0']:
        verbs=return_dict['test259']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test259']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test259']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test259']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test259']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test259():
    text="""Bree Prime Minister Romendacil most certainly really did not ever clash over the efforts of Eriadori  
to deal with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	11	nsubj	_	_
5	most	most	ADV	RBS	_	6	advmod	_	_
6	certainly	certainly	ADV	RB	_	11	advmod	_	_
7	really	really	ADV	RB	_	11	advmod	_	_
8	did	do	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	11	aux	_	_
9	not	not	PART	RB	_	11	neg	_	_
10	ever	ever	ADV	RB	_	11	advmod	_	_
11	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
12	over	over	ADP	IN	_	14	case	_	_
13	the	the	DET	DT	Definite=Def|PronType=Art	14	det	_	_
14	efforts	effort	NOUN	NNS	Number=Plur	11	nmod	_	_
15	of	of	ADP	IN	_	16	case	_	_
16	Eriadori	Eriadori	PROPN	NNP	Number=Sing	14	nmod	_	_
17	to	to	PART	TO	_	18	mark	_	_
18	deal	deal	VERB	VB	VerbForm=Inf	11	xcomp	_	_
19	with	with	ADP	IN	_	22	case	_	_
20	an	a	DET	DT	Definite=Ind|PronType=Art	22	det	_	_
21	orc	orc	ADJ	JJ	Degree=Pos	22	amod	_	_
22	infestation	infestation	NOUN	NN	Number=Sing	18	nmod	_	_
23	during	during	ADP	IN	_	27	case	_	_
24	a	a	DET	DT	Definite=Ind|PronType=Art	27	det	_	_
25	brief	brief	ADJ	JJ	Degree=Pos	27	amod	_	_
26	private	private	ADJ	JJ	Degree=Pos	27	amod	_	_
27	visit	visit	NOUN	NN	Number=Sing	18	nmod	_	_
28	to	to	ADP	IN	_	29	case	_	_
29	Eriador	Eriador	PROPN	NNP	Number=Sing	27	nmod	_	_
30	starting	start	VERB	VBG	VerbForm=Ger	27	acl	_	_
31	on	on	ADP	IN	_	32	case	_	_
32	Sunday	Sunday	PROPN	NNP	Number=Sing	30	nmod	_	_
33	.	.	PUNCT	.	_	11	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test260': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test260']['sents']['0']:
            print(return_dict['test260']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test260']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test260']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test260 Failed")
    except:
        print("test260 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test260']['sents']['0']:
        verbs=return_dict['test260']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test260']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test260']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test260']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test260']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test260():
    text="""Bree Prime Minister Romendacil most certainly really did not even ever clash over the efforts 
of Eriadori to deal with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	12	nsubj	_	_
5	most	most	ADV	RBS	_	6	advmod	_	_
6	certainly	certainly	ADV	RB	_	12	advmod	_	_
7	really	really	ADV	RB	_	12	advmod	_	_
8	did	do	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	12	aux	_	_
9	not	not	PART	RB	_	12	neg	_	_
10	even	even	ADV	RB	_	12	advmod	_	_
11	ever	ever	ADV	RB	_	12	advmod	_	_
12	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
13	over	over	ADP	IN	_	15	case	_	_
14	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
15	efforts	effort	NOUN	NNS	Number=Plur	12	nmod	_	_
16	of	of	ADP	IN	_	17	case	_	_
17	Eriadori	Eriadori	PROPN	NNP	Number=Sing	15	nmod	_	_
18	to	to	PART	TO	_	19	mark	_	_
19	deal	deal	VERB	VB	VerbForm=Inf	12	xcomp	_	_
20	with	with	ADP	IN	_	23	case	_	_
21	an	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
22	orc	orc	ADJ	JJ	Degree=Pos	23	amod	_	_
23	infestation	infestation	NOUN	NN	Number=Sing	19	nmod	_	_
24	during	during	ADP	IN	_	28	case	_	_
25	a	a	DET	DT	Definite=Ind|PronType=Art	28	det	_	_
26	brief	brief	ADJ	JJ	Degree=Pos	28	amod	_	_
27	private	private	ADJ	JJ	Degree=Pos	28	amod	_	_
28	visit	visit	NOUN	NN	Number=Sing	19	nmod	_	_
29	to	to	ADP	IN	_	30	case	_	_
30	Eriador	Eriador	PROPN	NNP	Number=Sing	28	nmod	_	_
31	starting	start	VERB	VBG	VerbForm=Ger	28	acl	_	_
32	on	on	ADP	IN	_	33	case	_	_
33	Sunday	Sunday	PROPN	NNP	Number=Sing	31	nmod	_	_
34	.	.	PUNCT	.	_	12	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test261': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test261']['sents']['0']:
            print(return_dict['test261']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test261']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test261']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test261 Failed")
    except:
        print("test261 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test261']['sents']['0']:
        verbs=return_dict['test261']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test261']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test261']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test261']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test261']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test261():
    text="""Bree Prime Minister Romendacil most certainly really won't even ever clash over the efforts 
of Eriadori to deal with an orc infestation during a brief private visit to Eriador starting on Sunday. 
"""
    parse="""1	Bree	Bree	PROPN	NNP	Number=Sing	4	compound	_	_
2	Prime	Prime	PROPN	NNP	Number=Sing	3	compound	_	_
3	Minister	Minister	PROPN	NNP	Number=Sing	4	compound	_	_
4	Romendacil	Romendacil	PROPN	NNP	Number=Sing	12	nsubj	_	_
5	most	most	ADV	RBS	_	6	advmod	_	_
6	certainly	certainly	ADV	RB	_	12	advmod	_	_
7	really	really	ADV	RB	_	12	advmod	_	_
8	wo	will	AUX	MD	VerbForm=Fin	12	aux	_	_
9	n't	not	PART	RB	_	12	neg	_	_
10	even	even	ADV	RB	_	12	advmod	_	_
11	ever	ever	ADV	RB	_	12	advmod	_	_
12	clash	clash	VERB	VB	VerbForm=Inf	0	root	_	_
13	over	over	ADP	IN	_	15	case	_	_
14	the	the	DET	DT	Definite=Def|PronType=Art	15	det	_	_
15	efforts	effort	NOUN	NNS	Number=Plur	12	nmod	_	_
16	of	of	ADP	IN	_	17	case	_	_
17	Eriadori	Eriadori	PROPN	NNP	Number=Sing	15	nmod	_	_
18	to	to	PART	TO	_	19	mark	_	_
19	deal	deal	VERB	VB	VerbForm=Inf	12	xcomp	_	_
20	with	with	ADP	IN	_	23	case	_	_
21	an	a	DET	DT	Definite=Ind|PronType=Art	23	det	_	_
22	orc	orc	ADJ	JJ	Degree=Pos	23	amod	_	_
23	infestation	infestation	NOUN	NN	Number=Sing	19	nmod	_	_
24	during	during	ADP	IN	_	28	case	_	_
25	a	a	DET	DT	Definite=Ind|PronType=Art	28	det	_	_
26	brief	brief	ADJ	JJ	Degree=Pos	28	amod	_	_
27	private	private	ADJ	JJ	Degree=Pos	28	amod	_	_
28	visit	visit	NOUN	NN	Number=Sing	19	nmod	_	_
29	to	to	ADP	IN	_	30	case	_	_
30	Eriador	Eriador	PROPN	NNP	Number=Sing	28	nmod	_	_
31	starting	start	VERB	VBG	VerbForm=Ger	28	acl	_	_
32	on	on	ADP	IN	_	33	case	_	_
33	Sunday	Sunday	PROPN	NNP	Number=Sing	31	nmod	_	_
34	.	.	PUNCT	.	_	12	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test262': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950111'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([BREGOV],[ERI],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test262']['sents']['0']:
            print(return_dict['test262']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test262']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)",str(return_dict['test262']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([BREGOV],[ERI],050)","noevent"]
            print("test262 Failed")
    except:
        print("test262 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test262']['sents']['0']:
        verbs=return_dict['test262']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test262']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test262']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test262']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test262']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test262():
    text="""Calenardhon welcomed memos from Bree on its role for in forthcoming peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	memos	memo	NOUN	NNS	Number=Plur	2	dobj	_	_
4	from	from	ADP	IN	_	5	case	_	_
5	Bree	Bree	PROPN	NNP	Number=Sing	2	nmod	_	_
6	on	on	ADP	IN	_	8	case	_	_
7	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	8	nmod:poss	_	_
8	role	role	NOUN	NN	Number=Sing	2	nmod	_	_
9	for	for	ADP	IN	_	13	case	_	_
10	in	in	ADP	IN	_	13	case	_	_
11	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	13	amod	_	_
12	peace	peace	NOUN	NN	Number=Sing	13	compound	_	_
13	talks	talk	NOUN	NNS	Number=Plur	2	nmod	_	_
14	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test263': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test263']['sents']['0']:
            print(return_dict['test263']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test263']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],050)",str(return_dict['test263']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],050)","noevent"]
            print("test263 Failed")
    except:
        print("test263 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test263']['sents']['0']:
        verbs=return_dict['test263']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test263']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test263']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test263']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test263']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test263():
    text="""Calenardhon welcomed economic memos from Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	economic	economic	ADJ	JJ	Degree=Pos	4	amod	_	_
4	memos	memo	NOUN	NNS	Number=Plur	2	dobj	_	_
5	from	from	ADP	IN	_	6	case	_	_
6	Bree	Bree	PROPN	NNP	Number=Sing	2	nmod	_	_
7	on	on	ADP	IN	_	9	case	_	_
8	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	9	nmod:poss	_	_
9	role	role	NOUN	NN	Number=Sing	2	nmod	_	_
10	for	for	ADP	IN	_	14	case	_	_
11	in	in	ADP	IN	_	14	case	_	_
12	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	14	amod	_	_
13	peace	peace	NOUN	NN	Number=Sing	14	compound	_	_
14	talks	talk	NOUN	NNS	Number=Plur	2	nmod	_	_
15	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test264': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],911)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test264']['sents']['0']:
            print(return_dict['test264']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test264']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],911)",str(return_dict['test264']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],911)","noevent"]
            print("test264 Failed")
    except:
        print("test264 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test264']['sents']['0']:
        verbs=return_dict['test264']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test264']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test264']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test264']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test264']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test264():
    text="""Calenardhon welcomed economic rumors about Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	economic	economic	ADJ	JJ	Degree=Pos	4	amod	_	_
4	rumors	rumor	NOUN	NNS	Number=Plur	2	dobj	_	_
5	about	about	ADP	IN	_	6	case	_	_
6	Bree	Bree	PROPN	NNP	Number=Sing	2	nmod	_	_
7	on	on	ADP	IN	_	9	case	_	_
8	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	9	nmod:poss	_	_
9	role	role	NOUN	NN	Number=Sing	2	nmod	_	_
10	for	for	ADP	IN	_	14	case	_	_
11	in	in	ADP	IN	_	14	case	_	_
12	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	14	amod	_	_
13	peace	peace	NOUN	NN	Number=Sing	14	compound	_	_
14	talks	talk	NOUN	NNS	Number=Plur	2	nmod	_	_
15	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test265': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],915)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test265']['sents']['0']:
            print(return_dict['test265']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test265']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],915)",str(return_dict['test265']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],915)","noevent"]
            print("test265 Failed")
    except:
        print("test265 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test265']['sents']['0']:
        verbs=return_dict['test265']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test265']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test265']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test265']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test265']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test265():
    text="""Calenardhon welcomed economic memos not about Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	economic	economic	ADJ	JJ	Degree=Pos	4	amod	_	_
4	memos	memo	NOUN	NNS	Number=Plur	2	dobj	_	_
5	not	not	ADV	RB	_	7	neg	_	_
6	about	about	ADP	IN	_	7	case	_	_
7	Bree	Bree	PROPN	NNP	Number=Sing	2	nmod	_	_
8	on	on	ADP	IN	_	10	case	_	_
9	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	10	nmod:poss	_	_
10	role	role	NOUN	NN	Number=Sing	7	nmod	_	_
11	for	for	ADP	IN	_	15	case	_	_
12	in	in	ADP	IN	_	15	case	_	_
13	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	15	amod	_	_
14	peace	peace	NOUN	NN	Number=Sing	15	compound	_	_
15	talks	talk	NOUN	NNS	Number=Plur	2	nmod	_	_
16	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test266': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],915)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test266']['sents']['0']:
            print(return_dict['test266']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test266']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],915)",str(return_dict['test266']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],915)","noevent"]
            print("test266 Failed")
    except:
        print("test266 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test266']['sents']['0']:
        verbs=return_dict['test266']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test266']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test266']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test266']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test266']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test266():
    text="""Calenardhon welcomed cultural memos sent by Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	cultural	cultural	ADJ	JJ	Degree=Pos	4	amod	_	_
4	memos	memo	NOUN	NNS	Number=Plur	2	dobj	_	_
5	sent	send	VERB	VBN	Tense=Past|VerbForm=Part	4	acl	_	_
6	by	by	ADP	IN	_	7	case	_	_
7	Bree	Bree	PROPN	NNP	Number=Sing	5	nmod	_	_
8	on	on	ADP	IN	_	10	case	_	_
9	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	10	nmod:poss	_	_
10	role	role	NOUN	NN	Number=Sing	5	nmod	_	_
11	for	for	ADP	IN	_	15	case	_	_
12	in	in	ADP	IN	_	15	case	_	_
13	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	15	amod	_	_
14	peace	peace	NOUN	NN	Number=Sing	15	compound	_	_
15	talks	talk	NOUN	NNS	Number=Plur	5	nmod	_	_
16	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test267': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],912)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test267']['sents']['0']:
            print(return_dict['test267']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test267']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],912)",str(return_dict['test267']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],912)","noevent"]
            print("test267 Failed")
    except:
        print("test267 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test267']['sents']['0']:
        verbs=return_dict['test267']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test267']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test267']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test267']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test267']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test267():
    text="""Calenardhon welcomed cultural secret memos sent by Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	cultural	cultural	ADJ	JJ	Degree=Pos	5	amod	_	_
4	secret	secret	ADJ	JJ	Degree=Pos	5	amod	_	_
5	memos	memo	NOUN	NNS	Number=Plur	2	dobj	_	_
6	sent	send	VERB	VBN	Tense=Past|VerbForm=Part	5	acl	_	_
7	by	by	ADP	IN	_	8	case	_	_
8	Bree	Bree	PROPN	NNP	Number=Sing	6	nmod	_	_
9	on	on	ADP	IN	_	11	case	_	_
10	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	11	nmod:poss	_	_
11	role	role	NOUN	NN	Number=Sing	6	nmod	_	_
12	for	for	ADP	IN	_	16	case	_	_
13	in	in	ADP	IN	_	16	case	_	_
14	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	16	amod	_	_
15	peace	peace	NOUN	NN	Number=Sing	16	compound	_	_
16	talks	talk	NOUN	NNS	Number=Plur	6	nmod	_	_
17	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test268': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test268']['sents']['0']:
            print(return_dict['test268']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test268']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],050)",str(return_dict['test268']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],050)","noevent"]
            print("test268 Failed")
    except:
        print("test268 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test268']['sents']['0']:
        verbs=return_dict['test268']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test268']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test268']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test268']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test268']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test268():
    text="""Calenardhon welcomed memos on economic issue from Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	memos	memo	NOUN	NNS	Number=Plur	2	dobj	_	_
4	on	on	ADP	IN	_	6	case	_	_
5	economic	economic	ADJ	JJ	Degree=Pos	6	amod	_	_
6	issue	issue	NOUN	NN	Number=Sing	3	nmod	_	_
7	from	from	ADP	IN	_	8	case	_	_
8	Bree	Bree	PROPN	NNP	Number=Sing	2	nmod	_	_
9	on	on	ADP	IN	_	11	case	_	_
10	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	11	nmod:poss	_	_
11	role	role	NOUN	NN	Number=Sing	2	nmod	_	_
12	for	for	ADP	IN	_	16	case	_	_
13	in	in	ADP	IN	_	16	case	_	_
14	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	16	amod	_	_
15	peace	peace	NOUN	NN	Number=Sing	16	compound	_	_
16	talks	talk	NOUN	NNS	Number=Plur	2	nmod	_	_
17	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test269': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],911)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test269']['sents']['0']:
            print(return_dict['test269']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test269']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],911)",str(return_dict['test269']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],911)","noevent"]
            print("test269 Failed")
    except:
        print("test269 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test269']['sents']['0']:
        verbs=return_dict['test269']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test269']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test269']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test269']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test269']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test269():
    text="""Calenardhon welcomed cultural internal memos from Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	cultural	cultural	ADJ	JJ	Degree=Pos	5	amod	_	_
4	internal	internal	ADJ	JJ	Degree=Pos	5	amod	_	_
5	memos	memo	NOUN	NNS	Number=Plur	2	dobj	_	_
6	from	from	ADP	IN	_	7	case	_	_
7	Bree	Bree	PROPN	NNP	Number=Sing	2	nmod	_	_
8	on	on	ADP	IN	_	10	case	_	_
9	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	10	nmod:poss	_	_
10	role	role	NOUN	NN	Number=Sing	2	nmod	_	_
11	for	for	ADP	IN	_	15	case	_	_
12	in	in	ADP	IN	_	15	case	_	_
13	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	15	amod	_	_
14	peace	peace	NOUN	NN	Number=Sing	15	compound	_	_
15	talks	talk	NOUN	NNS	Number=Plur	2	nmod	_	_
16	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test270': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test270']['sents']['0']:
            print(return_dict['test270']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test270']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],050)",str(return_dict['test270']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],050)","noevent"]
            print("test270 Failed")
    except:
        print("test270 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test270']['sents']['0']:
        verbs=return_dict['test270']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test270']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test270']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test270']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test270']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test270():
    text="""Calenardhon welcomed cultural internal assurances sent by Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	cultural	cultural	ADJ	JJ	Degree=Pos	5	amod	_	_
4	internal	internal	ADJ	JJ	Degree=Pos	5	amod	_	_
5	assurances	assurance	NOUN	NNS	Number=Plur	2	dobj	_	_
6	sent	send	VERB	VBN	Tense=Past|VerbForm=Part	5	acl	_	_
7	by	by	ADP	IN	_	8	case	_	_
8	Bree	Bree	PROPN	NNP	Number=Sing	6	nmod	_	_
9	on	on	ADP	IN	_	11	case	_	_
10	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	11	nmod:poss	_	_
11	role	role	NOUN	NN	Number=Sing	6	nmod	_	_
12	for	for	ADP	IN	_	16	case	_	_
13	in	in	ADP	IN	_	16	case	_	_
14	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	16	amod	_	_
15	peace	peace	NOUN	NN	Number=Sing	16	compound	_	_
16	talks	talk	NOUN	NNS	Number=Plur	6	nmod	_	_
17	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test271': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],030)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test271']['sents']['0']:
            print(return_dict['test271']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test271']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],030)",str(return_dict['test271']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],030)","noevent"]
            print("test271 Failed")
    except:
        print("test271 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test271']['sents']['0']:
        verbs=return_dict['test271']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test271']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test271']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test271']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test271']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test271():
    text="""Calenardhon welcomed assurances on cultural issues from Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	assurances	assurance	NOUN	NNS	Number=Plur	2	dobj	_	_
4	on	on	ADP	IN	_	6	case	_	_
5	cultural	cultural	ADJ	JJ	Degree=Pos	6	amod	_	_
6	issues	issue	NOUN	NNS	Number=Plur	2	nmod	_	_
7	from	from	ADP	IN	_	8	case	_	_
8	Bree	Bree	PROPN	NNP	Number=Sing	2	nmod	_	_
9	on	on	ADP	IN	_	11	case	_	_
10	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	11	nmod:poss	_	_
11	role	role	NOUN	NN	Number=Sing	2	nmod	_	_
12	for	for	ADP	IN	_	16	case	_	_
13	in	in	ADP	IN	_	16	case	_	_
14	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	16	amod	_	_
15	peace	peace	NOUN	NN	Number=Sing	16	compound	_	_
16	talks	talk	NOUN	NNS	Number=Plur	11	nmod	_	_
17	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test272': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],030)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test272']['sents']['0']:
            print(return_dict['test272']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test272']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],030)",str(return_dict['test272']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],030)","noevent"]
            print("test272 Failed")
    except:
        print("test272 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test272']['sents']['0']:
        verbs=return_dict['test272']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test272']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test272']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test272']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test272']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test272():
    text="""Calenardhon welcomed assurances on cultural issues sent from Bree on its role for in forthcoming 
peace talks. 
"""
    parse="""1	Calenardhon	Calenardhon	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	welcomed	welcom	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	assurances	assurance	NOUN	NNS	Number=Plur	2	dobj	_	_
4	on	on	ADP	IN	_	6	case	_	_
5	cultural	cultural	ADJ	JJ	Degree=Pos	6	amod	_	_
6	issues	issue	NOUN	NNS	Number=Plur	2	nmod	_	_
7	sent	send	VERB	VBN	Tense=Past|VerbForm=Part	6	acl	_	_
8	from	from	ADP	IN	_	9	case	_	_
9	Bree	Bree	PROPN	NNP	Number=Sing	7	nmod	_	_
10	on	on	ADP	IN	_	12	case	_	_
11	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	12	nmod:poss	_	_
12	role	role	NOUN	NN	Number=Sing	6	nmod	_	_
13	for	for	ADP	IN	_	17	case	_	_
14	in	in	ADP	IN	_	17	case	_	_
15	forthcoming	forthcoming	ADJ	JJ	Degree=Pos	17	amod	_	_
16	peace	peace	NOUN	NN	Number=Sing	17	compound	_	_
17	talks	talk	NOUN	NNS	Number=Plur	12	nmod	_	_
18	.	.	PUNCT	.	_	2	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test273': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950118'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([CAL],[BRE],030)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test273']['sents']['0']:
            print(return_dict['test273']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test273']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],030)",str(return_dict['test273']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([CAL],[BRE],030)","noevent"]
            print("test273 Failed")
    except:
        print("test273 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test273']['sents']['0']:
        verbs=return_dict['test273']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test273']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test273']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test273']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test273']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test273():
    text="""Arnor is inching nearer to accord with Gondor almost 
five years after crowds trashed its embassy, a senior official 
said on Saturday. 
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	AUX	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	aux	_	_
3	inching	inch	VERB	VBG	Tense=Pres|VerbForm=Part	0	root	_	_
4	nearer	nearer	ADJ	JJR	Degree=Cmp	3	xcomp	_	_
5	to	to	PART	TO	_	6	mark	_	_
6	accord	accord	VERB	VB	VerbForm=Inf	4	advcl	_	_
7	with	with	ADP	IN	_	8	case	_	_
8	Gondor	Gondor	PROPN	NNP	Number=Sing	6	nmod	_	_
9	almost	almost	ADV	RB	_	10	advmod	_	_
10	five	five	NUM	CD	NumType=Card	11	nummod	_	_
11	years	year	NOUN	NNS	Number=Plur	13	nmod:npmod	_	_
12	after	after	ADP	IN	_	13	case	_	_
13	crowds	crowd	NOUN	NNS	Number=Plur	6	nmod	_	_
14	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	6	advcl	_	_
15	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	16	nmod:poss	_	_
16	embassy	embassy	NOUN	NN	Number=Sing	14	dobj	_	_
17	,	,	PUNCT	,	_	16	punct	_	_
18	a	a	DET	DT	Definite=Ind|PronType=Art	20	det	_	_
19	senior	senior	ADJ	JJ	Degree=Pos	20	amod	_	_
20	official	official	NOUN	NN	Number=Sing	21	nsubj	_	_
21	said	say	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	16	acl:relcl	_	_
22	on	on	ADP	IN	_	23	case	_	_
23	Saturday	Saturday	PROPN	NNP	Number=Sing	21	nmod	_	_
24	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test274': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([ARN],[GON],013)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test274']['sents']['0']:
            print(return_dict['test274']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test274']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],013)",str(return_dict['test274']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([ARN],[GON],013)","noevent"]
            print("test274 Failed")
    except:
        print("test274 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test274']['sents']['0']:
        verbs=return_dict['test274']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test274']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test274']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test274']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test274']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test274():
    text="""CEBU CITY: -- Cordova Mayor Adelino Sitoy and the town's fisherfolk filed on Thursday a 
P225-million suit against two shipping firms whose vessels collided off Talisay City in 
August last year and caused a massive oil spill in Cebu.
"""
    parse="""1	CEBU	Cebu	PROPN	NNP	Number=Sing	2	compound	_	_
2	CITY	city	PROPN	NNP	Number=Sing	14	nsubj	_	_
3	:	:	PUNCT	:	_	2	punct	_	_
4	--	--	PUNCT	,	_	2	punct	_	_
5	Cordova	Cordova	PROPN	NNP	Number=Sing	8	name	_	_
6	Mayor	Mayor	PROPN	NNP	Number=Sing	8	name	_	_
7	Adelino	Adelino	PROPN	NNP	Number=Sing	8	name	_	_
8	Sitoy	Sitoy	PROPN	NNP	Number=Sing	2	appos	_	_
9	and	and	CONJ	CC	_	8	cc	_	_
10	the	the	DET	DT	Definite=Def|PronType=Art	11	det	_	_
11	town	town	NOUN	NN	Number=Sing	13	nmod:poss	_	_
12	's	's	PART	POS	_	11	case	_	_
13	fisherfolk	fisherfolk	NOUN	NNS	Number=Plur	8	conj	_	_
14	filed	file	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
15	on	on	ADP	IN	_	16	case	_	_
16	Thursday	Thursday	PROPN	NNP	Number=Sing	14	nmod	_	_
17	a	a	DET	DT	Definite=Ind|PronType=Art	19	det	_	_
18	P225-million	P225-million	NUM	CD	NumType=Card	19	nummod	_	_
19	suit	suit	NOUN	NN	Number=Sing	14	dobj	_	_
20	against	against	ADP	IN	_	23	case	_	_
21	two	two	NUM	CD	NumType=Card	23	nummod	_	_
22	shipping	shipping	NOUN	NN	Number=Sing	23	compound	_	_
23	firms	firm	NOUN	NNS	Number=Plur	19	nmod	_	_
24	whose	whose	PRON	WP$	Poss=Yes|PronType=Int	25	nmod:poss	_	_
25	vessels	vessel	NOUN	NNS	Number=Plur	26	nsubj	_	_
26	collided	collide	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	23	acl:relcl	_	_
27	off	off	ADP	RP	_	29	case	_	_
28	Talisay	Talisay	PROPN	NNP	Number=Sing	29	compound	_	_
29	City	City	PROPN	NNP	Number=Sing	26	nmod	_	_
30	in	in	ADP	IN	_	31	case	_	_
31	August	August	PROPN	NNP	Number=Sing	26	nmod	_	_
32	last	last	ADJ	JJ	Degree=Pos	33	amod	_	_
33	year	year	NOUN	NN	Number=Sing	26	nmod:tmod	_	_
34	and	and	CONJ	CC	_	14	cc	_	_
35	caused	cause	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	14	conj	_	_
36	a	a	DET	DT	Definite=Ind|PronType=Art	39	det	_	_
37	massive	massive	ADJ	JJ	Degree=Pos	39	amod	_	_
38	oil	oil	NOUN	NN	Number=Sing	39	compound	_	_
39	spill	spill	NOUN	NN	Number=Sing	35	dobj	_	_
40	in	in	ADP	IN	_	41	case	_	_
41	Cebu	Cebu	PROPN	NNP	Number=Sing	39	nmod	_	_
42	.	.	PUNCT	.	_	14	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test275': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'20080801'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([],[],ng error=)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test275']['sents']['0']:
            print(return_dict['test275']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test275']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([],[],ng error=)",str(return_dict['test275']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([],[],ng error=)","noevent"]
            print("test275 Failed")
    except:
        print("test275 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test275']['sents']['0']:
        verbs=return_dict['test275']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test275']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test275']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test275']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test275']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test275():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test276': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([arse],[],ng error=)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test276']['sents']['0']:
            print(return_dict['test276']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test276']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([arse],[],ng error=)",str(return_dict['test276']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([arse],[],ng error=)","noevent"]
            print("test276 Failed")
    except:
        print("test276 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test276']['sents']['0']:
        verbs=return_dict['test276']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test276']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test276']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test276']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test276']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test276():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	15	case	_	_
15	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
16	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	15	acl	_	_
17	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	18	nmod:poss	_	_
18	embassy	embassy	NOUN	NN	Number=Sing	16	dobj	_	_
19	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test277': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([arse],[],ng error=)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test277']['sents']['0']:
            print(return_dict['test277']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test277']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([arse],[],ng error=)",str(return_dict['test277']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([arse],[],ng error=)","noevent"]
            print("test277 Failed")
    except:
        print("test277 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test277']['sents']['0']:
        verbs=return_dict['test277']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test277']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test277']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test277']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test277']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test277():
    text="""Arnor is about to restore full diplomatic ties with Gondor almost 
five years after a typhoon trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	full	full	ADJ	JJ	Degree=Pos	8	amod	_	_
7	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	8	amod	_	_
8	ties	tie	NOUN	NNS	Number=Plur	5	dobj	_	_
9	with	with	ADP	IN	_	10	case	_	_
10	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
11	almost	almost	ADV	RB	_	12	advmod	_	_
12	five	five	NUM	CD	NumType=Card	13	nummod	_	_
13	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
14	after	after	ADP	IN	_	16	case	_	_
15	a	a	DET	DT	Definite=Ind|PronType=Art	16	det	_	_
16	typhoon	typhoon	NOUN	NN	Number=Sing	5	nmod	_	_
17	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
18	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
19	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
20	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test278': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([d],[],ng error=)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test278']['sents']['0']:
            print(return_dict['test278']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test278']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([d],[],ng error=)",str(return_dict['test278']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([d],[],ng error=)","noevent"]
            print("test278 Failed")
    except:
        print("test278 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test278']['sents']['0']:
        verbs=return_dict['test278']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test278']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test278']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test278']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test278']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test278():
    text="""Arnor is about to restore the World Golf Championships to Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
7	World	World	PROPN	NNP	Number=Sing	9	compound	_	_
8	Golf	golf	PROPN	NNP	Number=Sing	9	name	_	_
9	Championships	Championships	PROPN	NNP	Number=Sing	5	dobj	_	_
10	to	to	PART	TO	_	11	mark	_	_
11	Gondor	Gondor	VERB	VB	VerbForm=Inf	5	advcl	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	16	nmod:npmod	_	_
15	after	after	ADP	IN	_	16	case	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	11	nmod	_	_
17	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
18	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
19	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
20	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test279': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([d],[],ng error=)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test279']['sents']['0']:
            print(return_dict['test279']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test279']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([d],[],ng error=)",str(return_dict['test279']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([d],[],ng error=)","noevent"]
            print("test279 Failed")
    except:
        print("test279 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test279']['sents']['0']:
        verbs=return_dict['test279']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test279']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test279']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test279']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test279']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test279():
    text="""Arnor is about to restore baseball competition with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	baseball	baseball	NOUN	NN	Number=Sing	7	compound	_	_
7	competition	competition	NOUN	NN	Number=Sing	5	dobj	_	_
8	with	with	ADP	IN	_	9	case	_	_
9	Gondor	Gondor	PROPN	NNP	Number=Sing	5	nmod	_	_
10	almost	almost	ADV	RB	_	11	advmod	_	_
11	five	five	NUM	CD	NumType=Card	12	nummod	_	_
12	years	year	NOUN	NNS	Number=Plur	5	nmod:tmod	_	_
13	after	after	ADP	IN	_	14	case	_	_
14	crowds	crowd	NOUN	NNS	Number=Plur	5	nmod	_	_
15	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	14	acl	_	_
16	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	17	nmod:poss	_	_
17	embassy	embassy	NOUN	NN	Number=Sing	15	dobj	_	_
18	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test280': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([card],[],ng error=)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test280']['sents']['0']:
            print(return_dict['test280']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test280']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([card],[],ng error=)",str(return_dict['test280']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([card],[],ng error=)","noevent"]
            print("test280 Failed")
    except:
        print("test280 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test280']['sents']['0']:
        verbs=return_dict['test280']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test280']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test280']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test280']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test280']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test280():
    text="""Arnor is about to restore the African Nations Cup to Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	Arnor	Arnor	PROPN	NNP	Number=Sing	3	nsubj	_	_
2	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	3	cop	_	_
3	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
4	to	to	PART	TO	_	5	mark	_	_
5	restore	restore	VERB	VB	VerbForm=Inf	3	xcomp	_	_
6	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
7	African	african	PROPN	NNP	Number=Sing	8	compound	_	_
8	Nations	Nations	PROPN	NNP	Number=Sing	9	compound	_	_
9	Cup	cup	PROPN	NNP	Number=Sing	5	dobj	_	_
10	to	to	PART	TO	_	11	mark	_	_
11	Gondor	Gondor	VERB	VB	VerbForm=Inf	5	advcl	_	_
12	almost	almost	ADV	RB	_	13	advmod	_	_
13	five	five	NUM	CD	NumType=Card	14	nummod	_	_
14	years	year	NOUN	NNS	Number=Plur	11	dobj	_	_
15	after	after	ADP	IN	_	16	case	_	_
16	crowds	crowd	NOUN	NNS	Number=Plur	14	nmod	_	_
17	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	16	acl	_	_
18	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	19	nmod:poss	_	_
19	embassy	embassy	NOUN	NN	Number=Sing	17	dobj	_	_
20	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test281': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950101'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([card],[],ng error=)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test281']['sents']['0']:
            print(return_dict['test281']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test281']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([card],[],ng error=)",str(return_dict['test281']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([card],[],ng error=)","noevent"]
            print("test281 Failed")
    except:
        print("test281 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test281']['sents']['0']:
        verbs=return_dict['test281']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test281']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test281']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test281']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test281']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test281():
    text="""Russian police arrested Russian students in Moscow today.
"""
    parse="""1	Russian	russian	ADJ	JJ	Degree=Pos	2	amod	_	_
2	police	police	NOUN	NNS	Number=Plur	3	nsubj	_	_
3	arrested	arrest	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
4	Russian	russian	ADJ	JJ	Degree=Pos	5	amod	_	_
5	students	student	NOUN	NNS	Number=Plur	3	dobj	_	_
6	in	in	ADP	IN	_	7	case	_	_
7	Moscow	Moscow	PROPN	NNP	Number=Sing	3	nmod	_	_
8	today	today	NOUN	NN	Number=Sing	3	nmod:tmod	_	_
9	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test282': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([RUSCOP],[RUSEDU],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test282']['sents']['0']:
            print(return_dict['test282']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test282']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([RUSCOP],[RUSEDU],110)",str(return_dict['test282']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([RUSCOP],[RUSEDU],110)","noevent"]
            print("test282 Failed")
    except:
        print("test282 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test282']['sents']['0']:
        verbs=return_dict['test282']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test282']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test282']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test282']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test282']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test282():
    text="""Russian police arrested students in Moscow today.
"""
    parse="""1	Russian	russian	ADJ	JJ	Degree=Pos	2	amod	_	_
2	police	police	NOUN	NNS	Number=Plur	3	nsubj	_	_
3	arrested	arrest	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
4	students	student	NOUN	NNS	Number=Plur	3	dobj	_	_
5	in	in	ADP	IN	_	6	case	_	_
6	Moscow	Moscow	PROPN	NNP	Number=Sing	3	nmod	_	_
7	today	today	NOUN	NN	Number=Sing	3	nmod:tmod	_	_
8	.	.	PUNCT	.	_	3	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test283': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([RUSCOP],[---EDU],110)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test283']['sents']['0']:
            print(return_dict['test283']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test283']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([RUSCOP],[---EDU],110)",str(return_dict['test283']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([RUSCOP],[---EDU],110)","noevent"]
            print("test283 Failed")
    except:
        print("test283 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test283']['sents']['0']:
        verbs=return_dict['test283']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test283']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test283']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test283']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test283']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test283():
    text="""The International Criminal Court is about to restore full diplomatic ties with Gondor almost 
five years after crowds trashed its embassy.
"""
    parse="""1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	International	International	PROPN	NNP	Number=Sing	4	compound	_	_
3	Criminal	Criminal	PROPN	NNP	Number=Sing	4	compound	_	_
4	Court	Court	PROPN	NNP	Number=Sing	6	nsubj	_	_
5	is	be	VERB	VBZ	Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin	6	cop	_	_
6	about	about	ADJ	JJ	Degree=Pos	0	root	_	_
7	to	to	PART	TO	_	8	mark	_	_
8	restore	restore	VERB	VB	VerbForm=Inf	6	xcomp	_	_
9	full	full	ADJ	JJ	Degree=Pos	11	amod	_	_
10	diplomatic	diplomatic	ADJ	JJ	Degree=Pos	11	amod	_	_
11	ties	tie	NOUN	NNS	Number=Plur	8	dobj	_	_
12	with	with	ADP	IN	_	13	case	_	_
13	Gondor	Gondor	PROPN	NNP	Number=Sing	8	nmod	_	_
14	almost	almost	ADV	RB	_	15	advmod	_	_
15	five	five	NUM	CD	NumType=Card	16	nummod	_	_
16	years	year	NOUN	NNS	Number=Plur	8	nmod:tmod	_	_
17	after	after	ADP	IN	_	18	case	_	_
18	crowds	crowd	NOUN	NNS	Number=Plur	8	nmod	_	_
19	trashed	trash	VERB	VBN	Tense=Past|VerbForm=Part	18	acl	_	_
20	its	its	PRON	PRP$	Gender=Neut|Number=Sing|Person=3|Poss=Yes|PronType=Prs	21	nmod:poss	_	_
21	embassy	embassy	NOUN	NN	Number=Sing	19	dobj	_	_
22	.	.	PUNCT	.	_	6	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test284': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "([IGOCOPITP],[GON],050)", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test284']['sents']['0']:
            print(return_dict['test284']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test284']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([IGOCOPITP],[GON],050)",str(return_dict['test284']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"([IGOCOPITP],[GON],050)","noevent"]
            print("test284 Failed")
    except:
        print("test284 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test284']['sents']['0']:
        verbs=return_dict['test284']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test284']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test284']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test284']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test284']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
def test284():
    text="""ALL OF THE UNIT TESTS WERE CODED CORRECTLY.
"""
    parse="""1	ALL	all	ADV	RB	_	7	advmod	_	_
2	OF	of	ADP	IN	_	5	case	_	_
3	THE	the	DET	DT	Definite=Def|PronType=Art	5	det	_	_
4	UNIT	Unit	PROPN	NNP	Number=Sing	5	compound	_	_
5	TESTS	tests	PROPN	NNP	Number=Sing	1	nmod	_	_
6	WERE	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	7	auxpass	_	_
7	CODED	Cod	VERB	VBN	Tense=Past|VerbForm=Part	0	root	_	_
8	CORRECTLY	correctly	ADV	RB	_	7	advmod	_	_
9	.	.	PUNCT	.	_	7	punct	_	_
"""
    phrase_dict = parse_parser(parse)
    parsed = utilities._format_ud_parsed_str(parse)
    dict = {u'test285': {u'sents': {u'0': {u'content': text, u'parsed': parsed}},
   		u'meta': {u'date': u'19950104'}}}
    global write_str 
    write_str = []
    return_dict = "" 
    try: 
        return_dict = petrarch_ud.do_coding(dict)
    except Exception as e: 
        write_str = [text.replace("\n"," ") , parsed.replace("\n"," ") , "No Event", "Petrarch Runtime Error " + str(e)]
    try:
        if 'events' in return_dict['test285']['sents']['0']:
            print(return_dict['test285']['sents']['0']['events'])
            event_out = process_event_output(str(return_dict['test285']['sents']['0']['events']))
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event",str(return_dict['test285']['sents']['0']['events']),event_out]
        else:
            write_str = [text.replace("\n"," "),parsed.replace("\n"," "),"No Event","noevent"]
            print("test285 Failed")
    except:
        print("test285 Failed")
    #Print the verbs
    if 'verbs' in return_dict['test285']['sents']['0']:
        verbs=return_dict['test285']['sents']['0']['verbs']
        parse_verb(verbs,phrase_dict,text,parsed)
    if 'nouns' in return_dict['test285']['sents']['0']:
        #Print the nouns
        nouns=return_dict['test285']['sents']['0']['nouns']
        parse_noun(nouns,phrase_dict,text,parsed)
    if 'triplets' in return_dict['test285']['sents']['0']:
        #Print the nouns
        triplets=return_dict['test285']['sents']['0']['triplets']
        parse_triplets(triplets,phrase_dict)
    fout_report.writerow(write_str)
test1()
test2()
test3()
test4()
test5()
test6()
test7()
test8()
test9()
test10()
test11()
test12()
test13()
test14()
test15()
test16()
test17()
test18()
test19()
test20()
test21()
test22()
test23()
test24()
test25()
test26()
test27()
test28()
test29()
test30()
test31()
test32()
test33()
test34()
test35()
test36()
test37()
test38()
test39()
test40()
test41()
test42()
test43()
test44()
test45()
test46()
test47()
test48()
test49()
test50()
test51()
test52()
test53()
test54()
test55()
test56()
test57()
test58()
test59()
test60()
test61()
test62()
test63()
test64()
test65()
test66()
test67()
test68()
test69()
test70()
test71()
test72()
test73()
test74()
test75()
test76()
test77()
test78()
test79()
test80()
test81()
test82()
test83()
test84()
test85()
test86()
test87()
test88()
test89()
test90()
test91()
test92()
test93()
test94()
test95()
test96()
test97()
test98()
test99()
test100()
test101()
test102()
test103()
test104()
test105()
test106()
test107()
test108()
test109()
test110()
test111()
test112()
test113()
test114()
test115()
test116()
test117()
test118()
test119()
test120()
test121()
test122()
test123()
test124()
test125()
test126()
test127()
test128()
test129()
test130()
test131()
test132()
test133()
test134()
test135()
test136()
test137()
test138()
test139()
test140()
test141()
test142()
test143()
test144()
test145()
test146()
test147()
test148()
test149()
test150()
test151()
test152()
test153()
test154()
test155()
test156()
test157()
test158()
test159()
test160()
test161()
test162()
test163()
test164()
test165()
test166()
test167()
test168()
test169()
test170()
test171()
test172()
test173()
test174()
test175()
test176()
test177()
test178()
test179()
test180()
test181()
test182()
test183()
test184()
test185()
test186()
test187()
test188()
test189()
test190()
test191()
test192()
test193()
test194()
test195()
test196()
test197()
test198()
test199()
test200()
test201()
test202()
test203()
test204()
test205()
test206()
test207()
test208()
test209()
test210()
test211()
test212()
test213()
test214()
test215()
test216()
test217()
test218()
test219()
test220()
test221()
test222()
test223()
test224()
test225()
test226()
test227()
test228()
test229()
test230()
test231()
test232()
test233()
test234()
test235()
test236()
test237()
test238()
test239()
test240()
test241()
test242()
test243()
test244()
test245()
test246()
test247()
test248()
test249()
test250()
test251()
test252()
test253()
test254()
test255()
test256()
test257()
test258()
test259()
test260()
test261()
test262()
test263()
test264()
test265()
test266()
test267()
test268()
test269()
test270()
test271()
test272()
test273()
test274()
test275()
test276()
test277()
test278()
test279()
test280()
test281()
test282()
test283()
test284()

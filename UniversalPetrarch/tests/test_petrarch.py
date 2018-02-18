import sys
sys.path.append('..')
import datetime
from bson.objectid import ObjectId
import petrarch_ud
import PETRreader

# <Sentence date="20150501" id="AAW_ARB_20070301.0004-1" sentence="true" source="AAW"><Text></Text><Parse</Parse></Sentence><Sentence date="20150501" id="AAW_ARB_20070301.0004-2" sentence="true" source="AAW"><Text>A sniper opened fire on soldiers manning a checkpoint in southern Baghdad, killing a soldier and injuring three others, police officer Nader al-Janabi told Anadolu Agency.</Text><Parse>1	A	a	DET	DT	Definite=Ind|PronType=Art	2	det	_	_
# 2	sniper	sniper	NOUN	NN	Number=Sing	3	nsubj	_	_
# 3	opened	open	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
# 4	fire	fire	NOUN	NN	Number=Sing	3	dobj	_	_
# 5	on	on	ADP	IN	_	6	case	_	_
# 6	soldiers	soldier	NOUN	NNS	Number=Plur	3	nmod	_	_
# 7	manning	mann	VERB	VBG	VerbForm=Ger	6	acl	_	_
# 8	a	a	DET	DT	Definite=Ind|PronType=Art	9	det	_	_
# 9	checkpoint	checkpoint	NOUN	NN	Number=Sing	7	dobj	_	_
# 10	in	in	ADP	IN	_	12	case	_	_
# 11	southern	southern	ADJ	JJ	Degree=Pos	12	amod	_	_
# 12	Baghdad,	baghdad,	NOUN	NN	Number=Sing	7	nmod	_	_
# 13	killing	kill	VERB	VBG	VerbForm=Ger	3	advcl	_	_
# 14	a	a	DET	DT	Definite=Ind|PronType=Art	15	det	_	_
# 15	soldier	soldier	NOUN	NN	Number=Sing	13	dobj	_	_
# 16	and	and	CONJ	CC	_	13	cc	_	_
# 17	injuring	injure	VERB	VBG	VerbForm=Ger	13	conj	_	_
# 18	three	three	NUM	CD	NumType=Card	24	nummod	_	_
# 19	others,	others,	PUNCT	,	_	24	punct	_	_
# 20	police	police	NOUN	NN	Number=Sing	21	compound	_	_
# 21	officer	officer	NOUN	NN	Number=Sing	23	compound	_	_
# 22	Nader	Nader	PROPN	NNP	Number=Sing	23	name	_	_
# 23	al-Janabi	al-Janabi	PROPN	NNP	Number=Sing	24	nsubj	_	_
# 24	told	tell	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	17	ccomp	_	_
# 25	Anadolu	Anadolu	PROPN	NNP	Number=Sing	26	name	_	_
# 26	Agency.	Agency.	PROPN	NNP	Number=Sing	24	dobj	_	_
# </Parse></Sentence><Sentence date="20150501" id="AAW_ARB_20070301.0004-3" sentence="true" source="AAW"><Text>Two civilians were killed and six others injured in a bomb blast in al-Zafarana district in south-eastern Baghdad, he said.</Text><Parse>1	Two	two	NUM	CD	NumType=Card	2	nummod	_	_
# 2	civilians	civilian	NOUN	NNS	Number=Plur	4	nsubjpass	_	_
# 3	were	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	4	auxpass	_	_
# 4	killed	kill	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
# 5	and	and	CONJ	CC	_	4	cc	_	_
# 6	six	six	NUM	CD	NumType=Card	7	nummod	_	_
# 7	others	other	NOUN	NNS	Number=Plur	8	nsubj	_	_
# 8	injured	injure	VERB	VBN	Tense=Past|VerbForm=Part	4	conj	_	_
# 9	in	in	ADP	IN	_	12	case	_	_
# 10	a	a	DET	DT	Definite=Ind|PronType=Art	12	det	_	_
# 11	bomb	bomb	NOUN	NN	Number=Sing	12	compound	_	_
# 12	blast	blast	NOUN	NN	Number=Sing	8	nmod	_	_
# 13	in	in	ADP	IN	_	15	case	_	_
# 14	al-Zafarana	al-Zafarana	PROPN	NNP	Number=Sing	15	compound	_	_
# 15	district	district	NOUN	NN	Number=Sing	12	nmod	_	_
# 16	in	in	ADP	IN	_	18	case	_	_
# 17	south-eastern	south-eastern	ADJ	JJ	Degree=Pos	18	amod	_	_
# 18	Baghdad,	baghdad,	NOUN	NN	Number=Sing	8	nmod	_	_
# 19	he	he	PRON	PRP	Case=Nom|Gender=Masc|Number=Sing|Person=3|PronType=Prs	20	nsubj	_	_
# 20	said.	said.	SYM	NFP	_	4	punct	_	_
# </Parse></Sentence><Sentence date="20150501" id="AAW_ARB_20070301.0004-4" sentence="true" source="AAW"><Text>Three more civilians were killed and seven others injured in two bomb blasts in southern and northern Baghdad, according to al-Janabi.</Text><Parse>1	Three	three	NUM	CD	NumType=Card	3	nummod	_	_
# 2	more	more	ADJ	JJR	Degree=Cmp	3	amod	_	_
# 3	civilians	civilian	NOUN	NNS	Number=Plur	5	nsubjpass	_	_
# 4	were	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	5	auxpass	_	_
# 5	killed	kill	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
# 6	and	and	CONJ	CC	_	5	cc	_	_
# 7	seven	seven	NUM	CD	NumType=Card	8	nummod	_	_
# 8	others	other	NOUN	NNS	Number=Plur	5	conj	_	_
# 9	injured	injure	VERB	VBN	Tense=Past|VerbForm=Part	8	acl	_	_
# 10	in	in	ADP	IN	_	13	case	_	_
# 11	two	two	NUM	CD	NumType=Card	13	nummod	_	_
# 12	bomb	bomb	NOUN	NN	Number=Sing	13	compound	_	_
# 13	blasts	blast	NOUN	NNS	Number=Plur	8	nmod	_	_
# 14	in	in	ADP	IN	_	18	case	_	_
# 15	southern	southern	ADJ	JJ	Degree=Pos	18	amod	_	_
# 16	and	and	CONJ	CC	_	15	cc	_	_
# 17	northern	northern	ADJ	JJ	Degree=Pos	15	conj	_	_
# 18	Baghdad,	baghdad,	NOUN	NN	Number=Sing	13	nmod	_	_
# 19	according	accord	VERB	VBG	VerbForm=Ger	21	case	_	_
# 20	to	to	ADP	IN	_	21	case	_	_
# 21	al-Janabi.	al-Janabi.	PROPN	NNP	Number=Sing	8	nmod	_	_
# </Parse></Sentence><Sentence date="20150501" id="AAW_ARB_20070301.0004-5" sentence="true" source="AAW"><Text>
# </Text><Parse>
# </Parse></Sentence>
# """

formatted = [{u'language': u'english',
u'title': u'6 killed in attacks in Iraqi capital Friday',
u'url': u'http://www.menafn.com/1094827896/6-killed-in-attacks-in-Iraqi-capital-Friday?src=RSS',
u'stanford': 1,
u'content': "BAGHDAD: At least six people, including a soldier, were killed in a spate of attacks across Iraqi capital Baghdad on Friday.",
u'source': u'menafn_iraq',
u'parsed_sents': ["""1	BAGHDAD:	BAGHDAD:	PUNCT	-LRB-	_	10	punct	_	_
2	At	at	ADV	RB	_	4	advmod	_	_
3	least	least	ADV	RBS	Degree=Sup	2	mwe	_	_
4	six	six	NUM	CD	NumType=Card	5	nummod	_	_
5	people,	people,	X	GW	_	10	nsubjpass	_	_
6	including	include	VERB	VBG	VerbForm=Ger	8	case	_	_
7	a	a	DET	DT	Definite=Ind|PronType=Art	8	det	_	_
8	soldier,	soldier,	X	GW	_	5	nmod	_	_
9	were	be	AUX	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	10	auxpass	_	_
10	killed	kill	VERB	VBN	Tense=Past|VerbForm=Part|Voice=Pass	0	root	_	_
11	in	in	ADP	IN	_	13	case	_	_
12	a	a	DET	DT	Definite=Ind|PronType=Art	13	det	_	_
13	spate	spate	NOUN	NN	Number=Sing	10	nmod	_	_
14	of	of	ADP	IN	_	15	case	_	_
15	attacks	attack	NOUN	NNS	Number=Plur	13	nmod	_	_
16	across	across	ADP	IN	_	19	case	_	_
17	Iraqi	iraqi	ADJ	JJ	Degree=Pos	19	amod	_	_
18	capital	capital	NOUN	NN	Number=Sing	19	compound	_	_
19	Baghdad	Baghdad	PROPN	NNP	Number=Sing	13	nmod	_	_
20	on	on	ADP	IN	_	21	case	_	_
21	Friday.	Friday.	PROPN	NNP	Number=Sing	13	nmod	_	_"""],
u'date': u'160626',
u'date_added': datetime.datetime(2016, 6, 26, 19, 0, 17, 640000),
u'_id': ObjectId('57702641172ab87eb7dc98fa')},
{u'language': u'english',
u'title': u'Soldiers, Policemen Fight Over Rice',
u'url': u'http://www.thetidenewsonline.com/2016/06/24/soldiers-policemen-fight-over-rice/',
u'stanford': 1,
u'content': """Iraqi officials often blame the attacks on the Daesh terrorist group, which overran vast swathes of territory in Iraq.""",
u'source': u'nigeria_tidenews',
u'parsed_sents': ["""1	Iraqi	iraqi	ADJ	JJ	Degree=Pos	2	amod	_	_
2	officials	official	NOUN	NNS	Number=Plur	4	nsubj	_	_
3	often	often	ADV	RB	_	4	advmod	_	_
4	blame	blame	VERB	VBP	Mood=Ind|Tense=Pres|VerbForm=Fin	0	root	_	_
5	the	the	DET	DT	Definite=Def|PronType=Art	6	det	_	_
6	attacks	attack	NOUN	NNS	Number=Plur	4	dobj	_	_
7	on	on	ADP	IN	_	10	case	_	_
8	the	the	DET	DT	Definite=Def|PronType=Art	10	det	_	_
9	Daesh	Daesh	PROPN	NNP	Number=Sing	10	compound	_	_
10	terrorist	terrorist	NOUN	NN	Number=Sing	6	nmod	_	_
11	group,	group,	PUNCT	,	_	10	punct	_	_
12	which	which	DET	WDT	PronType=Rel	15	det	_	_
13	overran	overran	ADV	RB	_	14	advmod	_	_
14	vast	vast	ADJ	JJ	Degree=Pos	15	amod	_	_
15	swathes	swathes	NOUN	NNS	Number=Plur	10	acl:relcl	_	_
16	of	of	ADP	IN	_	17	case	_	_
17	territory	territory	NOUN	NN	Number=Sing	15	nmod	_	_
18	in	in	ADP	IN	_	19	case	_	_
19	Iraq	Iraq	PROPN	NNP	Number=Sing	15	nmod	_	_"""],
u'date': u'160624',
u'date_added': datetime.datetime(2016, 6, 26, 19, 0, 18),
u'_id': ObjectId('57702642172ab87eb5dc98e9')}]


def test_petr_formatted_to_results():
    petr_ud_results = petrarch_ud.run_pipeline(formatted, write_output=False,
                                                 parsed=True)
    print(petr_ud_results)
    #assert petr_ud_results == correct1_results

if __name__ == "__main__":
    test_petr_formatted_to_results()

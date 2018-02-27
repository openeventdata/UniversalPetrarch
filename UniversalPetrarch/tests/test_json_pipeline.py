import sys
sys.path.append('..')
import datetime
from bson.objectid import ObjectId
import petrarch_ud
import PETRreader

formatted = [{u'language': u'english',
u'title': u'6 killed in attacks in Iraqi capital Friday',
u'url': u'http://www.menafn.com/1094827896/6-killed-in-attacks-in-Iraqi-capital-Friday?src=RSS',
u'stanford': 1,
u'content': "Ukraine ratified a sweeping agreement with the European Union on Tuesday.",
u'source': u'menafn_iraq',
u'parsed_sents': ["""1	Ukraine	Ukraine	PROPN	NNP	Number=Sing	2	nsubj	_	_
2	ratified	ratify	VERB	VBD	Mood=Ind|Tense=Past|VerbForm=Fin	0	root	_	_
3	a	a	DET	DT	Definite=Ind|PronType=Art	5	det	_	_
4	sweeping	sweeping	ADJ	JJ	Degree=Pos	5	amod	_	_
5	agreement	agreement	NOUN	NN	Number=Sing	2	dobj	_	_
6	with	with	ADP	IN	_	9	case	_	_
7	the	the	DET	DT	Definite=Def|PronType=Art	9	det	_	_
8	European	european	PROPN	NNP	Number=Sing	9	compound	_	_
9	Union	Union	PROPN	NNP	Number=Sing	5	nmod	_	_
10	on	on	ADP	IN	_	11	case	_	_
11	Tuesday	Tuesday	PROPN	NNP	Number=Sing	2	nmod	_	_
12	.	.	PUNCT	.	_	2	punct	_	_"""],
u'date': u'160626',
u'date_added': datetime.datetime(2016, 6, 26, 19, 0, 17, 640000),
u'_id': ObjectId('57702641172ab87eb7dc98fa')}]


def test_petr_formatted_to_results():
    petr_ud_results = petrarch_ud.run_pipeline(formatted, write_output=False,
                                                 parsed=True)
    print(petr_ud_results)
    #assert petr_ud_results == correct1_results

if __name__ == "__main__":
    test_petr_formatted_to_results()

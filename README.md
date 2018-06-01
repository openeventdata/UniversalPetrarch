# UniversalPetrarch
Language-agnostic political event coding using universal dependencies


## 1. Prerequisites

If your input data is just raw text, you need to preprocess the data to get
part-of-speech tags and dependency parsed trees. Those are the toolkits that
you will need to do preprocessing:

1. tokenizer. You will need Standford Corenlp to do sentence splitting and
   tokenization, which can be downloaded at
   (http://stanfordnlp.github.io/CoreNLP/download.html). For Arabic documents,
   you will need Stanford word segmenter as well. You can download via the
   [link](http://nlp.stanford.edu/software/segmenter.html#Download) and unzip
   it. Put the segmenter under directory
   UniversalPetrarch/preprocessing/segmenter/


2. POS tagger and dependency parser: You will need UDpipe. Its pre-compiled
   binary package (udpipe-1.0.0-bin.zip) can be downloaded at
   [here](https://github.com/ufal/udpipe/releases/tag/v1.0.0). Put it under
   directory UniversalPetrarch/preprocessing/udpipe-1.0.0/. To use UDpipe, a
   language model is needed, which can be downloaded at
   [here](https://ufal.mff.cuni.cz/udpipe#download). Put the model under
   directory UniversalPetrarch/preprocessing/udpipe-1.0.0/model



## Preprocessing 



### XML Input data format  

The input data should be in XML format, each element is an article or a sentence. Here are two examples:  

Each element of input data is an article:  

``` 
<Articles>
<Article date="20070301" id="AAW_ARB_20070301.0001" mongoId="57aa0f5a172ab843ff83630a" sentence="true" source="AAW">
<Text>
Some 2,500 mainly university students formed a human chain in Japanese characters spelling out "No War" in Osaka on Sunday to protest against the ongoing US-led military campaign in Iraq. "We cannot forgive this war," Miyako Fuji, 20, one of the rally's organisers told Jiji news agency. "I want to join together the feelings of each of us as individuals who oppose the war." Protesters, who exceeded the 2,000 expected to show up at the park at Osaka Castle in the city's downtown neighbourhood, carried placards that read "Stop war" and "Love and Peace" while forming the human chain after 3:00 pm (0600 GMT), Jiji said.
</Text>
</Article>
</Articles>
```

Each element of input data is a sentence:  

```
<Sentences>
<Sentence date = "20000715" id="AFP_ARB_20000715.0015_1" source = "afp" sentence = "True">
<Text>
Brazil and the United States are seeking to deepen a partnership in energy, especially by promoting biofuels and other alternatives to oil, US Deputy Secretary of Energy Jeffrey Kupfer said here Wednesday. 
</Text>
</Sentence>
</Sentences>
```

### Preprocessing Usage  

Shell scripts run_sentence.sh and run_document.sh are provided to do preprocessing of an English, Spanish or Arabic input file. 

```
run_sentence.sh INPUT_FILE LANGUAGE
run_document.sh INPUT_FILE LANGUAGE
```

Required Arguments:  

```
INPUT_FILE	name of the input XML file. 
LANGEUAGE	language of the input XML file. [EN|ES|AR]
```

Before running `run_sentence.sh` or `run_document.sh`, you need change the value of following parameters based on your situation

``` 
* SCRIPT: the location where you put folder "preprocess_scripts"
example:
SCRIPT=../scripts

* FILE: the location where you put the input file 
example:
FILE=../data/text

* STANFORD_SEG: the location where the stanford segmenter is saved
example:
STANFORD_SEG=segmenter

* STANFORD_CORENLP: the location where the Stanford CoreNLP is saved
example:
STANFORD_CORENLP=/users/ljwinnie/toolbox/stanford-corenlp-full-2015-01-29

* STANFORD_PROPERTY: the location where the property file used for Stanford CoreNLP is saved
example:
STANFORD_PROPERTY=/config/StanfordCoreNLP-english.properties

* udpipePath: the location where UDpipe is saved
example:
udpipePath=udpipe-1.0.0-bin 

```

### Example of preprocessing usage

`> ./run_document.sh Sample_english_doc.xml EN`

The result from running above command are files `Sample_english_doc.xml-sent.xml` and `Sample_english_doc-sent_parsed.xml`

`> ./run_sentence.sh Sample_english_sent.xml EN`

The result from running above command is file `Sample_english_sent_parsed.xml`


## UniversalPetrarch


UniversalPetrarch can accept the same JSON story format the other OEDA tools
use. For an example of this format, please see
[`UniveralPetrarch/tests/test_json_pipeline.py`](https://github.com/openeventdata/UniversalPetrarch/blob/master/UniversalPetrarch/tests/test_json_pipeline.py). This data can be fed to `petrarch_ud.run_pipeline` for processing.

Alternatively, UniversalPetrarch can be run directly on the XML files produced
in the pre-processing step:

```
python petrarch_ud.py batch -i INPUT_FILE -o OUTPUT_FILE -c CONFIG_FILE -d
```

Required Arguments:  

``-i INPUT_FILE	Filepath for the input XML file. ``  
``-o OUTPUT_FILE	Filepath for the output file.``

Optional Arguments:  

``-c CONFIG_FILE  Filepath for the PETRARCH configuration file. Defaults to PETR_config.ini``  
``-d turn on debug mode``

## validation.py

This program runs the functional validation tests for UniversalPetrarch. In default mode, both the program and the `validate/` directory should be at the same directory level as `petrarch_ud.py` and its various support files. To run, just use

``python validation.py``

Output from the program is in the file `Validation_output.txt`: this shows the results for each of the records as well as a summary of accuracy by category. The program also produces a `UD-PETR_Validate.log` file with the detail controlled by the `debug` parameter in the call to `utilities.init_logger()` in `__main__`. The format of the `PETR_Validate_records_2_02.xml` should be fairly obvious from the existing 250 or so cases; you can use the UD parser at http://lindat.mff.cuni.cz/services/udpipe/run.php to generate new cases (be sure to select the English model unless you want your parse to be in Czech...)

### Command line options

None : Read the validation file `PETR_Validate_records_2_02.xml` and dictionaries from `validate/` directory

``-d``: Read the validation file `PETR_Validate_records_2_02.debug.xml` and dictionaries from `validate/` directory

``-i <filename>``: Read the validation file `<filename>` from `data/text/` and read dictionaries from `data/dictionaries/`

`-p1`, `-p2`: see batch comparison discussion below

### Validation files

`validate/PETR_Validate_records_2_02.xml`: Primary validation records based on TABARI and PETRARCH-1 "Lord of the Rings" suite (around 250 cases); uses validation dictionaries in `validate/`.

`data/text/PETR2_GSR_validation.xml`: Validation records based on the PETRARCH-2 GSR test cases (74 cases); uses standard dictionaries in `data/dictionaries`.


### Benchmark results

`validation.py` simply calls routines within the UD-PETRARCH system itself and should require no modifications of that code. The current version was tested against the code on the master branch downloaded on 24-May-2018 and returned the results

```
Summary: PETR_Validate_records_2_02.xml at 180525-152003
Category     Records   Correct   Uncoded     Extra      Null      TP        FN        FP  
DEMO              35        28        21         7        58    57.14%    42.86%    20.00%
COMPOUND          35        67        20         6        79    77.01%    22.99%    17.14%
DATE              21        18         4         0        28    81.82%    18.18%     0.00%
ACTOR             11         3         8         3        11    27.27%    72.73%    27.27%
VERB              22        19         3         1        32    86.36%    13.64%     4.55%
PATTERN           25        17         8         7        26    68.00%    32.00%    28.00%
MODIFY            20        12         8         5        39    60.00%    40.00%    25.00%
SYNSET            52        36        16        16       100    69.23%    30.77%    30.77%
AGENT             23        13        11        11        17    54.17%    45.83%    47.83%
Total            244       213        99        56       390    68.27%    31.73%    22.95%
```

### Batch comparison coding

The `-p1` and `-p2` options can be used to run comparisons against a large number of records coded with PETRARCH-1 and -2. We've been using this internally to test against 20,000 records: those files are too extensive to post on GitHub under fair use exemptions, but an example of the set-up with a small number of texts is included.

At present, the name of the batch comparison directory is hard-coded as `P1-2_compare/` and this should be at the same level as the `validation.py` program. Inside that directory is a file named `P1-2_compare_dictionaries.xml` which contains the `<Environment>` section of the validation XML file. The directory should also contain a file `files.list.txt` which is a list of the files to be coded; this allows a large corpus to be segmented into a set of smaller and thus more manageable files. A line beginning with `===` in this file will cause the evaluation of further files to stop. 

These files are similar to the `<Sentences>` section of the XML file but contain records of the form

```
<Sentence date="20150219" id="5502e474-2a15-48e0-8c13-1e2a6d2f9337_2" category="COMPARE" evaluate="true">
<P1Event [['AUT', 'SRBGOV', '046'], ['SRBGOV', 'AUT', '046']]>
<P2Event [['SRBGOV', 'AUT', '010'], ['SRBGOV', 'MEAREB', '010']]>
<Text>
The Serbian foreign minister spoke in Vienna on Thursday in his role as OSCE chairperson, during
the winter session of the organization's parliamentary assembly.
</Text>
<Parse>
1	The	the	DET	DT	Definite=Def|PronType=Art	4	det	_	_
2	Serbian	Serbian	ADJ	JJ	Degree=Pos	4	amod	_	_
3	foreign	foreign	ADJ	JJ	Degree=Pos	4	amod	_	_
... [rest of the parse] ...
25	's	's	PART	POS	_	24	case	_	_
26	parliamentary	parliamentary	NOUN	NN	Number=Sing	27	compound	_	_
27	assembly	assembly	NOUN	NN	Number=Sing	21	nmod	_	_
28	.	.	PUNCT	.	_	5	punct	_	_
</Parse></Sentence>
```

The `<P1Event...` and `<P2Event...` lines contain a Python list of lists -- these are read using Python's `ast.literal_eval()` -- of the coded events in the order `[<source code>, <target code>, <event code>]`. If there are `<EventCoding...` records, these will be ignored. The `category` labels can be used in the same manner as they are in the other validation options, with the categories to be evaluated specified in the `<Include>...</Include>` line in `P1-2_compare_dictionaries.xml`.

Because of the large number of records usually evaluated when `-p1` or `-p2` are used, the coding information in the `Validation_output.txt` file is more abbreviated and includes only the sentence ID and the comparison of the codings, not the text, parse or internal coding information.

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


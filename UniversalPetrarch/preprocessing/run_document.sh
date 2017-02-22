#!/bin/bash

SCRIPT=/users/ljwinnie/Desktop/petrarch2/UniversalPetrarch/scripts
FILE=/users/ljwinnie/Desktop/petrarch2/UniversalPetrarch/data/text
STANFORD_SEG=/users/ljwinnie/Downloads/stanford-segmenter-2015-12-09
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
STANFORD_PROPERTY=/users/ljwinnie/Desktop/petrarch2/UniversalPetrarch/preprocessing/config/StanfordCoreNLP-spanish.properties
udpipePath=/users/ljwinnie/toolbox/udpipe-1.0.0-bin
languageModel=/users/ljwinnie/toolbox/udpipe-1.0.0-bin/model/spanish-ud-1.2-160523.udpipe
STANFORD_CORENLP=/users/ljwinnie/toolbox/stanford-corenlp-full-2015-01-29

FILENAME=$1

echo "Call Stanford CoreNLP to do sentence splitting..."
java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${STANFORD_PROPERTY} -file ${FILE}/$FILENAME -outputFormat text -outputDirectory ${FILE}

echo "Generate sentence xml file..."
python preprocess_doc.py ${FILE}/$FILENAME

SFILENAME=$FILENAME-sent.xml

echo "Call udpipe to do pos tagging and dependency parsing..."
${SCRIPT}/create_conll_corpus_from_text.pl ${FILE}/$FILENAME-sent.txt > ${FILE}/$FILENAME.conll
${udpipePath}/udpipe --tag --parse --outfile=${FILE}/$SFILENAME.conll.predpos.pred --input=conllu $languageModel ${FILE}/$FILENAME.conll 
# Creates $FILENAME.conll.predpos.pred



echo "Ouput parsed xml file..."
python generateParsedFile.py ${FILE}/$SFILENAME


rm ${FILE}/$FILENAME.out
rm ${FILE}/$FILENAME-sent.txt
rm ${FILE}/$FILENAME.conll
rm ${FILE}/$SFILENAME.conll.predpos.pred

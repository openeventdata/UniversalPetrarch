#!/bin/bash

SCRIPT=/users/ljwinnie/Desktop/petrarch2/UniversalPetrarch/scripts
FILE=/users/ljwinnie/Desktop/petrarch2/UniversalPetrarch/data/text
STANFORD_SEG=/users/ljwinnie/Downloads/stanford-segmenter-2015-12-09
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
STANFORD_PROPERTY=/users/ljwinnie/Desktop/petrarch2/UniversalPetrarch/preprocessing/config/StanfordCoreNLP-english.properties
udpipePath=/users/ljwinnie/toolbox/udpipe-1.0.0-bin
languageModel=/users/ljwinnie/toolbox/udpipe-1.0.0-bin/model/english-ud-1.2-160523.udpipe
STANFORD_CORENLP=/users/ljwinnie/toolbox/stanford-corenlp-full-2015-01-29

FILENAME=$1

echo "Prepare file for stanford CoreNLP"
python preprocess_sent.py ${FILE}/$FILENAME

echo "Call Stanford CoreNLP to do sentence splitting..."
java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${STANFORD_PROPERTY} -ssplit.newlineIsSentenceBreak always -file ${FILE}/$FILENAME.raw.txt -outputFormat text -outputDirectory ${FILE}

echo "Generate sentence xml file..."
python preprocess.py ${FILE}/$FILENAME


echo "Call udpipe to do pos tagging and dependency parsing..."
${SCRIPT}/create_conll_corpus_from_text.pl ${FILE}/$FILENAME.txt > ${FILE}/$FILENAME.conll
${udpipePath}/udpipe --tag --parse --outfile=${FILE}/$FILENAME.conll.predpos.pred --input=conllu $languageModel ${FILE}/$FILENAME.conll 

echo "Ouput parsed xml file..."
python generateParsedFile.py ${FILE}/$FILENAME

rm ${FILE}/$FILENAME.raw.txt
rm ${FILE}/$FILENAME.txt
rm ${FILE}/$FILENAME.raw.txt.out
rm ${FILE}/$FILENAME.conll
rm ${FILE}/$FILENAME.conll.predpos.pred

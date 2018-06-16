#!/bin/bash

SCRIPT=/Users/kld/Documents/workspace/EventData/UniversalPetrarch/UniversalPetrarch/scripts
FILE=/Users/kld/Documents/workspace/EventData/UniversalPetrarch/UniversalPetrarch/data/text
STANFORD_SEG=/Users/kld/Documents/workspace/EventData/UniversalPetrarch/UniversalPetrarch/preprocessing/segmenter
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
STANFORD_PROPERTY=/Users/kld/Documents/workspace/EventData/UniversalPetrarch/UniversalPetrarch/preprocessing/config/StanfordCoreNLP-english.properties
udpipePath=/Users/kld/Documents/workspace/EventData/UniversalPetrarch/UniversalPetrarch/preprocessing/udpipe-1.0.0-bin/bin-osx
languageModel=/Users/kld/Documents/workspace/EventData/UniversalPetrarch/UniversalPetrarch/preprocessing/udpipe-1.0.0/model/english-ud-1.2-160523.udpipe
STANFORD_CORENLP=/Users/kld/Documents/workspace/EventData/UniversalPetrarch/UniversalPetrarch/preprocessing/stanford-corenlp-full-2018-01-31

FILENAME=$1

echo "Call Stanford CoreNLP to do sentence splitting..."
java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${STANFORD_PROPERTY} -file ${FILE}/$FILENAME -outputFormat text -outputDirectory ${FILE}

echo "Generate sentence xml file..."
# echo "File Name : " ${FILE}/$FILENAME
python preprocess_doc.py ${FILE}/$FILENAME

SFILENAME=$FILENAME-sent.xml

echo "Call udpipe to do pos tagging and dependency parsing..."
${SCRIPT}/create_conll_corpus_from_text.pl ${FILE}/$FILENAME-sent.txt > ${FILE}/$FILENAME.conll
${udpipePath}/udpipe --tag --parse --outfile=${FILE}/$SFILENAME.conll.predpos.pred --input=conllu $languageModel ${FILE}/$FILENAME.conll 
# Creates $FILENAME.conll.predpos.pred



echo "Ouput parsed xml file..."
python generateParsedFile.py ${FILE}/$SFILENAME


# rm ${FILE}/$FILENAME.out
# rm ${FILE}/$FILENAME-sent.txt
# rm ${FILE}/$FILENAME.conll
# rm ${FILE}/$SFILENAME.conll.predpos.pred

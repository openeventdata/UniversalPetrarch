#!/bin/bash

SCRIPT=/Users/ahalterman/MIT/NSF_RIDIR/UniversalPetrarch/UniversalPetrarch/scripts
FILE=/Users/ahalterman/MIT/NSF_RIDIR/UniversalPetrarch/UniversalPetrarch  #/data/text
STANFORD_SEG=/Users/ahalterman/MIT/NSF_RIDIR/stanford-segmenter
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
STANFORD_PROPERTY=/Users/ahalterman/MIT/NSF_RIDIR/UniversalPetrarch/UniversalPetrarch/preprocessing/config/StanfordCoreNLP-english.properties
udpipePath=/Users/ahalterman/MIT/NSF_RIDIR/udpipe-1.0.0-bin/bin-osx
languageModel=/Users/ahalterman/MIT/NSF_RIDIR/udpipe-1.0.0-bin/models/english-ud-1.2-160523.udpipe
STANFORD_CORENLP=/Users/ahalterman/MIT/NSF_RIDIR/stanford-corenlp

FILENAME=$1

echo "Call Stanford CoreNLP to do sentence splitting..."
java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${STANFORD_PROPERTY} -file ${FILE}/$FILENAME -outputFormat text -outputDirectory ${FILE}/data/text/ 

echo "Generate sentence xml file..."
python2 preprocessing/preprocess_doc.py ${FILE}/$FILENAME

SFILENAME=$FILENAME-sent.xml

echo "Call udpipe to do pos tagging and dependency parsing..."
${SCRIPT}/create_conll_corpus_from_text.pl ${FILE}/$FILENAME-sent.txt > ${FILE}/$FILENAME.conll
${udpipePath}/udpipe --tag --parse --outfile=${FILE}/$SFILENAME.conll.predpos.pred --input=conllu $languageModel ${FILE}/$FILENAME.conll 
# Creates $FILENAME.conll.predpos.pred



echo "Ouput parsed xml file..."
python2 $FILE/preprocessing/generateParsedFile.py ${FILE}/$SFILENAME


rm ${FILE}/$FILENAME.out
rm ${FILE}/$FILENAME-sent.txt
rm ${FILE}/$FILENAME.conll
rm ${FILE}/$SFILENAME.conll.predpos.pred

#!/bin/bash

FILENAME=$1
language=$2

SCRIPT=../scripts
FILEPATH=text
STANFORD_SEG=segmenter
CLASSPATH=$STANFORD_SEG/stanford-segmenter-3.6.0.jar:$STANFORD_SEG/slf4j-api.jar
STANFORD_CORENLP=/users/ljwinnie/toolbox/stanford-corenlp-full-2017-06-09

udpipePath=udpipe-1.0.0



if [ "$language" = "AR" ] 
then
	languageModel=${udpipePath}/model/arabic-ud-1.4.udpipe
	STANFORD_PROPERTY=config/StanfordCoreNLP-arabic.properties
	
	echo "Call Stanford CoreNLP to do sentence splitting..."
	java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${STANFORD_PROPERTY} -file ${FILEPATH}/$FILENAME -outputFormat text -outputDirectory ${FILEPATH}

	echo "Generate sentence xml file..."
	python preprocess_doc.py ${FILEPATH}/$FILENAME

	SFILENAME=$FILENAME-sent.xml
	
	echo "Call Stanford Segmenter to do word segmenting..."
	java -mx1g -cp $CLASSPATH edu.stanford.nlp.international.arabic.process.ArabicSegmenter -loadClassifier $STANFORD_SEG/data/arabic-segmenter-atb+bn+arztrain.ser.gz -textFile ${FILEPATH}/$FILENAME-sent.txt > ${FILEPATH}/$SFILENAME.segmented

	${SCRIPT}/create_conll_corpus_from_text.pl ${FILEPATH}/$SFILENAME.segmented > ${FILEPATH}/$SFILENAME.conll

	rm ${FILEPATH}/$SFILENAME.segmented

	
else 

	if [ "$language" = "ES" ] 
	then
		languageModel=${udpipePath}/model/spanish-ud-1.2-160523.udpipe
		STANFORD_PROPERTY=config/StanfordCoreNLP-spanish.properties

	elif [ "$language" = "EN" ]
	then
		languageModel=${udpipePath}/model/english-ud-1.2-160523.udpipe
		STANFORD_PROPERTY=config/StanfordCoreNLP-english.properties

	fi
	
	echo "Call Stanford CoreNLP to do sentence splitting..."
	java -cp "$STANFORD_CORENLP/*" -Xmx4g edu.stanford.nlp.pipeline.StanfordCoreNLP -props ${STANFORD_PROPERTY} -file ${FILEPATH}/$FILENAME -outputFormat text -outputDirectory ${FILEPATH}

	echo "Generate sentence xml file..."
	python preprocess_doc.py ${FILEPATH}/$FILENAME

	SFILENAME=$FILENAME-sent.xml


	${SCRIPT}/create_conll_corpus_from_text.pl ${FILEPATH}/$FILENAME-sent.txt > ${FILEPATH}/$SFILENAME.conll
	
	
fi

echo "Call udpipe to do pos tagging and dependency parsing..."
echo "Udpipe model path: "
echo $languageModel
${udpipePath}/udpipe --tag --parse --outfile=${FILEPATH}/$SFILENAME.conll.predpos.pred --input=conllu $languageModel ${FILEPATH}/$SFILENAME.conll 
# Creates $FILENAME.conll.predpos.pred



echo "Ouput parsed xml file..."
python generateParsedFile.py ${FILEPATH}/$SFILENAME


rm ${FILEPATH}/$FILENAME.out
rm ${FILEPATH}/$FILENAME-sent.txt
rm ${FILEPATH}/$SFILENAME.conll
rm ${FILEPATH}/$SFILENAME.conll.predpos.pred

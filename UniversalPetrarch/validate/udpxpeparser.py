import sys
import os
import logging

import utilities

from ufal.udpipe import Model,Pipeline,ProcessingError


class UDpipeparser():

    def __init__(self, modeldir):

        self.modeldir = os.path.abspath(modeldir)
        self.model = Model.load(self.modeldir)
        self.error = ProcessingError()

        if not self.model:
            sys.stderr.write("Udpipe language model loading failed:"+self.modeldir)
            sys.exit(1)

        self.pipeline = Pipeline(self.model,"tokenize",Pipeline.DEFAULT,Pipeline.DEFAULT,"conllu")


    def udpipe_parse_sent(self, text):
        logger = logging.getLogger('petr_log')

        processed = self.pipeline.process(text,self.error)

        if self.error.occurred():
            raise ValueError(self.error.message)

        #print(processed)
        parsed = []
        for line in processed.split("\n"):
            if line.startswith("#"):
                continue
            parsed.append(line)

        #print(("\n").join(parsed))
        #input(" ")
        return ("\n").join(parsed)


    def udpipe_parse_events(self, events):
        logger = logging.getLogger('petr_log')

        #modeldir = os.path.abspath(PETRglobals.udpipe_modsel_dir)
    
        #self.model = Model.load(modeldir)
        #self.pipeline = Pipeline(model,"tokenize",Pipeline.DEFAULT,Pipeline.DEFAULT,"conllu")


        total = len(list(event_dict.keys()))
        logger.info("Starting parse of {} stories.'.format(total)")

        for i, key in enumerate(event_dict.keys()):
            if (i / float(total)) * 100 in [10.0, 25.0, 50, 75.0]:
                print('Parse is {}% complete...'.format((i / float(total)) * 100))
            for sent in event_dict[key]['sents']:
                logger.info('Udpipe parsing {}_{}...'.format(key, sent))
                sent_dict = event_dict[key]['sents'][sent]

                processed = self.pipeline.process(sent_dict['content'],self.error)

                if self.error.occurred():
                    #sys.stderr.write("An error occurred when running run_udpipe: ")
                    #sys.stderr.write(error.message)
                    #sys.stderr.write("\n")
                    raise ValueError(self.error.message)

                parsed = []
                for line in processed.split("\n"):
                    if line.startswith("#"):
                        continue
                    parsed.append(line)

                sent_dict['parsed'] = utilities._format_ud_parsed_str(("\n").join(parsed))
                print(sent_dict['parsed'])
                input("")

        #print('Done with UDpipe parse...\n\n')
        logger.info('Done with UDpipe parse.')
        return event_dict

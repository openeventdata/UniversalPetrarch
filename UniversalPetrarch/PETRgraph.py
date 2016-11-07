# -*- coding: utf-8 -*-


import networkx as nx
import PETRglobals
import PETRreader
import logging


class NounPhrase:

	def __init__(self,sentence,npIDs,headID,date):

		self.npIDs = npIDs
		self.text = ""
		self.head = None
		self.headID = headID
		self.meaning = ""
		self.date = date
		self.sentence = sentence
		self.matched_txt = None

	def get_meaning(self):
		npText = self.text.upper().split(" ")
		# matching the entire noun phrase string first in the actor or agent dictionary
		codes,roots,matched_txt = self.textMatching(npText)

		actorcodes, agentcodes = self.resolve_codes(codes)
		self.meaning = self.mix_codes(agentcodes, actorcodes)
		self.matched_txt = matched_txt

		return codes,roots,matched_txt

	def textMatching(self,npText):
		codes = []
		roots = []
		matched_txt = []

		index = 0
		while index < len(npText):
		    match = self.code_extraction(PETRglobals.ActorDict, npText[index:], 0)  # checking for actors
		    if match:
		        # --                print('NPgm-m-1:',match)
		        codes += match[0]
		        roots += match[3]
		        index += match[2]
		        matched_txt += [match[1]]
		# --                print('NPgm-1:',matched_txt)
		        continue

		    match = self.code_extraction(PETRglobals.AgentDict, npText[index:], 0)  # checking for agents
		    if match:
		        # --                print('NPgm-2.0:',roots)
		        codes += match[0]
		        roots += [['~']]
		        index += match[2]
		        matched_txt += [match[1]]
		        """print('NPgm-2:',matched_txt) # --
		        print('NPgm-2.1:',roots)"""
		        continue
		    index += 1

		return codes,roots,matched_txt

	def code_extraction(self,path, words, length, so_far=""):
		""" this method returns the code of noun phrase string in the actor or agent dictionary
		"""
		# --            print('NPgm-rec-lev:',len(getouterframes(currentframe(1))))  # --

		if words and words[0] in path:
		    match = self.code_extraction(path[words[0]], words[1:], length + 1, so_far + " " + words[0])
		    if match:
		        return match
		if '#' in path:
		    if isinstance(path["#"], list):
		        code = self.check_date(path['#'])
		        if not code is None:
		            # --                         print('NPgm-rec-1:',code)  # --
		            # --                         print('NPgm-rec-1.1:',path['#'][-1])
		            # 16.04.25 this branch always resolves to an actor;
		            # path['#'][-1] is the root string
		            return [code], so_far, length, [path['#'][-1]]
		    else:
		        # --                    print('NPgm-rec-2:',path['#'])
		        # 16.04.25 this branch always resolves to an agent
		        return [path['#']], so_far, length
		return False

	def resolve_codes(self, codes):
		"""
		Method that divides a list of mixed codes into actor and agent codes

		Parameters
		-----------
		codes: list
		       Mixed list of codes

		Returns
		-------
		actorcodes: list
		            List of actor codes

		agentcodes: list
		            List of actor codes

		"""
		if not codes:
			return [], []

		actorcodes = []
		agentcodes = []
		for code in codes:
			if not code:
			    continue
			if code.startswith("~"):
				agentcodes.append(code)
			else:
				actorcodes.append(code)
		return actorcodes, agentcodes

	def mix_codes(self, agents, actors):
		"""
		Combine the actor codes and agent codes addressing duplicates
		and removing the general "~PPL" if there's a better option.

		Parameters
		-----------
		agents, actors : Lists of their respective codes


		Returns
		-------
		codes: list
		       [Agent codes] x [Actor codes]

		"""

		# --        print('mc-entry',actors,agents)
		codes = set()
		mix = lambda a, b: a + b if not b in a else a
		actors = actors if actors else ['~']
		for ag in agents:
			if ag == '~PPL' and len(agents) > 1:
				continue
		#            actors = map( lambda a : mix( a[0], ag[1:]), actors)
			actors = map(lambda a: mix(a, ag[1:]), actors)

		# --        print('mc-1',actors)
		return filter(lambda a: a not in ['', '~', '~~', None], actors)

		# 16.04.25 hmmm, this is either a construct of utterly phenomenal
		# subtlety or else we never hit this code...
		codes = set()
		# --        print('WTF-1')
		for act in (actors if actors else ['~']):
			for ag in (agents if agents else ['~']):
				if ag == "~PPL" and len(agents) > 1:
					continue
				code = act
				if not ag[1:] in act:
					code += ag[1:]
				if not code in ['~', '~~', ""]:
					codes.add(code)
		return list(codes)


	def check_date(self,match):
		"""
		Method for resolving date restrictions on actor codes.

		Parameters
		-----------
		match: list
		       Dates and codes from the dictionary

		Returns
		-------
		code: string
		      The code corresponding to how the actor should be coded given the date


		Note <16.06.10 pas>
		-------------------
		In a very small set of cases involving a reflexive PRP inside a PP, the system can get into an infinite
		recursion where it first backs up a couple levels from the (PP, then this call to child.get_meaning() drops
		back down to the same point via the two child invocations in NounPhrase.get_meaning()

		            elif child.label == "PP":
		                m = self.resolve_codes(child.get_meaning())

		and in PrepPhrase.get_meaning()

		            self.meaning = self.children[1].get_meaning() if isinstance(self.children[1],NounPhrase) else ""

		which takes one back to the same point at one deeper level of recursion. These structures occurred about five times
		in a 20M sentence corpus, and I couldn't find any fix that didn't break something else, so I just trapped it
		here.

		There are a bunch of commented-out debugging prints remaining from this futile pursuit that could presumably be
		removed at some point.

		The full record for one of the offending cases is:

		<Sentence date = "20150824" id ="e35ef55a-fa30-4c34-baae-965dea33d8d8_3" source = "ANOTHER INFINITE RECURSION" sentence = "True">
		<Text>
		He started out at the bottom of the Hollywood rung, directed his own movie and managed to get noticed by Steven
		Spielberg himself to nab a tiny role in 1998s Saving Private Ryan .
		</Text>
		<Parse>
		(ROOT (S (S (NP (PRP He))
		(VP (VBD started) (PRT (RP out))
		(PP (IN at)
		(NP (NP (DT the) (NN bottom))
		(PP (IN of) (NP (DT the) (NNP Hollywood) ))))))
		(VP (VBD rung))
		(, ,)
		(S (VP
		(VP (VBD directed) (NP (PRP$ his) (JJ own) (NN movie))) (CC and)
		(VP (VBD managed) (S
		(VP (TO to)
		(VP (VB get)
		    (VP (VBN noticed)
		    (PP (IN by)
		        (NP (NNP Steven) (NNP Spielberg) (PRP himself))
		    )
		    (S  (VP (TO to)  (VP (VB nab)
		            (NP (NP (DT a) (JJ tiny) (NN role))
		            (PP (IN in)
		                (NP (NP (NNS 1998s))  (VP (VBG Saving)  (NP (JJ Private) (NNP Ryan))
		            ))))))))))))))
		(. .)))
		</Parse>
		</Sentence>

		"""
		
		code = None
		#try:
		for j in match:
			dates = j[1]
			date = []
			code = ""
			for d in dates:
				if d[0] in '<>':
					date.append(d[0] + str(PETRreader.dstr_to_ordate(d[1:])))
				else:
					date.append(str(PETRreader.dstr_to_ordate(d)))

			curdate = self.date
			
			if not date:
				code = j[0]
			elif len(date) == 1:
				if date[0][0] == '<':
					if curdate < int(date[0][1:]):
						code = j[0]
				else:
					if curdate >= int(date[0][1:]):
						code = j[0]
			else:
				if curdate < int(date[1]):
					if curdate >= int(date[0]):
						code = j[0]

			if code:
				return code
		
		#except Exception as e:
			# print(e)
		#	return code

		return code

class VerbPhrase:

	def __init__(self,sentence,vpIDs,headID):

		self.vpIDs = vpIDs
		self.text = ""
		self.head = None
		self.headID = headID
		self.meaning = ""
		self.sentence = sentence
		self.code = None
		self.passive = False




class Sentence:
	"""
    Holds the information of a sentence and its dependency tree.
    

    Methods
    -------
    
    __init__ : Initialization and instantiation
    
    str_to_graph: Reads UD parse into memory
	"""

	def __init__(self, parse, text, date):
		"""
        Initialization for Sentence classes.


        Parameters
        -----------

        parse: string
               parse tree read from input file

        date: string
        verbs: dictionary
               verb phrases in the sentence
               key is the headID in the dependency parse tree graph, value is a VerbPhrase object
        nouns: dictionary
               noun phrases in the sentence
               key is the headID in the dependency parse tree graph, value is a NounPhrase object
        
        udgraph: graph
        		 store denpendency parse tree as a graph


        Returns
        -------
        An instantiated Sentence object

        """
		self.parse = parse
		#self.agent = ""
		self.ID = -1
		#self.actor = ""
		self.date = date
		self.longlat = (-1,-1)
		self.verbs = {}
		self.nouns = {}
		self.triplets = {}
		self.rootID = ""
		self.txt = ""
		self.udgraph = self.str_to_graph(parse)
		#self.verb_analysis = {}
		self.events = {}
		self.metadata = {'nouns': [], 'verbs':[],'triplets':[]}
    

	def str_to_graph(self,str):
		dpgraph = nx.DiGraph()
		parsed = self.parse.split("\n")
		#print(parsed)

		dpgraph.add_node(0, token = 'ROOT')
		for p in parsed:
			temp = p.split("\t")

			#print(temp)
			dpgraph.add_node(int(temp[0]), token = temp[1], pos = temp[3])
			dpgraph.add_edge(int(temp[6]),int(temp[0]),relation = temp[7])

		return dpgraph

	def get_rootNode(self):
		for successor in self.udgraph.successors(0):
			if('relation' in self.udgraph[0][successor]):
				#print(self.udgraph[nodeID][successor]['relation'])
				if self.udgraph[0][successor]['relation'] in ['root']:
					self.rootID = successor

	def get_nounPharse(self, nounhead):
		npIDs=[]
		if(self.udgraph.node[nounhead]['pos'] in ['NOUN','ADJ','PROPN']):
			allsuccessors = nx.dfs_successors(self.udgraph,nounhead)

			flag = True
			parents = [nounhead]
			
			while len(parents)>0:
				temp = []
				'''ignore the conjunt nouns''' 
				for parent in parents:
					if parent in allsuccessors.keys():
						for child in allsuccessors[parent]:
							if parent!=nounhead or self.udgraph[parent][child]['relation'] not in ['cc','conj']:
								npIDs.append(child)
								temp.append(child)
				parents = temp
			
			'''
			for parent,child in allsuccessors.items():
				print(str(parent))
				print(child)
			'''		


			#for value in allsuccessors.values():
			#	npIDs.extend(value)
			#print(npIDs)

		npIDs.append(nounhead)
		npTokens =[]
		npIDs.sort()
		#print(npIDs)
		if self.udgraph.node[npIDs[0]]['pos']=='ADP':
			npIDs = npIDs[1:]
		for npID in npIDs:
			npTokens.append(self.udgraph.node[npID]['token'])
			
		nounPhrasetext = (' ').join(npTokens)

		np = NounPhrase(self,npIDs,nounhead,self.date)
		np.text = nounPhrasetext
		np.head = self.udgraph.node[nounhead]['token']
		return np

	def get_verbPhrase(self,verbhead):

		vpIDs = []
		for successor in self.udgraph.successors(verbhead):
			if('relation' in self.udgraph[verbhead][successor]):
				#print(self.udgraph[nodeID][successor]['relation'])
				if self.udgraph[verbhead][successor]['relation'].startswith('compound'):
					vpIDs.append(successor)
		vpIDs.append(verbhead)
		vpTokens =[]
		vpIDs.sort()
		for vpID in vpIDs:
			vpTokens.append(self.udgraph.node[vpID]['token'])

		verbPhrasetext = (' ').join(vpTokens)
		vp = VerbPhrase(self,vpIDs,verbhead)
		vp.text = verbPhrasetext
		vp.head = self.udgraph.node[verbhead]['token']
		return vp





	def get_source_target(self,nodeID):
		source = []
		target = []
		othernoun = []
		for successor in self.udgraph.successors(nodeID):
			#print(str(nodeID)+"\t"+str(successor)+"\t"+self.udgraph.node[successor]['pos'])
			if('relation' in self.udgraph[nodeID][successor]):
				#print(self.udgraph[nodeID][successor]['relation'])
				if(self.udgraph[nodeID][successor]['relation']=='nsubj'):
					#source.append(self.udgraph.node[successor]['token'])
					source.append(self.get_nounPharse(successor))
					source.extend(self.get_conj_noun(successor))
				elif(self.udgraph[nodeID][successor]['relation'] in ['dobj','iobj','nsubjpass']):
					target.append(self.get_nounPharse(successor))
					target.extend(self.get_conj_noun(successor))
				elif(self.udgraph[nodeID][successor]['relation'] in ['nmod']):
					othernoun.append(self.get_nounPharse(successor))
					othernoun.extend(self.get_conj_noun(successor))

		return source,target,othernoun

	def get_conj_noun(self,nodeID):
		""" method for extracting other conjunt nouns of this noun
			for example: Brazil and the United States, given the nodeID of Brazil, 
			it will return noun phrase object of "the United States"
		"""
		conj_noun = []
		for successor in self.udgraph.successors(nodeID):
			if(self.udgraph[nodeID][successor]['relation']=='conj'):
				conj_noun.append(self.get_nounPharse(successor))

		return conj_noun


	def get_phrases(self):
		for node in self.udgraph.nodes(data=True):
			nodeID = node[0]
			attrs = node[1]
			if 'pos' in attrs and attrs['pos']== 'VERB':
				#print(str(nodeID)+"\t"+attrs['pos']+"\t"+(" ").join(str(e) for e in self.udgraph.successors(nodeID)))
				#print(self.udgraph.successors(nodeID))
				verb = self.get_verbPhrase(nodeID)

				if verb.headID in self.verbs:
					raw_input("verb:"+self.verbs[verb.headID])
				else:
					self.verbs[verb.headID] = verb

				source,target,othernoun = self.get_source_target(nodeID)

				for s in source:
					if s.headID in self.nouns:
						raw_input("source:"+self.nouns[s.headID])
					else:
						self.nouns[s.headID] = s

				for t in target:
					if t.headID in self.nouns:
						raw_input("target:"+self.nouns[t.headID])
					else:
						self.nouns[t.headID] = t

				for o in othernoun:
					if o.headID in self.nouns:
						raw_input("othernoun:"+self.nouns[o.headID])
					else:
						self.nouns[o.headID] = o


				#for t in target: print(t)
				if len(source)==0 and len(target)>0:
					for t in target:
						triplet = ("-",t,verb,othernoun)
						self.metadata['triplets'].append(triplet)
						#self.triplet["-#"+str(t.headID)+"#"]
				elif len(source)>0 and len(target)==0:
					for s in source:
						triplet = (s,"-",verb,othernoun)
						self.metadata['triplets'].append(triplet)
				#elif len(source)==0 and len(target)==0:
				#	continue
				else:
					for s in source:
						for t in target:
							triplet = (s,t,verb,othernoun)
							self.metadata['triplets'].append(triplet)

				self.metadata['verbs'].append(verb)
				self.metadata['nouns'].extend(source)
				self.metadata['nouns'].extend(target)
				self.metadata['nouns'].extend(othernoun)


	def get_verb_code(self):
		logger = logging.getLogger('petr_log.PETRgraph')

		def match_phrase(path, noun_phrase):
			# Having matched the head of the phrase, this matches the full noun
			# phrase, if specified
			logger.debug("mphrase-entry")
			if not noun_phrase:
				return False
			for npID in filter(lambda a: a<noun_phrase.headID,noun_phrase.npIDs):				
				nptoken = self.udgraph.node[npID]['token'].upper()
				logger.debug(str(npID)+" "+nptoken)
				if nptoken in path:
					subpath = path[nptoken]
					match = reroute(subpath, lambda a: match_phrase(a, None))
					if match:
						return match
			return reroute(path, lambda a: match_phrase(a, noun_phrase))

		def match_noun(path, noun_phrase):
			logger.debug("mn-entry")
			
			if not isinstance(noun_phrase,basestring):
				logger.debug("noun:"+noun_phrase.head+"#"+noun_phrase.text)
				head = noun_phrase.head.upper()
				if head in path:
					subpath = path[head]
					logger.debug(head +" found in pattern dictionary")
					match = reroute(subpath, (lambda a: match_phrase(a, noun_phrase)) if isinstance(noun_phrase, NounPhrase) else None)
					if match:
						logger.debug(match)
						return match

		def match_prep(path, prep_phrase):
			print("mp-entry")


		def reroute(subpath, o1=match_noun, o2=match_noun,o3=match_prep, o4=match_noun, exit=1):
			#print('rr-entry:') # ,subpath
			if not o1:  # match_noun() can call reroute() with o1 == None; guessing returning False is the appropriate response pas 16.04.21
				return False
			if '-' in subpath:
				match = o1(subpath['-'])
				if match:
					#print('rr-- match')
					#print(match)
					return match

			if ',' in subpath:
				#print('rr-,')
				print(subpath[','])
				#match = o2(subpath[','])
				#if match:
					#print(match)
					#return match

			if '|' in subpath:
				#print('rr-|')
				print(subpath['|'])
				#match = o3(subpath['|'])
				#if match:
				#    print(match)
				#    return match

			if '*' in subpath:
				#print('rr-*')
				print(subpath['*'])
				#return subpath['*']
				#match = o4(subpath['*'])
				#if match:
				#	print(match)
				#	return match

			if '#' in subpath and exit:
				#print('rr-#')
				#print(subpath['#'])
				return subpath['#']

			#print('rr-False')
			return False



		for triple in self.metadata['triplets']:
			source = triple[0]
			target = triple[1]
			verb = triple[2]

			'''get code from verb dictionary'''
			logger.debug("finding code of verb:"+verb.text)					
			verbDictionary = PETRglobals.VerbDict['verbs']
			verbDictPath = verbDictionary
			code = None
			meaning = None
			matched_txt = []
			for verbtext in verb.text.upper().split(" "):
				if verbtext in verbDictPath:
					matched_txt.append(verbtext)
					verbDictPath = verbDictPath[verbtext]

			if "#" in verbDictPath:
				try:
					code = verbDictPath['#']['#']['code']
					meaning = verbDictPath['#']['#']['meaning']
				except:
					print("passing:"+verb.text)
					pass

					
			if code != None and meaning != None:	
				logger.debug(code+"\t"+meaning+"\t"+verb.text+"\t"+(" ").join(matched_txt))
			else:
				logger.debug("None code and none meaning")
			

			'''get code from pattern dictionary'''
			patternDictionary = PETRglobals.VerbDict['phrases']
			patternDictPath = patternDictionary
			matched_pattern = None
			if meaning in patternDictionary:
				patternDictPath = patternDictPath[meaning]
				logger.debug("processing source:")
				match = match_noun(patternDictPath,source)
				if match:
					code = match['code']
					matched_pattern = match['line']
					logger.debug("matched:"+code+"\t"+matched_pattern)

				if '*' in patternDictPath:
					patternDictPath = patternDictPath['*']

				logger.debug("processing target:")
				match = match_noun(patternDictPath,target)
				if match:
					code = match['code']
					matched_pattern = match['line']
					logger.debug("matched:"+code+"\t"+matched_pattern)

			tripleID = ('-' if isinstance(source,basestring) else str(source.headID)) + '#' + \
			           ('-' if isinstance(target,basestring) else str(target.headID)) + '#' + \
			           str(verb.headID)

			self.triplets[tripleID] = {}   
			self.triplets[tripleID]['triple']=triple
			self.triplets[tripleID]['verbcode'] = code
			self.triplets[tripleID]['matched_txt'] = matched_pattern if matched_pattern != None else (" ").join(matched_txt)
			self.triplets[tripleID]['meaning'] = meaning

			#raw_input("Press Enter to continue...")
	
	def get_events(self):
		logger = logging.getLogger('petr_log.PETRgraph')
		self.get_phrases()
		self.get_verb_code()
		self.get_rootNode()

		root_event = None
		root_eventID=""
		events = {}

		for tripleID, triple in self.triplets.items():
			logger.debug("check event:"+tripleID)
			source = triple['triple'][0]
			source_meaning=""
			if not isinstance(source,basestring):
				source.get_meaning() 
				source_meaning=source.meaning if source.meaning != None else ""
				logger.debug("source: "+ source.head+" code: "+(("#").join(source.meaning) if source.meaning != None else '-'))

			target = triple['triple'][1]
			target_meaning=""
			if not isinstance(target,basestring):
				target.get_meaning() 
				target_meaning=target.meaning if target.meaning != None else ""
				logger.debug("target: "+ target.head+" code: "+(("#").join(target.meaning) if target.meaning != None else '-'))

			verb = triple['triple'][2]

			if(verb.headID == self.rootID):
				root_event = (source_meaning,target_meaning,triple['verbcode'])
				root_eventID = tripleID
				logger.debug("Root verb:"+verb.text+" code:"+(triple['verbcode'] if triple['verbcode'] != None else "-"))
			else:
				logger.debug("verb:"+verb.text+" code:"+(triple['verbcode'] if triple['verbcode'] != None else "-"))
				if verb.headID in self.udgraph.neighbors(self.rootID):
					relation_with_root = self.udgraph[self.rootID][verb.headID]['relation']
					logger.debug("verb:"+verb.text+" relation:"+relation_with_root)

			event = (source_meaning,target_meaning,triple['verbcode'])
			logger.debug(event)

			events[tripleID]= event
			triple['event'] = event


		logger.debug("event transformation....")

		if root_event == None:
			logger.debug("root_event is None")
			return {}

		for tripleID, triple in self.triplets.items():
			verb = triple['triple'][2]

			if verb.headID in self.udgraph.neighbors(self.rootID):
					relation_with_root = self.udgraph[self.rootID][verb.headID]['relation']
					if relation_with_root in ['advcl','ccomp','xcomp']:
						current_event = (source_meaning,target_meaning,triple['verbcode'])
						event_before_transfer = (root_event[0],current_event,root_event[2])
						event_after_transfer = self.match_transform(event_before_transfer)
						logger.debug("event"+tripleID+"transformation:")
						logger.debug(event_after_transfer)
						for e in event_after_transfer:
							if isinstance(e,tuple) and not isinstance(e[1],tuple):
								if tripleID not in self.events:
									self.events[tripleID] = []
								self.events[tripleID].append(e)

		if(len(self.events)==0):
			self.events[root_eventID]=[]
			self.events[root_eventID].append(root_event)

		return self.events
			


	def match_transform(self, e):
		"""
		Check to see if the event e follows one of the verb transformation patterns
		specified at the bottom of the Verb Dictionary file.

		If the transformation is present, adjust the event accordingly.
		If no transformation is present, check if the event is of the form:

		            a ( b . Q ) P , where Q is not a top-level verb.

		    and then convert this to ( a b P+Q )

		Otherwise, return the event as-is.

		Parameters
		-----------
		e: tuple
		   Event to be transformed

		Returns
		-------
		t: list of tuples, matched_transformation if exist
		   List of modified events, since multiple events can come from one single event
		"""

		logger = logging.getLogger('petr_log.PETRgraph')

		def recurse(pdict, event, a2v={}, v2a={}):
			'''
			Parameters
			-----------
			a2v: dictionary
				 actor to variable mapping

			v2a: dictionary
				 variable to actor mapping

			'''
			logger.debug("recurse entry..")
            
			path = pdict
			if isinstance(pdict, list):
				#transfromation pattern is found
				line = pdict[1]
				path = pdict[0]
				verb = utilities.convert_code(path[2])[0] if not path[2] == "Q" else v2a["Q"]
				if isinstance(v2a[path[1]], tuple):
					results = []
					for item in v2a[path[1]]:
						results.append((list(v2a[path[0]]), item, verb))
					return results, line
				return [(list(v2a[path[0]]), v2a[path[1]], verb)], line

			if isinstance(event, tuple):
				actor = None if not event[0] else tuple(event[0])
				masks = filter(lambda a: a in pdict, [event[2], event[2] - event[2] % 0x10,
				                                      event[2] - event[2] % 0x100, event[2] - event[2] % 0x1000])
				logger.debug("actor:")
				logger.debug(actor)

				logger.debug("masks:")
				logger.debug(masks)

				if masks:
					path = pdict[masks[0]]
				elif -1 in pdict:
					v2a["Q"] = event[2]
					path = pdict[-1]
				else:
				    return False
			else:
				actor = event

			if actor in a2v:
				actor = a2v[actor]

			if not actor:
				actor = "_"

			if actor in path:
				return recurse(path[actor], event[1], a2v, v2a)
			elif not actor == '_':
				for var in sorted(path.keys())[::-1]:
					if var in v2a:
						continue
					if not var == '.':
						v2a[var] = actor
						a2v[actor] = var
					return recurse(path[var], event[1], a2v, v2a)
			return False

		logger.debug("match_transform entry...")

		try:            
			logger.debug(e)

			t = recurse(PETRglobals.VerbDict['transformations'], e)
			if t:
				logger.debug("transformation is present:")
				logger.debug("t:")
				logger.debug(t)
				return t
			else:
				logger.debug("no transformation is present:")
				if e[0] and e[2] and isinstance(e[1], tuple) and e[1][0] and not e[1][2] / (16 ** 3):
					logger.debug("the event is of the form: a ( b . Q ) P")
					if isinstance(e[1][0], list):
						results = []
						for item in e[1][0]:
							event = (e[0], item, utilities.combine_code(e[1][2], e[2]))
							logger.debug(event)
							results.append(event)
						return results
					
					event = (e[0], e[1][0], utilities.combine_code(e[2], e[1][2]))
					logger.debug(event)
					return [event]

		except Exception as ex:
			pass  # print(ex)
		return [e]













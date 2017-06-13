# -*- coding: utf-8 -*-


import networkx as nx
import PETRglobals
import PETRreader
import logging
import utilities
from sets import Set


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
		self.prep_phrase = []

	def get_meaning(self):
		logger = logging.getLogger('petr_log.NPgetmeaning')

		# 1. matching the main part of noun phrase string in the actor or agent dictionary
		# main part is extracted by removing all the prepositional phrases in the noun phrase

		npMainText = self.text
		for prep_phrase in self.prep_phrase:
			logger.debug("pphrase:"+prep_phrase.text)
			npMainText = npMainText.replace(prep_phrase.text,"")

		logger.debug("npMainText:"+npMainText)
		codes,roots,matched_txt = self.textMatching(npMainText.upper().split(" "))
		actorcodes, agentcodes = self.resolve_codes(codes)
		if actorcodes and agentcodes:
			# if both actor and agent are found, return the code
			self.meaning = self.mix_codes(agentcodes, actorcodes)
			self.matched_txt = matched_txt
			logger.debug("npMainText meaning:"+(",").join(self.meaning))
			return codes,roots,matched_txt


		# 2. if actor code is not found, matching the entire noun phrase string in the actor or agent dictionary
		npText = self.text.upper().split(" ")
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
			if code.startswith("~") or code.endswith("~"):
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
		

		def mix(a,b):
			if not b[1:] in a[-len(b[1:]):] and b[0] in '~':
				# handle agents such as "~GOV"
				return a + b[1:]
			elif not b[:-1] in a[0:len(b[:-1])] and b[-1] in '~':
				# handle agents such as "NGO~"
				return b[:-1] + a
			else:
				return a 

		codes = set()
		actors = actors if actors else ['~']
		for ag in agents:
			if ag == '~PPL' and len(agents) > 1:
				continue
		#            actors = map( lambda a : mix( a[0], ag[1:]), actors)
			actors = map(lambda a: mix(a, ag), actors)

		# --        print('mc-1',actors)
		for code in filter(lambda a: a not in ['', '~', '~~', None], actors):
			codes.add(code)
		return list(codes)

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
		
		finalcode = None
		matched_code = []

		#curdate = self.date
		#print("curdate:"+ str(curdate))
		#print(PETRreader.ordate_to_dstr(curdate))
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

			#print(("\n").join(date))
			#print("curdate:"+ str(self.date))
			
			if not date:
				nodatecode = j[0]
			elif len(date) == 1:
				if date[0][0] == '<':
					if curdate <= int(date[0][1:]):
						code = j[0]
						matched_code.append(j)
				else:
					if curdate >= int(date[0][1:]):
						code = j[0]
						matched_code.append(j)
			else:
				if curdate <= int(date[1]):
					if curdate >= int(date[0]):
						code = j[0]
						matched_code.append(j)

		if len(matched_code)>1:
			# two cases:
			# 1. embedded time restrictions: pick the smaller one
			# 2. multiple same restrictions: pick the first one
			best_date = ""
			best_code = ""
			best_date_range = float('inf')
			for item in matched_code:
				print("matched:"+item[0]+"\t"+(" ").join(item[1]))
				date = item[1]
				if len(date)==2:
					date_range = PETRreader.dstr_to_ordate(date[1]) - PETRreader.dstr_to_ordate(date[0])
					if date_range < best_date_range:
						best_date_range = date_range
						best_code = item[0]
						best_date = date

			finalcode = best_code
		elif len(matched_code)==1:
			finalcode = matched_code[0][0]

		if not finalcode and nodatecode:
			finalcode = nodatecode

		#print("finalcode:"+finalcode)
		return finalcode

class PrepPhrase:

	def __init__(self,sentence,ppIDs):

		self.ppIDs = ppIDs
		self.text = ""

class VerbPhrase:

	def __init__(self,sentence,vpIDs,headID):

		self.vpIDs = vpIDs
		self.text = ""
		self.head = None
		self.headID = headID
		self.verbIDs = []
		self.meaning = ""
		self.sentence = sentence
		self.code = None
		self.passive = False
		self.negative = False




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

		verbIDs: list
				 store the token ID of all verbs in the sentence

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
		self.rootID = []
		self.verbIDs = []
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
			dpgraph.add_node(int(temp[0]), token = temp[1], pos = temp[3], lemma = temp[2])
			dpgraph.add_edge(int(temp[6]),int(temp[0]),relation = temp[7])

		return dpgraph

	def get_rootNode(self):
		for successor in self.udgraph.successors(0):
			#if('relation' in self.udgraph[0][successor]):
				#print(self.udgraph[nodeID][successor]['relation'])
			if self.udgraph[0][successor]['relation'] in ['root']:
				root = successor
				#if the root node is a verb, add it directly and find whether any conjunctive verb exists
				if self.udgraph.node[root]['pos'] == 'VERB':
					self.rootID.append(root)
				
				else:
					#if the root node is not a verb
					#if a copula relation exist, find the verb connected to the root, and the verb as root
					for rsuccessor in self.udgraph.successors(root):
						if self.udgraph[root][rsuccessor]['relation'] != 'cop' and self.udgraph.node[rsuccessor]['pos'] == 'VERB':
							self.rootID.append(rsuccessor)
							#raw_input('root is not verb')

				#raw_input("roots: "+("#").join(str(x) for x in self.rootID))

				#found other root nodes from parallel relation ('conj' & 'parataxis')
				rsuccessors = self.udgraph.successors(root)
				for rsuccessor in rsuccessors:
					if self.udgraph[root][rsuccessor]['relation'] in ['conj','parataxis']:
						self.rootID.append(rsuccessor)

				#raw_input("roots: "+("#").join(str(x) for x in self.rootID))

		#raw_input("roots: "+("#").join(str(x) for x in self.rootID))
							


	def get_nounPharse(self, nounhead):
		"""
			Extract noun phrase given the head of the phrase

		"""
		logger = logging.getLogger('petr_log.getNP')
		npIDs=[]
		prep_phrase = []
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
							if parent==nounhead and self.udgraph[nounhead][child]['relation'] in ['nmod']:
								# extract prepositional phrases in a noun phrase
								#logger.debug(self.udgraph[nounhead][child]['relation'])
								#logger.debug(self.udgraph.node[nounhead])
								nmod_successors = nx.dfs_successors(self.udgraph,child)
								
								pptemp = []
								pptemp.append(child)
								for key in nmod_successors.keys():
									pptemp.extend(nmod_successors[key]) 
								pptemp.sort()
								logger.debug(pptemp)
								if self.udgraph.node[pptemp[0]]['pos'] in ['ADP']:

									prep_phrase.append(pptemp)

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
		#if self.udgraph.node[npIDs[0]]['pos']=='ADP':
		#	npIDs = npIDs[1:]
		for npID in npIDs:
			npTokens.append(self.udgraph.node[npID]['token'])
			
		nounPhrasetext = (' ').join(npTokens)

		np = NounPhrase(self,npIDs,nounhead,self.date)
		np.text = nounPhrasetext
		np.head = self.udgraph.node[nounhead]['token']

		logger.debug("noun:"+nounPhrasetext)
		for pp in prep_phrase:
			ppTokens = []
			for ppID in pp:
				ppTokens.append(self.udgraph.node[ppID]['token'])

			pptext = (' ').join(ppTokens)
			pphrase = PrepPhrase(self,pp)
			pphrase.text = pptext
			np.prep_phrase.append(pphrase)

			logger.debug(pptext)

		return np

	def get_nounPharses(self, nounhead):
		"""
			Extract noun phrases given the head of the phrase. 
			It is an extension of funciton get_nounPharse()
			1. If conjunctions are found in the modifiers, split the noun phrases into several noun phrases.
			e.g. "the ambassadors of Arnor, Osgiliath and Gondor"
			three noun phrases will be generated: the ambassadors of Arnor, the ambassadors of Osgiliath , the ambassadors of Gondor"
			
			2. apply modifier to each conjunctive nouns
			e.g. "Lawmakers and officials in Arnor"
			two noun phrases will be generated: lawmakers in Arnor, officials in Arnor
			
		"""
		nps = []

		logger = logging.getLogger('petr_log.getNP')

		nmod_conjs = {}
		npIDs=[]
		prep_phrase = []
		if(self.udgraph.node[nounhead]['pos'] in ['NOUN','ADJ','PROPN','PRON']):
			allsuccessors = nx.dfs_successors(self.udgraph,nounhead)

			flag = True
			parents = [nounhead]
			
			
			while len(parents)>0:
				temp = []
				'''ignore the conjunt nouns''' 
				parentgen = (parent for parent in parents if parent in allsuccessors.keys())
				for parent in parentgen:
					for child in allsuccessors[parent]:
						if parent!=nounhead or self.udgraph[parent][child]['relation'] not in ['cc','conj']:
							
							#find noun modifiers conjuctions
							if self.udgraph[parent][child]['relation'] in ['nmod']:
								nmod_conjs[child]=[]
								for nmodchild in allsuccessors[child]:
									if self.udgraph[child][nmodchild]['relation'] in ['conj']:
										nmod_conjs[child].append(nmodchild)

							temp.append(child)
							
							if parent in nmod_conjs and child in nmod_conjs[parent]:
								print(str(parent)+":"+str(child))
							else:
								npIDs.append(child)
	
				parents = temp

			parents = [nounhead]
			while len(parents)>0:
				temp = []

				parentgen = (parent for parent in parents if parent in allsuccessors.keys())

				for parent in parentgen:
					for child in allsuccessors[parent]:
						if parent!=nounhead or self.udgraph[parent][child]['relation'] not in ['cc','conj']:
							temp.append(child)

						if parent==nounhead and self.udgraph[nounhead][child]['relation'] in ['nmod']:
							# extract prepositional phrases in a noun phrase
							nmod_successors = nx.dfs_successors(self.udgraph,child)
							
							pptemp = []
							pptemp.append(child)
							for key in nmod_successors.keys():
								pptemp.extend(nmod_successors[key]) 
							pptemp.sort()
							logger.debug(pptemp)
							if self.udgraph.node[pptemp[0]]['pos'] in ['ADP']:

								prep_phrase.append(pptemp)

				parents = temp
			
			'''
			for parent,child in allsuccessors.items():
				print(str(parent))
				print(child)
			'''		
			'''	

			for nmod,nmodchildren in nmod_conjs.items():
				print("nmod:"+str(nmod)+":"+self.udgraph.node[nmod]['token'])
				for nmodchild in nmodchildren:
					print("nmodchild:"+str(nmodchild)+":"+self.udgraph.node[nmodchild]['token'])
			'''
				
				#if len(nmodchildren)>0:
					#raw_input(" compound nous")


		npIDs.append(nounhead)
		npTokens =[]
		npIDs.sort()
		#print(npIDs)
		#if self.udgraph.node[npIDs[0]]['pos']=='ADP':
		#	npIDs = npIDs[1:]
		for npID in npIDs:
			npTokens.append(self.udgraph.node[npID]['token'])
			
		nounPhrasetext = (' ').join(npTokens)
		logger.debug("noun:"+nounPhrasetext)

		np = NounPhrase(self,npIDs,nounhead,self.date)
		np.text = nounPhrasetext
		np.head = self.udgraph.node[nounhead]['token']

		for pp in prep_phrase:
			ppTokens = []
			for ppID in pp:
				ppTokens.append(self.udgraph.node[ppID]['token'])

			pptext = (' ').join(ppTokens)
			pphrase = PrepPhrase(self,pp)
			pphrase.text = pptext
			np.prep_phrase.append(pphrase)

			logger.debug(pptext)

		nps.append(np)

		for nmod,nmodchildren in nmod_conjs.items():
			logger.debug("nmod:"+str(nmod)+":"+self.udgraph.node[nmod]['token'])
			for nmodchild in nmodchildren:
				logger.debug("nmodchild:"+str(nmodchild)+":"+self.udgraph.node[nmodchild]['token'])
				conjnpIDs=[]
				conjnpTokens=[]
				for npID in npIDs:
					if npID in self.udgraph[nmod] and self.udgraph[nmod][npID]['relation'] in ['name',"compound"]:
						continue

					if npID == nmod:
						conjnpIDs.append(nmodchild)
						conjnpTokens.append(self.udgraph.node[nmodchild]['token'])
					else:
						conjnpIDs.append(npID)
						conjnpTokens.append(self.udgraph.node[npID]['token'])
			
				conjnounPhrasetext = (' ').join(conjnpTokens)
				logger.debug("conjnoun:"+conjnounPhrasetext)

				conjnp = NounPhrase(self,conjnpIDs,nounhead,self.date)
				conjnp.text = conjnounPhrasetext
				conjnp.head = self.udgraph.node[nounhead]['token']
				conjnp.prep_phrase = np.prep_phrase
				nps.append(conjnp)

		self.metadata['nouns'].extend(nps)
		return nps

	def get_verbPhrase(self,verbhead):

		vpIDs = []
		self.verbIDs.append(verbhead)

		vp = VerbPhrase(self,vpIDs,verbhead)
		vp.verbIDs.append(verbhead)

		for successor in self.udgraph.successors(verbhead):
			if('relation' in self.udgraph[verbhead][successor]):
				#print(self.udgraph[nodeID][successor]['relation'])
				if self.udgraph[verbhead][successor]['relation'].startswith('compound'):
					vpIDs.append(successor)
				if self.udgraph[verbhead][successor]['relation'].startswith('neg'):
					vp.negative = True
				'''
				if self.udgraph[verbhead][successor]['relation'].startswith('advcl'):
					# check the to + verb structure
					if self.udgraph.node[successor]['pos']=="VERB":
						for ss in self.udgraph.successors(successor):
							if self.udgraph[successor][ss]['relation'].startswith('mark') and self.udgraph.node[ss]['pos']=='PART':
								vpIDs.append(successor)
								vpIDs.append(ss)
								self.verbIDs.append(successor)
								vp.verbIDs.append(successor)
				'''




		vpIDs.append(verbhead)
		vpTokens =[]
		vpIDs.sort()
		for vpID in vpIDs:
			vpTokens.append(self.udgraph.node[vpID]['token'])

		verbPhrasetext = (' ').join(vpTokens)
		
		vp.text = verbPhrasetext
		vp.head = self.udgraph.node[verbhead]['token']
		
		return vp





	def get_source_target(self,verbIDs):
		logger = logging.getLogger("petr_log.get_source_target")
		def resolve_pronoun(pronounID,verbID,pronounrole):
			predecessors = self.udgraph.predecessors(verbID)
			for predecessor in predecessors:
				if 'relation' in self.udgraph[predecessor][verbID] and self.udgraph[predecessor][verbID]['relation'] in ['ccomp']: 
					logger.debug("resolve pronoun: found the governer of ccomp verb:"+ self.udgraph.node[predecessor]['token'])
					psource,ptarget,pothernoun = self.get_source_target([predecessor])
					if pronounrole in ['source']:
						logger.debug("resolve pronoun: found resolved source:"+str(len(psource)))
						return psource
						
			return []
						
						
					
					
		source = []
		target = []
		othernoun = []
		for verbID in verbIDs:
			for successor in self.udgraph.successors(verbID):
				#print(str(verbID)+"\t"+str(successor)+"\t"+self.udgraph.node[successor]['pos'])
				if('relation' in self.udgraph[verbID][successor]):
					#print(self.udgraph[nodeID][successor]['relation'])
					if(self.udgraph[verbID][successor]['relation']=='nsubj'):
						#source.append(self.get_nounPharse(successor))
						if self.udgraph.node[successor]['pos'] in ['PRON']:
							source.extend(resolve_pronoun(successor,verbID,'source'))
						else:
							source.extend(self.get_nounPharses(successor))
							source.extend(self.get_conj_noun(successor))

					elif(self.udgraph[verbID][successor]['relation'] in ['dobj','iobj','nsubjpass']):
						#target.append(self.get_nounPharse(successor))
						target.extend(self.get_nounPharses(successor))
						target.extend(self.get_conj_noun(successor))
						if self.udgraph[verbID][successor]['relation'] in ['nsubjpass']:
							self.verbs[verbID].passive = True

					elif(self.udgraph[verbID][successor]['relation'] in ['nmod']):
						#othernoun.append(self.get_nounPharse(successor))
						othernoun.extend(self.get_nounPharses(successor))
						othernoun.extend(self.get_conj_noun(successor))

		return source,target,othernoun

	def get_conj_noun(self,nodeID):
		""" method for extracting other conjunt nouns of this noun
			for example: Brazil and the United States, given the nodeID of Brazil, 
			it will return noun phrase object of "the United States"

			apply modifier to each conjunctive nouns
			e.g. "Lawmakers and officials in Arnor"
			two noun phrases will be generated: lawmakers in Arnor, officials in Arnor
		"""
		conj_noun = []
		for successor in self.udgraph.successors(nodeID):
			if(self.udgraph[nodeID][successor]['relation']=='conj'):
				#conj_noun.append(self.get_nounPharse(successor))
				conjnouns = self.get_nounPharses(successor)

				for noun in self.metadata['nouns']:
					#find predecessors, move the modifier from its predecessor
					if noun.headID == nodeID:
						for conjnoun in conjnouns:
							conjnoun.prep_phrase.extend(noun.prep_phrase)
							for prep in conjnoun.prep_phrase:
								conjnoun.npIDs.extend(prep.ppIDs)

							tempprepset = set(conjnoun.prep_phrase)
							conjnoun.prep_phrase = list(tempprepset)

							tempIDset = set(conjnoun.npIDs)
							conjnoun.npIDs = list(tempIDset)
							conjnoun.npIDs.sort()
							#print(conjnoun.prep_phrase)
							npTokens =[]
							for npID in conjnoun.npIDs:
								npTokens.append(self.udgraph.node[npID]['token'])

							nntext = (' ').join(npTokens)
							conjnoun.text = nntext

				conj_noun.extend(conjnouns)

		return conj_noun


	def get_phrases(self):
		logger = logging.getLogger("petr_log.getPhrase")
		for node in self.udgraph.nodes(data=True):
			nodeID = node[0]
			attrs = node[1]

			#if nodeID in self.verbIDs:
				#continue

			if 'pos' in attrs and attrs['pos']== 'VERB':

				#print(str(nodeID)+"\t"+attrs['pos']+"\t"+(" ").join(str(e) for e in self.udgraph.successors(nodeID)))
				#print(self.udgraph.successors(nodeID))
				verb = self.get_verbPhrase(nodeID)

				#if verb.headID in self.verbs:
				#	raw_input("verb:"+self.verbs[verb.headID].text)
				#else:
				#	self.verbs[verb.headID] = verb
				if verb.headID not in self.verbs:
					self.verbs[verb.headID] = verb
					
				source,target,othernoun = self.get_source_target(verb.verbIDs)

				#check for conjuncting verbs
				predecessors = self.udgraph.predecessors(verb.headID)
				for predecessor in predecessors:
					if 'relation' in self.udgraph[predecessor][verb.headID] and self.udgraph[predecessor][verb.headID]['relation'] in ['conj']:
						logger.debug("found conj verb:"+ self.udgraph.node[predecessor]['token'])
						psource,ptarget,pothernoun = self.get_source_target([predecessor])
						source.extend(psource)

				#find the subject for 'xcomp' relation
				#An open clausal complement (xcomp) of a verb or an adjective is a predicative or clausal complement without its own subject. 
				#The reference of the subject is necessarily determined by an argument external to the xcomp 
				#(normally by the object of the next higher clause, if there is one, or else by the subject of the next higher clause).
				for predecessor in predecessors:
					if 'relation' in self.udgraph[predecessor][verb.headID] and self.udgraph[predecessor][verb.headID]['relation'] in ['xcomp']: 
						logger.debug("found the governer of xcomp verb:"+ self.udgraph.node[predecessor]['token'])
						psource,ptarget,pothernoun = self.get_source_target([predecessor])
						if len(ptarget)>0:
							source.extend(ptarget)
						elif len(psource)>0:
							source.extend(psource)
						#raw_input("find xcomp relation")					

				#find targets from the subjects of subordinate clause
				for successor in self.udgraph.successors(verb.headID):
					if 'relation' in self.udgraph[verb.headID][successor] and self.udgraph[verb.headID][successor]['relation'] in ['ccomp']:
						cverb = self.get_verbPhrase(successor)
						#if cverb in self.verbs:
							#raw_input("verb:"+self.verbs[successor])
							#raw_input("verb:"+self.verbs[successor].text)
						#else:
						#	self.verbs[successor] = cverb
							
						if cverb not in self.verbs:
							self.verbs[successor] = cverb	
							
						logger.debug("found the ccomp verb:"+ self.udgraph.node[successor]['token'])
						ssource,starget,sothernoun = self.get_source_target([successor])
						if len(ssource)>0:
							target.extend(ssource)
					
				#for t in target: print(t)
				if len(source)==0 and len(target)>0:
					for t in target:
						triplet = ("-",t,verb)
						self.metadata['triplets'].append(triplet)
						#self.triplet["-#"+str(t.headID)+"#"+str(verb.headID)] = triplet
				elif len(source)>0 and len(target)==0:
					for s in source:
						triplet = (s,"-",verb)
						self.metadata['triplets'].append(triplet)
				else:
					for s in source:
						for t in target:
							triplet = (s,t,verb)
							self.metadata['triplets'].append(triplet)

				#othernoun are usually prepositional phrase, combine the verb and preposition as the new verb phrase
				#make the noun phrase in prepositional phrase as new target
				#improvement is still needed			
				if len(othernoun)>0:
					for o in othernoun:
						if self.udgraph.node[o.npIDs[0]]['pos']=='ADP':
							vpTokens = []
							vpIDs = []
							vpIDs.extend(verb.vpIDs)
							vpIDs.append(o.npIDs[0])
							vpIDs.sort()

							newverb = VerbPhrase(self,vpIDs,verb.headID)
							for vpID in vpIDs:
								vpTokens.append(self.udgraph.node[vpID]['token'])

							verbPhrasetext = (' ').join(vpTokens)
							
							newverb.text = verbPhrasetext
							newverb.head = verb.head
							newverb.passive = verb.passive
							newverb.negative = verb.negative
							logger.debug("construct new vp:"+newverb.text)
						
							newnoun = NounPhrase(self,o.npIDs[1:],o.headID,o.date)
							targetTokens = []
							for tID in newnoun.npIDs:
								targetTokens.append(self.udgraph.node[tID]['token'])
							newnoun.text = (' ').join(targetTokens)
							newnoun.head = o.head
							newnoun.prep_phrase = o.prep_phrase
							if newverb.passive == False:
								newtarget = newnoun
								logger.debug("construct new target:"+newtarget.text)

								if len(source)==0:
									triplet = ("-",newtarget,newverb)
									self.metadata['triplets'].append(triplet)
								else:
									for s in source:
										triplet = (s,newtarget,newverb)
										self.metadata['triplets'].append(triplet)
										
							else:
								newsource = newnoun
								logger.debug("construct new source:"+newsource.text)

								if len(target)==0:
									triplet = (newsource,'-',newverb)
									self.metadata['triplets'].append(triplet)
								else:
									for t in target:
										triplet = (newsource,t,newverb)
										self.metadata['triplets'].append(triplet)

							# if the noun has conjunction, build a new triplet using the verb and conjunction 
							for successor in self.udgraph.successors(o.headID):
								if 'relation' in self.udgraph[o.headID][successor] and self.udgraph[o.headID][successor]['relation'] in ['conj']:
									
									newconjnpids = o.npIDs[1:]
									headidx = newconjnpids.index(o.headID)
									newconjnpids[headidx] = successor
									newconjnpids.sort()
									newconjnoun = NounPhrase(self,newconjnpids,successor,o.date)
									tokens = []
									for tID in newconjnoun.npIDs:
										tokens.append(self.udgraph.node[tID]['token'])
									newconjnoun.text = (' ').join(tokens)
									newconjnoun.head = self.udgraph.node[newconjnoun.headID]['token']
									newconjnoun.prep_phrase = o.prep_phrase

									if newverb.passive == False:
										newtarget = newconjnoun
										logger.debug("construct new target:"+newtarget.text)

										if len(source)==0:
											triplet = ("-",newtarget,newverb)
											self.metadata['triplets'].append(triplet)
										else:
											for s in source:
												triplet = (s,newtarget,newverb)
												self.metadata['triplets'].append(triplet)
										
									else:
										newsource = newconjnoun
										logger.debug("construct new source:"+newsource.text)

										if len(target)==0:
											triplet = (newsource,'-',newverb)
											self.metadata['triplets'].append(triplet)
										else:
											for t in target:
												triplet = (newsource,t,newverb)
												self.metadata['triplets'].append(triplet)

									#raw_input("found conjective other noun")
				self.metadata['verbs'].append(verb)
				#self.metadata['nouns'].extend(source)
				#self.metadata['nouns'].extend(target)
				#self.metadata['nouns'].extend(othernoun)

		


	def get_verb_code(self):
		logger = logging.getLogger('petr_log.PETRgraph')

		def match_phrase(path, noun_phrase):
			# Having matched the head of the phrase, this matches the full noun
			# phrase, if specified
			logger.debug("mphrase-entry")
			if not noun_phrase:
				return False

			cfound = True
			match = ""
			for npID in filter(lambda a: a!=noun_phrase.headID,noun_phrase.npIDs):				
				nptoken = self.udgraph.node[npID]['token'].upper()
				nplemma = self.udgraph.node[npID]['lemma'].upper()

				logger.debug(str(npID)+" "+nptoken+" "+str(cfound))

				barfound = False
				if '-' in path and cfound:
					path = path['-']
					barfound = True
				if '|' in path:
					path = path['|']

				logger.debug(path)
				if nptoken in path:
					subpath = path[nptoken]
					logger.debug(subpath)
					
					cfound = True	
					match = reroute(subpath, lambda a: match_phrase(a, None))
					#if match:
						#return match

					path = subpath
				elif nplemma in path:
					subpath = path[nplemma]
					logger.debug(subpath)
					
					cfound = True	
					match = reroute(subpath, lambda a: match_phrase(a, None))
					#if match:
						#return match

					path = subpath
				else:
					cfound = False

			if match:
				return match

			return reroute(path, lambda a: match_phrase(a, noun_phrase))

		#def match_continus_noun(path,noun_phrase,start_ID):


		def match_noun(path, noun_phrase):
			logger.debug("mn-entry")
			
			if not isinstance(noun_phrase,basestring):
				logger.debug("noun:"+noun_phrase.head+"#"+noun_phrase.text)
				head = noun_phrase.head.upper()
				headlemma = self.udgraph.node[noun_phrase.headID]['lemma'].upper()
				if head in path:
					subpath = path[head]
					logger.debug(head +" found in pattern dictionary")
					match = reroute(subpath, (lambda a: match_phrase(a, noun_phrase)) if isinstance(noun_phrase, NounPhrase) else None)
					if match:
						logger.debug(match)
						return match
				elif headlemma in path:
					subpath = path[headlemma]
					logger.debug(headlemma +" found in pattern dictionary (lemma)")
					match = reroute(subpath, (lambda a: match_phrase(a, noun_phrase)) if isinstance(noun_phrase, NounPhrase) else None)
					if match:
						logger.debug(match)
						return match
			
			if "$" in path:
				#print("$ "+path)
				temppath = path["$"]
				if "#" in temppath:
					match = temppath['#']
					if match:
						logger.debug(match)
						return match

			if "#" in path:
				match = path['#']
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

			if '$' in subpath:
				print('rr$ found')
				match = reroute(subpath['$'],True)
				if match:
					print('rr$ match')
					return match

			if ',' in subpath:
				#print('rr-,')
				print(subpath[','])
				match = reroute(subpath[','],True)
				if match:
					print(match)
					return match

			if '|' in subpath:
				#print('rr-|')
				print(subpath['|'])
				#raw_input("match preposition")
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

		def match_lower(path,verb,target):
			match = False
			if '*' in path:
				path = path['*']
				logger.debug("'*' matched")

			if "$" in path:
				path = path["$"]
				logger.debug("'$' matched")

			if len(verb.vpIDs)>1:
				logger.debug("matching prep:")
				temppatternDictPath = path
				found = False
				if '|' in temppatternDictPath:
					logger.debug("'|' matched")
					temppatternDictPath = temppatternDictPath['|']
					for vpID in verb.vpIDs:
						if(vpID <= verb.headID):
							continue
						if self.udgraph.node[vpID]['pos']=='ADP' and self.udgraph.node[vpID]['token'].upper() in temppatternDictPath:
							temppatternDictPath = temppatternDictPath[self.udgraph.node[vpID]['token'].upper()]
							logger.debug("prep matched:"+self.udgraph.node[vpID]['token'].upper())
							found = True

				if found==True:
					path = temppatternDictPath
					if '#' in path:
						path = path['#']
						match = path
					if '-' in path:
						path = path['-']


				if match:
					code = match['code']
					matched_pattern = match['line']
					logger.debug("matched:"+code+"\t"+matched_pattern)

			logger.debug("processing target:")
			targetmatch = match_noun(path,target)

			if targetmatch:
				return targetmatch
			elif match:
				return match
			else:
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

			codes = []
			meanings = []
			matched_txts = []

			verbtokens = verb.text.upper().split(" ")
			for vidx in range(0,len(verbtokens)):
				verbtext = verbtokens[vidx]
				logger.debug("match vp token:"+verbtext)
				if verbtext in verbDictPath:
					matched_txt = []
					tempverbDictPath = verbDictPath[verbtext]
					matched_txt.append(verbtext)


					for j in range(vidx,len(verbtokens)):
						if verbtokens[j] in tempverbDictPath:
							tempverbDictPath = tempverbDictPath[verbtokens[j]]
							matched_txt.append(verbtokens[j])


					if "#" in tempverbDictPath:
						try:
							code = tempverbDictPath['#']['#']['code']
							meaning = tempverbDictPath['#']['#']['meaning']
						except:
							print("passing:"+verb.text)
							pass

					if (code != None and meaning != None):
						codes.append(code)
						meanings.append(meaning)
						matched_txts.append(matched_txt)

			if(len(verbtokens)>1):
				logger.debug(codes)
				logger.debug(meanings)
				logger.debug(matched_txts)
				#raw_input("verb pharse has length large than 1")

					
			if code != None and meaning != None:	
				logger.debug(code+"\t"+meaning+"\t"+verb.text+"\t"+(" ").join(matched_txt)+"\t"+str(len(verb.vpIDs)))
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

				pairmatch = False
				if '%' in patternDictPath: 
					temppatternDictPath = patternDictPath['%']
					logger.debug("'%' matched")
					pairmatch = match_lower(temppatternDictPath,verb,target)
					if pairmatch:
						code = pairmatch['code']
						matched_pattern = pairmatch['line']
						logger.debug("pair matched:"+code+"\t"+matched_pattern)

				if '+' in patternDictPath: 
					temppatternDictPath = patternDictPath['+']
					logger.debug("'+' matched")
					match = match_lower(temppatternDictPath,verb,target)
					if match:
						code = match['code']
						matched_pattern = match['line']
						logger.debug("matched:"+code+"\t"+matched_pattern)

				lowermatch = match_lower(patternDictPath,verb,target)
				
				if pairmatch and "(" in pairmatch['line']:
					match = pairmatch
				elif lowermatch and "(" in lowermatch['line']:
					match = lowermatch
				elif pairmatch:
					match = pairmatch
				elif lowermatch:
					match = lowermatch


				'''
				if '*' in patternDictPath:
					patternDictPath = patternDictPath['*']
					logger.debug("'*' matched")

				
				if len(verb.vpIDs)>1:
					logger.debug("matching prep:")
					temppatternDictPath = patternDictPath
					found = False
					if '|' in temppatternDictPath:
						logger.debug("'|' matched")
						temppatternDictPath = temppatternDictPath['|']
						for vpID in verb.vpIDs:
							if(vpID <= verb.headID):
								continue
							if self.udgraph.node[vpID]['pos']=='ADP' and self.udgraph.node[vpID]['token'].upper() in temppatternDictPath:
								temppatternDictPath = temppatternDictPath[self.udgraph.node[vpID]['token'].upper()]
								logger.debug("prep matched:"+self.udgraph.node[vpID]['token'].upper())
								found = True

					if found==True:
						patternDictPath = temppatternDictPath
						if '#' in patternDictPath:
							patternDictPath = patternDictPath['#']
							match = patternDictPath
						if '-' in patternDictPath:
							patternDictPath = patternDictPath['-']

					if match:
						code = match['code']
						matched_pattern = match['line']
						logger.debug("matched:"+code+"\t"+matched_pattern)

						
				logger.debug("processing target:")
				match = match_noun(patternDictPath,target)
				'''
				if match:
					code = match['code']
					matched_pattern = match['line']
					#switch source and target
					newsource = '-'
					newtarget = '-'

					if not verb.passive and "+" in matched_pattern and matched_pattern.index("+") < matched_pattern.index("*"):
						newsource = target
						logger.debug("+ in pattern, switch target to source")

					if not verb.passive and "$" in matched_pattern and matched_pattern.index("$") > matched_pattern.index("*"):
						newtarget = source
						logger.debug("$ in pattern, switch source to target")

					logger.debug("matched:"+code+"\t"+matched_pattern)

					source = newsource if not isinstance(newsource,basestring) else source
					target = newtarget if not isinstance(newtarget,basestring) else target
					

			tripleID = ('-' if isinstance(source,basestring) else str(source.headID)) + '#' + \
			           ('-' if isinstance(target,basestring) else str(target.headID)) + '#' + \
			           str(verb.headID)+"#"+str(len(self.triplets))
			newtriple = (source,target,verb)

			if code != None:
				if len(code.split(":"))==2:
					active_code, passive_code = code.split(":")
					if verb.passive == True:
						verbcode = passive_code
					else:
						verbcode = active_code
				else:
					verbcode = code
				if verb.negative == True:
					#raw_input("before negated:"+verbcode)
					if int(verbcode)<=200: 
					#validation verbs have codes over 200, add this condition to make sure the program is not crashed. 
						tempcode = utilities.convert_code(verbcode)[0] - 0xFFFF
						tempverbcode = str(utilities.convert_code(tempcode,0))
						logger.debug("negated:"+verbcode+"\thex:"+hex(tempcode))
						if tempverbcode=="0":
							verbcode = verbcode+"#"+hex(tempcode)
						else:
							verbcode = tempverbcode
						#raw_input("find negated verb:")
				
			else:
				verbcode = None


			self.triplets[tripleID] = {}   
			self.triplets[tripleID]['triple']=newtriple
			self.triplets[tripleID]['verbcode'] = verbcode
			self.triplets[tripleID]['matched_txt'] = matched_pattern if matched_pattern != None else (" ").join(matched_txt)
			self.triplets[tripleID]['meaning'] = meaning

			#raw_input("Press Enter to continue...")
	
	def get_events(self):
		logger = logging.getLogger('petr_log.PETRgraph')
		self.get_phrases()
		self.filter_triplet_with_time_expression()
		self.get_verb_code()
		self.get_rootNode()

		root_event = {}
		root_eventID={}
		events = {}

		paired_event = {}

		for tripleID, triple in self.triplets.items():
			logger.debug("check event:"+tripleID)

			source = triple['triple'][0]
			target = triple['triple'][1]

			#Test of %, if % in pattern, and no target is found, PETRARCH generates a paired event coded on a compound
			if '%' in triple['matched_txt'] and  (not target or not isinstance(target,basestring) or target == '-'):
				paired_event[tripleID]=triple
				#continue
			
			source_meaning=''
			if not isinstance(source,basestring):
				source.get_meaning() 
				source_meaning=source.meaning if source.meaning != None else ''
				logger.debug("source: "+ source.head+" code: "+(("#").join(source.meaning) if source.meaning != None else '-'))
				self.nouns[source.headID]=source

			target_meaning=['---']
			if not isinstance(target,basestring):
				target.get_meaning() 
				target_meaning=target.meaning if target.meaning != None else ['---']
				logger.debug("target: "+ target.head+" code: "+(("#").join(target.meaning) if target.meaning != None else '-'))
				self.nouns[target.headID]=target

			verb = triple['triple'][2]

			if verb.headID in self.rootID and tripleID not in paired_event:
				if verb.headID in root_eventID:
					root_event[verb.headID][tripleID]=([s.replace('~','---') for s in source_meaning],[t.replace('~','---') for t in target_meaning],triple['verbcode'])
					root_eventID[verb.headID].append(tripleID)
				else:
					root_event[verb.headID] = {}
					root_event[verb.headID][tripleID]=([s.replace('~','---') for s in source_meaning],[t.replace('~','---') for t in target_meaning],triple['verbcode'])
					root_eventID[verb.headID] = [tripleID]
				logger.debug("Root verb:"+verb.text+" code:"+(triple['verbcode'] if triple['verbcode'] != None else "-"))
			else:
				logger.debug("verb:"+verb.text+" code:"+(triple['verbcode'] if triple['verbcode'] != None else "-"))
				#rootNeighbours = []
				#for root in self.rootID:
				#	rootNeighbours.extend(self.udgraph.neighbors(root))
				#if verb.headID in rootNeighbours:
				#	relation_with_root = self.udgraph[self.rootID][verb.headID]['relation']
				#	logger.debug("verb:"+verb.text+" relation:"+relation_with_root)

			event = ([s.replace('~','---') for s in source_meaning],[t.replace('~','---') for t in target_meaning],triple['verbcode'])
			logger.debug(event)

			events[tripleID]= event
			triple['event'] = event


		logger.debug("event transformation....")

		if len(root_event) == 0:
			logger.debug("root_event is None")
			#return {}

		for tripleID, triple in self.triplets.items():
			if tripleID in paired_event:
				continue

			verb = triple['triple'][2]
			

			if len(root_event)==0:
				self.events[tripleID]=[]
				self.events[tripleID]=(list(triple['event']))
				
			for root in self.rootID:
				if root not in root_event:
					continue

				if verb.headID in self.udgraph.neighbors(root):
					relation_with_root = self.udgraph[root][verb.headID]['relation']
					if relation_with_root in ['advcl','ccomp','xcomp']:
						current_event = triple['event'] #4.27
						#(source_meaning,target_meaning,triple['verbcode'])
						logger.debug("root"+str(root))
						for reventID, revent in root_event[root].items():

							event_before_transfer = (revent[0],current_event,revent[2])
							if revent[0] and revent[2] not in ['---']:
								event_after_transfer = self.match_transform(event_before_transfer)
							elif current_event[0] and current_event[1]:
								event_after_transfer = [current_event]
							else:
								event_after_transfer = [event_before_transfer]
								
							logger.debug("event"+tripleID+"transformation:")
							logger.debug(event_after_transfer)

							for e in event_after_transfer:
								if isinstance(e,tuple) and not isinstance(e[1],tuple):
									if reventID not in self.events:
										self.events[reventID] = []
										self.events[reventID].extend(list(e))
									else:
										logger.debug(reventID+" repeated")
										self.events[reventID+"0"] = []
										self.events[reventID+"0"].extend(list(e))
									

								elif isinstance(e,tuple) and isinstance(e[1],tuple) and e[2]== None and e[1][2] != None :
									if tripleID not in self.events:
										self.events[tripleID] = []
										self.events[tripleID].extend(list(e[1]))

		logger.debug("self.events: "+ str(len(self.events)))
		for key, value in self.events.items():
			logger.debug(key+":")
			logger.debug(value)

		if(len(self.events)==0):
			for root in root_eventID:
				for eventID in root_eventID[root]:
					self.events[eventID]=[]
					self.events[eventID].extend(root_event[root][eventID])

		# check the verb codes
		finalverbs = {} 
		for eventID in self.events:
			if eventID not in self.triplets:
				continue

			triplet = self.triplets[eventID]
			ids = eventID.split("#")
			vid = ids[2]

			if len(self.events[eventID])!=3:
				raw_input(self.events[eventID])
				continue

			if vid not in finalverbs:
				finalverbs[vid] = self.events[eventID][2]
			else:
				logger.debug(self.events[eventID][1])
				#if len(self.events[eventID][1])==0 and self.events[eventID][2] not in ['---',None,'None']: 
				#and self.events[evnetID][2] != PETRglobals.VerbDict['verbs'][triplet['meaning']]['#']['#']['code'] :
				if self.events[eventID][2] not in ['---',None,'None'] and self.events[eventID][2] != PETRglobals.VerbDict['verbs'][triplet['meaning']]['#']['#']['code']:
					finalverbs[vid] = self.events[eventID][2]

		for vid,value in finalverbs.items():
			if value != None:
				logger.debug("vid: "+vid+"\t"+str(value))
			else:
				logger.debug("vid: "+vid+"\tNone")

		for eventID in self.events:
			ids = eventID.split("#")
			vid = ids[2]
			self.events[eventID][2] = finalverbs[vid]
	

		# handle paired event, add comments
		allactors = {}
		for tripleID, triple in paired_event.items():
			logger.debug("paired_event:"+tripleID)
			logger.debug(triple['event'])
			verbcode = triple['event'][2]
			ids = tripleID.split("#")
			if verbcode not in allactors:
				allactors[verbcode]={}
				allactors[verbcode]['vid'] = ids[2]
			allactors[verbcode][ids[0]] =  triple['event'][0]

		for verbcode,actors in allactors.items():
			idx = len(self.events)
			for sid in actors.keys():
				for tid in actors.keys():
					if sid != tid and sid != 'vid' and tid != 'vid':
						tripleID = sid+"#"+tid+"#"+actors['vid']+"#"+str(idx)
						self.events[tripleID] = [actors[sid],actors[tid],verbcode]
						idx = idx + 1

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
					logger.debug("line:"+line)
					return results, line
				logger.debug("line:"+line)
				return [(list(v2a[path[0]]), v2a[path[1]], verb)], line

			if isinstance(event, tuple):
				actor = None if not event[0] else tuple(event[0])
				
				eventcode = utilities.convert_code(event[2])[0]
				codelist = [eventcode] #, eventcode - eventcode % 0x10,eventcode - eventcode % 0x100, eventcode - eventcode % 0x1000]
				masks = filter(lambda a: a in pdict, codelist)
				
				logger.debug("actor:")
				logger.debug(actor)

				logger.debug("masks:")
				logger.debug(masks)

				if masks:
					#print(masks)
					path = pdict[masks[0]]
				elif -1 in pdict:
					v2a["Q"] = event[2]
					path = pdict[-1]
					#print(path)
				else:
					#print("nothing is found")
					return False
			else:
				actor = event

			if actor in a2v:
				actor = a2v[actor]

			if not actor:
				actor = "_"

			logger.debug("actor:")
			logger.debug(actor)
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
			
			#logger.debug("no transformation is present")

			return False


		logger.debug("match_transform entry...")

		try:            
			logger.debug(e)

			t = recurse(PETRglobals.VerbDict['transformations'], e)
			#print(t)
			if t:
				logger.debug("transformation is present:")
				logger.debug("t:")
				logger.debug(t)
				return t
			else:
				logger.debug("no transformation is present:")
				#c = utilities.convert_code(e[1][2])[0]
				#print(c)
				#print(16 ** 3)
				#print(c / (16 ** 3))
				if e[0] and e[2] and isinstance(e[1], tuple) and e[1][0] and e[1][2] and e[0]!=e[1][0]: #not e[1][2] / (16 ** 3):
					logger.debug(utilities.convert_code(e[2])[0])
					logger.debug(e[2])


					logger.debug("the event is of the form: a ( b . Q ) P")
					if isinstance(e[1][0], list):
						results = []
						for item in e[1][0]:
							code_combined = utilities.combine_code(utilities.convert_code(e[2])[0],utilities.convert_code(e[1][2])[0])
							#target = []
							#target.append(item)
							event = (e[0], [item], utilities.convert_code(code_combined,0))
							logger.debug(event)
							results.append(event)
						return results
					
					code_combined = utilities.combine_code(utilities.convert_code(e[2])[0],utilities.convert_code(e[1][2])[0])
					event = (e[0], [e[1][0]], utilities.convert_code(code_combined,0))
					logger.debug(event)
					return [event]

		except Exception as ex:
			pass  # print(ex)
		return [e]


	def filter_triplet_with_time_expression(self):
		#filter out triplet containing time expressions as target
		#only works for English now 
		timeexps=Set(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])

		def has_time_expression(triplet):
			target  = triplet[1]
			if target=="-":
				return False

			if target.text in timeexps:
				return True
			else:
				return False

		self.metadata['triplets'] = [t for t in self.metadata['triplets'] if not has_time_expression(t)]
			













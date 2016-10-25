# -*- coding: utf-8 -*-


import networkx as nx
import PETRglobals
import PETRreader

class NounPhrase:

	def __init__(self,sentence,npIDs,headID,date):

		self.npIDs = npIDs
		self.text = ""
		self.head = None
		self.headID = headID
		self.meaning = ""
		self.date = date
		self.sentence = sentence

	def get_meaning(self):
		npText = self.text.upper().split(" ")
		# matching the entire noun phrase string first in the actor or agent dictionary
		codes,roots,matched_txt = self.textMatching(npText)

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

class Sentence:
	"""
    Holds the information of a sentence and its tree.
    
    Methods
    -------
    
    __init__ : Initialization and instantiation
    
    str_to_graph: Reads UD parse into memory
	"""

	def __init__(self, parse, text, date):
		self.parse = parse
		self.agent = ""
		self.ID = -1
		self.actor = ""
		self.date = date
		self.longlat = (-1,-1)
		self.verbs = []
		self.txt = ""
		self.udgraph = self.str_to_graph(parse)
		self.verb_analysis = {}
		self.events = []
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
		print(npIDs)
		if self.udgraph.node[npIDs[0]]['pos']=='ADP':
			npIDs = npIDs[1:]
		for npID in npIDs:
			npTokens.append(self.udgraph.node[npID]['token'])
			
		nounPhrasetext = (' ').join(npTokens)

		np = NounPhrase(self,npIDs,nounhead,self.date)
		np.text = nounPhrasetext
		return np





	def get_source_target(self,nodeID):
		source = []
		target = []
		othernoun = []
		for successor in self.udgraph.successors(nodeID):
			print(str(nodeID)+"\t"+str(successor)+"\t"+self.udgraph.node[successor]['pos'])
			if('relation' in self.udgraph[nodeID][successor]):
				print(self.udgraph[nodeID][successor]['relation'])
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
				print(str(nodeID)+"\t"+attrs['pos']+"\t"+(" ").join(str(e) for e in self.udgraph.successors(nodeID)))
				#print(self.udgraph.successors(nodeID))
				
				verb = attrs['token']
				source,target,othernoun = self.get_source_target(nodeID)

				#for s in source: print(s)
				#for t in target: print(t)
				if len(source)==0 and len(target)>0:
					for t in target:
						triplet = ("-",t,verb,othernoun)
						self.metadata['triplets'].append(triplet)
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


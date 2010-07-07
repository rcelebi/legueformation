#!/usr/bin/env python
import habitat
import topology
import scalefree
import master
import slave

import math
import random
import getopt
import csv
import sys
import time
from mpi4py import MPI

"""
Payoff matrix elements
T: temptation
R: reward
P: penalty
S: sucker's payoff
"""
PAYOFF_T = 1.4
PAYOFF_R = 1.0
PAYOFF_P = 0.0
PAYOFF_S = 0.0

STRATEGY_COOPERATE 	= 1
STRATEGY_DEFECT 	= 0
PROB_COOPERATE = 0.5
STRATEGY_COOPERATE = 0
STRATEGY_DEFECT = 1
SCALEFREE_INIT_NODES_NUM = 4
SCALEFREE_EDGES_NUM_TO_ATTACH= 4
OUTPUT_FILE_NAME = ""
RUN_ID=0
AVALUE=1.0
BVALUE= 1.0
K1VALUE = 0.05
K2VALUE = 2.5
ITERATION_NUM = 1000

DIVERSITY_DISTR_TYPE= 0 
DIVERSITY_EXP_DISTR = 0
DIVERSITY_POW_LAW_DISTR = 1
DIVERSITY_GAUSS_DISTR = 2

GAUSS_CENTER_ROW = 100
GAUSS_CENTER_COL = 100
GAUSS_MAGNITUDE = 1.0
GAUSS_SPREAD = 5000.0
 
AGENTS_NUM = 100
STRATEGY_UPDATE = 1
TOPOLOGY_FILE_NAME =""

MOBILE = 1
MOBILITY = 1 

nextId=1

comm = MPI.COMM_WORLD
MSG_INIT_TYPE = 10 
MSG_MOVE_TYPE = 12 


class Simulation:

	def __init__(self,habitatNeighMap=dict()):
		self.habitats = dict()
		self.habitatNeighborMap = habitatNeighMap
		"""
		
		sfdmat = []
		for i in range(4):
			sfdmat.append([])
			for j in range(4):
				sfdmat[i].append( self.getNextDiversity() )

		self.createHabitats(4, 4, sfdmat, 16)	
		"""
	

	def master():
		return None

	def startSimulation(self, logger):
		times = {}
		times[0] = time.time()
		agentsremovedfromhab ={}
		agentsaddedtohab = {}	
		
		for i in range(ITERATION_NUM):
			totalagentnum = 0
			totaldefnum = 0
			totalcoopnum = 0
			
			if i == ITERATION_NUM:
				logger.writerow([])
			
			for k,habitat in self.habitats.items():
				totalagentnum+= habitat.agentnum
				totaldefnum+= habitat.defnum
				totalcoopnum+= habitat.coopnum
			# printing the last situation of all habitats at last iteration
				if i == ITERATION_NUM:
					logger.writerow([habitat.id, habitat.diversity, habitat.coopnum, habitat.defnum])
			
			fc = float(totalcoopnum) / float(totalagentnum)
			print "Number of defects %d and number of cooperates %d"%(totaldefnum,totalcoopnum) 
	
			if i != ITERATION_NUM:
				logger.writerow([i, totalcoopnum, totaldefnum, len(agentsremovedfromhab)])	
			
			times[1] = time.time()

			print "Iteration %d"%(i)
			print "Logging time : %d"%(times[1]-times[0])

			for k,habitat in self.habitats.items():
				habitat.startTournament()
			
			times[2] = time.time()
			
			print "Encounter time : %d"%(times[2]-times[1])

			agentsremovedfromhab.clear()
			agentsaddedtohab.clear()

			#find which agens will be moved between habitats
			for k,habitat in seagentsMovedBtwSlaveslf.habitats.items():
				
				prob = 0.0
				for agent in habitat.agents:
							
					habitat.changeStrategyOfAgent(agent)
					if MOBILITY == MOBILE:
						if agent.score == 0.0:
							prob = 1.0
						elif agent.strategy == STRATEGY_DEFECT:
							prob = 1.0 - float(agent.score)/ ( habitat.rescalePayoff(BVALUE*float(agent.outdegree)))
						else:
							prob = 1.0 - float(agent.score) / ( habitat.rescalePayoff( 1.0* float(agent.outdegree)))
						
						if random.random() < prob:

							neighbors = [self.habitats[x] for x in  self.habitatNeighborMap[habitat.id]]
							selhab = self.selectANeighborHabitat(habitat, neighbors)

							if selhab == None: continue
			
							agentsremovedfromhab[agent] = habitat.id
							agentsaddedtohab[agent] = selhab.id
			#=====================================================================
			#transfer agents between containers
			self.moveAgents(agentsremovedfromhab, agentsaddedtohab)
			
			times[3] = time.time()
			print "Transfer time: %d"%(times[3]-times[2])
			print "Total moves : %d"%(len( agentsremovedfromhab))

		times[4] = time.time()
		print "Total running time: %d"%(times[4]-times[0])
									
	"""
	select a neighbor habitat for agents to be transfered 
	"""				
	def selectANeighborHabitat(self, habitat, neighbors):
		selhab = random.randint(0,len(neighbors)-1)
		prob = 1.0 / (1.0 + math.exp( habitat.diversity - neighbors[selhab].diversity) / K2VALUE )
		if random.random() < prob:
			return neighbors[selhab] 
		
		return None
	"""
	remove agent from old habitat and add agent to new habitat
	"""
	def moveAgents(self, agentRemovedFromHab, agentsAddedToHab):
		
		for agent,habId in agentRemovedFromHab.items():

			self.removeAgentFromHabitat(agent, self.habitats[habId])
			 
			self.addAgentIntoHabitat(agent, self.habitats[agentsAddedToHab.get(agent)], SCALEFREE_EDGES_NUM_TO_ATTACH)
			
	"""
	do a binary search for the location i such that
	probabilities [i-1]< val <= probabilites[i]
	"""
	def selectProb(self, n, prob):
		val = random.random()
		 
		left =0
		right = n-1
		i = 0
		while right >= left:
			middle = (left+right)/2
 			if (val- prob[middle]) < 0.0:
				right = middle-1
			elif (val - prob[middle]) > 0.0:
				left = middle+1
			else:
			 	i = midlle
				break
	 		
		if right < left:
			i= left
		# in the case there were neighboring items with probability 0
		while i > 0 and prob[i-1] == val:
			i-=1

		return i

	"""
	while removing agent, to not lose connections of peer from the graph,
	there is rewiring process
		- no rewiring required if only it has one or no connections
		- selecting a node (agent) to transfer all removed one' connection onto it
			 with some probability based on it degree .
		- transfer removed connections to selected peer 
	"""

	def removeAgentFromHabitat(self, agent, habitat):
		agentsConnected = habitat.getConnectedAgents(agent)
		edgesConnectedToRemoved = habitat.getConnectedEdges(agent)

		agentsConnectedNum = len(agentsConnected)
		if agentsConnectedNum <= 1:
			for e in edgesConnectedToRemoved:
				habitat.removeEdge(e)
			habitat.removeAgent(agent)
			return True
			
		prob=[]
		totalDegree= float( sum(a.outdegree for a in agentsConnected))
		prob.append( float(agentsConnected[0].outdegree)/ totalDegree )
		for i in range(1, agentsConnectedNum):
			prob.append( prob[i-1] + float(agentsConnected[i].outdegree)/totalDegree )

		
		selected = self.selectProb(agentsConnectedNum, prob)
		selAgent = agentsConnected[selected]
		
		while selAgent == agent:
			selected = self.selectProb(agentsConnectedNum, prob)
			selAgent = agentsConnected[selected]
		# remove agent and rewires its connections with a selected connected agent.
		
		
		edgesTobeAdded = [] 
		for edge in edgesConnectedToRemoved:
			if agent.id == edge[1]	and selAgent.id != edge[0]:
				newedge = [edge[0], selAgent.id]
				edgesTobeAdded.append(newedge)
			elif agent.id == edge[0] and selAgent.id != edge[1]:
				newedge = [selAgent.id, edge[1]]				
				edgesTobeAdded.append(newedge)
	
		# remove agent and its connections
		for e in edgesConnectedToRemoved:
			habitat.removeEdge(e)
		habitat.removeAgent(agent)

		edgesConnectedToSelected = habitat.getConnectedEdges(selAgent)
		# connect edges to selected agent if there is no connection between these nodes 
		for edge in edgesTobeAdded:
			crossedge = [edge[1],edge[0]]
			if edge not in edgesConnectedToSelected and crossedge not in edgesConnectedToSelected:
				habitat.addEdge(edge)
		
		return True	

	def createRandomEdge(self, numAgents, agents, newAgent, prob, totalDegre):	
		attachPoint = self.selectProb(numAgents, prob)
		attachAgent = agents[ attachPoint ]
		return [newAgent.id, attachAgent.id]

	def addAgentIntoHabitat(self, newAgent, habitat, numConn):
		numAgents = len( habitat.agents ) 
		if numAgents == 0:
			habitat.addAgent(newAgent)
			return True
		
		if numAgents == 1:
			habitat.addAgent(newAgent)
			habitat.addEdge([newAgent.id,habitat.agents[0].id])
			return True
		
		if numConn > numAgents:	numConn = numAgents	
			
		totalDegree = float(habitat.totalOutDegree)
		prob = []
		prob.append( float(habitat.agents[0].outdegree)/ totalDegree)
		for i in range(1, len(habitat.agents)):
			prob.append( prob[i-1] + float(habitat.agents[i].outdegree)/totalDegree )

		edges = []
		for k in range(1,numConn):
			edge = self.createRandomEdge(numAgents, habitat.agents, newAgent, prob, totalDegree)
			if edge in edges or [edge[1], edge[0]] in edges:
				k-=1
			else: edges.append(edge)

		habitat.addAgent(newAgent)
		
		for e in edges:
			habitat.addEdge(e)

		return True

	# exponential distribution of diversity values
	def expDist(self, x):
		return AVALUE * (1.0 / math.sqrt(x)-2.0)
	
	# power distribution of diversity values
	def powLawDist(self, x):
		return AVALUE * (math.log(x) -1.0)

	# calculate Gaussian potential value for individual environment point
	def calculateGaussPotentialValue(self, i, j):
		resulut = 1.0
		# calculates distance between two points
		dist2 = (i-GAUSS_CENTER_ROW)*(i-GAUSS_CENTER_ROW) + (j-GAUSS_CENTER_COL)*(j-GAUSS_CENTER_COL);
		norm = int( math.sqrt(dist2) )
		result = GAUSS_MAGNITUDE * math.exp((-1.0* norm* norm)/GAUSS_SPREAD) 

	# get next diversity value
	def getNextDiversity(self,i=0,j=0):
		x = random.random()
		if DIVERSITY_DISTR_TYPE == DIVERSITY_EXP_DISTR:
			return self.expDist(x)
		elif DIVERSITY_DISTR_TYPE == DIVERSITY_POW_LAW_DISTR:
			return self.powLawDist(x)
		elif DIVERSITY_DISTR_TYPE == DIVERSITY_GAUSS_DISTR:
			return self.calculateGaussPotentialValue(i,j)
		else: 
			return None 

"""
 Find nearst neighbor of a habitat set and return that. 
"""
def getNearstNeighbor(habNeighMap,habs,used):
	nsets = []	
	for h in habs:
		nsets.extend(habNeighMap[h])
	#print "before",nsets
	#print "used  ",used
	#print "habs  ",habs
	nsets = [e for e in nsets if e not in habs and e not in used]
	#print "after ",nsets
	
	if not nsets : return None

	return max(nsets, key= lambda a: nsets.count(a) )
	

def divideGridToSection(habNeighMap, sectnum, numhabs):
	sects = {}
	last = 1
	used =[]
	
	size= sectnum*numhabs
	
	for i in range(sectnum):		
		habs = []
		while last in used:
			last = random.randint(1,size)
			print "last ",last
		habs.append(last)
		for k in range(numhabs-1):
			nearst = getNearstNeighbor(habNeighMap,habs,used)
			if nearst is None: break
			habs.append(nearst)
			last = nearst
		used.extend(habs)
		sects[i] = habs
		print "habs ", habs
		print "used ", used
		print "size of used", len(used)
		print "============="	
	return sects		

def makeNeighConnMap(topo):
	
	habitatNeighMap= {}
	for edge in topo.getInterconnMatInt():
		if edge[0] not in habitatNeighMap:
			habitatNeighMap[edge[0]] = []
		if edge[1] not in habitatNeighMap[edge[0]]: 
			habitatNeighMap[edge[0]].append(edge[1])

		if edge[1] not in habitatNeighMap:
			habitatNeighMap[edge[1]] = []
		if edge[0] not in habitatNeighMap[edge[1]]:
			habitatNeighMap[edge[1]].append(edge[0])
	return habitatNeighMap	

if __name__ =='__main__':

	args, opts = getopt.getopt(sys.argv[1:],"r:a:b:d:g:p:k:i:s:m:f:o")
	

	print args

	if "-r" in args:
		RUN_ID = int(args["-r"])
	if "-a" in args:
		AVALUE = float(args["-a"])
	if "-b" in args:
		BVALUE = float(args["-b"])
	if "-d" in args:
		DIVERSITY_DIST_TYPE = int(args["-d"])
	if "-g" in args:
		GAME_ID = int(args["-g"])
	if "-p" in args:
		AGENTS_NUM = int(args["-p"])
	if "-k" in args:
		K1VALUE = float(args["-k"])
		K2VALUE = float(args["-k"])
	if "-i" in args:
		ITERATION_NUM = int(args["-i"])
	if "-s" in args:
		STRATEGY_UPDATE = int(args["-s"])
	if "-m" in args:
		MOBILITY = int(args["-m"])
	if "-f" in args:
		TOPOLOGY_FILE_NAME = str(args["-f"])
	if "-o" in args:
		OUTPUT_FILE_NAME = str(args["-o"])
#	else: OUTPUT_FILE_NAME = "R"+str(RUN_ID)+"_A"+str(AVALUE)+"_B"+str(BVALUE)+"_M"+str(DIVERSITY_DSTR_TYPE)  
	OUTPUT_FILE_NAME ="output.txt"
	TOPOLOGY_FILE_NAME ="topology_20.txt"
		
	logWriter = csv.writer(open(OUTPUT_FILE_NAME+"csv", 'w'), delimiter='\t', quotechar='|',  quoting=csv.QUOTE_MINIMAL)

	topo = topology.Topology()
	try:
		topo.importFromFile(TOPOLOGY_FILE_NAME)
	except: 
		print "could not read topo [360, 380, 379]logy file",TOPOLOGY_FILE_NAME

	habitatNeighMap = makeNeighConnMap(topo) 
	print habitatNeighMap

	habitatids = [int(node.label) for node in topo.nodes]
	simm = Simulation()
	rank = comm.Get_rank()
	
	if rank ==0:
		master = master.Master()
	else:
		sfdmat = []
		for i in range(20):
			sfdmat.append([])
			for j in range(20):
				sfdmat[i].append( simm.getNextDiversity() )

		slave = slave.Slave(rank, 20, 20, sfdmat, 25, habitatids, habitatNeighMap)
	
	sim = Simulation()
	sim.startSimulation(logWriter)
	
	

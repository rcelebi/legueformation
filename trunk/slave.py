#!/usr/bin/env python
import simulation
import scalefree
import random
import habitat

import csv
import sys
import time
import math

"""
Slave consits of a group of habitats, responsible for execution of interactions among agents in those
habitats
"""
class Slave:
	def __init__(self, slaveId, habitats, habitatNeighMap, hab2sfd):
		self.masterId = 0
		self.slaveId = slaveId
		self.totalScore = 0
		self.habitatNeighborMap = habitatNeighMap
		self.habitats = habitats
		self.step = 0
		self.agentsremovedfromhab ={}
		self.agentsaddedtohab = {}	
		self.totalAgentNum = 0
		self.totalDefNum = 0
		self.totalCoopNum = 0
		self.hab2sfd = hab2sfd
			
		iteration = 1
		step = 0
		while( True ):
			if step == 0:
				print "slave---step 0"
				data = simulation.comm.recv(source=self.masterId,tag = simulation.MSG_INIT_TYPE)
				print "data"
				print data
				self.startTournament(iteration)
				step= step +1
			elif step == 1:
				agentstransfered = {}					
				for agent,habid in self.agentsaddedtohab.items():
					if habid not in hab2sfd.keys():
						agentstransfered[agent] = habid

				self.sendTournamentEndInfoMsg(self.slaveId, agentstransfered, self.totalScore, self.totalCoopNum, self.totalDefNum)
				print "Total moves : %d"%(len(  self.agentsaddedtohab ))
				self.moveAgents(self.agentsremovedfromhab, self.agentsaddedtohab)
				step= step +1
			elif step == 2:
				self.recieveDoMovementMsg()
				step= step +1
			elif step == 3:
				self.sendMovementEndAck()
				step = 0
			iteration +=1	

		print "*******FINISH****** SLAVE"		 

	"""
	After recieving signal from Master, start Tournament in its all habitats
	update scores and define movements
	if movement is occured in a habitat of the same slave, do that
	if not, send movement_msg to the Master
	"""
	def startTournament(self, i):

		times= {}
		times[0] = time.time()
		
		
		self.totalAgentNum = 0
		self.totalDefNum = 0
		self.totalCoopNum = 0
					
		times[1] = time.time()

		print "%d. slave:  Number of defects %d and number of cooperates %d"%(self.slaveId,self.totalDefNum,self.totalCoopNum) 

		print "%d. slave: Iteration %d"%(self.slaveId,i)
		print "%d. slave: Logging time : %d"%(self.slaveId, times[1]-times[0])

		for k,habitat in self.habitats.items():
			habitat.startTournament()
		
		times[2] = time.time()
		
		print "%d. slave: Encounter time : %d"%(self.slaveId, times[2]-times[1])

		self.agentsremovedfromhab.clear()
		self.agentsaddedtohab.clear()

		#find which agents will be moved between habitats
		for k,habitat in self.habitats.items():
			
			prob = 0.0
			for agent in habitat.agents:
						
				habitat.changeStrategyOfAgent(agent)
				if simulation.MOBILITY == simulation.MOBILE:
					if agent.score == 0.0:
						prob = 1.0
					elif agent.strategy == simulation.STRATEGY_DEFECT:
						prob = 1.0 - float(agent.score)/ ( habitat.rescalePayoff(simulation.BVALUE*float(agent.outdegree)))
					else:
						prob = 1.0 - float(agent.score) / ( habitat.rescalePayoff( 1.0* float(agent.outdegree)))
					
					if random.random() < prob:

						neighborsfds = [ self.hab2sfd[x] for x in  self.habitatNeighborMap[habitat.id]]
						habids = [ x for x in  self.habitatNeighborMap[habitat.id]]
						selhab = self.selectANeighborHabitat(habitat, neighborsfds)

						if selhab == None: continue
		
						self.agentsremovedfromhab[agent] = habitat.id
						self.agentsaddedtohab[agent] = habids[selhab]

		#=====================================================================
		#transfer agents between containers
		#self.moveAgents(self.agentsremovedfromhab, self.agentsaddedtohab)
		
		times[3] = time.time()
		print "%d. slave: Transfer time: %d"%(self.slaveId, times[3]-times[2])
		print "%d. slave: Total moves : %d"%(self.slaveId, len( self.agentsremovedfromhab))

		times[4] = time.time()
		print "%d. slave: Total running time: %d"%(self.slaveId,times[4]-times[0])
		
		for k,habitat in self.habitats.items():
			self.totalAgentNum+= habitat.agentnum
			self.totalDefNum+= habitat.defnum
			self.totalCoopNum+= habitat.coopnum
		if self.totalAgentNum != 0:
			fc = float(self.totalCoopNum) / float(self.totalAgentNum)
		else: fc = 0.0		
		print "%d. slave:  Number of defects %d and number of cooperates %d"%(self.slaveId,self.totalDefNum,self.totalCoopNum) 



	"""
	select a neighbor habitat for agents to be transfered 
	"""				
	def selectANeighborHabitat(self, habitat, neighbors):
		selhab = random.randint(0,len(neighbors)-1)
		prob = 1.0 / (1.0 + math.exp( habitat.diversity - neighbors[selhab]) / simulation.K2VALUE )
		if random.random() < prob:
			return selhab 
		
		return None

	"""
 	After tournament edns, it sends to the master the mesagge containing following information:
		- its current slave-id
		- agent-new habitat location pair   (map)
		- each habitat' total score
		- each habitat' cooperates/defects number
	"""
	def sendTournamentEndInfoMsg(self, mySlaveId, agentstransfered, totalScore, coopNum, defNum):
		data = dict()
		if mySlaveId is not None:
			data["slaveId"] = mySlaveId
		if agentstransfered is not None:
			data["agentstransfered"] = agentstransfered
		if totalScore is not None:	
			data["score"] = totalScore
		if coopNum is not None:
			data["coopNum"] = coopNum
		if defNum is not None:
			data["defNum"] = defNum
		#send data to master
		simulation.comm.send(data, dest = 0, tag= simulation.MSG_TOURNAMENT_END_TYPE)
			
			
		
	
	"""
	gets msg having following information:
		- agents to be removed to new slave 
			-agents to be added
			- new locations (slave-ids)
	"""	
	def recieveDoMovementMsg(self):
		data = simulation.comm.recv(source=self.masterId,tag = simulation.MSG_MOVE_TYPE)
		agentstransfered ={}
		if data["sectionaddinfo"] is not None:
			agentstransfered = data["sectionaddinfo"]

		for agent in agentstransfered:
			if self.habitats.has_key( agentsAddedToHab[agent] ):  
				self.addAgentIntoHabitat(agent, self.habitats[agentsAddedToHab[agent]], simulation.SCALEFREE_EDGES_NUM_TO_ATTACH)


	"""
	a dummy msg for acknowledge to indicate tournament in that slave is end
	"""
	def sendMovementEndAck(self):
		data = "end"
		simulation.comm.send(data, dest=0, tag= simulation.MSG_END_TYPE)



	"""
	remove agent from old habitat and add agent to new habitat
	"""
	def moveAgents(self, agentRemovedFromHab, agentsAddedToHab):
		
		for agent,habId in agentRemovedFromHab.items():

			if self.habitats.has_key( habId ):
				self.removeAgentFromHabitat(agent, self.habitats[habId])
				
			if self.habitats.has_key( agentsAddedToHab[agent] ):
				self.addAgentIntoHabitat(agent, self.habitats[ agentsAddedToHab[agent] ], simulation.SCALEFREE_EDGES_NUM_TO_ATTACH)
			
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
		#print "agent %d removed from habitat %d"%(agent.id, habitat.id)
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
		#print "agent %d added from habitat %d"%(newAgent.id, habitat.id)
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


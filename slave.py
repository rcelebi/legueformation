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
	def __init__(self, slaveId, numRow, numCol, sdfMatrix, numAgents, habitatids, habitatNeighMap):
		self.masterId = 0
		self.slaveId = slaveId
		self.totalScore = 0
		self.numRow = numRow
		self.numCol = numCol
		self.sdfMatrix =sdfMatrix
		self.numAgents = numAgents
		self.habitatNeighborMap = habitatNeighMap
		self.habitats = {}
		self.step = 0
		self.agentsremovedfromhab ={}
		self.agentsaddedtohab = {}	
		self.totalAgentNum = 0
		self.totalDefNum = 0
		self.totalCoopNum = 0
		self.agentsTobeMoved=[]
		
		self.createHabitats(self.numRow, self.numCol, self.sdfMatrix, numAgents, habitatids)			

		step = 0
		while(True):
			if step == 0:
				print "slave---step 0"
				data = simulation.comm.recv(source=self.masterId,tag = simulation.MSG_INIT_TYPE)
				print "data"
				print data
				self.startTournament(step)
				step= step +1
			elif step == 1:	
				self.sendTournamentEndInfoMsg( self.agentsTobeMoved, self.slaveId, self.agentsaddedtohab, self.totalScore, self.totalCoopNum, self.totalDefNum)
				step= step +1
			elif step == 2:
				self.recieveDoMovementMsg()
				step= step +1
				

				 
				

	def createHabitats(self, numRow, numCol, sdfMatrix, numAgents, habitatids=None):
		global nextId
		nextId =1 
		timeSteps = numAgents - simulation.SCALEFREE_INIT_NODES_NUM
		topo = scalefree.ScaleFree(simulation.SCALEFREE_INIT_NODES_NUM, simulation.SCALEFREE_EDGES_NUM_TO_ATTACH, timeSteps)
		intmat = topo.getInterconnMatInt()
		
		for i in range(numRow):
			for j in range(numCol):
				node2agent= {}
				agents = self.createAgents(numAgents)
				k=0
				for node in topo.nodes:
					node2agent[node.label] = agents[k].id
					k+=1						
				aintmat = []		
				for e in intmat:
					aintmat.append([node2agent[e[0]], node2agent[e[1]]])
				
				#print intmat
				#print agentids
				if habitatids == None:
					habid = ++nextId
				else:
					habid = habitatids[i*numCol +j]
				self.habitats[habid] = habitat.Habitat(habid, agents, aintmat, sdfMatrix[i][j])					
					
		return self.habitats

	def createAgents(self, numAgents):
		agents=[]
		for i in range(numAgents):
			if random.random() < simulation.PROB_COOPERATE:
				strategy = simulation.STRATEGY_COOPERATE
			else:
				strategy = simulation.STRATEGY_DEFECT
			agents.append(habitat.Agent(strategy))			
		return agents
	
	
	"""
	After recieving signal from Master, start Tournament in its all habitats
	update scores and define movements
	if movement is occured in a habitat of the same slave, do that
	if not, send movement_msg to the Master
	"""
	def startTournament(self, i):

		times= {}
		times[0] = time.time()
		agentsTobeMoved =  []
		
		
		self.totalAgentNum = 0
		self.totalDefNum = 0
		self.totalCoopNum = 0
					
		for k,habitat in self.habitats.items():
			self.totalAgentNum+= habitat.agentnum
			self.totalDefNum+= habitat.defnum
			self.totalCoopNum+= habitat.coopnum
		
		fc = float(self.totalCoopNum) / float(self.totalAgentNum)
		print "%d. slave:  Number of defects %d and number of cooperates %d"%(self.slaveId,self.totalDefNum,self.totalCoopNum) 

		times[1] = time.time()

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

						neighbors = [self.habitats[x] for x in  self.habitatNeighborMap[habitat.id]]
						selhab = self.selectANeighborHabitat(habitat, neighbors)

						if selhab == None: continue
						agentsTobeMoved.append(agent)
						self.agentsremovedfromhab[agent] = habitat.id
						self.agentsaddedtohab[agent] = selhab.id

		#=====================================================================
		#transfer agents between containers
		#self.moveAgents(self.agentsremovedfromhab, self.agentsaddedtohab)
		
		times[3] = time.time()
		print "%d. slave: Transfer time: %d"%(self.slaveId, times[3]-times[2])
		print "%d. slave: Total moves : %d"%(self.slaveId, len( self.agentsremovedfromhab))

		times[4] = time.time()
		print "%d. slave: Total running time: %d"%(self.slaveId,times[4]-times[0])

	"""
	select a neighbor habitat for agents to be transfered 
	"""				
	def selectANeighborHabitat(self, habitat, neighbors):
		selhab = random.randint(0,len(neighbors)-1)
		prob = 1.0 / (1.0 + math.exp( habitat.diversity - neighbors[selhab].diversity) / simulation.K2VALUE )
		if random.random() < prob:
			return neighbors[selhab] 
		
		return None

	"""
 	After tournament edns, it sends to the master the mesagge containing following information:
		- agents to be moved between slaves (list)
		- its current slave-id
		- agent-new habitat location pair   (map)
		- each habitat' total score
		- each habitat' cooperates/defects number
	"""
	def sendTournamentEndInfoMsg(self, agentsMovedBtwSlaves, mySlaveId, locationsThatAgentsMoved, totalScore, coopNum, defNum):
		data = dict()
		if agentsMovedBtwSlaves is not None:
			data["agents"] = agentsMovedBtwSlaves
		if mySlaveId is not None:
			data["slaveId"] = mySlaveId
		if locationsThatAgentsMoved is not None:
			data["locations"] = locationsThatAgentsMoved
		if totalScore is not None:	
			data["score"] = totalScore
		if coopNum is not None:
			data["coopNum"] = coopNum
		if defNum is not None:
			data["defNum"] = defNum
		#send data to master
		simulation.comm.send(data, dest = 0,tag= simulation.MSG_MOVE_TYPE)
			
			
		
	
	"""
	gets msg having following information:
		- agents to be moved to new slave 
			-agents
			- new locations (slave-ids)
	"""	
	def recieveDoMovementMsg(self):
		print "recieveDoMovementMsg --not implemented"

	"""
	a dummy msg for acknowledge to indicate tournament in that slave is end
	"""
	def sendMovementEndAck():
		print "sendMovementEndAck --not implemented"


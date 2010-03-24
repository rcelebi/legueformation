#!/usr/bin/env python

import topology
import simulation

import math
import random

nextid = 0

class Agent:
	def __init__(self, strgy, sco=0, outdeg = 0):
		global nextid
		self.id = nextid
		self.strategy = strgy
		self.score = sco
		self.outdegree = outdeg
		
		nextid+=1
	
	def play(self):
		return self.strategy

class Payoff:
	def __init__(self, T, R, P, S):
		self.payoffmat=[[S,T],[P,R]]

	def getScore(self, action1, action2):
		return self.payoffmat[action1][action2]

class Habitat:
	def __init__(self, hid, agents, intmat, sdf):
		self.id = hid
		self.agents = []
		self.intmat = []
		self.diversity = sdf
		self.iteration = 0
		self.totalOutDegree = 0
		self.totalScore = 0
		self.agentnum = 0
		self.coopnum = 0
		self.defnum = 0
		self.id2agent = dict()
		self.gameID = 0
		self.payoff = Payoff(simulation.PAYOFF_T, simulation.PAYOFF_R, simulation.PAYOFF_P, simulation.PAYOFF_S)
		
		for agent in agents:
			self.addAgent(agent)
		
		for edge in intmat:
			self.addEdge(edge) 
	
	def addAgent(self, agent):	
		if agent in self.agents: return None
		agent.outdegree = 0
		self.agents.append(agent)
		self.id2agent[agent.id] = agent
		self.agentnum+=1
		if agent.strategy == simulation.STRATEGY_COOPERATE: self.coopnum+=1
		else: self.defnum+=1

	def removeAgent(self, agent):
		agent.outdegree = 0
		self.agents.remove(agent)
		self.id2agent.pop(agent.id)
		self.agentnum-=1
		if agent.strategy == simulation.STRATEGY_COOPERATE: 
			self.coopnum-=1
		else: self.defnum-=1 

	def removeEdge(self, edge):
		if edge in self.intmat:
			self.intmat.remove(edge)
		self.id2agent[edge[0]].outdegree-=1
		self.id2agent[edge[1]].outdegree-=1
		self.totalOutDegree-=2

	def addEdge(self, edge):
		self.intmat.append(edge)
		#print "ids:",edge[0], edge[1]
		self.id2agent[edge[0]].outdegree+=1
		self.id2agent[edge[1]].outdegree+=1
		self.totalOutDegree +=2

	def rescalePayoff(self, score):
		return score*(1.0 + self.diversity)

	def initiliaze(self):
		self.agentnum = len(self.agents)
		for agent in self.agents:
			agent.score = 0		

	def startTournament(self):
		self.initiliaze()
		self.iteration+=1
		if self.intmat == None or len(self.intmat) == 0: return None

		#print "intmat",self.intmat
		for encounter in self.intmat:
			
			firstagent = self.id2agent[encounter[0]]
			secondagent = self.id2agent[encounter[1]]
			firstaction = firstagent.play()
			secondaction= secondagent.play()
			score1 = self.payoff.getScore(firstaction, secondaction)
			score2 = self.payoff.getScore(secondaction,firstaction)		
			
			#print "encounters:",encounter
			#print "actons: ", firstaction, secondaction
			#print " scores: ",score1,score2 
			# rescale payoff
			score1 = self.rescalePayoff(score1)
			score2 = self.rescalePayoff(score2)
						
			# update each agents' score
			firstagent.score += score1
			firstagent.score +=score2
		
			self.totalScore += score1 + score2
	
	def getConnectedAgents(self, agent):
		agentsConnected=[]	
		for row in self.intmat:
			if agent.id in row:
				if agent.id == row[0]:	
				 	agentsConnected.append(self.id2agent[row[1]])
				else:
					agentsConnected.append(self.id2agent[row[0]])
		return agentsConnected

	def getConnectedEdges(self, agent):
		connected = []
		for e in self.intmat:
			if agent.id in e:
				connected.append(e)
		return connected

	def changeStrategyOfAgent(self, agent):

		if agent.outdegree == 0: return

		agentsconnected = self.getConnectedAgents(agent)
		pickedagent = agentsconnected[random.randint(0, agent.outdegree-1)]

		if pickedagent.strategy == agent.strategy:	return 	
		
		if simulation.STRATEGY_UPDATE == 0:
			prob = self.probabDistr1(agent.score, pickedagent.score)
		else: prob = self.probabDistr2(agent.score, pickedagent.score, agent.outdegree, pickedagent.outdegree)

		if random.random() < prob:
			if agent.strategy == simulation.STRATEGY_COOPERATE:
				self.coopnum-=1
				self.defnum+=1
			else:	
				self.coopnum+=1
				self.defnum-=1
			agent.strategy = pickedagent.strategy

	def probabDistr1(self, score1, score2):
		return 1.0/ (1.0 + math.exp((float(score1 -score2)))/ simulation.K1VALUE)

	def probabDistr2(self, score1, score2, o1, o2):
		omax = max([o1,o2])
		return float(score2- score1)/(simulation.BVALUE * omax)

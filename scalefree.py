#!/usr/bin/env python

import topology
import random
class ScaleFree(topology.Topology):

	def __init__(self,initNodesNum, numEdgesToAttach, timeSteps, nodeids = None):
		
		topology.Topology.__init__(self, label= "ScaleFree"+str(id(self)), nodes=[],edges=[])

		if initNodesNum < 1: return
		nodes = []
		nodeid = 0
		for i in range(initNodesNum):
			if nodeids != None: nodeid = nodeids[i]
			else: nodeid+=1 
			node = topology.Node(nodeid)
			self.addNode(node)
			nodes.append(node)		
		l = []		
		for anode in nodes:
			for bnode in nodes:
				if anode is not bnode and [anode, bnode] not in l:					
					self.addEdge(topology.Edge(anode, bnode))					
					l.append([anode, bnode])
					l.append([bnode, anode])
		steps=0 
		edges = []
		for i in range(initNodesNum, timeSteps+initNodesNum):
			if nodeids != None: nodeid = nodeids[i]
			else: nodeid+=1
			newnode = topology.Node(nodeid)
			self.addNode(newnode)
			++steps
			for j in range(numEdgesToAttach):
				newedge = self.createRandomEdge(nodes, newnode)
				if self.isEdgeInList(newedge,edges):	--j
				else: edges.append(newedge)
			for e in edges:
				self.addEdge(e)
			nodes.append(newnode)

	def isEdgeInList(self, edge, edges):
		for e in edges:
			if e.nodeFrom in [edge.nodeFrom, edge.nodeTo] and e.nodeTo in [edge.nodeFrom, edge.nodeTo]: 
				return True
		return False

	def createRandomEdge(self, nodes, newnode):
		
		while True:
			randomInt = random.randint(0, len(nodes)-1)
			attachNode = nodes[randomInt]
			attachProb =  float(self.getNodeOutdegree(attachNode)+1)/ float(len(self.edges) +len (self.nodes) -1)	
			if random.random() > attachProb: break

		return topology.Edge(newnode, attachNode)

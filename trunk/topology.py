#!/usr/bin/env python

class Node:
	def __init__(self, label=None, weight=None):
		self.label=label
	def equals(self, node):
		if self.label == node.label: 
			return True
		else:
			return False
	def toString(self):
		return self.label

	def getId(self):
		return self.label

class Edge:
	def __init__(self, nodefrom, nodeto, label=None, weight=None):
		self.label = label
		self.nodeFrom = nodefrom
		self.nodeTo = nodeto
		self.weight = weight
	def toString(self):
		return self.label
#weight+':['+(Node)nodefrom.toString()+'] -> ['+nodeto.toString()+']'

class Topology:

	def __init__(self, label=None, nodes=[], edges=[]):
		self.label=label
		self.nodes= nodes
		self.edges= edges
		self.transitionsFromMap = dict()
		self.transitionsToMap = dict()

	# get all edges connected to @node in front
	def getEdgesFromNode(self, node):
		if transitionsFromMap != None:
			return transitonsFromMap.get(node)
		return None

	# get all edges connected between @nodeFrom and @nodeTo
	def getEdgesFromNodeToNode(self, nodeFrom, nodeTo):
		if len(self.transitionsFromMap) == 0 or len(self.transitionsToMap) == 0:
			return list()
		transFrom = set(self.transitionsFromMap.get(nodeFrom))
		transTo  = set(self.transitionsToMap.get(nodeTo))
		return list(transFrom & transTo)

	# get all edge connected to @node from backend 
	def getEdgesToNodes(self, node):
		if transitionsToMap != None:
			return transitionsToMap.get(node)
		return None

	def addNode(self, node):
		self.nodes.append(node)
		self.transitionsFromMap[node]=[]
		self.transitionsToMap[node]=[]
	
	def addEdge(self, edge):
		nodeFrom = edge.nodeFrom
		nodeTo = edge.nodeTo
		if  len( self.getEdgesFromNodeToNode(nodeFrom, nodeTo) ) != 0 : return
		self.edges.append(edge)
		self.transitionsFromMap.get(nodeFrom).append(edge)
		self.transitionsToMap.get(nodeTo).append(edge)

	def removeEdge(self, edge):
		self.edges.remove(edge)
		l = self.transitionsFromMap.get()
		l.remove(edge)
		l= self.transitionsToMap.get()
		l.remove(edge)

	# get topology as interconnectivity matrix
	def getInterconnectivityMatrix(self):
		intmat = []
		for edge in self.edges:
			intmat.append( [ edge.nodeFrom.getId(), edge.nodeTo.getId()] )
		return intmat

	def getInterconnMatInt(self):
		intmat = []
		for edge in self.edges:
			intmat.append( [int( edge.nodeFrom.getId()), int(edge.nodeTo.getId())] )
		return intmat
	
	def getNodeOutdegree(self, node):
		outdegree=0	
		for edge in self.edges:
			if node in [edge.nodeTo, edge.nodeFrom]:
				outdegree+=1
		return outdegree
	"""
	todo: fill the function
	sample file
	 topology1
	 3
	 A
	 B
	 C
	 A > B C
	 B > A
	 C > A B
	"""
	def importFromFile(self, path):
		lines = [ line.strip() for line in file(path)]	
		lines = [line.split() for line in lines]		
		self.label = lines[0][0]
		numNodes = int(lines[1][0])
		label2node ={}
		
		for i in range(2,numNodes+2):
			label = lines[i][0]
			node = Node(label)
			label2node[label] = node
			self.addNode(node)
			#print "label ",label
		for i in range(numNodes+2,len(lines)):
			nodefrom = label2node[ lines[i][0] ]
			for l in lines[i]:
				if l == '>' or l ==' ' or l==lines[i][0]:  continue
				nodeto = label2node[l]
				self.addEdge(Edge(nodefrom, nodeto))

	def exportToFile(self, path):
		return None

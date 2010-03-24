#!/usr/bin/env python

import topology

def test():
	topo = topology.Topology()
	node1 = topology.Node("1")
	node2 = topology.Node("2")
	node3 = topology.Node("3")
	node4 = topology.Node("4")
	node5 = topology.Node("5")
	node6 = topology.Node("6")

	edge1 = topology.Edge(node1, node2)
	edge2 = topology.Edge(node3, node2)
	edge3 = topology.Edge(node4, node2)
	edge4 = topology.Edge(node4, node5)
	edge5 = topology.Edge(node2, node6)
	edge6 = topology.Edge(node5, node1)

	topo.addNode(node1)
	topo.addNode(node2)
	topo.addNode(node3)
	topo.addNode(node4)
	topo.addNode(node5)
	topo.addNode(node6)

	topo.addEdge(edge1)
	topo.addEdge(edge2)
	topo.addEdge(edge3)
	topo.addEdge(edge4)
	topo.addEdge(edge5)
	topo.addEdge(edge6)

	#print topo.edges

	intmat = topo.getInterconnectivityMatrix()
	print intmat
	
	#topo.exportToFile("topology.txt")

	print "=============="
	print "importing topology_20.txt file"
	topo.importFromFile("topology_20.txt")
	print topo.getInterconnectivityMatrix()

if __name__ == '__main__':
	test()

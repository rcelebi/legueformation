#! /usr/bin/env python

import simulation
import csv
import topology

OUTPUT_FILE_NAME = "sample"


 


def test():
	
	logWriter = csv.writer(open(OUTPUT_FILE_NAME+".csv", 'w'), delimiter='\t', quotechar='|',  quoting=csv.QUOTE_MINIMAL)

	topo = topology.Topology()
	topoFile="topology_200.txt"
	try:
		topo.importFromFile(topoFile)
	except: 
		print "could not read topology file",topoFile
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


	habitatids = [int(node.label) for node in topo.nodes]
	#print habitatids
	#print habitatNeighMap	
	#print topo.getInterconnMatInt()

	exit()	
	
	sim = simulation.Simulation(habitatNeighMap)
	print "============"
	#print "Diversity for 1. , 2. , 3. , ",sim.getNextDiversity(), sim.getNextDiversity(), sim.getNextDiversity()
	print " diversity for cell i=0, j=0", sim.getNextDiversity(0,0)
	print " diversity for cell i=10, j=10", sim.getNextDiversity(10,10)
	print " diversity for cell i=20, j=20", sim.getNextDiversity(20,20)
	
	
	#print "selected habitat %d from %s"(habitat.id,str(neighbors))
	print "============"
	
	agents = sim.createAgents(20)

	print "============"
	print "agents strategy"
	for agent in agents:
		print agent.strategy 

	print "============"
	sfdmat = []
	for i in range(200):
		sfdmat.append([])
		for j in range(200):
			sfdmat[i].append( sim.getNextDiversity() )

	habitats = sim.createHabitats(200, 200, sfdmat, 10, habitatids)	
	
	habitat = habitats[1]

	neighbors = [habitats[x] for x in  habitatNeighMap[habitat.id]]

	print "============"
	neighborids = [neigh.id for neigh in neighbors]
	print "habitat id", habitat.id
	print "neighbors ", neighborids
	aneigh = sim.selectANeighborHabitat(habitat, neighbors)
	print "selected habitat",aneigh
	aneigh = sim.selectANeighborHabitat(habitat, neighbors)
	print "selected habitat",aneigh
	aneigh = sim.selectANeighborHabitat(habitat, neighbors)
	print "selected habitat",aneigh
	aneigh = sim.selectANeighborHabitat(habitat, neighbors)
	print "selected habitat",aneigh

	print "============"
	prob = []
	totalDegree = float(habitat.totalOutDegree)
	prob.append( float(habitat.agents[0].outdegree)/ totalDegree)

	for i in range(1, len(habitat.agents)):
		prob.append( prob[i-1] + float(habitat.agents[i].outdegree)/totalDegree )

	print " outdegree of agents"
	for agent in habitat.agents:
		print agent.outdegree
	for ed in habitat.intmat:
		print ed
	print prob
	sel = sim.selectProb( habitat.agentnum, prob)
	print "selected id",sel
	print "============"
	print " agents number, coop num, def num ", habitat.agentnum, habitat.coopnum, habitat.defnum
	print "after adding a agent to habitat ;id ,strategy",agents[0].id, agents[0].strategy
	sim.addAgentIntoHabitat(agents[0], habitat, 10)
	print "intmat ",habitat.intmat
	ids=[agent.id for agent in habitat.agents]
	print "agents",ids	
	print " agents number, coop num, def num ", habitat.agentnum, habitat.coopnum, habitat.defnum

	print "============"

	print "after removing a agent to habitat ;id ,strategy",habitat.agents[0].id,habitat.agents[0].strategy
	sim.removeAgentFromHabitat(habitat.agents[0], habitat)
	print "intmat ",habitat.intmat
	ids=[agent.id for agent in habitat.agents]
	print "agents",ids	
	print " agents number, coop num, def num ", habitat.agentnum, habitat.coopnum, habitat.defnum

	print "after removing a agent to habitat ;id ,strategy",habitat.agents[1].id,habitat.agents[1].strategy
	sim.removeAgentFromHabitat(habitat.agents[1], habitat)
	print "intmat ",habitat.intmat
	ids=[agent.id for agent in habitat.agents]
	print "agents",ids	
	print " agents number, coop num, def num ", habitat.agentnum, habitat.coopnum, habitat.defnum

	print "after removing a agent to habitat ;id ,strategy",habitat.agents[3].id,habitat.agents[3].strategy
	sim.removeAgentFromHabitat(habitat.agents[3], habitat)
	print "intmat ",habitat.intmat
	ids=[agent.id for agent in habitat.agents]
	print "agents",ids	
	print " agents number, coop num, def num ", habitat.agentnum, habitat.coopnum, habitat.defnum
	sim.createRandomEdge(len(agents), agents, habitats[1].agents[1], prob, totalDegree)	


	#for k,hab in habitats.items():
	#	print hab.agentnum


	sim.startSimulation(logWriter)

if __name__ =="__main__":
	test()
	

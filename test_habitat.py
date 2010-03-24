#!/usr/bin/env python
import habitat
import scalefree
import simulation

AGENTS_NUM =20

def test():
	payoff = habitat.Payoff(2.0,1.0,0,0)
	print payoff.payoffmat

	agents = []
	for i in range(AGENTS_NUM):
		agent =	habitat.Agent(i%2)
		agents.append(agent)

	agentids = [agent.id for agent in agents]
	scalef = scalefree.ScaleFree(4,4,AGENTS_NUM-4, agentids)
	topo = scalef
	intmat =topo.getInterconnMatInt()
	print "Initial  4 nodes and 10 new nodes each with 4 edges to attache"	
	print intmat
	
	
	hab = habitat.Habitat( 1, agents, intmat, sdf=1.0)

	print hab.id2agent
	
	hab.startTournament()
	
	print hab.payoff.payoffmat

	print "============="
	print "agent, coop, defect number and degree",hab.agentnum, hab.coopnum, hab.defnum, hab.totalOutDegree	
	ag_coop = habitat.Agent(   simulation.STRATEGY_COOPERATE )
	hab.addAgent(ag_coop)
	print "after adding a cooperate, numbers and degree",hab.agentnum, hab.coopnum, hab.defnum,  hab.totalOutDegree	

	hab.addEdge([ag_coop.id,hab.agents[0].id])
	print "after adding  edge; a cooperate, numbers and degree",hab.agentnum, hab.coopnum, hab.defnum,  hab.totalOutDegree	

	hab.addEdge([ag_coop.id,hab.agents[1].id])
	print "after adding  edge; a cooperate, numbers and degree",hab.agentnum, hab.coopnum, hab.defnum,  hab.totalOutDegree	
	
	hab.removeEdge([ag_coop.id,hab.agents[0].id])
	print "after removing  edge; a cooperate, numbers and degree",hab.agentnum, hab.coopnum, hab.defnum,  hab.totalOutDegree
	
	hab.removeEdge([ag_coop.id,hab.agents[1].id])
	print "after removing  edge; a cooperate, numbers and degree",hab.agentnum, hab.coopnum, hab.defnum,  hab.totalOutDegree
	
	ag_def = habitat.Agent(simulation.STRATEGY_DEFECT )
	hab.addAgent(ag_def)
	print "after adding a defect, numbers and degre",hab.agentnum, hab.coopnum, hab.defnum, hab.totalOutDegree
	
	print "============="
	
	for agent in agents:
		agent.score =2

	hab.changeStrategyOfAgent(agents[0])
	print "change strategy of a agent, numbers(agent,coop, def) ",hab.agentnum, hab.coopnum, hab.defnum, agents[0].strategy

	hab.changeStrategyOfAgent(agents[1])
	print "change strategy of a agent, numbers(agent,coop, def) ",hab.agentnum, hab.coopnum, hab.defnum, agents[1].strategy

	hab.changeStrategyOfAgent(agents[2])
	print "change strategy of a agent, numbers(agent,coop, def) ",hab.agentnum, hab.coopnum, hab.defnum, agents[2].strategy
		
	print "============="

	agentsconnected = hab.getConnectedAgents(ag_coop)
	edgesconnected =  hab.getConnectedEdges(ag_coop)
	hab.removeAgent(ag_coop)
	print "after removing a cooperate, numbers and degree",hab.agentnum, hab.coopnum, hab.defnum, hab.totalOutDegree
	hab.removeAgent(ag_def)
	print "after removing a def, numbers and degree ",hab.agentnum, hab.coopnum, hab.defnum, hab.totalOutDegree
	
	print "============="
	hab.diversity = 1.0
	print " scaled value of 2.0  with d = 1.0",hab.rescalePayoff(2.0)
	
	hab.diversity = 0.588
	print " scaled value of 1.5  with d = 0.588 ",hab.rescalePayoff(1.5)

	print "============="
	
	#print " removed edges " len(edgesconnected), (habitat.intmat)
	

	

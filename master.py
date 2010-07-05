#!/usr/bin/env python
import simulation


class Master:
	def __init__(self):
		self.ntasks = simulation.comm.Get_size()
		self.slaves = range(1,self.ntasks)
		self.loc2ag = {}
		self.totaldefnum = 0
		self.totalcoopnum = 0
		step = 0
		
		while(True):
			if step == 0:
				print "master---step 0"
				self.startTournament()
				step=step+1
			elif step == 1:	
				print "master---step 1"
				for rank in range(1, self.ntasks):
					self.recieveTournamentEndInfo(rank)
				print "Number of defects %d and number of cooperates %d"%(self.totaldefnum,self.totalcoopnum) 	
				step= step +1
			elif step == 2:
				#print "good"
				for rank in range(1,self.ntasks):
					print "good"
					#self.doMigration(agents, habitatId, slaveId)
				step= step +1
				


	"""
	boardcast init msg to all slaves
	"""
	def startTournament(self):
		data = "Init"
		for rank in range(1, self.ntasks):
			simulation.comm.send(data, rank,tag= simulation.MSG_INIT_TYPE)
	
	"""
	recieve msg from slaves contiaining following info:
		- agents to be moved 
		- from which habitat to where
		- each habitat' scores in the slave
		- habitat cooperate/ defect numbers
	"""
	def recieveTournamentEndInfo(self,rank):

		data = simulation.comm.recv(source=rank,tag = simulation.MSG_MOVE_TYPE)

		if data is not None: return

		if data["agents"] is not None:
			agents = data["agents"]
		if data["slaveId"] is not None:
			slaveId= data["slaveId"]
		if data["locations"] is not None:
			locationsTobeMoved = data["locations"]
		if data["score"] is not None:	
			totalScore = data["score"]
		if data["coopNum"] is not None:
			coopNum = data["coopNum"]
		if data["defNum"] is not None:
			defNum = data["defNum"]

		self.totaldefnum += coopNum
		self.totalcoopnum += defNum

		print "RECEIVED- form slave %d cooperate num: %d defect num: %d"%(slaveId,coopNum,defNum)
		
		for ag,loc in locations:
			if self.loc2ag.__contains__(loc):
				self.loc2ag[loc].append(ag)
			else:
				self.loc2ag[loc] =[ag]
		
	
	"""
	 send Movement msg to related slaves:
		- set of agents
		- moved location (habitat ids)	
	"""
	def doMigration(self, agents, habitatId, slaveId):

		data = dict()
		if agents is not None:
			data["agents"] = agents
		if locationsThatAgentsMoved is not None:
			data["habitatId"] = habitatId
		
		simulation.comm.send(data, slaveId,tag = simulation.MSG_MOVE_TYPE)
		

	"""
	after migration, gather all ack msgs from related slaves (not from all slaves) 
	"""
	def waitAcknowledge(self):	
		print "not implemented"

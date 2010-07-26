#!/usr/bin/env python
import simulation


class Master:
	def __init__(self, sects, allhabitats):
		self.ntasks = simulation.comm.Get_size()
		self.slaves = range(1,self.ntasks)
		self.sect2hab = sects
		self.allhabitats = allhabitats
		self.totaldefnum = 0
		self.totalcoopnum = 0
	 	self.habid2agentsadded = dict()
		step = 0
		iteration = 1
		while(iteration  < simulation.ITERATION_NUM ):
			if step == 0:
				print "master---step 0"
				self.startTournament()
				step=step+1
			elif step == 1:	
				print "master---step 1"
				self.habid2agentsadded = {}
				for rank in range(1, self.ntasks):
					self.recieveTournamentEndInfo(rank)
				print "Number of defects %d and number of cooperates %d"%(self.totaldefnum,self.totalcoopnum) 	
				step=step +1
			elif step == 2:
				print "master---step 2"
				for sid,habs in self.sect2hab.items():
					sectainfo = {}
					for habid in habs:
						if self.habid2agentsadded.has_key(habid):
							sectainfo[self.habid2agentsadded[habid]] = habid
					self.doMigration(sectainfo, sid)
				step= step +1
			elif step == 3:
				self.waitAcknowledge()
				step = 0
			iteration += 1
	
	print "*******FINISH****** MASTER"

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


 		- agents to be moved between slaves (list)
		- its current slave-id
		- agent-new habitat location pair   (map)
		- each habitat' total score
		- each habitat' cooperates/defects number
	"""
	def recieveTournamentEndInfo(self,rank):

		data = simulation.comm.recv(source=rank,tag = simulation.MSG_TOURNAMENT_END_TYPE)

		#print "master data", data
		if data is None: return

		if data["slaveId"] is not None:
			slaveId= data["slaveId"]
		if data["agentstransfered"] is not None:
			agentstransfered = data["agentstransfered"]
		if data["score"] is not None:	
			totalScore = data["score"]
		if data["coopNum"] is not None:
			coopNum = data["coopNum"]
		if data["defNum"] is not None:
			defNum = data["defNum"]

		self.totaldefnum += coopNum
		self.totalcoopnum += defNum

		print "RECEIVED- from slave %d cooperate num: %d defect num: %d"%(slaveId,coopNum,defNum)

		for agent,hid in agentstransfered.items():
			if not self.habid2agentsadded.has_key(hid):
				 self.habid2agentsadded[hid] = [agent]
			else:
				self.habid2agentsadded[hid].append(agent)


	def doMigration(self, sectainfo, sid):
		print "send doMigration"
		data = dict()
		if sectainfo is not None:
			data["sectionaddinfo"] = sectainfo

		
		simulation.comm.send(data, dest = sid, tag = simulation.MSG_MOVE_TYPE)
		
		

	"""
	after migration, gather all ack msgs from related slaves (not from all slaves) 
	"""
	def waitAcknowledge(self):
		for rank in self.slaves:	
			data = simulation.comm.recv(source=rank,tag = simulation.MSG_END_TYPE)




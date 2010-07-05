#!/usr/bin/env python
"""
Parallel Master-Slave Example 
"""
from mpi4py import MPI
import time

comm = MPI.COMM_WORLD

def master():	
	print "master"
	ntasks = comm.Get_size()
	data = dict()
	data["aa"]= {"xx":"yy"}
	data["bb"]="ttt"
	data["cc"]=1
	for rank in range(1,ntasks):
		print "master -giden"
		print data
		comm.send(data, rank,tag=11)
	data = None
	n = 2
	for rank in range(1,ntasks): 
 		data =comm.recv(source=rank,tag=12)
		print "master -gelen"
		print data
	"""
	while True:
		data2 = comm.recv()
		print data2
		if n > ntasks: break
		n+=1
	"""

def slave():
	print "slave -gelen"
	#comm.send(data={"a":12,"b":34},dest=0,tag=11)
	#while True:
	data = comm.recv(source=0,tag =11)
	
	print data["aa"]
	time.sleep(1)
	data = "ok"
	comm.send(data,dest=0,tag=12)

if __name__ == '__main__':
	myrank = comm.Get_rank()
	if myrank == 0:
		master()
	else:
		slave()

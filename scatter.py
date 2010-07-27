from mpi4py import MPI
import simulation
import topology

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
	topo = topology.Topology()
	topoFile="topology_200.txt"
	try:
		topo.importFromFile(topoFile)
	except: 
		print "could not read topology file",topoFile
	
	habNM = simulation.makeNeighConnMap(topo)
	secs = simulation.divideGridToSection(habNM,size,20)
	data =[]	
	for i in range(size):
		data.append(secs[i])
	print "before scattering ",data
else:
	data = None
data = comm.scatter(data, root=0)
#assert data == (rank+1)**2
print "rank ",rank
print "data ",data

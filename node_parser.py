#@author dposch

class Link(object):
	def __init__(self,n1, n2, bw_n1_to_n2, bw_n2_to_n1, delay_n1_to_n2, delay_n2_to_n1, loss_n1_to_n2, loss_n2_to_n1):
		self.n1=n1
		self.n2=n2
		self.ip1=""
		self.ip2=""
		self.bw_n1_to_n2 = bw_n1_to_n2
		self.bw_n2_to_n1 = bw_n2_to_n1
		self.delay_n1_to_n2 = delay_n1_to_n2
		self.delay_n2_to_n1 = delay_n2_to_n1
		self.loss_n1_to_n2 = loss_n1_to_n2
		self.loss_n2_to_n1 = loss_n2_to_n1

	def __str__(self):
		return "Link(" + self.n1 + ", " + self.n2 + ", " +str(self.bw_n1_to_n2) + ", " + str(self.bw_n2_to_n1)+ ", " + str(self.delay_n1_to_n2) + ", "
		+ str(self.delay_n2_to_n1) + ", " + str(self.loss_n1_to_n2) + ", " + str(self.loss_n2_to_n1) + ")"

class Property(object):
	def __init__(self, client, server):
		self.client = client
		self.server = server
		self.ip_client=""
		self.ip_server=""

	def __str__(self):
		return "Property(" + str(self.client) + ", " + str(self.server) +") or with IPs: Property(" + self.ip_client + ", " + self.ip_server +")"

def parseNetwork(fileName):

	nodes = 0
	link_list = []
	property_list = []

	print "Parsing NetworkFile: " + fileName
	with open(fileName,"r") as f:

		for line in f:
			if line.startswith("#number of nodes"):
				nodes = int(next(f)) #skip header and read number of nodes

			if line.startswith("#nodes setting"):
				line = next(f)
				while(line[0] != '#'):
					tmp_str = line.rstrip('\n').split(',')

					if (len(tmp_str) == 6):
						link_list.append(Link(tmp_str[0],tmp_str[1],int(tmp_str[2]), int(tmp_str[3]), int(tmp_str[4]), int(tmp_str[5]), "", ""))
					elif (len(tmp_str) == 8):
						 link_list.append(Link(tmp_str[0],tmp_str[1],int(tmp_str[2]), int(tmp_str[3]), int(tmp_str[4]), int(tmp_str[5]), tmp_str[6], tmp_str[7]))
					else:
						print "Parsing Error"
						exit(-1)
					#print str(Link(tmp_str[0],tmp_str[1],int(tmp_str[2]), int(tmp_str[3]), int(tmp_str[4]), int(tmp_str[5])))

					line = next(f)

			if line.startswith("#properties"):
				line = next(f)
				while(line[0] != '#'):
					tmp_str = line.rstrip('\n').split(',')

					if(len(tmp_str) != 2):
						print "Parsing Error"
						exit(-1)

					#print Property(tmp_str[0],tmp_str[1]).client
					property_list.append(Property(int(tmp_str[0]),int(tmp_str[1])))

					line = next(f)

		f.close()
	print "Network parsed!\n"
	return (nodes, link_list, property_list)

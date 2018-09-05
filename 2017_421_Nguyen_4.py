import numpy as np
import xml.etree.ElementTree as ET 

class System:
 
	def __init__(self, N, M, cost_limit, data):
		self.R = 1
		self.C = 0
		self.N = N
		self.M = M
		self.data = data
		self.cost_limit = cost_limit

		self.modules = np.empty((self.N, 2))
		self.cur_state = np.empty((self.N))
		self.best_state = np.empty((self.N))

		try:
			self.cur_state = self.init_state()
		except Error:
			raise

		self.R = self.count_R(self.cur_state) 


	def print_system(self, whole = 0):
		if (whole != 0):
			for x in xrange(self.N):
				for y in xrange(self.M):
					print self.data[x][y]
				print '---'
		else:
			for x in xrange(self.N):
				print self.modules[x]

	def count_R(self, cur_state):
		R = 1.0
		for x in xrange(self.N):
			R *= self.data[x][int(cur_state[x])][0]

		return R

	def count_C(self, cur_state):
		C = 0
		for x in xrange(self.N):
			C += self.data[x][int(cur_state[x])][1]
		return C
	def init_state(self):
		count = 0
		count_limit = 10
		num_change = int(self.N/3)	

		new_state = np.empty((self.N))
		n_cost = 0

		while True:
			for x in xrange(self.N):
				new_state[x] = np.random.randint(0,self.M)
			n_cost = self.count_C(new_state)
			count += 1
		 	if (n_cost < cost_limit or count > count_limit):
		 		break

		if (count >= count_limit):
			print('Could not generate a state in ', count_limit)
			raise Error(self.count_R(self.best_state))
		else:		
			return new_state

	def gen_state(self):
		count = 0
		count_limit = 10
		num_change = int(self.N/3)	

		new_state = np.empty((self.N))
		new_state = np.copy(self.cur_state)
		n_cost = 0

		while True:
			for x in xrange(num_change):
				i = np.random.randint(1,self.M)
				new_state[i] = np.random.randint(0,self.M)
			n_cost = self.count_C(new_state)
			count += 1
		 	if (n_cost < cost_limit or count > count_limit):
		 		break

		if (count >= count_limit):
			print('Could not generate a state in ', count_limit)
			raise Error(self.count_R(self.best_state))
		else:		
			return new_state		


	def Probability(self, dE, T):
		return 1/(1+np.exp(dE/T))

	def Change_T(self, T0, k): #To - cur temp; k - step;
		return T0*0.8/k		 	

	def Parallel_aneal(self):
		solution = np.empty((self.M))
		for x in xrange(self.M):
			self.cur_state[0] = x
			solution[x] = self.Annealing(100,1)
		

		return np.amax(solution)

	def Annealing(self, start_t, fin_t):

		self.best_state = self.cur_state	
		t = start_t
		count = 1

		while (t > fin_t):
			try:
				next_state = self.gen_state()
				dE = self.R - self.count_R(next_state) 
				if (dE < 0):
					self.cur_state = next_state
				else:
					if ( np.random.random() < self.Probability(dE, t) ):
						self.cur_state = next_state
				if (self.count_R(self.cur_state) > self.count_R(self.best_state)):
					self.best_state = self.cur_state			
			except Error as e:
				print ('Could not generate new state')	
			
			t = self.Change_T(t, count)

		return self.count_R(self.best_state)

	def Solve(self, prop_realibility, n_experience, start_t, fin_t, output):
		solution = np.empty((n_experience))
		root = ET.Element("root")

		for i in xrange(n_experience):
			solution[i] = self.Parallel_aneal()
			subelem = ET.SubElement(root, "R")
			subelem.text = str(solution[i])
			subelem.set('id', str(i))

		message = ET.tostring(root, "utf-8")
		doc = '<?xml version="1.0" encoding="UTF-8"?>' + message.decode('utf-8')  
		with open(output, 'w') as out_xml:
			out_xml.write(doc)




class Error(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)



def gen_randomize_data(N, M, a=1, b=10):
	sys = np.empty((N,M,2))
	for x in range(N):
		for y in range(M):
			sys[x][y] = ((np.random.random(), np.random.randint(a,b)))
	
	return sys

def gen_randomize_data_xml(n_experience, N, M, cost_limit, file_name):
	root = ET.Element("root")
	N_elem = ET.SubElement(root, "N")
	N_elem.text = str(N)
	M_elem = ET.SubElement(root, "M")
	M_elem.text = str(M)
	cost_limit_elem = ET.SubElement(root, "cost_limit")
	cost_limit_elem.text = str(cost_limit)
	n_exp_elem = ET.SubElement(root, "n_experience")
	n_exp_elem.text = str(n_experience)
	
	#for i in xrange(n_experience):
		#problem = ET.SubElement(root, "problem")
		#problem.set("id", str(i+1))
	for x in xrange(N):
		module = ET.SubElement(root, "module")
		module.set("id", str(x+1))
		for y in xrange(M): 	
			version = ET.SubElement(module, "version")
			version.set("id", str(y+1))
			version.set("R", str(float(0.9+np.random.randint(1,9)*0.01)))
			version.set("C", str(np.random.randint(1,50)))

	text = ET.tostring(root, "utf-8")
	doc = '<?xml version="1.0" encoding="UTF-8"?>' + text.decode('utf-8')

	with open(file_name, 'w') as file:
	    file.write(doc)

def Parse_xml(input, n_experience, N, M, cost_limit):

	with open(input, 'r') as in_file:
		tree = ET.parse(in_file)

	data = np.empty(1)
		
	root = tree.getroot()
	for data_xml in root.getchildren():
		if (data_xml.tag == "N"):
			N = int(data_xml.text)
		elif (data_xml.tag == "M"):
			M = int(data_xml.text)
		elif (data_xml.tag == "cost_limit"):
			cost_limit = int(data_xml.text)
		elif (data_xml.tag == "n_experience"):
			n_experience = int(data_xml.text)
			data = np.empty((N, M, 2))
		elif (data_xml.tag == 'module'):
			x = int(data_xml.attrib['id']) - 1
			#for module in data_xml.getchildren():
			for version in data_xml.getchildren():
				y = int(version.attrib['id']) - 1
				data[x][y][0] = float(version.attrib['R'])
				data[x][y][1] = int(version.attrib['C'])
		else: 
			print('tag not found - ',data.tag)

	system = System(N,M, cost_limit, data)


	return system

	
def Parse_solution(input, prop_realibility):
	with open(input, 'r') as in_file:
		tree = ET.parse(in_file)

	sum_good = 0.0
	
	root = tree.getroot()
	for node in root.getchildren():
		#print(node.text)
		if (prop_realibility < float(node.text)):
			sum_good += 1
	P = float(sum_good / n_experience)
	print ('Probability of a good solution ', P)





##############	MAIN ###################
N = 10
M = 10
cost_limit = 3000
n_experience = 1000
start_t = 100
fin_t = 1
prop_realibility = 0.01
file_solution = '2017_421_Nguyen_results_4.xml'
file_input = '2017_421_Nguyen_id_4.xml'


try:
	gen_randomize_data_xml(n_experience, N,M, cost_limit, file_input)
	system = Parse_xml(file_input, n_experience, N, M, cost_limit)

	system.Solve(prop_realibility, n_experience, start_t, fin_t, file_solution)
	Parse_solution(file_solution, prop_realibility)

except Error:
	print 'Ooooops'


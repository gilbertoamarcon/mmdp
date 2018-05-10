#!/usr/bin/env python

import numpy as np
import math

prob_tolerance = 0.01
dec_cases = int(math.log10(prob_tolerance**-1))


class Mdp:

	@staticmethod
	def print_format_error(error_code=[]):
		print 'Error Reading File.'
		for e in error_code:
			print e
		exit(0)

	@staticmethod
	def max_norm(arr):
		return max([abs(i) for i in arr])

	@staticmethod
	def max_norm_dist(arr_a,arr_b):
		return Mdp.max_norm([a-b for a,b in zip(arr_a,arr_b)])

	@staticmethod
	def print_array(arr):
		return ' '.join(['%*.*f'%(dec_cases+2,dec_cases,i) for i in arr])

	@staticmethod
	def print_infinite_horizon_array(arr, title):
		print title
		dec_idx = 1+int(math.log10(len(arr)-1))
		dec_val = 1+int(math.log10(max([abs(a) for a in arr])))
		for k,s in enumerate(arr):
			if type(s) is int:
				print 'S%0*d: %*d' % (dec_idx,k,dec_val,s)
			if type(s) is float:
				print 'S%0*d: %*f' % (dec_idx,k,dec_val,s)


	def __init__(self,
			filename=None,
			verbose=False,
			T = [],
			R = [],
			m = 0,
			n = 0,
		):
		self.T = T
		self.R = R
		self.m = m
		self.n = n
		self.verbose = verbose
		if filename is not None:
			with open(filename, 'r') as f:
				for row_number,l in enumerate(f.readlines()):
					row = l.decode("utf-8-sig").encode("utf-8").split()

					# First Row: Header
					if not row_number:
						self.n = int(row[0])
						self.m = int(row[1])

					# Body
					else:
						
						# Empty Rows: Table Transition
						if len(row) == 0:

							# New Table 'T'
							if len(self.T) < self.m:
								self.T.append([])

							# Tables 'T' and 'R' finished reading;
							elif len(self.R) == self.n:
								break

						# Reading Table 'T' entry
						elif len(row) == self.n and len(self.T[-1]) < self.n:
							self.T[-1].append([float(e) for e in row])

						# Reading Table 'R' entry
						elif len(row) == self.m:
							self.R.append([float(e) for e in row])

						# File format issue
						else:
							Mdp.print_format_error()

	def __exit__(self):
		pass

	def __str__(self):
		buff = '%s %s\n' % (self.n,self.m)
		buff += '\n'

		for a,x in enumerate(self.T):
			for e in x:
				buff += Mdp.print_array(e) + '\n'
			buff += '\n'

		for x in self.R:
			buff += ' '.join(['%f'%i for i in x]) + '\n'
		return buff

	def validate_model(self):
		if len(self.T) != self.m:
			return ['Table \'T\' with lenght %i, not %i' % (len(self.T),self.m)]
		for a,action in enumerate(self.T):
			if len(action) != self.n:
				return ['Action %i with lenght %i, not %i' % (action,len(action),self.n)]
			for s,state in enumerate(action):
				if abs(sum(state)-1.0) > prob_tolerance:
					return ['sum: %f'%sum(state),'Action: %i'%a,'State: %i'%s]
				if len(state) != self.n:
					return ['Action %i, State %i with lenght %i, not %i' % (action,state,len(state),self.n)]
		if len(self.R) != self.n:
			return ['Table \'R\' with lenght %i, not %i' % (len(self.R),self.n)]
		for state in self.R:
			if len(state) != self.m:
				return ['State %i with reward lenght %i, not %i' % (state,len(state),self.m)]
		return []

	def getT(self, s=None, a=None, sn=None):
		if a is None or s is None or sn is None:
			return None
		return self.T[a][s][sn]

	def getR(self, s=None, a=None):
		if a is None or s is None:
			return None
		return self.R[s][a]

	def finite_horizon_value_iteration(self, horizon):
		if self.verbose:
			print 'Non-Stationary Value Function:'
		self.V = self.n*[0.0]
		self.pol = []
		for k in range(horizon):
			aux = [[self.getR(s=s,a=a)+sum([self.getT(s=s,a=a,sn=sn)*self.V[sn] for sn in range(self.n)]) for a in range(self.m)] for s in range(self.n)]
			self.V = [max(s) for s in aux]
			if self.verbose:
				print '%2d:'%k,Mdp.print_array(self.V)
			self.pol.append([int(np.argmax(s)) for s in aux])
		if self.verbose:
			print ''
		return  self.pol

	def infinite_horizon_value_iteration(self, discount, bound):
		stopping_threshold = bound*(1-discount)**2/(2*discount**2)
		self.V = self.n*[0.0]
		if self.verbose:
			print 'Iterative Value Function:'
		while True:
			oldV = self.V
			aux = [[self.getR(s=s,a=a)+discount*sum([self.getT(s=s,a=a,sn=sn)*self.V[sn] for sn in range(self.n)]) for a in range(self.m)] for s in range(self.n)]
			self.V = [max(s) for s in aux]
			if self.verbose:
				print Mdp.print_array(self.V)
			self.pol = [int(np.argmax(s)) for s in aux]
			if Mdp.max_norm_dist(self.V,oldV) < stopping_threshold:
				break
		if self.verbose:
			print ''
		return self.pol, self.V

	def store_infinite_horizon_policy(self,filename):
		buff = 'policy,value\n'
		for p,v in zip(self.pol,self.V):
			buff += '%d,%f\n' % (p,v)
		with open(filename,'w') as f:
			f.write(buff)

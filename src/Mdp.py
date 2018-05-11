#!/usr/bin/env python

import deepdish as dd
import numpy as np
import math

prob_tolerance = 0.01
dec_cases = int(math.log10(prob_tolerance**-1))


class Mdp:

	@staticmethod
	def max_norm(arr):
		return max([abs(i) for i in arr])

	@staticmethod
	def max_norm_dist(arr_a,arr_b):
		return Mdp.max_norm([a-b for a,b in zip(arr_a,arr_b)])

	def __init__(self,
			filename=None,
			T = [],
			R = [],
		):
		if filename is None:
			self.T = np.array(T)
			self.R = np.array(R)
		else:
			self.load_problem(filename)
		self.m = self.T.shape[0]
		self.n = self.T.shape[1]

	def __exit__(self):
		pass

	def load_problem(self,filename):
		raw = dd.io.load(filename)
		self.T = raw['T']
		self.R = raw['R']

	def store_problem(self,filename):
		raw = {
			'T': self.T,
			'R': self.R,
		}
		dd.io.save(filename, raw, compression='zlib')

	def store_policy(self,filename):
		raw = {
			'pol': np.array(self.pol),
			'V': np.array(self.V),
		}
		dd.io.save(filename, raw, compression='zlib')

	def load_policy(self,filename):
		raw = dd.io.load(filename)
		self.pol = raw['pol']
		self.V = raw['V']

	def getT(self, s=None, a=None, sn=None):
		if a is None or s is None or sn is None:
			return None
		return self.T[a][s][sn]

	def getR(self, s=None, a=None):
		if a is None or s is None:
			return None
		return self.R[s][a]

	def solve(self, discount, bound):
		stopping_threshold = bound*(1-discount)**2/(2*discount**2)
		self.V = self.n*[0.0]
		while True:
			oldV = self.V
			aux = [[self.getR(s=s,a=a)+discount*sum([self.getT(s=s,a=a,sn=sn)*self.V[sn] for sn in range(self.n)]) for a in range(self.m)] for s in range(self.n)]
			self.V = [max(s) for s in aux]
			self.pol = [int(np.argmax(s)) for s in aux]
			if Mdp.max_norm_dist(self.V,oldV) < stopping_threshold:
				break

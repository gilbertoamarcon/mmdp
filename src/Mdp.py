#!/usr/bin/env python

import deepdish as dd
import numpy as np

class Mdp:

	def __init__(self, T = [], R = []):
		if T and R:
			self.T = np.array(T)
			self.R = np.array(R)
			self.m = self.T.shape[0]
			self.n = self.T.shape[1]

	def __exit__(self):
		pass

	def load_problem(self,filename):
		raw = dd.io.load(filename)
		self.T = raw['T']
		self.R = raw['R']
		self.m = self.T.shape[0]
		self.n = self.T.shape[1]

	def load_policy(self,filename):
		raw = dd.io.load(filename)
		self.p = raw['p']
		self.V = raw['V']

	def store_problem(self,filename):
		raw = {
			'T': self.T,
			'R': self.R,
		}
		dd.io.save(filename, raw, compression='zlib')

	def store_policy(self,filename):
		raw = {
			'p': self.p,
			'V': self.V,
		}
		dd.io.save(filename, raw, compression='zlib')

	def solve(self, discount, bound):
		stopping_threshold = bound*(1-discount)**2/(2*discount**2)
		self.V = np.zeros((self.n,1))
		while True:
			oldV = self.V
			self.Q = np.array([[self.R[s][a] + discount*np.dot(self.T[a][s],self.V) for a in range(self.m)] for s in range(self.n)])
			self.V = np.array([np.max(s) for s in self.Q])
			if np.linalg.norm(self.V-oldV, np.inf) < stopping_threshold:
				break
		self.p = np.array([np.int(np.argmax(s)) for s in self.Q])

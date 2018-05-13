#!/usr/bin/env python

import deepdish as dd
import numpy as np
from numba import njit, prange
from tqdm import tqdm

@njit(parallel=True)
def iterate_q(Q, T, R, V, d):
	for a in prange(T.shape[0]):
		Q[a] = R[a] + d*np.dot(T[a],V)

class Mdp:

	def __init__(self, T = [], R = []):
		if len(T) and len(R):
			self.T = np.array(T).astype(np.float32)
			self.R = np.array(R).astype(np.float32)
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

	def solve(self, discount, bound, parallel=True):
		stopping_threshold = bound*(1-discount)**2/(2*discount**2)
		self.V = np.zeros(self.n).astype(np.float32)
		self.Q = np.zeros((self.m,self.n)).astype(np.float32)
		for i in tqdm(range(1000)):
			oldV = self.V
			if parallel:
				iterate_q(self.Q, self.T, self.R, self.V, discount)
			else:
				self.Q = self.R + discount*np.dot(self.T,self.V)
			self.V = np.max(self.Q, axis=0)
			if np.linalg.norm(self.V-oldV, np.inf) < stopping_threshold:
				break
		self.p = np.argmax(self.Q, axis=0)

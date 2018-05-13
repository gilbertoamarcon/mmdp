#!/usr/bin/env python

from collections import OrderedDict
from tqdm import tqdm
import numpy as np
import itertools as it
import yaml

class Problem:

	@staticmethod
	def encoder(data,code=None):
		if code is None:
			return {e:i for i,e in enumerate(data)}
		else:
			return [[code[e] for e in d] for d in data]

	@staticmethod
	def get_state_code(locs,goal_state):
		return sum([g*(len(locs)**i) for i,g in enumerate(reversed(goal_state))])


	def __init__(self,filename):

		# Loading problem description
		with open(filename,'r') as f:
			self.problem = yaml.load(f.read())
		# asd
		self.locs	= Problem.encoder(self.problem['locs'])
		self.agents	= Problem.encoder(self.problem['agents'])

		print self.locs
		print self.problem['locs']

		items	= {k:v for d in [self.locs,self.agents] for k,v in d.items()}
		self.roads	= Problem.encoder(self.problem['roads'],items)
		goals	= Problem.encoder(self.problem['goal']['at'],items)
		self.s = list(it.product(range(len(self.locs)),repeat=len(self.agents)))
		acts = [[] for l in self.locs]
		for r in self.roads:
			acts[r[0]].append(r[1])
		nact = max([len(a) for a in acts])
		self.A = np.zeros((nact,len(self.locs))).astype(np.int32)
		for ai,a in enumerate(self.A):
			for si,s in enumerate(a):
				if len(acts[si]) > ai:
					self.A[ai][si] = acts[si][ai]
				else:
					self.A[ai][si] = si
		self.a = list(it.product(range(nact),repeat=len(self.agents)))
		self.n = len(self.s)
		self.m = len(self.a)

		print 'Flattening R...'
		self.R = np.zeros((self.m,self.n),dtype=np.float32)
		for si,s in enumerate(self.s):
			for a in range(self.m):
				for agx in range(len(self.agents)):
					if goals[agx][1]==s[agx]:
						self.R[a][si] += 1.0

		print 'Flattening T...'
		self.T = np.zeros((self.m,self.n,self.n),dtype=np.float32)
		for si,s in enumerate(tqdm(self.s)):
			for ai,a in enumerate(self.a):
				nxt = tuple([self.A[a[i]][s[i]] for i in range(len(self.agents))])
				self.T[ai][si][Problem.get_state_code(self.locs,nxt)] = 1.0


	def parse_policy(self, policy):
		px = {}
		for si,s in enumerate(self.s):
			entry = []
			for a,ai in self.agents.items():
				pol = policy[si]
				origin_idx = s[ai]
				dest_idx = self.A[self.a[pol][ai]][s[ai]]
				origin = self.problem['locs'][origin_idx]
				dest = self.problem['locs'][dest_idx]
				entry.append('%s: move(%s,%s)'%(a, origin, dest))
			statex = ' and '.join(['at(%s,%s)'%(self.problem['agents'][ai],self.problem['locs'][l]) for ai,l in enumerate(s)])
			px[statex] = entry
		return px

#!/usr/bin/env python

from collections import OrderedDict
from tqdm import tqdm
import numpy as np
import itertools as it
import yaml

class Problem:

	@staticmethod
	def encodex(data,code=None):
		if code is None:
			return OrderedDict([(e,i) for i,e in enumerate(data)])
		else:
			return [[code[e] for e in d] for d in data]

	@staticmethod
	def get_state_code(locs,goal_state):
		return sum([g*(len(locs)**i) for i,g in enumerate(reversed(goal_state))])

	def encoder(self):

		# Lists
		self.locs	= Problem.encodex(self.problem['locs'])
		self.agents	= Problem.encodex(self.problem['agents'])
		self.items	= {k:v for d in [self.locs,self.agents] for k,v in d.items()}

		# Relations
		self.roads	= Problem.encodex(self.problem['roads'],self.items)
		self.goals	= Problem.encodex(self.problem['goal']['at'],self.items)

		# Dataset
		self.els = {
			'locs':		Problem.encodex(self.problem['locs']),
			'agents':	Problem.encodex(self.problem['agents']),
			'items':	{k:v for d in [self.locs,self.agents] for k,v in d.items()},
		}

	def encode(self, cls, name):
		return self.els[cls][name]

	def decode(self, cls, num):
		return self.els[cls].keys()[num]

	def __init__(self,filename):

		# Loading problem description
		with open(filename,'r') as f:
			self.problem = yaml.load(f.read())
		self.encoder()

		# Enumerating states
		self.s = list(it.product(range(len(self.locs)),repeat=len(self.agents)))

		# List of node adjacency
		node_connectivity = [[] for l in self.locs]
		for r in self.roads:
			node_connectivity[r[0]].append(r[1])

		# Max number of connections per node
		nact = max([len(a) for a in node_connectivity])

		# Action-transition matrix
		self.agent_transition = np.zeros((nact,len(self.locs))).astype(np.int32)
		for a in range(nact):
			for s in range(len(self.locs)):
				self.agent_transition[a][s] = node_connectivity[s][a] if len(node_connectivity[s]) > a else s

		# Enumerating actions
		self.a = list(it.product(range(nact),repeat=len(self.agents)))
		self.n = len(self.s)
		self.m = len(self.a)

		print 'Flattening R...'
		self.R = np.zeros((self.m,self.n),dtype=np.float32)
		for si,s in enumerate(self.s):
			for a in range(self.m):
				for agx in range(len(self.agents)):
					if self.goals[agx][1] == s[agx]:
						self.R[a][si] += 1.0

		print 'Flattening T...'
		self.T = np.zeros((self.m,self.n,self.n),dtype=np.float32)
		for si,s in enumerate(tqdm(self.s)):
			for ai,a in enumerate(self.a):
				nxt = tuple([self.agent_transition[a[i]][s[i]] for i in range(len(self.agents))])
				self.T[ai][si][Problem.get_state_code(self.locs,nxt)] = 1.0


	def parse_policy(self, policy):
		px = {}
		for si,s in enumerate(self.s):
			entry = []
			for a,ai in self.agents.items():
				pol = policy[si]
				origin_idx = s[ai]
				dest_idx = self.agent_transition[self.a[pol][ai]][s[ai]]
				origin = self.problem['locs'][origin_idx]
				dest = self.problem['locs'][dest_idx]
				entry.append('%s: move(%s,%s)'%(a, origin, dest))
			statex = ' and '.join(['at(%s,%s)'%(self.problem['agents'][ai],self.problem['locs'][l]) for ai,l in enumerate(s)])
			px[statex] = entry
		return px

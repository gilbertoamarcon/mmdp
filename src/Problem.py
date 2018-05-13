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

		# Relations
		items		= {k:v for d in [self.locs,self.agents] for k,v in d.items()}
		self.roads	= Problem.encodex(self.problem['roads'],items)
		self.goals	= Problem.encodex(self.problem['goal']['at'],items)

		# Dataset
		self.data = {
			'locs':		Problem.encodex(self.problem['locs']),
			'agents':	Problem.encodex(self.problem['agents']),
		}

		self.num_agents	= len(self.agents)
		self.num_locs	= len(self.locs)

	def encode(self, cls, name):
		return self.data[cls][name]

	def decode(self, cls, num):
		return self.data[cls].keys()[num]

	def __init__(self,filename):

		# Loading problem description
		with open(filename,'r') as f:
			self.problem = yaml.load(f.read())
		self.encoder()

		# Connectivity boolean matrix
		self.conn = np.zeros((self.num_locs,self.num_locs)).astype(np.bool_)
		for r in self.roads:
			self.conn[r[0]][r[1]] = 1

		# Transition matrix
		x = np.linspace(0, self.num_locs-1, self.num_locs).astype(np.int32)
		y = np.linspace(0, self.num_locs-1, self.num_locs).astype(np.int32)
		xv, yv = np.meshgrid(x,y)
		self.agent_transition = np.multiply(yv,self.conn)+np.multiply(xv,np.invert(self.conn))

		# Enumerating states and actions
		self.s = list(it.product(self.locs.values(),repeat=self.num_agents))
		self.a = list(it.product(self.locs.values(),repeat=self.num_agents))
		self.n = len(self.s)
		self.m = len(self.a)

		print 'Flattening R...'
		self.R = np.zeros((self.m,self.n),dtype=np.float32)
		for si,s in enumerate(self.s):
			for agent_idx in self.agents.values():
				if self.goals[agent_idx][1] == s[agent_idx]:
					for a in range(self.m):
						self.R[a][si] += 1.0

		print 'Flattening T...'
		self.T = np.zeros((self.m,self.n,self.n),dtype=np.float32)
		for ai,a in enumerate(tqdm(self.a)):
			for si,s in enumerate(self.s):
				nxt = tuple([self.agent_transition[a[i]][s[i]] for i in self.agents.values()])
				self.T[ai][si][Problem.get_state_code(self.locs,nxt)] = 1.0


	def parse_policy(self, raw_policy):
		policy = []
		for si,s in enumerate(self.s):
			policy_action_idx		= raw_policy[si]
			policy_action			= self.a[policy_action_idx]
			state_buffer			= []
			action_buffer			= []

			for agent_idx in self.agents.values():
				agent_origin_idx	= s[agent_idx]
				agent_action		= policy_action[agent_idx]
				agent_dest_idx		= self.agent_transition[agent_action][agent_origin_idx]
				agent				= self.decode('agents',agent_idx)
				origin 				= self.decode('locs',agent_origin_idx)
				dest				= self.decode('locs',agent_dest_idx)
				action_buffer.append(['move',agent,origin,dest])
				state_buffer.append(['at',agent,origin])
			policy.append([state_buffer,action_buffer])

		return policy

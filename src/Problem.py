#!/usr/bin/env python

from collections import OrderedDict
import yaml

class Problem:

	@staticmethod
	def expand(problem,name,ctr=0):
		if ctr >= len(problem['agents']):
			return None
		local = [[(problem['agents'][ctr],action)] for action in problem[name]]
		nxt = Problem.expand(problem,name,ctr+1)
		if nxt is None:
			return local
		else:
			return [current+n for current in local for n in nxt]

	@staticmethod
	def to_str(problem,state):
		return '_'.join(['_'.join(e) for e in state.items()])

	def __init__(self,filename):
		with open(filename,'r') as f:
			self.problem = yaml.load(f.read())
		self.states = [OrderedDict(e) for e in Problem.expand(self.problem,'locs')]
		self.actions = [OrderedDict(e) for e in Problem.expand(self.problem,'actions')]
		self.n = len(self.states)
		self.m = len(self.actions)

	def flatten(self):
		self.R = [[1.0 if Problem.to_str(self.problem,s) == '_'.join(['_'.join(g) for g in self.problem['goal']['at']]) else 0 for a in self.actions] for s in self.states]
		self.T = [[[0 for sn in self.states] for s in self.states] for a in self.actions]
		for si,s in enumerate(self.states):
			for ai,a in enumerate(self.actions):
				nxt = OrderedDict([(agent,self.problem['actions'][a[agent]][s[agent]]) for agent in self.problem['agents']])
				for sni, sn in enumerate(self.states):
					if sn == nxt:
						self.T[ai][si][sni] = 1.0

	def parse_policy(self, policy):
		return {agent:{s[agent]: self.actions[policy[i]][agent] for i,s in enumerate(self.states)} for agent in self.problem['agents']}


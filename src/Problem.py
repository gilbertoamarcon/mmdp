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

	def __init__(self):
		pass

	def synth(self, problem):
		states = [OrderedDict(e) for e in Problem.expand(problem,'locs')]
		actions = [OrderedDict(e) for e in Problem.expand(problem,'actions')]
		self.n = len(states)
		self.m = len(actions)
		self.R = [[1.0 if Problem.to_str(problem,s) == '_'.join(['_'.join(g) for g in problem['goal']['at']]) else 0 for a in actions] for s in states]
		self.T = [[[0 for sn in states] for s in states] for a in actions]
		for si,s in enumerate(states):
			for ai,a in enumerate(actions):
				nxt = OrderedDict([(agent,problem['actions'][a[agent]][s[agent]]) for agent in problem['agents']])
				for sni, sn in enumerate(states):
					if sn == nxt:
						self.T[ai][si][sni] = 1.0

	def translate(self, problem, solution):
		states = [OrderedDict(e) for e in Problem.expand(problem,'locs')]
		actions = [OrderedDict(e) for e in Problem.expand(problem,'actions')]
		self.n = len(states)
		self.m = len(actions)
		return {agent:{s[agent]: actions[solution[i]][agent] for i,s in enumerate(states)} for agent in problem['agents']}


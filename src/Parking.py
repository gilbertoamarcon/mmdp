#!/usr/bin/env python

from tabulate import tabulate
from collections import OrderedDict
import math

class Parking:

	def __init__(self, problem,solution=None):
		self.n = problem['n']
		self.problem = problem
		self.states = OrderedDict([(k,i) for i,k in enumerate([(row,row_idx,o,p) if row=='B' else (row,self.n-1-row_idx,o,p) for o in [False,True] for p in [False,True] for row in ['B','A'] for row_idx in range(self.n)])])
		self.actions = OrderedDict([(k,i) for i,k in enumerate(['PARK','DRIVE'])])
		if solution is not None:
			self.solution = solution
	
	def __str__(self):
		return '\n'.join([
			'\nActions:',
			'\n'.join('%*d %s'% (1+int(math.log10(len(self.actions.items())-1)),v,str(k)) for k,v in self.actions.items()),
			'\nStates:',
			'\n'.join('%*d %s'% (1+int(math.log10(len(self.states.items())-1)),v,'Row: %s Spot: %d Ocupied: %d Parked: %d'%k) for k,v in self.states.items()),
		])


	def drive(self, row, row_idx):
		if row == 'B':
			row_idx += 1
			if row_idx >= self.n:
				row_idx -= 1
				row = 'A'
		else:
			row_idx -= 1
			if row_idx < 0:
				row_idx += 1
				row = 'B'
		return row,row_idx

		return self.states.keys()[state_idx]

	def get_state(self, state_idx):
		row, row_idx, o, p = self.states.keys()[state_idx]
		return OrderedDict([
			('row', row),
			('row_idx', row_idx),
			('o', o),
			('p', p),
		])

	def get_state_idx(self, state):
		return self.states[tuple(state.values())]

	def get_transitions(self):
		T = []
		for a in self.actions:
			T.append([])
			for sa in self.states.values():
				T[-1].append([])
				state_a = self.get_state(sa)
				state_b = self.get_state(sa)
				nxt = len(self.states)*[0.0]
				if state_a['p']:
					nxt[self.get_state_idx(state_a)] = 1.0
				else:
					if a == 'DRIVE':
						state_b['row'],state_b['row_idx'] = self.drive(state_a['row'],state_a['row_idx'])
						chc = float(self.n-state_b['row_idx'])/float(self.n) if state_b['row_idx'] else self.problem['transitions']['handicap']
						state_b['o'] = True
						nxt[self.get_state_idx(state_b)] = chc
						state_b['o'] = False
						nxt[self.get_state_idx(state_b)] = 1.0-chc
					if a == 'PARK':
						state_b['p'] = True
						nxt[self.get_state_idx(state_b)] = 1.0
				T[-1][-1] = nxt
		return T

	def get_rewards(self):
		rewards = []
		for s in self.states.values():
			aux = []
			for a in self.actions:
				state = self.get_state(s)
				if state['p']:
					rwd = 0.0
				if not state['p'] and a == 'DRIVE':
					rwd = self.problem['rewards']['not_parked']
				if not state['p'] and a == 'PARK' and state['o']:
					rwd = self.problem['rewards']['collision']
				if not state['p'] and a == 'PARK' and not state['o']:
					rwd = self.problem['rewards']['distance_cost']*state['row_idx'] + self.problem['rewards']['handicap']*(state['row_idx']==0)
				aux.append(rwd)
			rewards.append(aux)
		return rewards

	def get_num_states(self):
		return len(self.states)

	def get_num_actions(self):
		return len(self.actions)
	
	def analyse(self):
		if self.solution is not None:
			for s in self.solution:
				table = []
				table.append(['\multicolumn{2}{c}{Spot}','','\multicolumn{2}{c}{Not Parked}','','\multicolumn{2}{c}{Parked}',''])
				table.append(['Row','Number','Free','Occupied','Free','Occupied'])
				for row in ['A','B']:
					for row_idx in range(self.n):
						number_format = '%d' if s == 'policy' else '%.3f'
						row_label = '\\multirow{%d}{*}{%s}'%(self.n,row) if not row_idx else ''
						table.append([row_label,str(row_idx)]+['%.3f'%self.solution[s][self.states[(row,row_idx,o,p)]] if s == 'value' else self.actions.keys()[self.solution[s][self.states[(row,row_idx,o,p)]]] for p in [False,True] for o in [False,True]])
				print tabulate(table, headers='firstrow', tablefmt='latex_raw')


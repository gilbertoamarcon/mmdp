#!/usr/bin/env python

from collections import OrderedDict
from tqdm import tqdm
import numpy as np
import itertools as it
import yaml
import re
import networkx as nx
import matplotlib.pyplot as plt


class Problem:

	@staticmethod
	def encodex(data,code=None):
		if code is None:
			return OrderedDict([(e,i) for i,e in enumerate(data)])
		else:
			if type(data) is list:
				return [Problem.encodex(d,code) for d in data]
			if type(data) is dict:
				return {Problem.encodex(k,code):Problem.encodex(v,code) for k,v in data.items()}
			return code[data]

	@staticmethod
	def get_state_code(locs,goal_state):
		return sum([g*(len(locs)**i) for i,g in enumerate(reversed(goal_state))])

	def encoder(self):


		# Lists
		self.types		= Problem.encodex(self.problem['types'])
		self.locs		= Problem.encodex(self.problem['locs'])
		self.agents		= Problem.encodex([a[0] for a in self.problem['agents']])

		# Relations
		items			= {k:v for d in [self.types,self.locs,self.agents] for k,v in d.items()}
		self.roads		= Problem.encodex(self.problem['roads'],items)
		self.goals		= Problem.encodex(self.problem['goal'],items)
		self.agent_cls	= Problem.encodex({a[0]:a[1] for a in self.problem['agents']},items)

		# Dataset
		self.data = {
			'types':	Problem.encodex(self.problem['types']),
			'locs':		Problem.encodex(self.problem['locs']),
			'agents':	Problem.encodex([a[0] for a in self.problem['agents']]),
		}

		self.num_types	= len(self.types)
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
			cl = {l:[] for l in s}
			for agent_idx,l in enumerate(s):
				cl[l].append(self.agent_cls[agent_idx])
			ctr = sum([gi in cl and not sum([x not in cl[gi] for x in g]) for gi,g in self.goals.items()])
			for a in range(self.m):
				self.R[a][si] = ctr

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
				if origin == dest:
					action = ['stay',agent,origin]
				else:
					action = ['move',agent,origin,dest]
				state_buffer.append(['at',agent,origin])
				action_buffer.append(action)
			policy.append([state_buffer,action_buffer])

		return policy

	def plot(self, policy, file_prefix):

		print 'Generating and storing plots...'
		for i,p in enumerate(tqdm(policy)):

			agts = [e[2] for e in p[0]]

			node_color='w'
			node_size=3000
			font_size=8

			# Building the graph
			G = nx.Graph()
			for node in self.problem['locs']:
				G.add_node(node)
			for edge in self.problem['roads']:
				G.add_edge(edge[0], edge[1])

			# Draw the graph structure
			pos = nx.spring_layout(G,random_state=0)
			nx.draw(G, pos, node_color=node_color, node_size=node_size)

			nx.draw_networkx_nodes(
									G,
									pos,
									nodelist=self.problem['goal'].keys(),
									node_color='r',
									node_size=node_size,
									alpha=0.5
								)
			# Regular node labels
			labels = {l:'$%s$'%l for l in self.problem['locs'] if l not in agts}
			nx.draw_networkx_labels(G, pos, labels, font_size=font_size)

			# Agent labels
			agx = {e:[] for e in agts}
			for e in p[1]:
				aux = '%s>%s'%(e[1],e[3]) if len(e) == 4 else e[1]
				agx[e[2]].append(aux)

			agents = {k:'\n'.join([k]+v) for k,v in agx.items()}
			agents = {k:re.sub(r'([A-Za-z_>]+)(\d+)', r'$\1{\2}$', v) for k,v in agents.items()}
			nx.draw_networkx_labels(G, pos, agents, font_size=font_size)

			plt.savefig(file_prefix%i)
			plt.clf()

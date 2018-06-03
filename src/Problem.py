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

	def decode(self, cls, num):
		return self.data[cls].keys()[num]

	def __init__(self,filename):

		# Loading problem description
		with open(filename,'r') as f:
			self.problem = yaml.load(f.read())
		self.encoder()

		# Connectivity boolean matrix
		conn = np.zeros((self.num_locs,self.num_locs)).astype(np.bool_)
		for r in self.roads:
			conn[r[0]][r[1]] = 1

		# Transition matrix
		x = np.linspace(0, self.num_locs-1, self.num_locs).astype(np.int32)
		y = np.linspace(0, self.num_locs-1, self.num_locs).astype(np.int32)
		xv, yv = np.meshgrid(x,y)
		self.agent_transition = np.multiply(yv,conn)+np.multiply(xv,np.invert(conn))

		# Enumerating states and actions
		self.s = list(it.product(self.locs.values(),repeat=self.num_agents))
		self.a = list(it.product(self.locs.values(),repeat=self.num_agents))
		self.n = len(self.s)
		self.m = len(self.a)

	def flatten(self):
		
		print 'Flattening R...'
		self.R = np.zeros((self.m,self.n),dtype=np.float32)
		for si,s in enumerate(self.s):
			for ai,a in enumerate(self.a):
				agent_classes_on_loc = {l:[] for l in s}
				for agent_idx,l in enumerate(s):
					if a[agent_idx] == l:
						agent_classes_on_loc[l].append(self.agent_cls[agent_idx])
				self.R[ai][si] = sum([gi in agent_classes_on_loc and not sum([x not in agent_classes_on_loc[gi] for x in g]) for gi,g in self.goals.items()])

		print 'Flattening T...'
		self.T = np.zeros((self.m,self.n,self.n),dtype=np.float32)
		for ai,a in enumerate(tqdm(self.a)):
			for si,s in enumerate(self.s):
				sn_prob = []
				for i in self.agents.values():
					agent_next_loc_prob = self.problem['error']*np.ones(self.num_locs,dtype=np.float32)/(self.num_locs-1)
					agent_next_loc_prob[self.agent_transition[a[i]][s[i]]] = 1.0-self.problem['error']
					sn_prob.append(agent_next_loc_prob)
				for sni,sn in enumerate(self.s):
					self.T[ai][si][sni] = sum([sn_prob[i][sn[i]] for i in self.agents.values()])
				norm = sum(self.T[ai][si])
				self.T[ai][si] /= norm

	def parse_policy(self, raw_policy):
		policy = []
		for si,s in enumerate(self.s):
			policy_action_idx		= raw_policy[si]
			policy_action			= self.a[policy_action_idx]
			state_buffer			= {}
			action_buffer			= {}

			for agent_idx in self.agents.values():
				agent_origin_idx	= s[agent_idx]
				agent_action		= policy_action[agent_idx]
				agent_dest_idx		= self.agent_transition[agent_action][agent_origin_idx]
				agent				= self.decode('agents',agent_idx)
				origin 				= self.decode('locs',agent_origin_idx)
				dest				= self.decode('locs',agent_dest_idx)
				if origin == dest:
					action = ['stay',origin]
				else:
					action = ['move',origin,dest]
				state_buffer[agent] = ['at',origin]
				action_buffer[agent] = action
			policy.append({'state':state_buffer,'action':action_buffer})

		return policy

	def plot(self, policy, file_prefix):

		print 'Generating and storing plots...'
		for i,p in enumerate(tqdm(policy)):

			agts = [p['state'][e][1] for e in p['state']]

			node_color='w'
			node_size=10000
			font_size=16

			# Building the graph
			plt.figure(figsize=(14,10)) 
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
			for agent in self.agents.keys():
				aux = '%s>%s'%(agent,p['action'][agent][2]) if len(p['action'][agent]) == 3 else agent
				agx[p['action'][agent][1]].append(aux)

			agents = {k:'\n'.join([k]+v) for k,v in agx.items()}
			agents = {k:re.sub(r'([A-Za-z_>]+)(\d+)', r'$\1{\2}$', v) for k,v in agents.items()}
			nx.draw_networkx_labels(G, pos, agents, font_size=font_size)

			plt.savefig(file_prefix%i)
			plt.clf()
			plt.close()

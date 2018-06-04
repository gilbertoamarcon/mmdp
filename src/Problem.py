#!/usr/bin/env python

from tqdm import tqdm
import numpy as np
import itertools as it
import yaml
import random
import networkx as nx
import numbers
import matplotlib.pyplot as plt

# List with fast index query
class DualList:

	def __init__(self, list):
		self.list = list
		self.rev = {value:index for index,value in enumerate(list)}
		
	def __str__(self):
		return self.list.__str__()

	def __getitem__(self, key):

		# Get value from index
		if isinstance(key, numbers.Number):
			return self.list[key]

		# Get index from value
		else:
			return self.rev[key]

	def __setitem__(self, key, value):
		if type(key) is int:
			self.list[key] = value
			self.rev[value] = key

	def __len__(self):
		return len(self.list)


class Problem:

	def __init__(self,filename):

		# Loading problem description
		with open(filename,'r') as f:
			self.problem = yaml.load(f.read())

		# Error tolerance
		self.error				= self.problem['error']

		# Lists
		self.agents				= DualList([a[0] for a in self.problem['agents']])
		self.types				= DualList(self.problem['types'])
		self.locs				= DualList(self.problem['locs'])

		# Named Relationships
		self.name_roads			= self.problem['roads']
		self.agents_types		= {a[0]:a[1] for a in self.problem['agents']}
		self.name_goal			= self.problem['goal']

		# Idx Relationships
		self.idx_roads			= [[self.locs[l] for l in r] for r in self.problem['roads']]
		self.idx_agents_types	= {self.agents[a[0]]:self.types[a[1]] for a in self.problem['agents']}
		self.idx_goals			= {self.locs[loc]:[self.types[t] for t in type] for loc,type in self.problem['goal'].items()}

		# Connectivity boolean matrix
		conn = np.zeros((len(self.locs),len(self.locs))).astype(np.bool_)
		for r in self.name_roads:
			conn[self.locs[r[0]]][self.locs[r[1]]] = 1

		# Transition matrix
		x = np.linspace(0, len(self.locs)-1, len(self.locs)).astype(np.int32)
		y = np.linspace(0, len(self.locs)-1, len(self.locs)).astype(np.int32)
		xv, yv = np.meshgrid(x,y)
		self.agent_transition = np.multiply(yv,conn)+np.multiply(xv,np.invert(conn))

		# Enumerating states and actions
		self.s = list(it.product(range(len(self.locs)),repeat=len(self.agents)))
		self.a = list(it.product(range(len(self.locs)),repeat=len(self.agents)))
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
						agent_classes_on_loc[l].append(self.idx_agents_types[agent_idx])
				self.R[ai][si] = sum([gi in agent_classes_on_loc and not sum([x not in agent_classes_on_loc[gi] for x in g]) for gi,g in self.idx_goals.items()])

		print 'Flattening T...'
		self.T = np.zeros((self.m,self.n,self.n),dtype=np.float32)
		for ai,a in enumerate(tqdm(self.a)):
			for si,s in enumerate(self.s):
				sn_prob = []

				# For each agent
				for agent_idx,agent in enumerate(self.agents):
					agent_next_loc_prob = self.error*np.ones(len(self.locs),dtype=np.float32)/(len(self.locs)-1)
					agent_next_loc_prob[self.agent_transition[a[agent_idx]][s[agent_idx]]] = 1.0-self.error
					sn_prob.append(agent_next_loc_prob)

				# For each next state
				for sni,sn in enumerate(self.s):
					self.T[ai][si][sni] = sum([sn_prob[agent_idx][sn[agent_idx]] for agent_idx,agent in enumerate(self.agents)])

				# Normalizing
				self.T[ai][si] /= sum(self.T[ai][si])

	def parse_policy(self, raw_policy):
		policy = []
		for si,s in enumerate(self.s):
			policy_action_idx		= raw_policy[si]
			policy_action			= self.a[policy_action_idx]
			state_buffer			= {}
			action_buffer			= {}

			for agent_idx,agent in enumerate(self.agents):
				agent_origin_idx	= s[agent_idx]
				agent_action		= policy_action[agent_idx]
				agent_dest_idx		= self.agent_transition[agent_action][agent_origin_idx]
				origin 				= self.locs[agent_origin_idx]
				dest				= self.locs[agent_dest_idx]
				if origin == dest:
					action = ['stay',origin]
				else:
					action = ['move',origin,dest]
				state_buffer[agent] = ['at',origin]
				action_buffer[agent] = action
			policy.append({'state':state_buffer,'action':action_buffer})

		return policy

	def plot(self, policy, file_prefix):

		# Parameters
		regular_node_color	= 'w'
		goal_node_color		= 'g'
		goal_node_alpha		= 0.5
		node_size			= 25000
		font_size			= 18
		figsize				= (14,10)

		# For each state
		print 'Generating and storing plots...'
		for i,p in enumerate(tqdm(policy)):

			# Agent locations
			agent_locs = [p['state'][e][1] for e in p['state']]

			# Figure
			plt.figure(figsize=figsize) 

			# Building the graph
			G = nx.Graph()

			# Locations
			for node in self.locs:
				G.add_node(node)

			# Roads
			for edge in self.name_roads:
				G.add_edge(edge[0], edge[1])

			# Drawing the graph structure
			pos = nx.spring_layout(G,random_state=0)
			nx.draw(G, pos, node_color=regular_node_color, node_size=node_size)

			# Goal node shading
			nx.draw_networkx_nodes(
									G,
									pos,
									nodelist	= self.name_goal.keys(),
									node_color	= goal_node_color,
									node_size	= node_size,
									alpha		= goal_node_alpha
								)

			# Node labels
			labels = {}
			for l,loc in enumerate(self.locs):

				# Location name and goal requirements
				labels[loc] = '$%s%s$'%(loc,'(%s)'%','.join(self.types[self.idx_agents_types[k]] for k in self.idx_goals[l]) if l in self.idx_goals else '')

				# For each agent at loc
				agent_at_locs = [agent_idx for agent_idx,agent_loc in enumerate(agent_locs) if agent_loc == loc]
				for a,c in [(self.agents[agent_idx],self.types[self.idx_agents_types[agent_idx]]) for agent_idx in agent_at_locs]:
					labels[loc] += '\n$%s(%s)>%s$'%(a,c,p['action'][a][-1]) if len(p['action'][a]) == 3 else '\n$%s(%s)$'%(a,c)

			# Adding Labels
			nx.draw_networkx_labels(G, pos, labels, font_size=font_size)

			# Saving and clearing
			plt.savefig(file_prefix%i)
			plt.clf()
			plt.close()

	def simulate(self, policy, file_prefix):

		agent_states = {agent:None for agent in self.agents}

		dict_pol = {tuple([p['state'][agent][1] for agent in self.agents]):p['action'] for p in policy}

		print ''
		print 'Goal State Set:'
		print self.name_goal


		print ''
		print 'Initial State:'
		for agent in self.agents:
			agent_states[agent] = random.choice(self.locs)
			print '%s: %s' % (agent,agent_states[agent])

		print ''
		print 'Steps'
		for i in range(10):

			# State tuple
			state = tuple([agent_states[agent] for agent in self.agents])

			# Types of agent on each state
			types_on_state = {s:[] for s in state}
			for agent in self.agents:
				types_on_state[agent_states[agent]].append(self.agents_types[agent])

			# Action at this state 
			pol = dict_pol[state]
			agent_states = {agent:pol[agent][-1] for agent in self.agents}

			# Computing rewards
			rwd = 0
			for g in self.name_goal:
				if g in types_on_state:
					goal_set = set(self.name_goal[g])
					current_set = set(types_on_state[g])
					if not goal_set - current_set:
						rwd += 1

			stx =  self.s.index(tuple([self.locs[s] for s in state]))
			print i, stx, state, types_on_state, rwd
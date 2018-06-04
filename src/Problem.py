#!/usr/bin/env python

from tqdm import tqdm
import numpy as np
import itertools as it
import yaml
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
		self.name_loc_roads		= {loc:[] for loc in self.locs}
		for road in self.name_roads:
			self.name_loc_roads[road[0]].append(road[1])

		# Idx Relationships
		self.idx_roads			= [[self.locs[road[0]],self.locs[road[1]]] for road in self.problem['roads']]
		self.idx_agents_types	= {self.agents[a[0]]:self.types[a[1]] for a in self.problem['agents']}
		self.idx_goals			= {self.locs[loc]:[self.types[t] for t in type] for loc,type in self.problem['goal'].items()}
		self.idx_loc_roads		= {loc_idx:[] for loc_idx,loc in enumerate(self.locs)}
		for road_idx in self.idx_roads:
			self.idx_loc_roads[road_idx[0]].append(road_idx[1])

		# Connectivity boolean matrix
		conn = np.zeros((len(self.locs),len(self.locs))).astype(np.bool_)
		for road in self.name_roads:
			conn[self.locs[road[0]]][self.locs[road[1]]] = 1

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

		# Initializing reward table
		self.R = np.zeros((self.m,self.n),dtype=np.float32)

		# For each state
		for si,s in enumerate(self.s):

			# For each action
			for ai,a in enumerate(self.a):

				# Agents classes staying at each location
				agent_classes_on_loc = {loc_idx:[] for loc_idx in s}

				# For each agent
				for agent_idx,loc_idx in enumerate(s):

					# If agent action is to stay
					if a[agent_idx] == loc_idx:

						# Register agent's class at location
						agent_classes_on_loc[loc_idx].append(self.idx_agents_types[agent_idx])
				
				# Computing reward
				self.R[ai][si] = 0

				# For each goal requirement, location id and list of type ids
				for loc_idx,types_idx in self.idx_goals.items():

					# If there are the location has agents on it 
					if loc_idx in agent_classes_on_loc:

						# All the required types at location have been filled by agents at the location
						if not (set(types_idx)-set(agent_classes_on_loc[loc_idx])):
							self.R[ai][si] += 1


		print 'Flattening T...'

		# Initializing transition table
		self.T = np.zeros((self.m,self.n,self.n),dtype=np.float32)

		# For each action
		# for ai,a in enumerate(tqdm(self.a)):
		for ai,a in enumerate(self.a):

			# For each state
			for si,s in enumerate(self.s):

				# For each agent
				sn_prob = []
				for agent_idx,agent in enumerate(self.agents):

					# Locations adjacent to the agent location
					adj_loc_idxs = self.idx_loc_roads[s[agent_idx]]

					# Baseline probability of going to any adjacent location (error)
					agent_next_loc_prob = np.zeros(len(self.locs),dtype=np.float32)
					for adj_loc_idx in adj_loc_idxs:
						agent_next_loc_prob[adj_loc_idx] = self.error/(len(adj_loc_idxs)-1)

					# Agent intended next state
					sn = self.agent_transition[a[agent_idx]][s[agent_idx]]

					# Success probability
					agent_next_loc_prob[sn] = 1.0-self.error

					# Next state probabilities
					sn_prob.append(agent_next_loc_prob)

				# For each next state
				for sni,sn in enumerate(self.s):

					# Probability of going to next state sn
					self.T[ai][si][sni] = np.prod([sn_prob[agent_idx][sn[agent_idx]] for agent_idx,agent in enumerate(self.agents)])


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
		# for i,pol in enumerate(tqdm(policy)):
		for i,pol in enumerate(policy):

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
			for loc in self.locs:

				# Location name and goal requirements
				labels[loc] = '$%s%s$'%(loc,'(%s)'%','.join(self.name_goal[loc]) if loc in self.name_goal else '')

				# For each agent at loc
				for agent,type in [(agent,self.agents_types[agent]) for agent in pol['state'] if pol['state'][agent][-1] == loc]:
					labels[loc] += '\n$%s(%s)%s$'%(agent,type,'>'+pol['action'][agent][-1] if pol['action'][agent][0] == 'move' else '')

			# Adding Labels
			nx.draw_networkx_labels(G, pos, labels, font_size=font_size)

			# Saving and clearing
			plt.savefig(file_prefix%i)
			plt.clf()
			plt.close()

	def simulate(self, policy, file_prefix):

		agent_locs = {agent:None for agent in self.agents}

		pol = {tuple([pol['state'][agent][1] for agent in self.agents]):pol['action'] for pol in policy}

		print ''
		print 'Goal State Set:'
		print self.name_goal


		print ''
		print 'Initial State:'
		for agent in self.agents:
			agent_locs[agent] = np.random.choice(self.locs)
			print '%s: %s' % (agent,agent_locs[agent])

		print ''
		print 'Steps'
		for i in range(10):

			# State tuple
			state = tuple([agent_locs[agent] for agent in self.agents])

			# Types of agent on each location
			agent_classes_on_loc = {loc:[] for loc in state}
			for agent in self.agents:
				agent_classes_on_loc[agent_locs[agent]].append(self.agents_types[agent])

			# Updating agent location, given policy
			agent_locs = {}
			for agent in self.agents:

				# Baseline probability of going to any state (error)
				pdf = self.error*np.ones(len(self.locs),dtype=np.float32)/(len(self.locs)-1)

				# Agent intended next state
				sn = self.locs[pol[state][agent][-1]]

				# Success probability
				pdf[sn] = 1.0-self.error

				# Transition
				agent_locs[agent] = np.random.choice(self.locs,p=pdf)

			# Computing rewards
			rwd = 0
			for loc,types in self.name_goal.items():
				if loc in agent_classes_on_loc:
					if not (set(types) - set(agent_classes_on_loc[loc])):
						rwd += 1

			# State idx
			stx =  self.s.index(tuple([self.locs[s] for s in state]))

			# Printing history
			print i, stx, agent_locs, state, agent_classes_on_loc, rwd
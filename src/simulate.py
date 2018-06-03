#!/usr/bin/env python

import argparse as ap
from Mdp import *
from Problem import *
import random

# Main
def main():

	# Parsing user input
	parser = ap.ArgumentParser()
	parser.add_argument(
			'-i','--input_problem',
			nargs='?',
			required=True,
			help='Input problem file (YAML filename).'
		)
	parser.add_argument(
			'-s','--input_solution',
			nargs='?',
			required=True,
			help='Input solution file (YAML filename).'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output image file (directory and file prefix).'
		)
	args = parser.parse_args()

	prob = Problem(args.input_problem)

	with open(args.input_problem,'r') as f:
		problem = yaml.load(f.read())

	with open(args.input_solution,'r') as f:
		policy = yaml.load(f.read())

	print problem['locs']
	agents = [a[0] for a in problem['agents']]
	agent_classes = {a[0]:a[1] for a in problem['agents']}
	agent_states = {a[0]:None for a in problem['agents']}
	print agent_classes

	dict_pol = {tuple([p['state'][a][1] for a in agents]):p['action'] for p in policy}

	print ''
	print 'Goal State Set:'
	print problem['goal']


	print ''
	print 'Initial State:'
	for a in agents:
		agent_states[a] = random.choice(problem['locs'])
		print '%s: %s' % (a,agent_states[a])

	print ''
	print 'Steps'
	for i in range(10):

		# State tuple
		state = tuple([agent_states[a] for a in agents])

		# Types of agent on each state
		types_on_state = {s:[] for s in state}
		for a in agents:
			types_on_state[agent_states[a]].append(agent_classes[a])

		# Action at this state 
		pol = dict_pol[state]
		agent_states = {a:pol[a][-1] for a in agents}

		# Computing rewards
		rwd = 0
		for g in problem['goal']:
			if g in types_on_state:
				goal_set = set(problem['goal'][g])
				current_set = set(types_on_state[g])
				if not goal_set - current_set:
					rwd += 1

		stx =  prob.s.index(tuple([prob.data['locs'][s] for s in state]))
		print i, stx, state, types_on_state, rwd





if __name__ == "__main__":
	main()


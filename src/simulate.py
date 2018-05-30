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
	args = parser.parse_args()

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
	for i in range(100):
		state = tuple([agent_states[a] for a in agents])
		goal = {s:[] for s in state}
		for a in agents:
			goal[agent_states[a]].append(agent_classes[a])
		pol = dict_pol[state]
		agent_states = {a:pol[a][-1] for a in agents}
		rwd = 0
		for g in problem['goal']:
			if g in goal:
				goal_set = set(problem['goal'][g])
				current_set = set(goal[g])
				if not goal_set - current_set:
					rwd += 1
		print i, state, goal, pol, rwd





if __name__ == "__main__":
	main()


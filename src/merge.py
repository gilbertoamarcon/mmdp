#!/usr/bin/env python

import argparse as ap
from copy import deepcopy
from Problem import *

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
			'-s','--input_sols',
			nargs='*',
			required=True,
			help='Input policy files (YAML filename).'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output policy file (YAML filename).'
		)
	args = parser.parse_args()



	# Loading problem
	problem = Problem(args.input_problem)

	# Loading solutions
	sols = {s:None for s in args.input_sols}
	for sol_filename in sols:
		with open(sol_filename,'r') as f:
			sols[sol_filename] = yaml.load(f.read())


	# For each state
	pol = []
	for s in problem.s:

		action = {}
		state = {}

		# For each agent 
		for agent_idx,loc_idx in enumerate(s):

			# Agent and agent location
			agent	= problem.agents[agent_idx]
			loc		= problem.locs[loc_idx]

			# Agent state
			state[agent] = ['at',loc]

			# Agent Action
			for sol in sols.values():
				for p in sol:
					if agent in p['action'] and agent in p['state'] and loc in p['state'][agent]:
						action[agent] = p['action'][agent]

		# Appending policy entry: new state and corresponding action
		pol.append({'action':deepcopy(action),'state':deepcopy(state)})

	# Storing merged policy
	with open(args.output, 'w') as f:
		yaml.dump(pol, f)



if __name__ == "__main__":
	main()


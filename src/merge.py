#!/usr/bin/env python

import argparse as ap
from copy import deepcopy
from Problem import *
import itertools as it


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


	sols = {s:None for s in args.input_sols}

	problem = Problem(args.input_problem)

	for sol_filename in sols:
		with open(sol_filename,'r') as f:
			sols[sol_filename] = yaml.load(f.read())

	pol = []
	for s in problem.s:
		action = {}
		state = {}
		for agent_idx,loc_idx in enumerate(s):
			agent	= problem.decode('agents',agent_idx)
			loc 	= problem.decode('locs',loc_idx)
			state[agent] = ['at',loc]
			aux = {agent:p['action'][agent] for sol in sols.values() for p in sol if agent in p['action'] and agent in p['state'] and loc in p['state'][agent]}
			action[agent] = aux[agent]
		pol.append({'action':deepcopy(action),'state':deepcopy(state)})

	with open(args.output, 'w') as f:
		yaml.dump(pol, f)



if __name__ == "__main__":
	main()


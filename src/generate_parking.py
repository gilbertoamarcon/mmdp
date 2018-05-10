#!/usr/bin/env python

from Mdp import *
from Parking import *
import argparse as ap
import yaml

# Main
def main():

	# Parsing user input
	parser = ap.ArgumentParser()
	parser.add_argument(
			'-i','--input',
			nargs='?',
			required=True,
			help='Input YAML file name with the problem parameters.'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output MDP file name.'
		)
	parser.add_argument(
			'-v','--verbose',
			action='count',
			help='Verbose mode.'
		)
	args = parser.parse_args()

	with open(args.input,'r') as f:
		problem = yaml.load(f.read())

	pking = Parking(problem)
	if args.verbose:
		print pking

	mdp = Mdp(
		T=pking.get_transitions(),
		R=pking.get_rewards(),
		n=pking.get_num_states(),
		m=pking.get_num_actions(),
	)

	with open(args.output,'w') as f:
		f.write(str(mdp))

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import argparse as ap
from Mdp import *
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
			'-s','--input_solution',
			nargs='?',
			required=True,
			help='Input solution file (HDF5 filename).'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output image file (directory and file prefix).'
		)
	args = parser.parse_args()

	mdp = Mdp()
	mdp.load_policy(args.input_solution)
	raw_policy = mdp.p

	problem = Problem(args.input_problem)
	policy = problem.parse_policy(raw_policy)
	problem.plot(policy,args.output)


if __name__ == "__main__":
    main()

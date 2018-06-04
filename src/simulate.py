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
			help='Input solution file (YAML filename).'
		)
	parser.add_argument(
			'-f','--figure_template',
			nargs='?',
			required=True,
			help='Figure image file template.'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output html report file (relative directory and file name).'
		)
	parser.add_argument(
			'-x','--iterations',
			nargs='?',
			type=int,
			required=True,
			help='The number of simulation steps.'
		)
	args = parser.parse_args()

	with open(args.input_solution,'r') as f:
		policy = yaml.load(f.read())

	problem = Problem(args.input_problem)
	problem.simulate(policy,args.iterations,args.figure_template,args.output)


if __name__ == "__main__":
	main()


#!/usr/bin/env python

from Problem import *
import argparse as ap
import deepdish as dd
import yaml
import csv

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
			'-s','--solution',
			nargs='?',
			required=True,
			help='Input MDP solution file name.'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output MDP solution file name.'
		)

	args = parser.parse_args()

	with open(args.input,'r') as f:
		yaml_problem = yaml.load(f.read())

	raw = dd.io.load(args.solution)

	prob = Problem()

	sol = prob.translate(yaml_problem,raw['pol'])
	with open(args.output, 'w') as f:
		yaml.dump(sol,f, default_flow_style=False)


if __name__ == "__main__":
    main()

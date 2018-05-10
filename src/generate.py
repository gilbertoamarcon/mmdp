#!/usr/bin/env python

from Mdp import *
from Problem import *
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
		yaml_problem = yaml.load(f.read())

	problem = Problem()
	problem.synth(yaml_problem)

	mdp = Mdp(
		T=problem.T,
		R=problem.R,
		n=problem.n,
		m=problem.m,
	)

	with open(args.output,'w') as f:
		f.write(str(mdp))

if __name__ == "__main__":
    main()

#!/usr/bin/env python

import argparse as ap
from Mdp import *
from Problem import *

# Main
def main():

	# Parsing user input
	parser = ap.ArgumentParser()
	parser.add_argument(
			'-i','--input',
			nargs='?',
			required=True,
			help='Input problem file (YAML filename).'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output problem file (HDF5 filename).'
		)
	args = parser.parse_args()

	problem = Problem(args.input)
	problem.flatten()

	mdp = Mdp(T=problem.T,R=problem.R)
	mdp.store_problem(args.output)

if __name__ == "__main__":
    main()

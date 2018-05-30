#!/usr/bin/env python

import argparse as ap
from Mdp import *


# Main
def main():

	# Parsing user input
	parser = ap.ArgumentParser()
	parser.add_argument(
			'-i','--input',
			nargs='?',
			required=True,
			help='Input problem file (HDF5 filename).'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output solution file (HDF5 filename).'
		)
	parser.add_argument(
			'-d','--discount',
			nargs='?',
			type=float,
			required=True,
			help='The discount value.'
		)
	parser.add_argument(
			'-b','--bound',
			nargs='?',
			type=float,
			default=0.0001,
			help='The bound from the optimal.'
		)
	args = parser.parse_args()

	mdp = Mdp()
	mdp.load_problem(args.input)
	mdp.solve(discount=args.discount,bound=args.bound)
	mdp.store_policy(args.output)




if __name__ == "__main__":
    main()


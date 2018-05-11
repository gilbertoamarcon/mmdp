#!/usr/bin/env python

from Mdp import *
import argparse as ap

# Main
def main():

	# Parsing user input
	parser = ap.ArgumentParser()
	parser.add_argument(
			'-i','--input',
			nargs='?',
			required=True,
			help='Input MDP file name.'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output CSV policy file name.'
		)
	parser.add_argument(
			'-t','--horizon',
			nargs='?',
			type=int,
			default=None,
			help='Time horizon.'
		)
	parser.add_argument(
			'-d','--discount',
			nargs='?',
			type=float,
			default=None,
			help='The discount value.'
		)
	parser.add_argument(
			'-b','--bound',
			nargs='?',
			type=float,
			default=0.1,
			help='The bound from the optimal.'
		)
	args = parser.parse_args()

	# Loading and checking MDP
	mdp = Mdp(args.input)

	# Infinite Horizon
	if args.discount is not None:
		mdp.solve(discount=args.discount,bound=args.bound)
		mdp.store_policy(args.output)




if __name__ == "__main__":
    main()


#!/usr/bin/env python

from Mdp import *
from Parking import *
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
			default=None,
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
			default=0.001,
			help='The bound from the optimal.'
		)
	parser.add_argument(
			'-v','--verbose',
			action='count',
			help='Verbose mode.'
		)
	args = parser.parse_args()

	# Loading and checking MDP
	mdp = Mdp(args.input,verbose=args.verbose)
	error_code = mdp.validate_model()
	if error_code:
		Mdp.print_format_error(error_code=error_code)

	# Finite Horizon
	if args.horizon is not None:
		pol = mdp.finite_horizon_value_iteration(horizon=args.horizon)
		if args.verbose:
			print 'Solution:'
			for k,s in enumerate(pol):
				print '%2d:'%k,' '.join([str(a) for a in s])

	# Infinite Horizon
	if args.discount is not None:
		pol,val = mdp.infinite_horizon_value_iteration(discount=args.discount,bound=args.bound)
		if args.verbose:
			Mdp.print_infinite_horizon_array(pol,'\nSolution:')
			Mdp.print_infinite_horizon_array(val,'\nValue Function:')
		if args.output is not None:
			mdp.store_infinite_horizon_policy(args.output)




if __name__ == "__main__":
    main()


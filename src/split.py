#!/usr/bin/env python

import argparse as ap
from copy import deepcopy
import itertools as it
import yaml

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
			'-c','--input_cf',
			nargs='?',
			required=True,
			help='Input CF file (YAML filename).'
		)
	parser.add_argument(
			'-o','--output_prefix',
			nargs='?',
			required=True,
			help='Prefix.'
		)
	args = parser.parse_args()


	with open(args.input_problem,'r') as f:
		problem = yaml.load(f.read())

	with open(args.input_cf,'r') as f:
		cf = yaml.load(f.read())


	for ct in cf:
		prob = deepcopy(problem)
		prob['goal'] = {ct:problem['goal'][ct]}
		prob['agents'] = [a for a in problem['agents'] if a[0] in cf[ct]]
		with open(args.output_prefix+ct+'.yaml', 'w') as f:
			yaml.dump(prob, f)
	with open(args.output_prefix+'coalitions', 'w') as f:
		f.write(' '.join(cf.keys()))




if __name__ == "__main__":
	main()


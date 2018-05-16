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
			'-c','--output_cf',
			nargs='?',
			required=True,
			help='Output CF file (YAML filename).'
		)
	args = parser.parse_args()

	with open(args.input_problem,'r') as f:
		problem = yaml.load(f.read())

	cf = {}
	for g in problem['goal']:
		cf[g] = []
		while problem['goal'][g]:
			for a in problem['agents']:
				if a[1] in problem['goal'][g]:
					problem['goal'][g].remove(a[1])
					cf[g].append(a[0])
					problem['agents'].remove(a)
					break

	with open(args.output_cf, 'w') as f:
		yaml.dump(cf, f)


if __name__ == "__main__":
	main()


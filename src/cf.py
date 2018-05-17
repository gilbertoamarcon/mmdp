#!/usr/bin/env python

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
			help='Input problem file (YAML filename).'
		)
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output Coalition-Task file (YAML filename).'
		)
	args = parser.parse_args()

	with open(args.input,'r') as f:
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

	with open(args.output, 'w') as f:
		yaml.dump(cf, f)


if __name__ == "__main__":
	main()


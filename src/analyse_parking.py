#!/usr/bin/env python

from Parking import *
import argparse as ap
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

	args = parser.parse_args()

	with open(args.input,'r') as f:
		problem = yaml.load(f.read())

	with open(args.solution,'r') as f:
		data = map(list,zip(*[row for row in csv.reader(f)]))
		solution = {data[0][0]: [int(d) for d in data[0][1:]],data[1][0]: [float(d) for d in data[1][1:]]}

	pking = Parking(problem,solution)

	pking.analyse()


if __name__ == "__main__":
    main()

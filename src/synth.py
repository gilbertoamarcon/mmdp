#!/usr/bin/env python

import argparse as ap
import math
import yaml

def int_str(ceil,i):
	return '%0*d'%(int(math.ceil(math.log10(ceil))),i)

def item_name(template, ceil, nums):
	return template %  tuple([int_str(ceil,i) for i in nums])
	
# Main
def main():

	# Parsing user input
	parser = ap.ArgumentParser()
	parser.add_argument(
			'-o','--output',
			nargs='?',
			required=True,
			help='Output problem file (YAML filename).'
		)
	args = parser.parse_args()

	num_agents = 1
	grid_size = 2

	agent_name_template = r'ag_%s'
	loc_name_template = r'loc_%s_%s'

	# Goal
	goal = {
	  'at': [
	    [(0,),(1,1)],
	  ]
	}

	problem = {}

	# Agents
	problem['agents'] = [item_name(agent_name_template, num_agents, (i,)) for i in range(num_agents)]

	# Objects
	problem['locs']	= [item_name(loc_name_template, grid_size, (i,j)) for i in range(grid_size) for j in range(grid_size)]

	problem['goal'] = {gi: [[item_name(agent_name_template,num_agents,a[0]),item_name(loc_name_template,grid_size,a[1])] for a in g] for gi,g in goal.items()}
	
	# Actions
	problem['actions'] = {}
	problem['actions']['up'] = {}
	problem['actions']['down'] = {}
	problem['actions']['left'] = {}
	problem['actions']['right'] = {}
	for i in range(grid_size):
		for j in range(grid_size):
			problem['actions']['up'][loc_name_template%(i,j)] = loc_name_template%(i,min(j+1,grid_size-1))
			problem['actions']['down'][loc_name_template%(i,j)] = loc_name_template%(i,max(j-1,0))
			problem['actions']['left'][loc_name_template%(i,j)] = loc_name_template%(max(i-1,0),j)
			problem['actions']['right'][loc_name_template%(i,j)] = loc_name_template%(min(i+1,grid_size-1),j)

	with open(args.output, 'w') as f:
		yaml.dump(problem, f, default_flow_style=False)
		# yaml.dump(problem, f)

if __name__ == "__main__":
    main()

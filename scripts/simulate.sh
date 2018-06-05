#!/bin/bash

# 
# Usage:
# ./scripts/simulate.sh <yaml-problem-input> <yaml-solution-output>
# 
# Example:
# ./scripts/simulate.sh problems/rescue.yaml sols/rescue.yaml
# 

# Command-line input parsing
prob=$1
sol=$2

# Simulation
python src/simulate.py -i $prob -s $sol -o sim/run.html -x 10 -f fig/state_%09.svg


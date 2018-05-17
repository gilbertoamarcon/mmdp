#!/bin/bash

# 
# Usage:
# ./scripts/pa.sh <yaml-problem-input> <yaml-solution-output>
# 
# Example:
# ./scripts/pa.sh problems/rescue.yaml sols/rescue.yaml
# 

# Command-line input parsing
prob=$1
sol=$2

# Modules
flatten=src/flatten.py
solve=src/solve.py
parse=src/parse-policy.py

# Temporary directory
temp=temp
rm -Rf $temp > /dev/null 2>&1
mkdir -p $temp

# Planning
python $flatten -i $prob -o $temp/problem.h5
python $solve -i $temp/problem.h5 -o $temp/solution.h5 -d 0.9
python $parse -i $prob -s $temp/solution.h5 -o $sol


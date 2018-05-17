#!/bin/bash

# 
# Usage:
# ./scripts/cfp.sh <yaml-problem-input> <yaml-solution-output>
# 
# Example:
# ./scripts/cfp.sh problems/rescue.yaml sols/rescue.yaml
# 

# Command-line input parsing
prob=$1
sol=$2

# Modules
cf=src/cf.py
split=src/split.py
merge=src/merge.py
flatten=src/flatten.py
solve=src/solve.py
parse=src/parse-policy.py

# Temporary directory
temp=temp
rm -Rf $temp > /dev/null 2>&1
mkdir -p $temp

# Coalition Formation
python $cf -i $prob -o $temp/coalition-tasks.yaml

# Synthesizing coalition-task problems
python $split -i $prob -c $temp/coalition-tasks.yaml -o $temp/problem-

# Planning loop for each coalition-task problem
for t in $(cat $temp/problem-coalitions); do
	python $flatten -i $temp/problem-$t.yaml -o $temp/problem-$t.h5
	python $solve -i $temp/problem-$t.h5 -o $temp/solution-$t.h5 -d 0.9
	python $parse -i $temp/problem-$t.yaml -s $temp/solution-$t.h5 -o $temp/solution-$t.yaml
done

# Merging coalition-task policies into a a global policy
sols=$(for t in $(cat $temp/problem-coalitions); do echo $temp/solution-$t.yaml; done)
python $merge -i $prob -s $sols -o $sol




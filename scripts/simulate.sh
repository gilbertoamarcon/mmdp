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
iter=10
x=2
y=3


# Simulation
for i in {1..5}
do
  name="$prob"_"$x"x"$y"_h"$iter"_"$i"
  mkdir sim/$name
  mkdir sim/$name/fig
  python src/generate-problem.py -e 0.1 -x $x -y $y -d 0.$i -o problems/$name.yaml
  python src/flatten.py -i problems/$name.yaml -o temp/problem.h5
  python src/solve.py -i temp/problem.h5 -o temp/policy.h5 -d 0.9
  python src/parse-policy.py -i problems/$name.yaml -s temp/policy.h5 -o sols/$name.yaml
  python src/plot.py -i problems/$name.yaml -s sols/$name.yaml -o sim/$name/fig/state_%09d.svg
  python src/simulate.py -i problems/$name.yaml -s sols/$name.yaml -o sim/$name/run_$name.html -x $iter -f fig/state_%09d.svg
done


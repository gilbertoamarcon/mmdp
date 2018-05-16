#!/bin/bash

# ./scripts/pa.sh problems/rescue.yaml sols/rescue.yaml

prob=$1
sol=$2

temp=aux

python src/flatten.py -i $prob -o $temp/problem.h5
python src/solve.py -i $temp/problem.h5 -o $temp/solution.h5 -d 0.9
python src/parse-policy.py -i $prob -s $temp/solution.h5 -o $sol



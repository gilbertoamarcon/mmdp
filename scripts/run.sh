#!/bin/bash

prob=$1

# python src/synth.py -o problems/$prob.yaml
python src/flatten.py -i problems/$prob.yaml -o problems/$prob.h5
python src/solve.py -i problems/$prob.h5 -o sols/$prob.h5 -d 0.9
python src/parse-policy.py -i problems/$prob.yaml -s sols/$prob.h5 -o sols/$prob.yaml
python src/plot.py -i problems/$prob.yaml -s sols/$prob.h5 -o plots/graph_%09d.svg


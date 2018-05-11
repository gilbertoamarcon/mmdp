#!/bin/bash

prob=$1

python src/generate.py -i problems/$prob.yaml -o problems/$prob.h5
python src/solve.py -i problems/$prob.h5 -d 0.9 -o sols/$prob.h5
python src/analyse.py -i problems/$prob.yaml -s sols/$prob.h5 -o sols/$prob.yaml

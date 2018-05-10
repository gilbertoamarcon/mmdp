#!/bin/bash

prob=$1

python src/generate_parking.py -i problems/$prob.yaml -o problems/$prob.txt
python src/solve.py -i problems/$prob.txt -d 0.9 -o sols/$prob.csv
python src/analyse_parking.py -i problems/$prob.yaml -s sols/$prob.csv

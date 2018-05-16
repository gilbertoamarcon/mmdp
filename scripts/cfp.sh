#!/bin/bash

# ./scripts/cfp.sh problems/rescue.yaml sols/rescue.yaml

prob=$1
sol=$2

temp=aux
cf=$temp/cf.yaml

python src/cf.py -i $prob -c $cf
python src/split.py -i $prob -c $cf -o $temp/problem-
for t in $(cat $temp/problem-coalitions); do
	python src/flatten.py -i $temp/problem-$t.yaml -o $temp/problem-$t.h5
	python src/solve.py -i $temp/problem-$t.h5 -o $temp/solution-$t.h5 -d 0.9
	python src/parse-policy.py -i $temp/problem-$t.yaml -s $temp/solution-$t.h5 -o $temp/solution-$t.yaml
done
sols=$(for t in $(cat $temp/problem-coalitions); do echo $temp/solution-$t.yaml; done)
python src/merge.py -i $prob -s $sols -o $sol
rm $temp/*



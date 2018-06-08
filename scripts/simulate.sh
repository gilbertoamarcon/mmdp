
prob=$1
iter=10
x=2
y=3


for i in {1..4}
do
  for g in {1..4}
  do
    name="$prob"_"$x"x"$y"_h"$iter"_g"$g"_i
    for k in {1..10}
    do
      python src/simulate.py -i problems/$name.yaml -s sols/$name.yaml -o sim/$name -x $iter -f fig/state_%09d.svg
    done
  done
done

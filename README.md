# Mdp

## Standalone Module Usage


Flatten MDP problem using parameters in the ```problems/rescue.yaml``` file into  ```temp/problem.h5```:
```
python src/flatten.py -i problems/rescue.yaml -o temp/problem.h5
```

Solve the flat MDP problem ```temp/problem.h5``` with discount rate ```0.9```, and store policy to file ```temp/policy.h5```:
```
python src/solve.py -i temp/problem.h5 -o temp/policy.h5 -d 0.9
```

Parse the policy file ```temp/policy.h5``` into a high-level policy file ```sols/rescue.yaml```:
```
python src/parse-policy.py -i problems/rescue.yaml -s temp/policy.h5 -o sols/rescue.yaml
```

Plot the results of the policy file ```sols/rescue.yaml```:
```
python src/plot.py -i problems/rescue.yaml -s sols/rescue.yaml -o sim/fig/state_%09d.svg
```

Simulate the policy file ```sols/rescue.yaml``` and generate graphic HTML report inside directory ```sim/```:
```
python src/simulate.py -i problems/rescue.yaml -s sols/rescue.yaml -f fig/state_%09d.svg -r sim/run.html
```

Example HTML report: [report]:sim/run.html "Report"

## Script Usage

Solving problem ```problems/rescue.yaml``` using Planning Alone and storing the high-level policy ```sols/rescue.yaml```:
```
./scripts/pa.sh problems/rescue.yaml sols/rescue.yaml
```

Solving problem ```problems/rescue.yaml``` using Coalition Formation and Planning and storing the high-level policy ```sols/rescue.yaml```:
```
./scripts/cfp.sh problems/rescue.yaml sols/rescue.yaml
```

![pipeline](cfp-complete.dot.png?raw=true "Data Flow")

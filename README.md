# Mdp

Synthesize MDP problem using parameters in the ```problems/rescue.yaml``` file into  ```problems/rescue.h5```:
```
python src/generate.py -i problems/rescue.yaml -o problems/rescue.h5
```

Solve the MDP problem ```problems/rescue.h5``` with discount rate ```0.9```, and store policy to file ```sols/rescue.h5```:
```
python src/solve.py -i problems/rescue.h5 -d 0.9 -o sols/rescue.h5
```

Analyse the results of the policy file ```sols/rescue.h5```:
```
python src/analyse.py -i problems/rescue.yaml -s sols/rescue.h5 -o sols/rescue.yaml
```

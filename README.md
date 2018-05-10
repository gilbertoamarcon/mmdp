# Mdp

Synthesize MDP problem using parameters in the ```problems/rescue.yaml``` file into  ```problems/rescue.txt```:
```
python src/generate.py -i problems/rescue.yaml -o problems/rescue.txt
```

Solve the MDP problem ```problems/rescue.txt``` with discount rate ```0.9```, and store policy to CSV file ```sols/rescue.csv```:
```
python src/solve.py -i problems/rescue.txt -d 0.9 -o sols/rescue.csv
```

Analyse the results of the policy CSV file ```sols/rescue.csv```:
```
python src/analyse.py -i problems/rescue.yaml -s sols/rescue.csv
```

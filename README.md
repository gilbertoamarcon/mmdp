# Mdp

Synthesize parking MDP problem using parameters in the ```problems/parking-a.yaml``` file into  ```problems/parking-a.txt```:
```
python src/generate_parking.py -i problems/parking-a.yaml -o problems/parking-a.txt
```

Solve the parking MDP problem ```problems/parking-a.txt``` with discount rate ```0.9```, and store policy to CSV file ```sols/parking-a.csv```:
```
python src/solve.py -i problems/parking-a.txt -d 0.9 -o sols/parking-a.csv
```

Analyse the results of the policy CSV file ```sols/parking-a.csv```:
```
python src/analyse_parking.py -i problems/parking-a.yaml -s sols/parking-a.csv
```

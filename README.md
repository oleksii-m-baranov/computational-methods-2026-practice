# Computational Methods 2026: Practice

This repository is intended for practical assignments for the "Computational Methods" course during the 1st semester of 
the 2026-27 academic year at Odesa National Polytechnic University.

## Practice Docs
All practice docs are stored in the directory `./docs` and organized by practice lesson number 

## Local Environment
1. Install Python 3.12
2. Create a `venv` using Python 3.12
3. Activate the venv

## How To Contribute
(One time)
1. Fork the original repository
2. Add the original repo as the `upstream` remote
```bash 
git remote add upstream git@github.com:oleksii-m-baranov/computational-methods-2026-practice.git
```

(For each practical assignment)
1. Create a branch using the following template `<group>-<surname-name>-lab<lab_number>` (all lowercase). 
Example: `ai-123-baranov-oleksii-lab4`
2. Create a directory using the following template `./students/<group>/<surname-name>/lab<lab_number>` 
Example: 
```text
computational-methods-2026-practice/
├── docs/
└── students/
    └── ai-123/
        └── baranov-oleksii/
            └── lab4/
                └── ...
```
and place all related files there.
3. Create a PR to the master branch in the upstream repo. The PR name should match the following template `<GROUP> <Surname Name> - Lab <lab_number>`. 
Example: `AI-123 Baranov Oleksii - Lab 1`
4. Wait for approval. Resolve comments if necessary.
5. ...
6. PROFIT!
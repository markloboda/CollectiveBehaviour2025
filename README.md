# Collective Behaviour project 2025/26
Group project repository for the course Collective Behaviour 2025/26 at FRI Ljubljana.

Group members:
- Mark Loboda [markloboda](https://github.com/markloboda)
- Klemen Plestenjak [klemenpl](https://github.com/klemenpl)


## Topic: Simulation of the collective behaviour of flocking sheep to a herding dog
For our project on Simulation of a collective behaviour of flocking sheep to a herding dog, we plan to implement the method described in the paper [Collective responses of flocking sheep (Ovis aries) to a herding dog (border collie)](https://doi.org/10.1038/s42003-024-07245-8) and expand on the implementation.

This repository contains a Python reimplementation and extension of the agent-based herding model introduced in *Collective responses of flocking sheep (Ovis aries) to a herding dog (border collie)* by Jadhav et al. (2024). The goal of the project is to reproduce the original model’s collective dynamics and extend it with interactive visualization, explicit target setting, two-dog herding, and static environmental obstacles. The implementation successfully reproduces the qualitative behaviour reported in the paper and explores how simple multi-dog coordination strategies scale with flock size.

## Project scope and achieved goals
- Reimplementation of the original MATLAB herding model in Python
- Real-time visualization of sheep–dog dynamics
- Support for explicit herding targets
- Extension to two-dog herding via flock splitting
- Static obstacle avoidance for sheep and dogs
- Quantitative comparison of one-dog vs two-dog herding performance
- Introduction of idle state
- Runners, and plotters for easier testing


## How to run?

Create a virtual environment (recommended), then install dependencies:

```cmd
pip install -r requirements.txt
python ./src/demo01.py
```

### Requirements
- Python 3.10 or newer
- Tested on Linux and Windows
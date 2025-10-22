# Collective Behaviour project 2025/26
Group project repository for the course Collective Behaviour 2025/26 at FRI Ljubljana.

Group members:
- Mark Loboda [markloboda](https://github.com/markloboda)
- Klemen Plestenjak [klemenpl](https://github.com/klemenpl)

## Topic: Simulation of the collective behaviour of flocking sheep to a herding dog
For our project on Simulation of a collective behaviour of flocking sheep to a herding dog, we plan to implement the method described in the paper [Collective responses of flocking sheep (Ovis aries) to a herding dog (border collie)](https://doi.org/10.1038/s42003-024-07245-8) and expand on the implementation.
The paper provides a linked GitHub repository with a MATLAB implementation of the model. We will reimplement this method in Python and add visualization to better understand and reproduce the collective dynamics between the sheep and the herding dog. After successfully replicating the results, we will expand the model by testing alternative herding strategies, including driving (pushing the flock from behind), collecting (gathering dispersed sheep before driving), and flanking (using lateral motion to guide direction). We will also introduce environmental obstacles to study how spatial constraints affect group cohesion and efficiency.

## Milestones:
- First report - 16.11.2025
  - Review of the base existing implementation and other implementations
  - Python implementation of the MATLAB model
  - Basic visualization
- Second report - 7.12.2025
  - Implementation of obstacles
  - Dog obstacle avoidance when herding
- Third report - 11.1.2026
  - Research and implementation of different herding strategies and flocking behaviours
  - Testing and analysis of each strategy’s efficiency
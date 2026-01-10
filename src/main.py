import time

import numpy as np
from matplotlib import pyplot as plt

from simulation import Simulation, SimulationConfig
from plotter import plot_all_metrics
from simulation_state import SimulationState
from obstacle import RectObstacle
from visulizer import SimulationVisualizer, SimulationRecorder


def main():
  WORLD_WIDTH = 100
  WORLD_HEIGHT = 100

  obstacles = [
    RectObstacle(00, -2, 100, 0)
  ]

  num_sheep = 120

  # For figure 6
  cfg = SimulationConfig(
    field_size=(100, 100),
    obstacles=obstacles,

    num_sheep=num_sheep,
    num_shepherds=2,

    neighbors_num=10,  # K_atr

    # social attraction / alignment
    w_att=0.8,  # c
    n_att=4,  # k_atr
    w_ali=0.8,  # alg_str
    n_ali=1,  # k_alg

    # social repulsion
    w_rep=2.0,  # rho_a
    d_rep=2.0,  # rad_rep_s

    sheep_inertia=0.8,

    # sheep noise
    w_noise=0.2, # e

    # obstacles
    sheep_obs_rep=10.0,
    sheep_obs_range=3.0,

    dog_obs_rep=1.5,
    dog_obs_range=1.0,

    # dog repulsion
    dog_inertia=0.85,  # h
    w_dog=1.0,  # rho_d
    d_dog=12.0,  # rad_rep_dog

    # dog to dog repulsion
    w_dog_dog=0.1,
    d_dog_dog=4.0,

    goal_pos=(50, 50),

    # global dog-logic parameters
    speed_dog=1.4,  # v_dog
    noise_dog=0.3,  # noise strength e

    # flock cohesion threshold and collecting / driving offsets
    f_n=2.0 * (num_sheep ** (2 / 3)),  # rad_rep_s * no_shp^(2/3)
    pc=2.0,  # collecting offset (pc = rad_rep_s)
    pd=2.0 * (num_sheep ** 0.5),  # pd = rad_rep_s * sqrt(no_shp)

    # sheep group splitting frequency
    group_split_frequency=0.1,
  )

  sim = Simulation(cfg, seed=5)
  sim_steps = sim.steps(steps=3000)
  # print(list(sim_steps()))
  # plot_all_metrics(list(sim_steps)[1:])


  # CTRL + LMB to set goal pos
  player = SimulationVisualizer(sim)
  player.run(sim_steps)

  #recorder = SimulationRecorder(sim, WORLD_WIDTH, WORLD_HEIGHT)
  #recorder.record(sim_steps, "test.gif")

  #print(sim.steps())

  # sim.run(
  #  steps=100,
  #  dt = 1.0  # seconds
  # )

if __name__ == "__main__":
  main()

import time

import numpy as np
from matplotlib import pyplot as plt

from simulation import Simulation, SimulationConfig
from src.plotter import plot_all_metrics
from src.simulation_state import SimulationState
from visulizer import SimulationVisualizer, SimulationRecorder


def main():
  WORLD_WIDTH = 100
  WORLD_HEIGHT = 100

  # For figure 6
  cfg = SimulationConfig(
    field_size=(250, 250),

    num_sheep=14,
    num_shepherds=1,

    neighbors_num=10,  # K_atr

    # social attraction / alignment
    w_att=1.5,  # c
    n_att=4,  # k_atr
    w_ali=1.3,  # alg_str
    n_ali=1,  # k_alg

    # social repulsion
    w_rep=2.0,  # rho_a
    d_rep=2.0,  # rad_rep_s

    # dog repulsion
    inertia_dog=0.5,  # h
    w_dog=1.0,  # rho_d
    d_dog=12.0,  # rad_rep_dog

    goal_pos=(50, 50),

    # global dog-logic parameters
    v_dog=1.5,  # v_dog
    e=0.3,  # noise strength e

    # flock cohesion threshold and collecting / driving offsets
    f_n=2.0 * (14 ** (2 / 3)),  # rad_rep_s * no_shp^(2/3)
    pc=2.0,  # collecting offset (pc = rad_rep_s)
    pd=2.0 * (14 ** 0.5),  # pd = rad_rep_s * sqrt(no_shp)
  )

  sim = Simulation(cfg, seed=10)
  #sim_steps = sim.steps(steps=310)
  #print(list(sim_steps()))

  plot_all_metrics(list(sim_steps)[1:])


  # CTRL + LMB to set goal pos
  #player = SimulationVisualizer(sim)
  #player.run(sim_steps)

  #recorder = SimulationRecorder(WORLD_WIDTH, WORLD_HEIGHT)
  #recorder.record(sim_steps, "test.gif")

  #print(sim.steps())

  #sim.run(
  #  steps=100,
  #  dt = 1.0  # seconds
  #)

if __name__ == "__main__":
  main()

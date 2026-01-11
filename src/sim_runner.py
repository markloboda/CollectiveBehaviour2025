import math
import random
import time

import numpy as np
from matplotlib import pyplot as plt

from simulation import Simulation, SimulationConfig
from plotter import plot_all_metrics
from simulation_state import SimulationState
from obstacle import RectObstacle
from visulizer import SimulationVisualizer, SimulationRecorder


num_sheep = 14

w, h = 100, 100


obstacles = [


  RectObstacle(-10, -10, w + 10, 0), # top
  RectObstacle(w + 10, -10, w + 20, h + 10), # right
  RectObstacle(-20, h + 10, w + 20, h + 20), # bottom
  RectObstacle(-10, -10, -20, h + 10), # lef

]

cfg = SimulationConfig(
  field_size=(w, h),
  obstacles=obstacles,

  num_sheep=num_sheep,
  num_shepherds=2,

  neighbors_num=10,  # K_atr

  sheep_sight_range=4.0,

  # social attraction / alignment
  w_att=1.5,  # c
  n_att=4,  # k_atr
  w_ali=1.3,  # alg_str
  n_ali=1,  # k_alg

  # social repulsion
  w_rep=2.0,  # rho_a
  d_rep=2.0,  # rad_rep_s

  sheep_inertia=0.2,

  # sheep noise
  w_noise=0.3,  # e

  # obstacles
  sheep_obs_rep=10.0,
  sheep_obs_range=3.0,

  dog_obs_rep=1.5,
  dog_obs_range=1.0,

  # dog repulsion
  dog_inertia=0.3,  # h
  w_dog=1.0,  # rho_d
  d_dog=12.0,  # rad_rep_dog

  # dog to dog repulsion
  w_dog_dog=0.5,
  d_dog_dog=4.0,

  goal_pos=(w // 2, h // 2),

  # global dog-logic parameters
  speed_dog=1.5,  # v_dog
  noise_dog=0.3,  # noise strength e

  # flock cohesion threshold and collecting / driving offsets
  f_n=2.0 * (num_sheep ** (2 / 3)),  # rad_rep_s * no_shp^(2/3)
  pc=2.0,  # collecting offset (pc = rad_rep_s)
  pd=2.0 * (num_sheep ** 0.5),  # pd = rad_rep_s * sqrt(no_shp)

  # sheep group splitting frequency
  group_split_frequency=0.1,
)

SEED = 42
STEPS = 2000

def original_one_dog_vs_two(cfg):
  #cfg.num_sheep = 1
  cfg.num_shepherds = 1
  sim = Simulation(cfg, seed=SEED, collect_metrics=True)
  single_dog = list(sim.steps(steps=STEPS))[1:]

  cfg.num_shepherds = 2
  sim = Simulation(cfg, seed=SEED, collect_metrics=True)
  dual_dog = list(sim.steps(steps=STEPS))[1:]

  inp = {
    "One Dog": single_dog,
    "Two Dogs": dual_dog,
  }


  plot_all_metrics(inp, "results", "original_model_")

def plot_time_to_goal(cfg):
  sheep_counts = sorted([14, 24, 48, 60, 100])
  time_1dog = []
  time_2dogs = []

  def avg_polarization(ticks, tolerance = 15.0):
    #ticks = list(ticks)
    #return sum([ t.polarization for t in ticks ]) / len(ticks)
    for i, t in enumerate(ticks):
      if t.cohesion < tolerance:
        return i
    assert False

  def time_to_cohesion(ticks, tolerence = 15):
    for i, t in enumerate(ticks):
      if t.cohesion < tolerence:
        return i
    assert False

  for n_sheep in sheep_counts:
    print("Running", n_sheep)
    cfg.num_sheep = n_sheep
    #cfg.goal_pos = (random.randrange(0, 200), random.randrange(0, 200))

    cfg.f_n = 2.0 * (n_sheep ** (2 / 3))  # rad_rep_s * no_shp^(2/3)
    cfg.pc = 2.0  # collecting offset (pc = rad_rep_s)
    cfg.pd = 2.0 * (n_sheep ** 0.5)  # pd = rad_rep_s * sqrt(no_shp)

    time_run_1dog = 0
    time_run_2dogs = 0

    N_RUNS = 20

    for run in range(N_RUNS):
      cfg.num_shepherds = 1
      sim = Simulation(cfg, seed=SEED + run)
      time_run_1dog += (time_to_cohesion(sim.steps(STEPS)) / N_RUNS)

      cfg.num_shepherds = 2
      sim = Simulation(cfg, seed=SEED + run)
      time_run_2dogs += (time_to_cohesion(sim.steps(STEPS)) / N_RUNS)

    time_1dog.append(time_run_1dog)
    time_2dogs.append(time_run_2dogs)

  x = np.arange(len(sheep_counts))  # group positions
  width = 0.35  # width of each bar

  fig, ax = plt.subplots()

  ax.bar(x - width / 2, time_1dog, width, label="1 Shephard")
  ax.bar(x + width / 2, time_2dogs, width, label="2 Shepherds")

  ax.set_xlabel("Number of sheep")
  ax.set_ylabel("Average number of ticks to reach cohesion")
  ax.set_xticks(x)
  ax.set_xticklabels(np.asarray(sheep_counts))
  ax.legend()

  plt.tight_layout()
  plt.show()

#"""

cfg.num_sheep = 80
sim = Simulation(cfg, seed=SEED)
sim_steps = sim.steps(steps=3000)
player = SimulationVisualizer(sim)
player.run(sim_steps)

#original_one_dog_vs_two(cfg)
#plot_time_to_goal(cfg)



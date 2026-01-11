import math
import random
import time

import numpy as np
from matplotlib import pyplot as plt

from simulation import Simulation, SimulationConfig
from obstacle import RectObstacle
from visulizer import SimulationVisualizer, SimulationRecorder


num_sheep = 60

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

  sheep_sight_range=15.0,

  sheep_idle_range=12.0,
  idle_social_scale = 0.30,
  idle_noise_scale = 0.2,

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
  group_split_frequency=0.05,
)

SEED = 42


sim = Simulation(cfg, seed=SEED)
sim_steps = sim.steps(steps=30000)
player = SimulationVisualizer(sim)
player.run(sim_steps)



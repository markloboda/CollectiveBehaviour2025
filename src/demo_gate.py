import math
import random
import time

from simulation import Simulation, SimulationConfig
from simulation_state import SimulationState
from obstacle import RectObstacle
from visulizer import SimulationVisualizer

SEED = 42
STEPS = 2000
wall_width = 10
w, h = 100, 100
gap = 20
l_w = 350, 350

obstacles = [
  # inner box width=w, height=h, top one gap=gap, centered at 0, 0
  RectObstacle(-w//2, -h//2, -gap//2, -h//2 + wall_width),  # top
  RectObstacle(gap//2, -h//2, w//2, -h//2 + wall_width),  # top
  RectObstacle(-w//2, h//2 - wall_width, w//2, h//2),  # bottom
  RectObstacle(-w//2, -h//2, -w//2 + wall_width, h//2),  # left
  RectObstacle(w//2 - wall_width, -h//2, w//2, h//2),  # right

  # outer box with no gap
  RectObstacle(-l_w[0]//2, -l_w[1]//2, l_w[0]//2, -l_w[1]//2 + wall_width),  # top
  RectObstacle(-l_w[0]//2, l_w[1]//2 - wall_width, l_w[0]//2, l_w[1]//2),  # bottom
  RectObstacle(-l_w[0]//2, -l_w[1]//2, -l_w[0]//2 + wall_width, l_w[1]//2),  # left
  RectObstacle(l_w[0]//2 - wall_width, -l_w[1]//2, l_w[0]//2, l_w[1]//2),  # right
]

num_sheep = 120

cfg = SimulationConfig(
  field_size=(w, h),
  obstacles=obstacles,

  num_sheep=num_sheep,
  num_shepherds=2,

  neighbors_num=30,  # K_atr

  sheep_sight_range=40.0,

  sheep_idle_range=120.0,
  idle_social_scale = 0.5,
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
  w_dog=3.0,  # rho_d
  d_dog=12.0,  # rad_rep_dog

  # dog to dog repulsion
  w_dog_dog=0.5,
  d_dog_dog=4.0,

  goal_pos=(0, -h//2 + 10),

  # global dog-logic parameters
  speed_dog=1.5,  # v_dog
  noise_dog=0.3,  # noise strength e

  # flock cohesion threshold and collecting / driving offsets
  f_n=1.5 * (num_sheep ** (2 / 3)),  # rad_rep_s * no_shp^(2/3)
  pc =1.2,  # collecting offset (pc = rad_rep_s)
  pd =1.2 * (num_sheep ** 0.5),  # pd = rad_rep_s * sqrt(no_shp)

  # sheep group splitting frequency
  group_split_frequency=0.2,
)

sim = Simulation(cfg, seed=SEED, spawn_rect=(-100, -150, 100, -50))
sim_steps = sim.steps(steps=3000)
player = SimulationVisualizer(sim)
player.run(sim_steps)
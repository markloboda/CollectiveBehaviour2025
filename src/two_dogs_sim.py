import time

import numpy as np
from matplotlib import pyplot as plt

from simulation import Simulation, SimulationConfig


def main():


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

  def plot_time_to_goal():
    sheep_counts = [16, 32, 64]
    time_1dog = []
    time_2dogs = []

    def dst(a, b):
      return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def find_time_to_target(ticks, tolerance = 40.0):
      for i, t in enumerate(ticks):
        #print(t.barycenter)
        if dst(t.barycenter,  cfg.goal_pos) < tolerance:
          return i
      return 0

    N_STEPS = 500

    for n_sheep in sheep_counts:
      cfg.num_sheep = n_sheep

      cfg.num_shepherds = 1
      sim = Simulation(cfg, seed=n_sheep)
      time_1dog.append(find_time_to_target(sim.steps(N_STEPS)))

      cfg.num_shepherds = 2
      sim = Simulation(cfg, seed=n_sheep)
      time_2dogs.append(find_time_to_target(sim.steps(N_STEPS)))

    x = np.arange(len(sheep_counts))  # group positions
    width = 0.35  # width of each bar

    fig, ax = plt.subplots()

    ax.bar(x - width / 2, time_1dog, width, label="1 Shephard")
    ax.bar(x + width / 2, time_2dogs, width, label="2 Shepherds")

    ax.set_xlabel("Number of sheep")
    ax.set_ylabel("Time to target")
    ax.set_xticks(x)
    ax.set_xticklabels(np.asarray(sheep_counts))
    ax.legend()

    plt.tight_layout()
    plt.show()


  plot_time_to_goal()


if __name__ == "__main__":
  main()

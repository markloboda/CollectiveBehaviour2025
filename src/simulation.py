import random
import time
import math
import os
from agents import Sheep, Dog
from src.simulation_state import SimulationState


class Simulation:
  def __init__(self, num_sheep, num_shepherds, field_size, seed=42):
    random.seed(seed)

    self.field_size = field_size
    self.sheep = [Sheep(random.uniform(0, field_size[0]), random.uniform(0, field_size[1])) for _ in range(num_sheep)]
    self.shepherds = [Dog(random.uniform(0, field_size[0]), random.uniform(0, field_size[1])) for _ in range(num_shepherds)]

    self.neighbors_num = num_sheep # number of neighbors for social interaction between sheep
    # social attraction
    self.w_att = 1.0 # positiove weight on interaction
    self.n_att = 5   # number of nearest neighbors used (note: that n_att <= self.neighbors_num)
    # social alignment
    self.w_ali = 1.0 # positiove weight on interaction
    self.n_ali = 3   # number of randomly chosen from n_att nearest neighbours (note: that n_ali <= n_att)
    # social repulsion
    self.w_rep = 1.0 # positiove weight on interaction
    self.d_rep = 0.5 # distance for social repulsion
    # dog repulsion
    self.w_dog = 1.0
    self.d_dog = 0.5

  def run(self, steps=100, dt=1.0, delay=0.1):
    print("Starting simulation...")
    for step in range(steps):
      self.update(dt)
      self.draw()
      print(f"Step {step + 1}")
      time.sleep(delay)
    print("Simulation finished.")

  def steps(self, steps=100, dt=1.0):
      accum = 0.0
      for step in range(steps):
          state = SimulationState(
              tick=step,
              time=accum,

              bounds=self.field_size,

              sheep=self.sheep,
              dogs=self.shepherds
          )
          accum += dt
          self.update(dt)

          yield state

  def update(self, dt):
    for sheep in self.sheep:
      neighbors = [s for s in self.sheep if s != sheep]
      sheep.update_social(neighbors, wAtt=1.0, wAli=0.5, wRep=1.0, nAtt=3, nAli=2, dRep=1.5)
      sheep.update_repulsion(self.shepherds[0], self.w_dog, self.d_dog)
      sheep.update_noise()
      sheep.move(dt)

    for shepherd in self.shepherds:
      pass

  def draw(self, width=40, height=20):
    """Draw sheep (blue) and dogs (red) as square-ish blocks in terminal."""
    # ANSI codes for colors
    BLUE = '\033[44m'   # blue background
    RED = '\033[41m'    # red background
    RESET = '\033[0m'   # reset color

    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Create empty grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    color_grid = [[RESET for _ in range(width)] for _ in range(height)]

    # Helper to convert world coordinates to grid indices
    def to_grid(x, y):
      gx = int(x / self.field_size[0] * (width - 1))
      gy = int(y / self.field_size[1] * (height - 1))
      gx = max(0, min(width - 1, gx))
      gy = max(0, min(height - 1, gy))
      return gx, gy

    # Draw sheep (blue)
    for s in self.sheep:
      gx, gy = to_grid(s.x, s.y)
      grid[gy][gx] = '  '   # double-width
      color_grid[gy][gx] = BLUE

    # Draw dogs (red, overwrite if overlapping)
    for d in self.shepherds:
      gx, gy = to_grid(d.x, d.y)
      grid[gy][gx] = '  '
      color_grid[gy][gx] = RED

    # Print grid row by row (top row = y=0)
    for row_idx in reversed(range(height)):
      row = ''.join(f"{color_grid[row_idx][col]}{grid[row_idx][col]}{RESET}" for col in range(width))
      print(row)

  # --- Utility Methods ---
  def calculate_barycenter(self):
    if not self.sheep:
      raise ValueError("Cannot calculate barycenter: no sheep in simulation")
    avg_x = sum(a.x for a in self.sheep) / len(self.sheep)
    avg_y = sum(a.y for a in self.sheep) / len(self.sheep)
    return (avg_x, avg_y)

  def calculate_group_cohesion(self, barycenter=None):
    if not self.sheep:
      raise ValueError("Cannot calculate group cohesion: no sheep in simulation")
    if barycenter is None:
      barycenter = self.calculate_barycenter()
    avg_x, avg_y = barycenter
    avg_dx = sum(a.x - avg_x for a in self.sheep) / len(self.sheep)
    avg_dy = sum(a.y - avg_y for a in self.sheep) / len(self.sheep)
    return math.hypot(avg_dx, avg_dy)

  def calculate_group_polarization(self):
    if not self.sheep:
      raise ValueError("Cannot calculate group polarization: no sheep in simulation")
    avg_dx = sum(a.direction[0] for a in self.sheep) / len(self.sheep)
    avg_dy = sum(a.direction[1] for a in self.sheep) / len(self.sheep)
    return math.hypot(avg_dx, avg_dy)

  def calculate_barycenter_velocity(self):
    if not self.sheep:
      raise ValueError("Cannot calculate group barycenter velocity: no sheep in simulation")
    avg_vx = sum(s.vx for s in self.sheep) / len(self.sheep)
    avg_vy = sum(s.vy for s in self.sheep) / len(self.sheep)
    return avg_vx, avg_vy

def flock_metrics(self):
    """Computes oriented coordinates and group metrics"""
    vx_b, vy_b = self.calculate_barycenter_velocity()
    speed_b = math.hypot(vx_b, vy_b)
    if speed_b == 0:
      cos_theta, sin_theta = 1.0, 0.0
    else:
      cos_theta = vx_b / speed_b
      sin_theta = vy_b / speed_b

    avg_x, avg_y = self.calculate_barycenter()
    positions = {}

    for agent in self.sheep + self.dogs:
      dx = agent.x - avg_x
      dy = agent.y - avg_y
      # rotate coordinates
      x_bar = dx * (-sin_theta) + dy * cos_theta  # lateral
      y_bar = dx * cos_theta + dy * sin_theta     # longitudinal
      positions[agent] = (x_bar, y_bar)

    x_vals = [pos[0] for pos in positions.values()]
    y_vals = [pos[1] for pos in positions.values()]

    length = max(y_vals) - min(y_vals) if y_vals else 0.0
    width = max(x_vals) - min(x_vals) if x_vals else 0.0
    elongation = length / width if width != 0 else float('inf')

    return {
      "positions": positions,
      "length": length,
      "width": width,
      "elongation": elongation
    }
import dataclasses
import random
import time
import math
import os
from typing import *
from agents import *
from simulation_state import SimulationState
from obstacle import RectObstacle


@dataclasses.dataclass
class SimulationConfig:
  field_size: Tuple[int, int]

  obstacles: List[RectObstacle]

  num_sheep: int
  num_shepherds: int

  neighbors_num: int  # number of neighbors for social interaction between sheep (k_atr)
  # social attraction
  w_att: float  # weight on interaction (c)
  n_att: int  # number of nearest neighbours used (k_atr)
  w_ali: float  # weight on interaction (alg_str)
  n_ali: int  # number of randomly chosen from n_att nearest neighbours (k_alg)

  # social repulsion
  w_rep: float  # weight on interaction (rho_a)
  d_rep: float  # distance for social repulsion (rad_rep_s)

  sheep_inertia: float

  # sheep noise
  w_noise: float  # noise strength for sheep (e)

  sheep_obs_rep: float
  sheep_obs_range: float

  dog_obs_rep: float
  dog_obs_range: float

  # dog repulsion
  dog_inertia: float  # inertia of dog direction (h)
  w_dog: float  # weight on interaction (rho_d)
  d_dog: float  # distance for dog repulsion (rad_rep_dog = pd + 1 with pd = 2)

  # dog to dog repulsion
  w_dog_dog: float  # weight on interaction between dogs
  d_dog_dog: float  # distance for dog to dog repulsion

  goal_pos: Tuple[float, float] | None

  # “global” model parameters used in dog logic
  speed_dog: float  # dog speed (v_dog)
  noise_dog: float  # noise strength for dog (e)
  # group cohesion threshold f_n and collecting/drive offsets pc, pd
  f_n: float  # cohesion threshold (f_n)
  pc: float  # collecting offset (pc)
  pd: float  # driving offset (pd)

  # sheep group splitting frequency
  group_split_frequency: float = 0.2  # fraction of frames to update split (0.2 = every 5 frames)



class Simulation:
  def __init__(self, simCfg: SimulationConfig, collect_metrics=True, seed: int = 42):
    self.collect_metrics = collect_metrics
    random.seed(seed)

    self.cfg = simCfg
    self.sheep = [Sheep(random.uniform(0, simCfg.field_size[0]), random.uniform(0, simCfg.field_size[1])) for _ in range(simCfg.num_sheep)]
    self.shepherds = [Dog(random.uniform(0, simCfg.field_size[0]), random.uniform(0, simCfg.field_size[1])) for _ in
                      range(simCfg.num_shepherds)]

    self._cached_sheep_groups = None
    self._last_split_frame = -1
    self._current_frame = 0

  def run(self, steps: int = 100, dt: float = 1.0, delay: float = 0.1):
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

        bounds=self.cfg.field_size,

        sheep=self.sheep,
        dogs=self.shepherds,
        barycenter=None,
        velocity=None,
        direction=None,
        perp_direction=None,
        cohesion=None,
        polarization=None,
        elongation=None,
        dog_offsets=None,
        dog_rear_distance=None,
      )

      if self.collect_metrics:
        state.barycenter = self.calculate_barycenter()
        state.velocity = self.calculate_group_velocity()
        state.direction = self.calculate_group_direction()
        state.perp_direction = self.calculate_group_perp_direction()
        state.cohesion = self.calculate_group_cohesion()
        state.polarization = self.calculate_group_polarization()
        state.elongation = self.calculate_group_elongation()
        state.dog_offsets = self.calculate_dog_offsets()
        state.dog_rear_distance = self.calculate_dog_rear_distance()

      accum += dt
      self.update(dt)

      yield state

  def update(self, dt: float) -> None:
    for sheep in self.sheep:
      neighbors = [s for s in self.sheep if s != sheep]
      sheep.update_social(
        neighbors,
        wAtt=self.cfg.w_att,
        wAli=self.cfg.w_ali,
        wRep=self.cfg.w_rep,
        nAtt=self.cfg.n_att,
        nAli=self.cfg.n_ali,
        dRep=self.cfg.d_rep,
      )
      if self.shepherds:
        sheep.update_repulsion(self.shepherds, self.cfg.w_dog, self.cfg.d_dog)
      else:
        sheep.dog_repulsion = (0.0, 0.0)

    # Split sheep into groups for each dog
    sheep_groups = self.get_sheep_groups_cached()

    # update dog (using "previous" sheep state)
    if self.shepherds:
      for i, dog in enumerate(self.shepherds):
        dog.update_dog_repulsion(self.shepherds, self.cfg.w_dog_dog, self.cfg.d_dog_dog)
        assigned_sheep = sheep_groups[i] if i < len(sheep_groups) else []
        dog.update(
          assigned_sheep,
          obstacles=self.cfg.obstacles,
          dt=dt,
          cfg=self.cfg
        )

    for sheep in self.sheep:
      sheep.update_noise(self.cfg.w_noise)
      sheep.update_obstacles(self.cfg.obstacles, self.cfg.sheep_obs_range, self.cfg.sheep_obs_rep)
      sheep.move(dt, inertia=self.cfg.sheep_inertia, obstacles=self.cfg.obstacles)

    self._current_frame += 1

  def draw(self, width=40, height=20):
    """Draw sheep (blue) and dogs (red) as square-ish blocks in terminal."""
    # ANSI codes for colors
    BLUE = '\033[44m'  # blue background
    RED = '\033[41m'  # red background
    RESET = '\033[0m'  # reset color

    # Clear terminal
    os.system('cls' if os.name == 'nt' else 'clear')

    # Create empty grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    color_grid = [[RESET for _ in range(width)] for _ in range(height)]

    # Helper to convert world coordinates to grid indices
    def to_grid(x, y):
      gx = int(x / self.cfg.field_size[0] * (width - 1))
      gy = int(y / self.cfg.field_size[1] * (height - 1))
      gx = max(0, min(width - 1, gx))
      gy = max(0, min(height - 1, gy))
      return gx, gy

    # Draw sheep (blue)
    for s in self.sheep:
      gx, gy = to_grid(s.x, s.y)
      grid[gy][gx] = '  '  # double-width
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

  def calculate_barycenter(self) -> Tuple[float, float]:
    if not self.sheep:
      raise ValueError("Cannot calculate barycenter: no sheep in simulation")
    avg_x = sum(a.x for a in self.sheep) / len(self.sheep)
    avg_y = sum(a.y for a in self.sheep) / len(self.sheep)
    return (avg_x, avg_y)

  def calculate_group_velocity(self) -> Tuple[float, float]:
    if not self.sheep:
      raise ValueError("Cannot calculate barycenter: no sheep in simulation")

    avg_x = sum(a.vx for a in self.sheep) / len(self.sheep)
    avg_y = sum(a.vx for a in self.sheep) / len(self.sheep)
    return (avg_x, avg_y)

  def calculate_group_direction(self, vel=None) -> Tuple[float, float]:
    if not self.sheep:
      raise ValueError("Cannot calculate barycenter: no sheep in simulation")

    if vel is None:
      vel = self.calculate_group_velocity()

    vx, vy = vel

    norm = math.hypot(vx, vy)
    if norm == 0.0:
      # arbitrary direction if they are still
      return (0.0, 0.0)
    return (vx / norm, vy / norm)

  def calculate_group_perp_direction(self) -> Tuple[float, float]:
    dx, dy = self.calculate_group_direction()
    # rotate by +90°
    return (-dy, dx)

  def calculate_group_cohesion(self, barycenter=None) -> float:
    """Average distance of sheep to flock barycenter."""
    if not self.sheep:
      raise ValueError("Cannot calculate group cohesion: no sheep in simulation")
    if barycenter is None:
      barycenter = self.calculate_barycenter()
    bx, by = barycenter

    n = len(self.sheep)
    total_dist = 0.0
    for a in self.sheep:
      total_dist += math.hypot(a.x - bx, a.y - by)

    return total_dist / n

  def calculate_group_polarization(self) -> float:
    if not self.sheep:
      raise ValueError("Cannot calculate group polarization: no sheep in simulation")
    avg_dx = sum(a.direction[0] for a in self.sheep) / len(self.sheep)
    avg_dy = sum(a.direction[1] for a in self.sheep) / len(self.sheep)
    return math.hypot(avg_dx, avg_dy)


  def calculate_group_elongation(self) -> float:
    """
    E(t): length / width of flock in barycenter frame.
    length: along flock direction
    width : perpendicular to flock direction
    """
    n = len(self.sheep)
    if n == 0:
      return 0.0

    bx, by = self.calculate_barycenter()
    dir_x, dir_y = self.calculate_group_direction()
    perp_x, perp_y = self.calculate_group_perp_direction()

    # projections of sheep positions onto longitudinal and lateral axes
    first = True
    y_min = y_max = 0.0
    x_min = x_max = 0.0

    for s in self.sheep:
      rx = s.x - bx
      ry = s.y - by

      # along direction of motion
      y_along = rx * dir_x + ry * dir_y
      # across direction of motion
      x_across = rx * perp_x + ry * perp_y

      if first:
        y_min = y_max = y_along
        x_min = x_max = x_across
        first = False
      else:
        if y_along < y_min:
          y_min = y_along
        if y_along > y_max:
          y_max = y_along
        if x_across < x_min:
          x_min = x_across
        if x_across > x_max:
          x_max = x_across

    length = y_max - y_min
    width = x_max - x_min
    if width <= 0.0:
      return 0.0
    return length / width

  def calculate_dog_offsets(self):
    """
    x_D, y_D of first dog in flock-oriented frame:

    x_D: lateral offset (perpendicular to flock motion)
    y_D: longitudinal offset (along flock motion; >0 = in front of barycenter)
    """
    if not self.shepherds or not self.sheep:
      return None

    dog = self.shepherds[0]
    bx, by = self.calculate_barycenter()
    dir_x, dir_y = self.calculate_group_direction()
    perp_x, perp_y = self.calculate_group_perp_direction()

    rx = dog.x - bx
    ry = dog.y - by

    x_D = rx * perp_x + ry * perp_y
    y_D = rx * dir_x + ry * dir_y
    return (x_D, y_D)

  def calculate_dog_rear_distance(self):
    """
    y_RD: distance from dog to rear-most sheep along flock direction.

    y_RD = y_rear - y_D
    > 0 : dog is behind the rear sheep
    < 0 : dog has passed the rear sheep
    """
    if not self.shepherds or not self.sheep:
      return None

    bx, by = self.calculate_barycenter()
    dir_x, dir_y = self.calculate_group_direction()

    # project sheep onto direction axis to find rear-most
    y_min = None
    for s in self.sheep:
      rx = s.x - bx
      ry = s.y - by
      y_along = rx * dir_x + ry * dir_y
      if y_min is None or y_along < y_min:
        y_min = y_along

    dog = self.shepherds[0]
    rx_d = dog.x - bx
    ry_d = dog.y - by
    y_D = rx_d * dir_x + ry_d * dir_y

    y_RD = y_min - y_D
    return y_RD

  def calculate_barycenter_velocity(self) -> Tuple[float, float]:
    if not self.sheep:
      raise ValueError("Cannot calculate group barycenter velocity: no sheep in simulation")
    avg_vx = sum(s.vx for s in self.sheep) / len(self.sheep)
    avg_vy = sum(s.vy for s in self.sheep) / len(self.sheep)
    return avg_vx, avg_vy

  def get_sheep_groups_cached(self) -> List[List[Sheep]]:
    # how many frames between updates
    frames_between_updates = max(1, int(1.0 / self.cfg.group_split_frequency))
    # Check if we need to update the split
    should_update = (self._cached_sheep_groups is None or (self._current_frame - self._last_split_frame) >= frames_between_updates)
    if should_update:
      # Update the cached groups
      if len(self.shepherds) == 2:
        group1, group2 = self.split_sheep_groups()
        self._cached_sheep_groups = [group1, group2]
      else:
        # For single dog or more than 2 dogs, use all sheep
        self._cached_sheep_groups = [self.sheep] * len(self.shepherds)

      self._last_split_frame = self._current_frame
    return self._cached_sheep_groups

  def split_sheep_groups(self) -> Tuple[List[Sheep], List[Sheep]]:
    dog1, dog2 = self.shepherds[0], self.shepherds[1]
    barycenter = self.calculate_barycenter()
    # Middle point between the two dogs
    mid_x = (dog1.x + dog2.x) / 2
    mid_y = (dog1.y + dog2.y) / 2
    # Direction vector from middle point to barycenter
    dir_x = barycenter[0] - mid_x
    dir_y = barycenter[1] - mid_y
    norm = math.hypot(dir_x, dir_y)
    if norm == 0:
      # If middle point equals barycenter, split
      return self.sheep[:len(self.sheep)//2], self.sheep[len(self.sheep)//2:]

    dir_x /= norm
    dir_y /= norm
    # Perpendicular vector to the splitting line
    perp_x = -dir_y
    perp_y = dir_x

    group1 = []
    group2 = []

    for sheep in self.sheep:
      # Vector from middle point to sheep
      sheep_vec_x = sheep.x - mid_x
      sheep_vec_y = sheep.y - mid_y
      # Project onto perpendicular vector to determine which side
      projection = sheep_vec_x * perp_x + sheep_vec_y * perp_y
      if projection >= 0:
        group1.append(sheep)
      else:
        group2.append(sheep)

    return group1, group2

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

  for agent in (self.sheep + self.dogs):
    dx = agent.x - avg_x
    dy = agent.y - avg_y
    # rotate coordinates
    x_bar = dx * (-sin_theta) + dy * cos_theta  # lateral
    y_bar = dx * cos_theta + dy * sin_theta  # longitudinal
    positions[agent] = (x_bar, y_bar)

  x_vals = [pos[0] for pos in positions.values()]
  y_vals = [pos[1] for pos in positions.values()]

  length = max(y_vals) - min(y_vals) if y_vals else 0.0
  width = max(x_vals) - min(x_vals) if x_vals else 0.0
  elongation = length / width if width != 0 else math.inf

  return {
    "positions": positions,
    "length": length,
    "width": width,
    "elongation": elongation,
  }



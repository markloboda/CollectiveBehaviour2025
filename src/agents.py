import math
import random
from typing import List, Tuple


class Agent:
  def __init__(self, x: float, y: float):
    self.x = x
    self.y = y
    self.vx = 0.0
    self.vy = 0.0
    # params
    self.speed_const = 1.0

  @property
  def speed(self) -> float:
    return AgentUtils.speed(self.vx, self.vy)

  @property
  def heading(self) -> float:
    return AgentUtils.heading(self.vx, self.vy)

  @property
  def direction(self) -> Tuple[float, float]:
    return AgentUtils.direction(self.vx, self.vy)

  # def move(self, dt: float):
  #   (move_x, move_y) = (self.speed[0] * dt, self.speed[1] * dt)
  #   (dir_x, dir_y)   = self.direction[0]
  #   (self.x, self.y) = (self.x + move_x * dir_x, self.y + move_y * dir_y)

  def viewing_angle_to(self, other: 'Agent') -> float:
    theta_ij = math.atan2(other.y - self.y, other.x - self.x)
    psi_ij = theta_ij - self.heading
    psi_ij = (psi_ij + math.pi) % (2 * math.pi) - math.pi  # normalize to [-pi, pi]
    return psi_ij

  def alignment_with(self, other: 'Agent') -> float:
    phi_ij = other.heading - self.heading
    phi_ij = (phi_ij + math.pi) % (2 * math.pi) - math.pi
    return phi_ij


class Sheep(Agent):
  def __init__(self, x, y):
    super().__init__(x, y)
    self.social_attraction = (0.0, 0.0)
    self.social_alignment  = (0.0, 0.0)
    self.social_repulsion  = (0.0, 0.0)
    self.dog_repulsion     = (0.0, 0.0)
    self.noise             = (0.0, 0.0)

  def update_social(self, neighbors, wAtt, wAli, wRep, nAtt, nAli, dRep):
    if not neighbors:
      self.social_attraction = (0.0, 0.0)
      self.social_alignment  = (0.0, 0.0)
      self.social_repulsion  = (0.0, 0.0)
      return
    # --- 1. Attraction ---
    nAtt = min(nAtt, len(neighbors))
    att_neighbors = random.sample(neighbors, nAtt)

    sum_dx, sum_dy = 0.0, 0.0
    for n in att_neighbors:
      dx = n.x - self.x
      dy = n.y - self.y
      dist = math.hypot(dx, dy)
      if dist > 0:
        sum_dx += dx / dist
        sum_dy += dy / dist
    self.social_attraction = (wAtt * sum_dx / nAtt, wAtt * sum_dy / nAtt)
    # --- 2. Alignment ---
    nAli = min(nAli, nAtt)
    ali_neighbors = random.sample(att_neighbors, nAli)
    sum_dx, sum_dy = 0.0, 0.0
    for n in ali_neighbors:
      dir_x, dir_y = n.direction
      sum_dx += dir_x
      sum_dy += dir_y
    self.social_alignment = (wAli * sum_dx / nAli, wAli * sum_dy / nAli)
    # --- 3. Repulsion ---
    rep_neighbors = [n for n in neighbors if math.hypot(n.x - self.x, n.y - self.y) < dRep]
    nRep = len(rep_neighbors)
    if nRep == 0:
      self.social_repulsion = (0.0, 0.0)
    else:
      sum_dx, sum_dy = 0.0, 0.0
      for n in rep_neighbors:
        dx = n.x - self.x
        dy = n.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
          sum_dx += dx / dist
          sum_dy += dy / dist
      self.social_repulsion = (-wRep * sum_dx / nRep, -wRep * sum_dy / nRep)

  def update_repulsion(self, dog, wDog, dDog): #dDog = R_D in paper
    dx = self.x - dog.x
    dy = self.y - dog.y
    dist = math.hypot(dx, dy)
    if dist < dDog and dist > 0:
      self.dog_repulsion = (wDog * dx / dist, wDog * dy / dist)
    else:
      self.dog_repulsion = (0.0, 0.0)

  def update_noise(self):
    self.noise = (random.random(), random.random())


  def move(self, dt, alpha=0.5, epsilon=0.1):
    # Previous direction unit vector
    dir_x, dir_y = self.direction

    ux = (
            alpha * dir_x
            + self.social_attraction[0]
            + self.social_alignment[0]
            + self.social_repulsion[0]
            + self.dog_repulsion[0]
            + epsilon * (self.noise[0] - 0.5) * 2.0
    )
    uy = (
            alpha * dir_y
            + self.social_attraction[1]
            + self.social_alignment[1]
            + self.social_repulsion[1]
            + self.dog_repulsion[1]
            + epsilon * (self.noise[1] - 0.5) * 2.0
    )

    norm = math.hypot(ux, uy)
    if norm > 0:
      self.vx = ux / norm * self.speed_const
      self.vy = uy / norm * self.speed_const
    else:
      self.vx = 0.0
      self.vy = 0.0

    # Move sheep
    self.x += self.vx * dt
    self.y += self.vy * dt

class Dog(Agent):
  def __init__(self, x: float, y: float):
    super().__init__(x, y)
    # dog is faster than sheep in the model
    self.speed_const = 1.5

  def move_herding(self,
          sheep: List[Sheep],
          dt: float,
          rad_rep_s: float,
          f_n: float,
          pc: float,
          pd: float,
          noise_strength: float,
  ) -> None:

    if not sheep:
      return

    dists = []
    for s in sheep:
      dx = s.x - self.x
      dy = s.y - self.y
      dists.append((math.hypot(dx, dy), dx, dy, s))

    min_dist, _, _, _ = min(dists, key=lambda t: t[0])

    # If dog is very close to any sheep, slow down massively (force_slow)
    if min_dist <= rad_rep_s:
      self.x += self.vx * 0.05 * dt
      self.y += self.vy * 0.05 * dt
      return

    # --- flock barycenter and spread ---
    avg_x = sum(s.x for s in sheep) / len(sheep)
    avg_y = sum(s.y for s in sheep) / len(sheep)

    # vectors from barycenter to sheep
    r_gcm = []
    max_dist = -1.0
    max_idx = 0
    for idx, s in enumerate(sheep):
      rx = s.x - avg_x
      ry = s.y - avg_y
      d = math.hypot(rx, ry)
      r_gcm.append((rx, ry, d))
      if d > max_dist:
        max_dist = d
        max_idx = idx

    # collect or drive ?
    if max_dist >= f_n:
      # collect: go behind the farthest sheep relative to group centre
      rx, ry, d_far = r_gcm[max_idx]
      if d_far == 0.0:
        target_x, target_y = sheep[max_idx].x, sheep[max_idx].y
      else:
        d_behind = d_far + pc
        ux = rx / d_far
        uy = ry / d_far
        rcx = avg_x + d_behind * ux
        rcy = avg_y + d_behind * uy
        target_x, target_y = rcx, rcy
    else:
      # drive: go behind the whole group in its direction of motion (approx. from origin) :contentReference[oaicite:5]{index=5}
      grp_norm = math.hypot(avg_x, avg_y)
      if grp_norm == 0.0:
        # degenerate; don't move
        return
      d_behind = grp_norm + pd
      ux = avg_x / grp_norm
      uy = avg_y / grp_norm
      target_x = d_behind * ux
      target_y = d_behind * uy

    # move dog towards target with angular noise
    dir_x = target_x - self.x
    dir_y = target_y - self.y
    norm = math.hypot(dir_x, dir_y)
    if norm == 0.0:
      return

    dir_x /= norm
    dir_y /= norm

    theta_err = random.random() * 2.0 * math.pi
    err_x = math.cos(theta_err)
    err_y = math.sin(theta_err)

    ux = dir_x + noise_strength * err_x
    uy = dir_y + noise_strength * err_y
    norm2 = math.hypot(ux, uy)
    if norm2 == 0.0:
      return

    ux /= norm2
    uy /= norm2

    self.vx = ux * self.speed_const
    self.vy = uy * self.speed_const

    self.x += self.vx * dt
    self.y += self.vy * dt


class AgentUtils:
  @staticmethod
  def speed(vx, vy):
    return math.hypot(vx, vy)

  @staticmethod
  def heading(vx, vy):
    return math.atan2(vy, vx)

  @staticmethod
  def direction(vx, vy):
    speed = AgentUtils.speed(vx, vy)
    if speed == 0:
      return (0.0, 0.0)
    return (vx / speed, vy / speed)

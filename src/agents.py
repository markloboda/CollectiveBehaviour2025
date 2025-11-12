import math
import random

class Agent:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0

    @property
    def speed(self):
        return AgentUtils.speed(self.vx, self.vy)

    @property
    def heading(self):
        return AgentUtils.heading(self.vx, self.vy)

    @property
    def direction(self):
        return AgentUtils.direction(self.vx, self.vy)

    def move(self, dt: float):
      (move_x, move_y) = (self.speed[0] * dt, self.speed[1] * dt)
      (dir_x, dir_y)   = self.direction[0]
      (self.x, self.y) = (self.x + move_x * dir_x, self.y + move_y * dir_y)

    def viewing_angle_to(self, other: 'Agent') -> float:
      theta_ij = math.atan2(other.y - self.y, other.x - self.x)
      psi_ij = theta_ij - self.heading
      psi_ij = (psi_ij + math.pi) % (2 * math.pi) - math.pi # normalize to [-pi, pi]
      return psi_ij

    def alignment_with(self, other: 'Agent') -> float:
      phi_ij = other.heading - self.heading
      phi_ij = (phi_ij + math.pi) % (2 * math.pi) - math.pi
      return phi_ij

class Sheep(Agent):
  def __init__(self, x, y):
    super().__init__(x, y)
    # Runtime params
    self.social_interactions = (0, 0)
    self.dog_repulsion       = (0, 0)
    self.noise               = (0, 0)

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

  def update_repulsion(self, dogPos, wDog, dDog): #dDog = R_D in paper
    dx = self.x - dogPos[0]
    dy = self.y - dogPos[1]
    dist = math.hypot(dx, dy)
    if dist < dDog and dist > 0:
      self.dog_repulsion = (wDog * dx / dist, wDog * dy / dist)
    else:
      self.dog_repulsion = (0.0, 0.0)

  def update_noise(self):
    self.noise = (random.random(), random.random())

  def move(self, dt):
    # update position
    # update velocity
    pass

class Dog(Agent):
    pass

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
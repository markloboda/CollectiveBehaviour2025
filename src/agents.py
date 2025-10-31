import math

class Sheep:
  def __init__(self, x, y):
    self.x = x
    self.y = y

    self.heading_angle_deg = 0
    self.speed = 0

  def update_social(self, dt, neighbours):
    # updates social interactions to later be used with movement
    pass

  def update_repulsion(self, dt, shepherd):
    # update repulsion from the dog to later be used with movement
    pass

  def move(self, dt):
    # update heading and speed

    # update location
    heading_angle_rad = math.radians(self.heading_angle_deg)
    self.y += self.speed * math.sin(heading_angle_rad) * dt
    self.x += self.speed * math.cos(heading_angle_rad) * dt


class Dog:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.speed = 0
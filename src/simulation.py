import random
import time
from agents import Agent

class Simulation:
  def __init__(self, num_sheep, num_shepherds, field_size):
    self.num_sheep = num_sheep
    self.num_shepherds = num_shepherds
    self.field_size = field_size

    self.sheep = [Agent(random.uniform(0, field_size[0]), random.uniform(0, field_size[1]))
                  for _ in range(num_sheep)]

    self.shepherds = [Agent(random.uniform(0, field_size[0]), random.uniform(0, field_size[1]))
                      for _ in range(num_shepherds)]

  def update(self, dt):
    for sheep in self.sheep:
      pass

    avg_x = sum(s.x for s in self.sheep) / len(self.sheep)
    avg_y = sum(s.y for s in self.sheep) / len(self.sheep)
      
    for shepherd in self.shepherds:
      pass

  def run(self, steps=100, dt=1, delay=0.1):
    print("Starting simulation...")
    for step in range(steps):
      self.update(dt)
      print(f"Step {step + 1}")
      time.sleep(delay)
    print("Simulation finished.")

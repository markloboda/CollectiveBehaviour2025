from simulation import Simulation
from visulizer import SimulationVisualizer, SimulationRecorder


def main():
  WORLD_WIDTH = 100
  WORLD_HEIGHT = 100
  sim = Simulation(
    num_sheep=10,
    num_shepherds=1,
    field_size=(WORLD_WIDTH, WORLD_HEIGHT),
  )

  sim_steps = sim.steps(steps=1000)

  #print(list(sim_steps()))

  player = SimulationVisualizer()
  player.run(sim_steps)

  #recorder = SimulationRecorder(WORLD_WIDTH, WORLD_HEIGHT)
  #recorder.record(sim_steps, "test.gif")

  #print(sim.steps())

  #sim.run(
  #  steps=100,
  #  dt = 1.0  # seconds
  #)

if __name__ == "__main__":
  main()

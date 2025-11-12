from dataclasses import dataclass
from typing import List, Tuple

from agents import Sheep, Dog


@dataclass
class SimulationState:
  tick: int
  time: float

  bounds: Tuple[float, float]

  sheep: List[Sheep]
  dogs: List[Dog]

  # Barycenter, cohesion, polarization, barycenter_velocity, ...?

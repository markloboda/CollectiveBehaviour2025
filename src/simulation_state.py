import math
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

  # metrics:
  barycenter: Tuple[float, float] | None
  velocity: Tuple[float, float] | None
  direction: Tuple[float, float] | None
  perp_direction: Tuple[float, float] | None
  cohesion: float | None
  polarization: float | None
  elongation: float | None
  dog_offsets: Tuple[float, float] | None
  dog_rear_distance: Tuple[float, float] | None


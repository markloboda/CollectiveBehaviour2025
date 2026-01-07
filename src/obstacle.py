import math
from dataclasses import dataclass


def _clamp(v: float, lo: float, hi: float) -> float:
  return max(lo, min(hi, v))


@dataclass(frozen=True)
class RectObstacle:
  xmin: float
  ymin: float
  xmax: float
  ymax: float
  influence: float
  weight: float


  def repulsion(self, x: float, y: float) -> tuple[float, float]:
    # closest point on rectangle to (x,y)
    cx = _clamp(x, self.xmin, self.xmax)
    cy = _clamp(y, self.ymin, self.ymax)

    dx = x - cx
    dy = y - cy
    d = math.hypot(dx, dy)

    if d <= 1e-9:
      # inside rectangle (or exactly on boundary): push toward nearest side
      left   = abs(x - self.xmin)
      right  = abs(self.xmax - x)
      bottom = abs(y - self.ymin)
      top    = abs(self.ymax - y)

      m = min(left, right, bottom, top)
      if m == left:
        ux, uy = -1.0, 0.0
      elif m == right:
        ux, uy =  1.0, 0.0
      elif m == bottom:
        ux, uy = 0.0, -1.0
      else:
        ux, uy = 0.0,  1.0

      # treat as max-strength repulsion
      return (self.weight * ux, self.weight * uy)

    if d >= self.influence:
      return (0.0, 0.0)

    ux, uy = dx / d, dy / d
    t = (self.influence - d) / self.influence
    strength = self.weight * (t * t)
    return (strength * ux, strength * uy)
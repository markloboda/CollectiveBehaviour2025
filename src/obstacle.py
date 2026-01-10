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



  def repulsion(self, x: float, y: float, influence: float, repulsion_weight: float) -> tuple[float, float]:
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
      return (repulsion_weight * ux, repulsion_weight * uy)

    if d >= influence:
      return (0.0, 0.0)

    ux, uy = dx / d, dy / d
    t = (influence - d) / influence
    #strength = (1 - d / influence) * repulsion_weight
    strength = repulsion_weight * (t * t)
    return (-strength * ux, strength * uy)



  def deflect(self, x: float, y: float) -> tuple[float, float]:
    if not ((self.xmin <= x <= self.xmax) and (self.ymin <= y <= self.ymax)):
      return (x, y)

    # penetration depths to each side (non-negative when inside)
    left   = x - self.xmin
    right  = self.xmax - x
    bottom = y - self.ymin
    top    = self.ymax - y

    m = min(left, right, bottom, top)
    eps = 0.1  # tiny nudge outside

    if m == left:
      return (self.xmin - eps, y)
    if m == right:
      return (self.xmax + eps, y)
    if m == bottom:
      return (x, self.ymin - eps)
    return (x, self.ymax + eps)



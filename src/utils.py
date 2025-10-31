import math

class Vector2D:
  def __init__(self, x=0.0, y=0.0):
    self.x = x
    self.y = y

  def __add__(self, other):
    return Vector2D(self.x + other.x, self.y + other.y)

  def __sub__(self, other):
    return Vector2D(self.x - other.x, self.y - other.y)

  def __mul__(self, scalar):
    return Vector2D(self.x * scalar, self.y * scalar)

  __rmul__ = __mul__

  def __truediv__(self, scalar):
    return Vector2D(self.x / scalar, self.y / scalar)

  def __repr__(self):
    return f"Vector2D({self.x:.2f}, {self.y:.2f})"

  def length(self):
    return math.hypot(self.x, self.y)

  def normalized(self):
    l = self.length()
    return Vector2D(self.x / l, self.y / l) if l != 0 else Vector2D()

  @staticmethod
  def from_angle(deg):
    """Create a unit vector from an angle in degrees."""
    rad = math.radians(deg)
    return Vector2D(math.cos(rad), math.sin(rad))

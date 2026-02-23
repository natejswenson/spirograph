import math
from math import gcd


class SpiroMath:
    """Hypotrochoid parametric equations and period calculation."""

    def get_period(self, R, r):
        """Number of full inner-wheel loops to complete the curve."""
        ri = max(1, int(round(r)))
        Ri = max(1, int(round(R)))
        return ri // max(1, gcd(Ri, ri))

    def compute_points(self, R, r, d, steps=6000):
        """Return list of (x, y) hypotrochoid points centred at origin."""
        loops   = self.get_period(R, r)
        total_t = 2 * math.pi * loops
        pts = []
        for i in range(steps + 1):
            t = total_t * i / steps
            x = (R - r) * math.cos(t) + d * math.cos((R - r) * t / max(r, 0.001))
            y = (R - r) * math.sin(t) - d * math.sin((R - r) * t / max(r, 0.001))
            pts.append((x, y))
        return pts

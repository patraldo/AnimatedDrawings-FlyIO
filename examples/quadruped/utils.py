import math

def distance(p1, p2):
    """Calculate Euclidean distance between two points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def angle_between(a, b, c):
    """
    Calculate the angle at point b (in degrees) given three points a, b, and c.
    Angle is formed between vectors (a->b) and (c->b).
    """
    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]
    dot_prod = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])
    if mag_ba == 0 or mag_bc == 0:
        return 0
    angle = math.acos(dot_prod / (mag_ba * mag_bc))
    return math.degrees(angle)

def validate_y_within_bounds(loc, height):
    """Ensure the y-coordinate of a joint does not exceed the image height."""
    if loc[1] >= height:
        loc[1] = height - 1  # Clamp y value
    return loc

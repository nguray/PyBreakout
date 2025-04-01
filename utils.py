
def orientation(p, q, r):
    """Returns the orientation of the ordered triplet (p, q, r)."""
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0  # collinear
    elif val > 0:
        return 1  # clockwise
    else:
        return 2  # counterclockwise


def on_segment(p, q, r):
    """Checks if point q lies on segment pr."""
    if min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1]):
        return True
    return False


def compute_intersection(p1, p2, q1, q2):
    """Computes the intersection point of two line segments (if any)."""
    # Compute the orientation of the ordered triplets
    o1 = orientation(p1, p2, q1)
    o2 = orientation(p1, p2, q2)
    o3 = orientation(q1, q2, p1)
    o4 = orientation(q1, q2, p2)

    # General case: the segments straddle each other
    if o1 != o2 and o3 != o4:
        # Solve for the intersection point
        denom = (p1[0] - p2[0]) * (q1[1] - q2[1]) - (p1[1] - p2[1]) * (q1[0] - q2[0])
        num1 = (p1[0] * p2[1] - p1[1] * p2[0])
        num2 = (q1[0] * q2[1] - q1[1] * q2[0])
        
        intersect_x = (num1 * (q1[0] - q2[0]) - (p1[0] - p2[0]) * num2) / denom
        intersect_y = (num1 * (q1[1] - q2[1]) - (p1[1] - p2[1]) * num2) / denom
        
        return (intersect_x, intersect_y)
    
    # Special cases for collinear segments where the intersection lies on the segment
    # p1, p2, q1 are collinear and q1 lies on segment p1p2
    if o1 == 0 and on_segment(p1, q1, p2):
        return q1
    # p1, p2, q2 are collinear and q2 lies on segment p1p2
    if o2 == 0 and on_segment(p1, q2, p2):
        return q2
    # q1, q2, p1 are collinear and p1 lies on segment q1q2
    if o3 == 0 and on_segment(q1, p1, q2):
        return p1
    # q1, q2, p2 are collinear and p2 lies on segment q1q2
    if o4 == 0 and on_segment(q1, p2, q2):
        return p2
    
    return None  # No intersection


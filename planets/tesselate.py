from functools import lru_cache

@lru_cache(maxsize=128)
def tesselate(quad, segments=100):
    """
    This function takes a 3d quad and returns a grid of points
    in that quad such that the grid is segments x segments in size.
    This comes in handy when we want to do terrain stuff.
    """
    # Points
    p1, p2, p3, p4 = quad[0], quad[1], quad[2], quad[3]
    # New vertices
    new_verts = []
    
    for y in range(segments + 1):
        for x in range(segments + 1):
            # Calculate the point and add it to the list
            point = (
                p1[0] + (p2[0] - p1[0]) * x / segments + (p4[0] - p1[0]) * y / segments,
                p1[1] + (p2[1] - p1[1]) * x / segments + (p4[1] - p1[1]) * y / segments,
                p1[2] + (p2[2] - p1[2]) * x / segments + (p4[2] - p1[2]) * y / segments
            )
            new_verts.append(point)
    # Return the new vertices
    return new_verts

@lru_cache(maxsize=128)
def tesselate_partial(quad, segments=100, denominator=4, numerator=1):
    """
    Same as tesselate function, but only returns a partial grid.
    Useful for multiprocessing stuff.
    """
    # Points
    p1, p2, p3, p4 = quad[0], quad[1], quad[2], quad[3]
    # New vertices
    new_verts = []
    yrange_start = int(segments // denominator * numerator)
    yrange_end = int(segments // denominator * (numerator + 1))    
    for y in range(yrange_start, yrange_end):
        for x in range(segments + 1):
            # Calculate the point and add it to the list
            point = (
                p1[0] + (p2[0] - p1[0]) * x / segments + (p4[0] - p1[0]) * y / segments,
                p1[1] + (p2[1] - p1[1]) * x / segments + (p4[1] - p1[1]) * y / segments,
                p1[2] + (p2[2] - p1[2]) * x / segments + (p4[2] - p1[2]) * y / segments
            )
            new_verts.append(point)
    # Return the new vertices
    return new_verts
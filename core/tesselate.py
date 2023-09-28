import numba


@numba.jit(nopython=True)
def tesselate(quad, segments=100):
    """
    This function takes a 3d quad and returns a triangle mesh
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
            point1 = (
                p1[0] + (p2[0] - p1[0]) * x / segments +
                (p4[0] - p1[0]) * y / segments,
                p1[1] + (p2[1] - p1[1]) * x / segments +
                (p4[1] - p1[1]) * y / segments,
                p1[2] + (p2[2] - p1[2]) * x / segments +
                (p4[2] - p1[2]) * y / segments,
            )
            point2 = (
                p1[0] + (p2[0] - p1[0]) * x / segments + (p4[0] - p1[0]) *
                (y + 1) / segments,
                p1[1] + (p2[1] - p1[1]) * x / segments + (p4[1] - p1[1]) *
                (y + 1) / segments,
                p1[2] + (p2[2] - p1[2]) * x / segments + (p4[2] - p1[2]) *
                (y + 1) / segments,
            )
            point3 = (
                p1[0] + (p2[0] - p1[0]) * (x + 1) / segments +
                (p4[0] - p1[0]) * y / segments,
                p1[1] + (p2[1] - p1[1]) * (x + 1) / segments +
                (p4[1] - p1[1]) * y / segments,
                p1[2] + (p2[2] - p1[2]) * (x + 1) / segments +
                (p4[2] - p1[2]) * y / segments,
            )
            point4 = (
                p1[0] + (p2[0] - p1[0]) * (x + 1) / segments +
                (p4[0] - p1[0]) * (y + 1) / segments,
                p1[1] + (p2[1] - p1[1]) * (x + 1) / segments +
                (p4[1] - p1[1]) * (y + 1) / segments,
                p1[2] + (p2[2] - p1[2]) * (x + 1) / segments +
                (p4[2] - p1[2]) * (y + 1) / segments,
            )
            # Add the points to the list
            new_verts.extend((point1, point2, point3, point3, point2, point4))
    # Return the new vertices
    return new_verts


@numba.jit(nopython=True)
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
            point1 = (
                p1[0] + (p2[0] - p1[0]) * x / segments +
                (p4[0] - p1[0]) * y / segments,
                p1[1] + (p2[1] - p1[1]) * x / segments +
                (p4[1] - p1[1]) * y / segments,
                p1[2] + (p2[2] - p1[2]) * x / segments +
                (p4[2] - p1[2]) * y / segments,
            )
            point2 = (
                p1[0] + (p2[0] - p1[0]) * x / segments + (p4[0] - p1[0]) *
                (y + 1) / segments,
                p1[1] + (p2[1] - p1[1]) * x / segments + (p4[1] - p1[1]) *
                (y + 1) / segments,
                p1[2] + (p2[2] - p1[2]) * x / segments + (p4[2] - p1[2]) *
                (y + 1) / segments,
            )
            point3 = (
                p1[0] + (p2[0] - p1[0]) * (x + 1) / segments +
                (p4[0] - p1[0]) * y / segments,
                p1[1] + (p2[1] - p1[1]) * (x + 1) / segments +
                (p4[1] - p1[1]) * y / segments,
                p1[2] + (p2[2] - p1[2]) * (x + 1) / segments +
                (p4[2] - p1[2]) * y / segments,
            )
            point4 = (
                p1[0] + (p2[0] - p1[0]) * (x + 1) / segments +
                (p4[0] - p1[0]) * (y + 1) / segments,
                p1[1] + (p2[1] - p1[1]) * (x + 1) / segments +
                (p4[1] - p1[1]) * (y + 1) / segments,
                p1[2] + (p2[2] - p1[2]) * (x + 1) / segments +
                (p4[2] - p1[2]) * (y + 1) / segments,
            )
            # Add the points to the list
            new_verts.extend((point1, point2, point3, point3, point2, point4))
    # Return the new vertices
    return new_verts

import taichi as ti
import numpy as np
ti.init(arch=ti.cpu)

def fast_tesselate(quad: np.array, segments: int) -> np.array:
    """
    This function takes a rect in 3d space and tesselates it.
    
    :param quad: An np.array of shape (4, 3) which contains the vertices of the quad to be tesselated
    :param segments: The number of segments the quad must be tessellated into.
    """
    new_vertices = ti.field(dtype=ti.f64, shape=(segments + 1) ** 2 * 12)
    
    quad_field = ti.field(ti.f32, shape=quad.shape)
    quad_field.fill(0)
    for x in range(len(quad)):
        for y in range(len(quad[x])):
            quad_field[x, y] = quad[x, y]

    @ti.kernel
    def tesselate():
        p1 = [quad_field[0, 0], quad_field[0, 1], quad_field[0, 2]]
        p2 = [quad_field[1, 0], quad_field[1, 1], quad_field[1, 2]]
        p4 = [quad_field[3, 0], quad_field[3, 1], quad_field[3, 2]]
        
        inv_segments = 1 / segments
        
        ti.loop_config(parallelize=True)
        for y in range(segments + 1):
            yp1 = (y + 1)
            ti.loop_config(parallelize=True)
            for x in range(segments + 1):
                current = (y * (segments + 1) + x) * 12
                
                a = (p2[0] - p1[0]) * x * inv_segments + (p4[0] - p1[0])
                b = (p2[1] - p1[1]) * x * inv_segments + (p4[1] - p1[1])
                c = (p2[2] - p1[2]) * x * inv_segments + (p4[2] - p1[2])
                
                new_vertices[current +  0] = p1[0] + a * y * inv_segments
                new_vertices[current +  1] = p1[1] + b * y * inv_segments
                new_vertices[current +  2] = p1[2] + c * y * inv_segments
                
                new_vertices[current +  3] = p1[0] + a * yp1 * inv_segments
                new_vertices[current +  4] = p1[1] + b * yp1 * inv_segments
                new_vertices[current +  5] = p1[2] + x * yp1 * inv_segments
                
                d = (p2[0] - p1[0]) * (x + 1) * inv_segments + (p4[0] - p1[0])
                e = (p2[1] - p1[1]) * (x + 1) * inv_segments + (p4[1] - p1[1])
                f = (p2[2] - p1[2]) * (x + 1) * inv_segments + (p4[2] - p1[2])
                
                new_vertices[current +  6] = p1[0] + d * y * inv_segments
                new_vertices[current +  7] = p1[1] + e * y * inv_segments
                new_vertices[current +  8] = p1[2] + f * y * inv_segments
                
                new_vertices[current +  9] = p1[0] + d * yp1 * inv_segments
                new_vertices[current + 10] = p1[1] + e * yp1 * inv_segments
                new_vertices[current + 11] = p1[2] + f * yp1 * inv_segments

    tesselate()
    return np.asarray(new_vertices)

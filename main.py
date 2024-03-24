import taichi as ti
from time import perf_counter
ti.init(arch=ti.cpu)

# New vertices
segments = 128
new_verts = ti.field(dtype=ti.f64, shape=(segments + 1) ** 2 * 12)
last_written = 0

coords = ti.field(ti.f32, shape=(4, 3))
coords.fill(0)
coords[1, 0] = 1
coords[2, 0] = 1
coords[2, 1] = 1
coords[3, 1] = 1

@ti.kernel
def fast_tesselate():
    p1 = [coords[0, 0], coords[0, 1], coords[0, 2]]
    p2 = [coords[1, 0], coords[1, 1], coords[1, 2]]
    p4 = [coords[3, 0], coords[3, 1], coords[3, 2]]
    
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
            
            new_verts[current +  0] = p1[0] + a * y * inv_segments
            new_verts[current +  1] = p1[1] + b * y * inv_segments
            new_verts[current +  2] = p1[2] + c * y * inv_segments
            
            new_verts[current +  3] = p1[0] + a * yp1 * inv_segments
            new_verts[current +  4] = p1[1] + b * yp1 * inv_segments
            new_verts[current +  5] = p1[2] + x * yp1 * inv_segments
            
            d = (p2[0] - p1[0]) * (x + 1) * inv_segments + (p4[0] - p1[0])
            e = (p2[1] - p1[1]) * (x + 1) * inv_segments + (p4[1] - p1[1])
            f = (p2[2] - p1[2]) * (x + 1) * inv_segments + (p4[2] - p1[2])
            
            new_verts[current +  6] = p1[0] + d * y * inv_segments
            new_verts[current +  7] = p1[1] + e * y * inv_segments
            new_verts[current +  8] = p1[2] + f * y * inv_segments
            
            new_verts[current +  9] = p1[0] + d * yp1 * inv_segments
            new_verts[current + 10] = p1[1] + e * yp1 * inv_segments
            new_verts[current + 11] = p1[2] + f * yp1 * inv_segments

t = perf_counter()
n = 100
for i in range(n):
    fast_tesselate()
    print(new_verts)
new = perf_counter()
print(f"Done in {new - t}s! That's {(new - t) / n}s per operation!")
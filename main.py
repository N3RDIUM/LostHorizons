from time import perf_counter

import taichi as ti

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

    ti.loop_config(serialize=True)
    for y in range(segments + 1):
        for x in range(segments + 1):
            new_verts[(y * (segments + 1) + x) * 12 + 0] = (
                p1[0] + (p2[0] - p1[0]) * x / segments + (p4[0] - p1[0]) * y / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 1] = (
                p1[1] + (p2[1] - p1[1]) * x / segments + (p4[1] - p1[1]) * y / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 2] = (
                p1[2] + (p2[2] - p1[2]) * x / segments + (p4[2] - p1[2]) * y / segments
            )

            new_verts[(y * (segments + 1) + x) * 12 + 3] = (
                p1[0]
                + (p2[0] - p1[0]) * x / segments
                + (p4[0] - p1[0]) * (y + 1) / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 4] = (
                p1[1]
                + (p2[1] - p1[1]) * x / segments
                + (p4[1] - p1[1]) * (y + 1) / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 5] = (
                p1[2]
                + (p2[2] - p1[2]) * x / segments
                + (p4[2] - p1[2]) * (y + 1) / segments
            )

            new_verts[(y * (segments + 1) + x) * 12 + 6] = (
                p1[0]
                + (p2[0] - p1[0]) * (x + 1) / segments
                + (p4[0] - p1[0]) * y / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 7] = (
                p1[1]
                + (p2[1] - p1[1]) * (x + 1) / segments
                + (p4[1] - p1[1]) * y / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 8] = (
                p1[2]
                + (p2[2] - p1[2]) * (x + 1) / segments
                + (p4[2] - p1[2]) * y / segments
            )

            new_verts[(y * (segments + 1) + x) * 12 + 9] = (
                p1[0]
                + (p2[0] - p1[0]) * (x + 1) / segments
                + (p4[0] - p1[0]) * (y + 1) / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 10] = (
                p1[1]
                + (p2[1] - p1[1]) * (x + 1) / segments
                + (p4[1] - p1[1]) * (y + 1) / segments
            )
            new_verts[(y * (segments + 1) + x) * 12 + 11] = (
                p1[2]
                + (p2[2] - p1[2]) * (x + 1) / segments
                + (p4[2] - p1[2]) * (y + 1) / segments
            )


t = perf_counter()
tesselate()
print(new_verts)
print(f"done in {perf_counter() - t}s")

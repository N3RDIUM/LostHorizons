import numpy as np
import opensimplex
from time import perf_counter

noise = opensimplex.OpenSimplex(65536)
side = 128

t = perf_counter()
n = 100

for i in range(n):
    noisevals = np.zeros(shape=((side + 1) ** 2))
    for x in range(side + 1):
        for y in range(side + 1):
            noisevals[x * (side + 1) + y] = (noise.noise4(x, y, n, 9932))

print(f'Took {perf_counter() - t}s. That\'s {(perf_counter() - t) / 100}s per call!')
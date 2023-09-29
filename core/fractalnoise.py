import noise


def fractal_noise(point):
    noiseSum = 0
    amplitude = 1
    frequency = 1

    for i in range(16):
        noiseSum += (noise.pnoise3(point[0] * frequency, point[1] * frequency,
                                   point[2] * frequency) * amplitude)
        frequency *= 2
        amplitude *= 0.5

    return noiseSum


def fractal_ridge_noise(point):
    return 1 - abs(fractal_noise(point))

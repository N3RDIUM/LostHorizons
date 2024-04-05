import noise


def fractal_noise(point, seed, octaves):
    noiseSum = 0
    amplitude = 1
    frequency = 1

    for i in range(octaves):
        noiseSum += (
            noise.snoise4(
                point[0] * frequency,
                point[1] * frequency,
                point[2] * frequency,
                seed * 32,
            )
            * amplitude
        )
        frequency *= 2
        amplitude *= 0.5

    return noiseSum


def fractal_ridge_noise(point, seed=0, octaves=16):
    return 1 - abs(fractal_noise(point, seed, octaves))

import math


def normalize(vector):
    length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
    return vector[0] / length, vector[1] / length, vector[2] / length

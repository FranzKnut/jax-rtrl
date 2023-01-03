import numpy as np

from functions.Function import Function


### --- Define Identity --- ###

def identity_(z):
    return z


def identity_derivative(z):
    return np.ones_like(z)


identity = Function(identity_, identity_derivative)

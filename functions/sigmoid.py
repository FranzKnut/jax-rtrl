import numpy as np

from functions.Function import Function


### --- Define sigmoid --- ###

def sigmoid_(z):
    return 1 / (1 + np.exp(-z))


def sigmoid_derivative(z):
    return sigmoid_(z) * (1 - sigmoid_(z))


sigmoid = Function(sigmoid_, sigmoid_derivative)

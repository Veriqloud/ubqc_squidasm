import numpy as np

def measure_angle(M, outcome_array, input_angle):
    """Angle to measrue qubit i

    :M: gate object
    :outcome_array: list of qubit outcomes
    :input_angle: random angle in radians that was generated for measuring
    """
    c = 0
    s = 0
    computation_angle = M.angle
    for q in M.X_idxs:
        if q==0:
            c += 1
        else:
            c += outcome_array[q-1]
    for q in M.Z_idxs:
        if q==0:
            s += 1
        else:
            s += outcome_array[q-1]

    return (input_angle + ((-1) ** c) * (computation_angle) + (s * 128) ) % 256 #SimulaQron takes one step of angle as pi/255, hence the given description

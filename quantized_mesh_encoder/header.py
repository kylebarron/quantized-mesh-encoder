import numpy as np



def compute_header(positions, indices):

    cartesian_positions = to_ecef(positions)

    ecef_min_x = cartesian_positions[0].min()
    ecef_min_y = cartesian_positions[1].min()
    ecef_min_z = cartesian_positions[2].min()
    ecef_max_x = cartesian_positions[0].max()
    ecef_max_y = cartesian_positions[1].max()
    ecef_max_z = cartesian_positions[2].max()

    min_height = positions[:, 2].min()
    max_height = positions[:, 2].max()

    pass







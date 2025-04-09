'''Auxiliar functions to calculate Set Coverage and Epsilon Indicator'''
import numpy as np

import plotly.graph_objects as go


def dominates(point_a, point_b):

    cond1 = all(a >= b for a, b in zip(point_a, point_b))
    # cond2 = any(a > b for a, b in zip(point_a, point_b))
    cond2 = True  # To allow weak dominance A >= B

    return cond1 and cond2


def set_coverage(A, B):
    '''
    Number of solutions in reference front B dominated by any solution in evaluated front A.
    '''
    count = 0
    for b in B:
        if any(dominates(a, b) for a in A):
            count += 1
    return count / len(B)


def epsilon_indicator_mul(A, B):
    '''
    Calculates the smallest factor eps that moves the evaluated front A to ensure that every
    solution from reference front B is dominated by A.
    '''
    eps = float('-inf')
    for a in A:
        min_eps = float('inf')
        for b in B:
            max_ratio = max(b[i] / a[i] for i in range(len(a)))
            min_eps = min(min_eps, max_ratio)
        eps = max(eps, min_eps)
    return eps


def epsilon_indicator_add(A, B):
    '''
    Calculates the smallest distance eps that moves the evaluated front A to ensure that every
    solution from reference front B is dominated by A.
    '''
    eps = float('-inf')
    for b in B:
        min_eps = float('inf')
        for a in A:
            max_ratio = max(b[i] - a[i] for i in range(len(a)))
            min_eps = min(min_eps, max_ratio)
        eps = max(eps, min_eps)
    return eps


def add_front_area(figure: go.Figure, pareto_front: np.array, name: str, color):
    '''
    Adds a trace of the area generated under the Pareto front with respect to the origin (0, 0)
    '''
    # Start with the initial point
    new_points = np.array([[0, 0]])

    # Loop through each point in the original list
    for point in pareto_front:
        # Get the last point in the new_points list
        last_point = new_points[-1]

        # Step 1: Move horizontally to the x-coordinate of the current point
        if last_point[0] != point[0]:  # Only add if x-coordinates differ
            new_points = np.concatenate([new_points,
                                         np.array([[point[0], last_point[1]]])])

        # Step 2: Move vertically to the y-coordinate of the current point
        if last_point[1] != point[1]:  # Only add if y-coordinates differ
            new_points = np.concatenate([new_points, np.array([point])])

    # Add the final segment to return to the starting y-coordinate, then x-coordinate
    # Closing the loop by moving vertically, then horizontally back to [0, 0]
    new_points = np.concatenate([new_points,
                                 np.array([[0, new_points[-1][1]]]),
                                 np.array([[0, 0]])])

    figure.add_scatter(
        x=new_points[:, 0], y=new_points[:, 1], mode='lines', line_color=color,
        name=name, legendgroup=name, showlegend=True
    )
    figure.add_scatter(
        x=pareto_front[:, 0], y=pareto_front[:, 1], mode='markers', line_color=color,
        legendgroup=name, showlegend=False
    )

    return figure

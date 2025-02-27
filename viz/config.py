# Simulation parameters
T_FINAL = 10
N_COARSE = 5
DT_COARSE = T_FINAL / N_COARSE
N_FINE_STEPS = 30
N_ITERATIONS = 3  # Number of Parareal iterations

# Visualization settings
COLORS = {
    "exact": "GREY",
    "coarse": "BLUE",
    "fine": "RED",
    "iteration1": "YELLOW",
    "iteration2": "GREEN",
    "iteration3": "PURPLE",
}
AXES_CONFIG = {
    "x_range": [0, T_FINAL, 2],
    "y_range": [-2, 2, 1],
    "axis_config": {"color": "GREY"},
    "x_axis_config": {"numbers_to_include": [0, 2, 4, 6, 8, 10]},
    "y_axis_config": {"numbers_to_include": [-2, -1, 0, 1, 2]},
}

# ODE parameters
INITIAL_CONDITIONS = [1.0, 0.0]  # [position, velocity]

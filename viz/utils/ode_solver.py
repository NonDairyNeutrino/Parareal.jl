import numpy as np
from scipy.integrate import solve_ivp

def pendulum_ode(t, y):
    """
    The ODE for a damped pendulum:
    y[0] = position
    y[1] = velocity
    y'[0] = y[1]
    y'[1] = -0.1 * y[1] - sin(y[0])
    """
    return [y[1], -0.1 * y[1] - np.sin(y[0])]

def solve_exact(t_start, t_end, y_init, n_points=200):
    """
    Solve the ODE using a high-resolution method for an "exact" solution
    """
    t_eval = np.linspace(t_start, t_end, n_points)
    sol = solve_ivp(pendulum_ode, [t_start, t_end], y_init, t_eval=t_eval)
    return sol.t, sol.y

def solve_coarse(t_start, t_end, y_init, n_points=20):
    """
    Solve the ODE using a coarse method
    """
    # In practice, this would use a different/faster solver
    # For demonstration, we're using the same solver with fewer points
    t_eval = np.linspace(t_start, t_end, n_points)
    sol = solve_ivp(pendulum_ode, [t_start, t_end], y_init, t_eval=t_eval)
    return sol.t, sol.y

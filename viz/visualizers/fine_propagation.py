from manim import *
import numpy as np
from visualizers.base_visualizer import BaseVisualizer
from utils.ode_solver import solve_exact
from config import T_FINAL, N_COARSE, DT_COARSE, N_FINE_STEPS, INITIAL_CONDITIONS, COLORS

class FinePropagationVisualizer(BaseVisualizer):
    def __init__(self, scene, axes):
        super().__init__(scene, axes)
        self.points = []
        
    def create(self):
        # Get the exact solution for reference
        t_exact, y_exact = solve_exact(0, T_FINAL, INITIAL_CONDITIONS)
        
        # Initialize fine propagation points
        for i in range(N_COARSE + 1):
            point = Dot(self.axes.c2p(i * DT_COARSE, INITIAL_CONDITIONS[0]), color=eval(COLORS["fine"]))
            self.points.append(point)
            self.scene.add(point)
        
        # Animate fine propagation
        for step in range(N_FINE_STEPS):
            new_points = []
            for i in range(N_COARSE + 1):
                t = i * DT_COARSE + DT_COARSE * step / N_FINE_STEPS
                sol_value = np.interp(t, t_exact, y_exact[0])
                new_point = Dot(self.axes.c2p(t, sol_value), color=eval(COLORS["fine"]))
                new_points.append(new_point)
            
            self.scene.play(
                *[Transform(self.points[i], new_points[i]) for i in range(N_COARSE + 1)],
                run_time=0.1
            )
        
        return VGroup(*self.points)
        
    def remove(self):
        if self.points:
            self.scene.play(FadeOut(VGroup(*self.points)))
            self.points = []

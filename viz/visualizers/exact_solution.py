from manim import *
import numpy as np
from visualizers.base_visualizer import BaseVisualizer
from utils.ode_solver import solve_exact
from config import T_FINAL, INITIAL_CONDITIONS, COLORS

class ExactSolutionVisualizer(BaseVisualizer):
    def __init__(self, scene, axes):
        super().__init__(scene, axes)
        self.curve = None
        
    def create(self):
        # Solve the ODE for the entire time domain
        t, y = solve_exact(0, T_FINAL, INITIAL_CONDITIONS)
        
        # Create the curve
        self.curve = self.axes.plot(
            lambda x: np.interp(x, t, y[0]),
            color=eval(COLORS["exact"]),
            stroke_width=2,
            stroke_opacity=0.5
        )
        
        # Animate
        self.scene.play(
            Create(self.curve),
            run_time=2
        )
        
        return self.curve
        
    def remove(self):
        if self.curve:
            self.scene.play(FadeOut(self.curve))
            self.curve = None

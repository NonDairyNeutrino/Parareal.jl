from manim import *
import numpy as np
from visualizers.base_visualizer import BaseVisualizer
from utils.ode_solver import solve_coarse
from config import T_FINAL, N_COARSE, DT_COARSE, INITIAL_CONDITIONS, COLORS

class CoarsePropagationVisualizer(BaseVisualizer):
    def __init__(self, scene, axes):
        super().__init__(scene, axes)
        self.points = []
        self.lines = []
        self.subdomain_lines = None
        
    def create(self):
        y_current = INITIAL_CONDITIONS[0]
        v_current = INITIAL_CONDITIONS[1]
        
        for i in range(N_COARSE):
            t_start = i * DT_COARSE
            t_end = (i + 1) * DT_COARSE
            
            # Solve for this interval
            t_coarse, y_coarse = solve_coarse(t_start, t_end, [y_current, v_current])
            
            # Create dot at the starting point
            point = Dot(self.axes.c2p(t_start, y_current), color=eval(COLORS["coarse"]))
            self.points.append(point)
            
            # Create line for this interval
            line = self.axes.plot(
                lambda x: np.interp(x, t_coarse, y_coarse[0]),
                x_range=[t_start, t_end],
                color=eval(COLORS["coarse"])
            )
            self.lines.append(line)
            
            # Animate
            self.scene.play(
                Create(point),
                Create(line),
                run_time=1
            )
            
            # Update for next interval
            y_current = y_coarse[0][-1]
            v_current = y_coarse[1][-1]
        
        # Add final point
        final_point = Dot(self.axes.c2p(T_FINAL, y_current), color=eval(COLORS["coarse"]))
        self.points.append(final_point)
        self.scene.play(Create(final_point))
        
        return VGroup(*self.points, *self.lines)
    
    def create_subdomains(self):
        # Add vertical lines for subdomains
        self.subdomain_lines = VGroup(*[
            DashedLine(
                self.axes.c2p(i * DT_COARSE, -2),
                self.axes.c2p(i * DT_COARSE, 2),
                color=GREY,
                stroke_opacity=0.5
            )
            for i in range(1, N_COARSE)
        ])
        
        self.scene.play(
            Create(self.subdomain_lines),
            run_time=2
        )
        
        return self.subdomain_lines
        
    def remove(self):
        objects_to_remove = []
        
        if self.points:
            objects_to_remove.extend(self.points)
            self.points = []
            
        if self.lines:
            objects_to_remove.extend(self.lines)
            self.lines = []
            
        if self.subdomain_lines:
            objects_to_remove.append(self.subdomain_lines)
            self.subdomain_lines = None
            
        if objects_to_remove:
            self.scene.play(FadeOut(VGroup(*objects_to_remove)))

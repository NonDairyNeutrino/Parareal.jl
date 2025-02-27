from manim import *
import numpy as np
from visualizers.base_visualizer import BaseVisualizer
from utils.ode_solver import solve_exact
from config import T_FINAL, N_COARSE, DT_COARSE, N_FINE_STEPS, INITIAL_CONDITIONS, COLORS

class ParallelFineVisualizer(BaseVisualizer):
    def __init__(self, scene, axes):
        super().__init__(scene, axes)
        self.interval_solutions = []
        
    def create(self):
        # Get the exact solution for reference
        t_exact, y_exact = solve_exact(0, T_FINAL, INITIAL_CONDITIONS)
        
        # Show title
        subtitle = Text("Parallel Fine Propagation", font_size=28)
        subtitle.next_to(self.scene.title, DOWN)
        if hasattr(self.scene, 'subtitle') and self.scene.subtitle:
            self.scene.play(FadeOut(self.scene.subtitle), FadeIn(subtitle))
        else:
            self.scene.play(FadeIn(subtitle))
        self.scene.subtitle = subtitle
        
        # Create parallel solutions for each interval
        start_points = []
        interval_lines = []
        
        # First show the starting points at interval boundaries
        for i in range(N_COARSE + 1):
            t = i * DT_COARSE
            y_val = np.interp(t, t_exact, y_exact[0])
            point = Dot(self.axes.c2p(t, INITIAL_CONDITIONS[0]), color=eval(COLORS["fine"]))
            start_points.append(point)
        
        # Show starting points
        self.scene.play(
            *[Create(p) for p in start_points],
            run_time=1
        )
        
        # Add text indicators for parallel execution
        parallel_indicators = []
        for i in range(N_COARSE):
            t_mid = (i + 0.5) * DT_COARSE
            indicator = Text(f"P{i+1}", font_size=18, color=eval(COLORS["fine"]))
            indicator.move_to(self.axes.c2p(t_mid, -1.5))
            parallel_indicators.append(indicator)
        
        self.scene.play(
            *[FadeIn(indicator) for indicator in parallel_indicators],
            run_time=1
        )
        
        # Now show the fine propagation on each interval simultaneously
        self.interval_solutions = []
        
        for step in range(N_FINE_STEPS + 1):
            new_lines = []
            
            for i in range(N_COARSE):
                t_start = i * DT_COARSE
                t_end = (i + 1) * DT_COARSE
                
                # Calculate intermediate point based on step
                progress = step / N_FINE_STEPS
                t_current = t_start + progress * DT_COARSE
                
                # Get interpolated value from exact solution
                y_start = np.interp(t_start, t_exact, y_exact[0])
                y_current = np.interp(t_current, t_exact, y_exact[0])
                
                # Create line from start to current position
                line = self.axes.plot(
                    lambda x: np.interp(x, [t_start, t_current], [y_start, y_current]),
                    x_range=[t_start, t_current],
                    color=eval(COLORS["fine"])
                )
                
                # Replace previous line for this interval
                if i < len(interval_lines):
                    self.scene.remove(interval_lines[i])
                    interval_lines[i] = line
                else:
                    interval_lines.append(line)
                
                new_lines.append(line)
            
            # Show all lines simultaneously
            self.scene.play(
                *[Create(line) for line in new_lines],
                run_time=0.1
            )
            
            # For last step, store the final solutions
            if step == N_FINE_STEPS:
                self.interval_solutions = interval_lines[:]
        
        # Fade out the process indicators
        self.scene.play(
            *[FadeOut(indicator) for indicator in parallel_indicators],
            run_time=1
        )
        
        # Update the points to show the final values
        end_points = []
        for i in range(N_COARSE + 1):
            t = i * DT_COARSE
            y_val = np.interp(t, t_exact, y_exact[0])
            point = Dot(self.axes.c2p(t, y_val), color=eval(COLORS["fine"]))
            end_points.append(point)
        
        self.scene.play(
            *[Transform(start_points[i], end_points[i]) for i in range(len(start_points))],
            run_time=1
        )
        
        return VGroup(*start_points, *interval_lines)
        
    def remove(self):
        # Remove all mobjects related to this visualization
        self.scene.play(
            *[FadeOut(mob) for mob in self.scene.mobjects if mob != self.scene.axes and 
                                                             mob != self.scene.axes_labels and 
                                                             mob != self.scene.title and
                                                             mob != self.scene.subtitle],
            run_time=1
        )
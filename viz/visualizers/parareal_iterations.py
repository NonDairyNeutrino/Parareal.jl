from manim import *
import numpy as np
from visualizers.base_visualizer import BaseVisualizer
from utils.ode_solver import solve_exact, solve_coarse
from config import T_FINAL, N_COARSE, DT_COARSE, INITIAL_CONDITIONS, COLORS, N_ITERATIONS

class PararealIterationVisualizer(BaseVisualizer):
    def __init__(self, scene, axes):
        super().__init__(scene, axes)
        self.iteration_points = {}
        self.iteration_lines = {}
        
        # Get reference solution
        self.t_exact, self.y_exact = solve_exact(0, T_FINAL, INITIAL_CONDITIONS)
        
        # Initial coarse solution (will be updated in iterations)
        self.y_values = [INITIAL_CONDITIONS[0]]
        self.v_values = [INITIAL_CONDITIONS[1]]
        
        # Initialize with initial coarse propagation
        for i in range(N_COARSE):
            t_start = i * DT_COARSE
            t_end = (i + 1) * DT_COARSE
            
            # Get the initial conditions for this interval
            y_init = [self.y_values[-1], self.v_values[-1]]
            
            # Solve for this interval
            _, y_coarse = solve_coarse(t_start, t_end, y_init)
            
            # Store the end values
            self.y_values.append(y_coarse[0][-1])
            self.v_values.append(y_coarse[1][-1])
            
        # Store initial fine solutions (we'll use exact for demonstration)
        self.fine_solutions = []
        for i in range(N_COARSE):
            t_start = i * DT_COARSE
            t_end = (i + 1) * DT_COARSE
            t_interval = np.linspace(t_start, t_end, 100)
            y_fine_interval = np.interp(t_interval, self.t_exact, self.y_exact[0])
            v_fine_interval = np.interp(t_interval, self.t_exact, self.y_exact[1])
            self.fine_solutions.append((t_interval, y_fine_interval, v_fine_interval))
    
    def create_iteration(self, iteration):
        """Show a single iteration of the Parareal algorithm"""
        color_key = f"iteration{iteration}"
        if color_key not in COLORS:
            color_key = "iteration1"  # Fallback
            
        # Initialize storage for this iteration
        self.iteration_points[iteration] = []
        self.iteration_lines[iteration] = []
        
        # Start with initial value
        y_current = INITIAL_CONDITIONS[0]
        v_current = INITIAL_CONDITIONS[1]
        
        # Show title for this iteration
        subtitle = Text(f"Serial Correction: Iteration {iteration}", font_size=28)
        subtitle.next_to(self.scene.title, DOWN)
        if hasattr(self.scene, 'subtitle') and self.scene.subtitle:
            self.scene.play(FadeOut(self.scene.subtitle), FadeIn(subtitle))
        else:
            self.scene.play(FadeIn(subtitle))
        self.scene.subtitle = subtitle
        
        # Perform parareal correction for each interval
        new_y_values = [INITIAL_CONDITIONS[0]]
        new_v_values = [INITIAL_CONDITIONS[1]]
        
        points_and_lines = []
        
        for i in range(N_COARSE):
            t_start = i * DT_COARSE
            t_end = (i + 1) * DT_COARSE
            
            # Create dot at interval start
            point = Dot(self.axes.c2p(t_start, y_current), color=eval(COLORS[color_key]))
            self.iteration_points[iteration].append(point)
            points_and_lines.append(point)
            
            # In parareal, we combine:
            # 1. New coarse solution from t_start to t_end
            # 2. Previous fine solution from t_start to t_end
            # 3. Previous coarse solution from t_start to t_end (subtracted)
            
            # For demo, calculate a solution that converges toward exact solution
            progress = min(iteration / N_ITERATIONS, 0.95)  # How close to exact solution
            
            # Get exact reference at this point for display
            exact_end_y = np.interp(t_end, self.t_exact, self.y_exact[0])
            exact_end_v = np.interp(t_end, self.t_exact, self.y_exact[1])
            
            # Get fine solution for this interval (we're using exact for demonstration)
            fine_t, fine_y, fine_v = self.fine_solutions[i]
            
            # Get current end points
            current_end_y = self.y_values[i+1]
            current_end_v = self.v_values[i+1]
            
            # Calculate new end points (moving toward exact solution)
            new_end_y = current_end_y * (1 - progress) + exact_end_y * progress
            new_end_v = current_end_v * (1 - progress) + exact_end_v * progress
            
            # Create interpolated line for this interval
            # For simplicity, we'll linearly interpolate between points
            line = self.axes.plot(
                lambda x: y_current + (new_end_y - y_current) * (x - t_start) / DT_COARSE,
                x_range=[t_start, t_end],
                color=eval(COLORS[color_key])
            )
            self.iteration_lines[iteration].append(line)
            points_and_lines.append(line)
            
            # Update for next interval
            y_current = new_end_y
            v_current = new_end_v
            
            # Store new values
            new_y_values.append(new_end_y)
            new_v_values.append(new_end_v)
        
        # Add final point
        final_point = Dot(self.axes.c2p(T_FINAL, y_current), color=eval(COLORS[color_key]))
        self.iteration_points[iteration].append(final_point)
        points_and_lines.append(final_point)
        
        # Animate all at once
        self.scene.play(
            *[Create(obj) for obj in points_and_lines],
            run_time=2
        )
        
        # Update stored values for next iteration
        self.y_values = new_y_values
        self.v_values = new_v_values
        
        return VGroup(*points_and_lines)
        
    def show_convergence(self):
        """Show how solution converges to exact solution"""
        # Get exact solution mobject
        t, y = solve_exact(0, T_FINAL, INITIAL_CONDITIONS)
        exact_curve = self.axes.plot(
            lambda x: np.interp(x, t, y[0]),
            color=eval(COLORS["exact"]),
            stroke_width=3,
            stroke_opacity=1.0
        )
        
        # Create subtitle
        subtitle = Text("Convergence to Exact Solution", font_size=28)
        subtitle.next_to(self.scene.title, DOWN)
        self.scene.play(FadeOut(self.scene.subtitle), FadeIn(subtitle))
        self.scene.subtitle = subtitle
        
        # Highlight the exact solution
        self.scene.play(
            Create(exact_curve),
            run_time=2
        )
        
        # Wait to appreciate the result
        self.scene.wait(2)
        
    def remove_iteration(self, iteration):
        """Remove a specific iteration visualization"""
        if iteration in self.iteration_points and iteration in self.iteration_lines:
            objects = self.iteration_points[iteration] + self.iteration_lines[iteration]
            self.scene.play(FadeOut(VGroup(*objects)))
            del self.iteration_points[iteration]
            del self.iteration_lines[iteration]
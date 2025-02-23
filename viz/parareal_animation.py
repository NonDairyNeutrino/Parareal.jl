from manim import *
import numpy as np
from scipy.integrate import solve_ivp

class PararealAnimation(Scene):
    def construct(self):
        # Configuration
        self.t_final = 10
        self.n_coarse = 5
        self.dt_coarse = self.t_final / self.n_coarse
        
        # Create coordinate system
        axes = Axes(
            x_range=[0, self.t_final, 2],
            y_range=[-2, 2, 1],
            axis_config={"color": GREY},
            x_axis_config={"numbers_to_include": np.arange(0, self.t_final + 1, 2)},
            y_axis_config={"numbers_to_include": np.arange(-2, 3, 1)},
        ).add_coordinates()
        
        axes_labels = axes.get_axis_labels(x_label="t", y_label="y(t)")
        
        # Add title
        title = Text("Parareal Algorithm Visualization", font_size=36)
        title.to_edge(UP)
        
        # Setup the scene
        self.play(
            Create(axes),
            Write(axes_labels),
            Write(title)
        )
        
        # Draw exact solution
        def ode_exact(t, y):
            return [y[1], -0.1 * y[1] - np.sin(y[0])]
        
        t_eval = np.linspace(0, self.t_final, 200)
        sol = solve_ivp(ode_exact, [0, self.t_final], [1, 0], t_eval=t_eval)
        
        exact_plot = axes.plot(
            lambda x: np.interp(x, sol.t, sol.y[0]),
            color=GREY,
            stroke_width=2,
            stroke_opacity=0.5
        )
        
        self.play(
            Create(exact_plot),
            run_time=2
        )
        
        # Stage 1: Initial coarse propagation
        subtitle = Text("Stage 1: Initial Coarse Propagation", font_size=28)
        subtitle.next_to(title, DOWN)
        
        self.play(
            Write(subtitle)
        )
        
        coarse_points = []
        y_current = 1.0
        v_current = 0.0
        
        for i in range(self.n_coarse):
            t_start = i * self.dt_coarse
            t_end = (i + 1) * self.dt_coarse
            
            # Solve coarse propagator
            t_coarse = np.linspace(t_start, t_end, 20)
            sol_coarse = solve_ivp(ode_exact, [t_start, t_end], 
                                 [y_current, v_current], t_eval=t_coarse)
            
            # Create dots and lines for this interval
            point = Dot(axes.c2p(t_start, y_current), color=BLUE)
            coarse_points.append(point)
            
            line = axes.plot(
                lambda x: np.interp(x, sol_coarse.t, sol_coarse.y[0]),
                x_range=[t_start, t_end],
                color=BLUE
            )
            
            # Animate creation of line and point
            self.play(
                Create(point),
                Create(line),
                run_time=1
            )
            
            # Update for next interval
            y_current = sol_coarse.y[0][-1]
            v_current = sol_coarse.y[1][-1]
        
        # Add final point
        final_point = Dot(axes.c2p(self.t_final, y_current), color=BLUE)
        self.play(Create(final_point))
        
        # Stage 2: Setup subproblems
        self.play(
            FadeOut(subtitle),
            FadeIn(Text("Stage 2: Setup Subproblems", font_size=28).next_to(title, DOWN))
        )
        
        # Add vertical lines for subdomains
        subdomain_lines = VGroup(*[
            DashedLine(
                axes.c2p(i * self.dt_coarse, -2),
                axes.c2p(i * self.dt_coarse, 2),
                color=GREY,
                stroke_opacity=0.5
            )
            for i in range(1, self.n_coarse)
        ])
        
        self.play(
            Create(subdomain_lines),
            run_time=2
        )
        
        # Stage 3: Parallel fine propagation
        self.play(
            FadeOut(VGroup(*self.mobjects[3:])),  # Remove everything except axes and title
            FadeIn(Text("Stage 3: Parallel Fine Propagation", font_size=28).next_to(title, DOWN))
        )
        
        # Initialize fine propagation points
        fine_points = []
        for i in range(self.n_coarse):
            point = Dot(axes.c2p(i * self.dt_coarse, 1.0), color=RED)
            fine_points.append(point)
            self.add(point)
        
        # Animate fine propagation
        n_steps = 30
        for step in range(n_steps):
            new_points = []
            for i in range(self.n_coarse):
                t = i * self.dt_coarse + self.dt_coarse * step / n_steps
                sol_value = np.interp(t, sol.t, sol.y[0])
                new_point = Dot(axes.c2p(t, sol_value), color=RED)
                new_points.append(new_point)
            
            self.play(
                *[Transform(fine_points[i], new_points[i]) for i in range(self.n_coarse)],
                run_time=0.1
            )
        
        # Final pause
        self.wait(2)

if __name__ == "__main__":
    config.media_width = "75%"
    config.frame_rate = 30
    scene = PararealAnimation()
    scene.render()

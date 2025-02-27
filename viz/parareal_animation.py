from manim import *
from config import AXES_CONFIG, N_ITERATIONS
from visualizers.exact_solution import ExactSolutionVisualizer
from visualizers.coarse_propagation import CoarsePropagationVisualizer
from visualizers.fine_propagation import FinePropagationVisualizer
from visualizers.parallel_fine import ParallelFineVisualizer
from visualizers.parareal_iterations import PararealIterationVisualizer

class PararealAnimation(Scene):
    def construct(self):
        # Set up main components
        self.setup_scene()
        
        # Stage 1: Show exact solution and initial coarse propagation
        self.stage_initial_coarse_propagation()
        
        # Stage 2: Setup subproblems
        self.stage_setup_subproblems()
        
        # Stage 3: Parallel fine propagation
        self.stage_parallel_fine_propagation()
        
        # Stage 4: Parareal iterations (correction phase)
        self.stage_parareal_iterations()
        
        # Final pause
        self.wait(2)
    
    def setup_scene(self):
        # Create coordinate system
        self.axes = Axes(**AXES_CONFIG).add_coordinates()
        self.axes_labels = self.axes.get_axis_labels(x_label="t", y_label="y(t)")
        
        # Add title
        self.title = Text("Parareal Algorithm Visualization", font_size=36)
        self.title.to_edge(UP)
        self.subtitle = None
        
        # Create scene
        self.play(
            Create(self.axes),
            Write(self.axes_labels),
            Write(self.title)
        )
        
        # Create exact solution (faded in background for reference)
        self.exact_solution = ExactSolutionVisualizer(self, self.axes)
        self.exact_solution.create()
    
    def stage_initial_coarse_propagation(self):
        # Show subtitle
        subtitle = Text("Stage 1: Initial Coarse Propagation", font_size=28)
        subtitle.next_to(self.title, DOWN)
        self.play(Write(subtitle))
        self.subtitle = subtitle
        
        # Create coarse propagation
        self.coarse_propagation = CoarsePropagationVisualizer(self, self.axes)
        self.coarse_propagation.create()
    
    def stage_setup_subproblems(self):
        # Change subtitle
        new_subtitle = Text("Stage 2: Setup Subproblems", font_size=28)
        new_subtitle.next_to(self.title, DOWN)
        
        self.play(
            FadeOut(self.subtitle),
            FadeIn(new_subtitle)
        )
        self.subtitle = new_subtitle
        
        # Create subdomain lines
        self.coarse_propagation.create_subdomains()
    
    def stage_parallel_fine_propagation(self):
        # Create parallel fine propagation visualization
        self.parallel_fine = ParallelFineVisualizer(self, self.axes)
        self.parallel_fine.create()
    
    def stage_parareal_iterations(self):
        # Remove previous visualizations except axes, title, and subdomain lines
        self.parallel_fine.remove()
        
        # Create parareal iteration visualizer
        self.parareal_iterations = PararealIterationVisualizer(self, self.axes)
        
        # Show each iteration
        for iteration in range(1, N_ITERATIONS + 1):
            self.parareal_iterations.create_iteration(iteration)
            self.wait(1)
        
        # Show convergence to exact solution
        self.parareal_iterations.show_convergence()

if __name__ == "__main__":
    # These settings will be used if you run using python directly
    # But they'll be overridden by command line args when using manim CLI
    config.media_width = "75%"
    config.frame_rate = 30
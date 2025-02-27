from manim import *

class BaseVisualizer:
    """Base class for visualization components"""
    
    def __init__(self, scene, axes):
        self.scene = scene
        self.axes = axes
        
    def create(self):
        """Create and animate the visualization component"""
        raise NotImplementedError
        
    def remove(self):
        """Remove the visualization component"""
        raise NotImplementedError

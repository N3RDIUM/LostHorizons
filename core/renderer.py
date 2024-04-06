# Imports
from core.logger import logger
from core.mesh import UnifiedMesh

class Renderer:
    """
    A class which handles everything rendering-related in the game.
    """
    
    def __init__(self) -> None:
        """
        Initialize the renderer.
        """
        logger.info('[core/Renderer] Initializing Renderer...')
        
        # Create the unified mesh
        self.mesh = UnifiedMesh()
        
        # Redirect functions
        self.new_mesh = self.mesh.new_mesh
        self.delete_mesh = self.mesh.delete_mesh
    
    def draw(self) -> None:
        """
        Draw all meshes
        """
        self.UnifiedMesh.draw()

# Imports
from uuid import uuid4
import numpy as np
from threading import Lock

# Default constants
DEFAULT_VBO_SIZE = 1024 * 3

class Mesh:
    """
    A mesh used for storing a bunch of points and the colors of those points
    """
    
    def __init__(self) -> None:
        """
        Just initialize the empty arrays of the required size
        """
        self.lock = Lock()
        self.vertices = np.empty(DEFAULT_VBO_SIZE, dtype=np.float64)
        self.colors = np.empty(DEFAULT_VBO_SIZE, dtype=np.float64)
        # TODO: Get values from multiprocessing shared memory
        
class UnifiedMesh:
    """
    A unified mesh class which handles drawcalls for every single mesh.
    """
    
    def __init__(self) -> None:
        """
        Initialize the mesh queue and other required stuff
        """
        self.meshes = {} # The Renderer class takes care of this
        self.static_builds = {}
        self.update_times = {}

    def new_mesh(self, id=uuid4()):
        """
        Adds a mesh to the mesh list and returns the id
        """
        new = Mesh(self)
        self.meshes[id] = new
        self.update_later() # TODO: If an update is already scheduled, do nothing
        return id
    
    def delete_mesh(self, id):
        """
        Deletes a mesh by its id
        """
        self.meshes[id].dispose()
        del self.meshes[id]
        self.update_later()
        return id

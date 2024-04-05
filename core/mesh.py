# Imports
import numpy as np
from uuid import uuid4
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
        self.changed = False
        self.lock = Lock()
        self.vertices = np.empty(DEFAULT_VBO_SIZE, dtype=np.float64)
        self.colors = np.empty(DEFAULT_VBO_SIZE, dtype=np.float64)
        # TODO: Get values from multiprocessing shared memory
        
    def notify_change(self):
        """
        Notify that the mesh was modified after the last update
        """
        self.changed = True
        
    def notify_update(self):
        """
        Notify that the mesh modification was taken into account in the last update
        """
        self.changed = False
        
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
        self.sorted_ids = [] # Sorted by latest update

    def new_mesh(self, id=str(uuid4())):
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
        self.get_mesh(id).dispose()
        del self.meshes[id]
        self.update_later()
        return id
    
    def get_mesh(self, id):
        """
        Get a mesh by its id
        """
        return self.meshes[id]
    
    def update(self):
        """
        Handle the creation of static meshes and update the update times
        """
        static = self.static_available
        if not static:            
            new_id = str(uuid4())
            self.static_builds[new_id] = Mesh() # TODO: Create RenderMesh class which stores stuff in a VBO
            self.build_static(new_id)
            self.touch(new_id)
        else:
            self.build_static(static)
                        
        # TODO: Delete mesh if its too old / not updating / unneeded
        
        for mesh in self.meshes:
            self.meshes[mesh].notify_update()
        
    def build_static(self, id: str):
        """
        Combine all the mesh data into a single 1d numpy array
        """
        # Init empty arrays
        static_vertices = np.empty(0, dtype=np.float64)
        static_colors = np.empty(0, dtype=np.float64)
        
        # Update the arrays
        for mesh in self.meshes:
            mesh.lock.acquire()
            static_vertices = np.concatenate((static_vertices, mesh.vertices))
            static_colors = np.concatenate((static_colors, mesh.colors))
            mesh.lock.release()
        
        # Assign the arrays to the actual mesh
        static = self.static_builds[id]
        static.lock.acquire()
        del static.vertices
        del static.colors
        static.vertices = static_vertices
        static.colors = static_colors
        static.lock.release()

    @property
    def changed(self):
        """
        Return whether any mesh in the list was updated
        """
        return any([self.meshes[mesh].changed for mesh in self.meshes])

    @property
    def static_available(self):
        """
        Return whether any mesh in the static build list is not currently drawing/modifying
        """
        if any([self.static_builds[mesh].lock.locked() for mesh in self.static_builds]):
            return False
        for mesh in self.static_builds:
            if not self.static_builds[mesh].lock.locked(): return mesh
            break
    
    # TODO: Property static_drawable which gives the latest static mesh which is not busy updating
    
    def touch(self, id):
        """
        Move id to the first element in self.sorted_ids
        """
        self.sorted_ids.remove(id)
        self.sorted_ids = [id] + self.sorted_ids

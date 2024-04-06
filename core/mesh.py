# Imports
import numpy as np
from uuid import uuid4
from threading import Lock
from OpenGL.arrays import vbo

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
        
    def notify_change(self) -> None:
        """
        Notify that the mesh was modified after the last update
        """
        self.changed = True
        
    def notify_update(self) -> None:
        """
        Notify that the mesh modification was taken into account in the last update
        """
        self.changed = False

    def dispose(self) -> None:
        """
        Free memory and prepare the mesh for deletion
        """
        self.lock.acquire()
        del self.vertices
        del self.colors
        self.lock.release()
        
class RenderMesh(Mesh):
    """
    A Mesh but it also stores its stuff in a VBO.
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.vertex_buffer = None
        self.color_buffer = None
        
    def create_buffers(self) -> None:
        """
        Create the buffers for the thing
        """
        self.lock.acquire()
        self.vertex_buffer = vbo.VBO(
            self.vertices,
            usage="GL_STATIC_DRAW",
            target="GL_ARRAY_BUFFER"
        )
        self.color_buffer = vbo.VBO(
            self.colors,
            usage="GL_STATIC_DRAW",
            target="GL_ARRAY_BUFFER"
        )
        self.lock.release()
        
    def update_buffers(self) -> None:
        """
        Update the buffers with self.vertices and self.colors
        """
        if not self.vertex_buffer and not self.color_buffer:
            return
        self.lock.acquire()
        self.vertex_buffer.set_array(self.vertices)
        self.color_buffer.set_array(self.colors)
        self.lock.release()
        
    def delete_buffers(self) -> None:
        """
        If buffers exist, delete them and free up the memory
        """
        if not self.vertex_buffer and not self.color_buffer:
            return
        self.lock.acquire()
        self.vertex_buffer.delete()
        self.color_buffer.delete()
        self.lock.release()

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

    def new_mesh(self, id=str(uuid4())) -> str:
        """
        Adds a mesh to the mesh list and returns the id
        """
        new = Mesh()
        self.meshes[id] = new
        return id
    
    def delete_mesh(self, id) -> str:
        """
        Deletes a mesh by its id
        """
        self.meshes[id].dispose()
        del self.meshes[id]
        self.update_later()
        return id
    
    def update(self) -> None:
        """
        Handle the creation of static meshes and update the update times
        This function is to be called in the update thread of the window.
        """
        static = self.static_available
        if not static:
            new_id = str(uuid4())
            self.static_builds[new_id] = RenderMesh()
            self.build_static(new_id)
            self.touch(new_id)
        else:
            self.build_static(static[0])
            self.touch(static[0])
        
        if len(static) > 1:
            removed = static.pop(-1)
            self.static_builds[removed].dispose()
            del self.static_builds[removed]
        
        for mesh in self.meshes:
            self.meshes[mesh].notify_update()
        
    def build_static(self, id: str) -> None:
        """
        Combine all the mesh data into a single 1d numpy array
        """
        # Init empty arrays
        vertices = []
        colors = []
        
        # Update the arrays
        for mesh in self.meshes:
            mesh.lock.acquire()
            vertices += [mesh.vertices]
            colors += [mesh.colors]
            mesh.lock.release()
        static_vertices = np.concatenate(vertices, None)
        static_colors = np.concatenate(colors, None)
        
        # Assign the arrays to the actual mesh
        static = self.static_builds[id]
        static.lock.acquire()
        del static.vertices
        del static.colors
        static.vertices = static_vertices
        static.colors = static_colors
        static.lock.release()

    @property
    def changed(self) -> bool:
        """
        Return whether any mesh in the list was updated
        """
        return any([self.meshes[mesh].changed for mesh in self.meshes])

    @property
    def static_available(self) -> bool | list:
        """
        Return whether any mesh in the static build list is not currently drawing/modifying
        """
        if any([self.static_builds[mesh].lock.locked() for mesh in self.static_builds]):
            return False
        ret = []
        for mesh in self.sorted_ids:
            if not self.static_builds[mesh].lock.locked(): ret.append(mesh)
        return ret
    
    @property
    def static_drawable(self) -> str | None:
        """
        Return whether any mesh in the static build list is not currently drawing/modifying
        """
        for mesh in self.sorted_ids:
            if not self.static_builds[mesh].lock.locked(): return mesh
    
    def touch(self, id) -> None:
        """
        Move id to the first element in self.sorted_ids
        """
        self.sorted_ids.remove(id)
        self.sorted_ids = [id] + self.sorted_ids

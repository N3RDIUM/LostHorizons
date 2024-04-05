# Imports
from threading import Lock
from uuid import uuid4

import numpy as np

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
        self.meshes = {}  # The Renderer class takes care of this
        self.static_builds = {}
        self.sorted_ids = []  # Sorted by latest update

    def new_mesh(self, id=uuid4()):
        """
        Adds a mesh to the mesh list and returns the id
        """
        new = Mesh(self)
        self.meshes[id] = new
        self.update_later()  # TODO: If an update is already scheduled, do nothing
        return id

    def delete_mesh(self, id):
        """
        Deletes a mesh by its id
        """
        self.meshes[id].dispose()
        del self.meshes[id]
        self.update_later()
        return id

    def update(self):
        """
        Handle the creation of static meshes and update the update times
        """
        # TODO: Delete mesh if its too old / not updating / unneeded

    @property
    def changed(self):
        """
        Return whether any mesh in the list was updated
        """
        return any([self.meshes[mesh].changed for mesh in self.meshes])

    @property
    def mesh_available(self):
        """
        Return whether any mesh in the static build list is not currently drawing/modifying
        """
        return not any([self.meshes[mesh].lock.locked() for mesh in self.meshes])

    def touch(self, id):
        """
        Move id to the first element in self.sorted_ids
        """
        self.sorted_ids.remove(id)
        self.sorted_ids = [id] + self.sorted_ids

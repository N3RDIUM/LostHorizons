import numpy as np
import math
import numpy as np
from OpenGL.GL import glColor3f

from core.utils import midpoint
from core.mesh import Mesh
import noise
import noise

class LeafNode:
    def __init__(self, rect, tesselate_times=4, parent=None, planet=None):
        self.rect = rect
        self._tesselate_times = tesselate_times
        self.mesh = None
        self.parent = parent
        self.planet = planet
        self.color = [0, 102/256, 39/256]
        self.times_tessed = 0
        self.call_queue = []
        self._vertices = []
        self._indices = []
        self._normals = []
        self.generated = False
        self.type = "leaf"
        self._frame = self.planet.frame
        self.generate()
        
    def generate(self):
        corner1 = self.rect[0]
        corner2 = self.rect[1]
        corner3 = self.rect[2]
        corner4 = self.rect[3]
        
        # Now, make a simple quad
        self._vertices = np.array([
            corner1, corner2, corner3, corner4
        ], dtype=np.float32)
        
        for i in range(self._tesselate_times + 2):
            self.planet.call_queue.append(self._tes)
        
        self.planet.call_queue.append(self._sphere_noise)
        self.planet.call_queue.append(self._meshify)
        self.planet.call_queue.append(self._finalise_mesh)
    
    def _tes(self):
        if self.times_tessed >= self._tesselate_times:
            return
        # Tesselate the quad, make it a sphere, and add noise
        self._vertices = np.array(self.tesselate(self._vertices, times=1), dtype=np.float32)
        self.times_tessed += 1
    
    def _sphere_noise(self):
        # vertices = self.spherify_and_add_noise(vertices)
        self._vertices = self.spherify_and_add_noise(self._vertices)
    
    def _meshify(self):
        # Convert the points to a triangle mesh
        self._vertices = self.convert_to_mesh(self._vertices)
    
    def _finalise_mesh(self):
        # Indices 
        self._indices = self.get_indices(self._vertices)
        
        # Get the normals
        self._normals = self.get_normals(
            np.array(self._vertices)
        )
        self.parent.position = self.get_average_position(self._vertices)
        self.generated = True
        
    def tesselate(self, vertices, times=1):
        if times == 0:
            return vertices
        
        new_vertices = []
        
        for i in range(0, len(vertices), 4):
            corner1 = vertices[i]
            corner2 = vertices[i + 1]
            corner3 = vertices[i + 2]
            corner4 = vertices[i + 3]
            
            # Make a midpoint between each corner
            midpoint1 = midpoint(corner1, corner2)
            midpoint2 = midpoint(corner2, corner3)
            midpoint3 = midpoint(corner3, corner4)
            midpoint4 = midpoint(corner4, corner1)
            midpoint5 = midpoint(corner1, corner3)
            
            # Now, make a simple quad
            new_vertices.append(corner1)
            new_vertices.append(midpoint1)
            new_vertices.append(midpoint5)
            new_vertices.append(midpoint4)
            
            new_vertices.append(midpoint1)
            new_vertices.append(corner2)
            new_vertices.append(midpoint2)
            new_vertices.append(midpoint5)
            
            new_vertices.append(midpoint5)
            new_vertices.append(midpoint2)
            new_vertices.append(corner3)
            new_vertices.append(midpoint3)
            
            new_vertices.append(midpoint4)
            new_vertices.append(midpoint5)
            new_vertices.append(midpoint3)
            new_vertices.append(corner4)
            
        return np.array(self.tesselate(new_vertices, times - 1), dtype=np.float32)

    @staticmethod
    def normalize(vector):
        length = math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
        return vector[0] / length, vector[1] / length, vector[2] / length

    @staticmethod
    def avg(array):
        return sum(array) / len(array)
    
    def convert_to_mesh(self, vertices):
        # Convert the points to a triangle mesh
        new_vertices = []
        for i in range(0, len(vertices), 4):
            corner1 = vertices[i + 2]
            corner2 = vertices[i + 3]
            corner3 = vertices[i + 1]
            corner4 = vertices[i + 0]
            
            # This is for GL_TRIANGLES
            new_vertices.append(corner1)
            new_vertices.append(corner2)
            new_vertices.append(corner3)
            
            new_vertices.append(corner3)
            new_vertices.append(corner2)
            new_vertices.append(corner4)
        return new_vertices
    
    def add_noise(self, vertices):
        """
        This is for the 2d version
        """
        for i in range(len(vertices)):
            vertices[i] = [
                vertices[i][0],
                vertices[i][1] + noise.snoise2(vertices[i][0] / 100, vertices[i][2] / 100) * 32,
                vertices[i][2]
            ]
        return vertices
    
    def spherify_and_add_noise(self, vertices):
        CENTER = [self.planet.size / 2]*3
        CENTER[0] += self.planet.position[0]
        CENTER[1] += self.planet.position[1]
        CENTER[2] += self.planet.position[2]
        for i in range(len(vertices)):
            v = vertices[i]
            x = v[0] - CENTER[0]
            y = v[1] - CENTER[1]
            z = v[2] - CENTER[2]
            
            length = math.sqrt(x**2 + y**2 + z**2)
            
            x = x / length * self.planet.size
            y = y / length * self.planet.size
            z = z / length * self.planet.size
            
            # Add noise
            vector = [x, y, z]
            vector = self.normalize(vector)
            _noise = self.fractal_noise((x * vector[0], y * vector[1], z * vector[2])) * 100
            x = x + vector[0] * _noise
            y = y + vector[1] * _noise
            z = z + vector[2] * _noise
            
            vertices[i] = [x, y, z]
        return vertices
    
    def fractal_noise(self, coords):
        noiseSum = 0
        amplitude = 0.01
        frequency = 0.25
        x, y, z = tuple(coords)
        
        for i in range(12): # TODO: Add a config value named "octaves"
            noiseSum += noise.snoise3(x * frequency, y * frequency, z * frequency) * amplitude
            frequency *= 2
            amplitude /= 2
            
        return noiseSum
    
    def get_indices(self, vertices):
        indices = []
        for i in range(len(vertices)):
            indices.append(i)
        return indices

    @staticmethod
    def get_normals(vtx):
        normals = []
        for i in range(0, len(vtx), 3):
            p1 = vtx[i]
            p2 = vtx[i + 1]
            p3 = vtx[i + 2]
            u = p2 - p1
            v = p3 - p1
            n = np.cross(u, v)
            normals.append(n)
            normals.append(n)
            normals.append(n)
        return normals
    
    def get_average_position(self, vertices):
        x = 0
        y = 0
        z = 0
        for vertex in vertices:
            x += vertex[0]
            y += vertex[1]
            z += vertex[2]
        x /= len(vertices)
        y /= len(vertices)
        z /= len(vertices)
        return (x, y, z)
        
    def draw(self):
        if self.mesh is not None:
            glColor3f(self.color[0], self.color[1], self.color[2])
            self.mesh.draw()
        else:
            if self.generated: self.mesh = Mesh(self._vertices, self._indices, self._normals)
                
    def dispose(self):
        try:
            self.mesh.dispose()
        except AttributeError:
            pass
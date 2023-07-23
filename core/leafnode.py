import threading
import random
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
        self.color = [
            0.6+abs(random.random()*0.4),
            0.6+abs(random.random()*0.4),
            0.6+abs(random.random()*0.4)
        ]
        
        self.thread = threading.Thread(target=self.generate, daemon=True)
        self.thread.start()
        self.type = "leaf"
        
    def generate(self):
        corner1 = self.rect[0]
        corner2 = self.rect[1]
        corner3 = self.rect[2]
        corner4 = self.rect[3]
        
        # Now, make a simple quad
        vertices = [
            corner1, corner2, corner3, corner4
        ]
        
        # Tesselate the quad, make it a sphere, and add noise
        vertices = self.tesselate(vertices, times=self._tesselate_times)
        # vertices = self.spherify_and_add_noise(vertices)
        vertices = self.add_noise(vertices)
        
        # Convert the points to a triangle mesh
        vertices = self.convert_to_mesh(vertices)
        
        # Indices 
        indices = self.get_indices(vertices)
        
        # Get the normals
        normals = self.get_normals(
            np.array(vertices)
        )
        
        # Create a mesh
        self.mesh = Mesh(vertices, indices, normals)
        
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
            
        return self.tesselate(new_vertices, times - 1)

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
            vertices[i] = (
                vertices[i][0],
                vertices[i][1] + noise.snoise2(vertices[i][0] / 100, vertices[i][2] / 100) * 32,
                vertices[i][2]
            )
        return vertices
    
    def spherify_and_add_noise(self, vertices):
        CENTER = [self.planet.size / 2]*3
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
            _noise = self.avg([
                # Local noise
                noise.snoise3(x, y, z) * 0.25,
                noise.snoise3(x / 2, y / 2, z / 2) * 0.5,
                noise.snoise3(x / 4, y / 4, z / 4) * 2,
                noise.snoise3(x / 8, y / 8, z / 8) * 4,
                noise.snoise3(x / 16, y / 16, z / 16) * 8,
                noise.snoise3(x / 32, y / 32, z / 32) * 16,
                
                # Getting larger
                noise.snoise3(x / 320, y / 320, z / 320) * 32,
                noise.snoise3(x / 640, y / 640, z / 640) * 64,
                
                # Noise that produces continents
                noise.snoise3(x / 128, y / 128, z / 128) * 128,
            ])
            vector = [x, y, z]
            vector = self.normalize(vector)
            x = x + vector[0] * _noise
            y = y + vector[1] * _noise
            z = z + vector[2] * _noise
            
            vertices[i] = (x, y, z)
        return vertices
    
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
            # Reverse the normal for now
            # TODO: Remove this if we are doing planet normals
            n *= -1
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
                
    def dispose(self):
        try:
            self.mesh.dispose()
        except AttributeError:
            pass
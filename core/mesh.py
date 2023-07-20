import numpy as np
from OpenGL.GL import *
from core.utils import midpoint

# A mesh class which has its own VBO
from OpenGL.GL import *
from OpenGL.arrays import vbo
import numpy as np
import threading
import random
import math

glLineWidth(8)

class Mesh:
    def __init__(self, vertices, indices, normals=[], uvs=[]):
        self.vertices = vertices
        self.indices = indices
        self.normals = normals
        self.uvs = uvs
        
        # Only implement the vertices
        self.vbo = vbo.VBO(np.array(self.vertices, 'f'))
        self.normal_vbo = vbo.VBO(np.array(self.normals, 'f'))
        
    def draw(self):
        self.vbo.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self.vbo)
        
        self.normal_vbo.bind()
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, self.normal_vbo)
        
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))
        
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        
        self.vbo.unbind()
        self.normal_vbo.unbind()
            
    def __del__(self):
        self.vbo.delete()
        self.normal_vbo.delete()
        
class QuadMesh:
    def __init__(self, rect, tesselate_times=4):
        self.rect = rect
        self._tesselate_times = tesselate_times
        self.mesh = None
        self.color = [random.random(), random.random(), random.random()]
        
        self.thread = threading.Thread(target=self.generate, daemon=True)
        self.thread.start()
        
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
        
        # Convert the points to a triangle mesh
        vertices = self.convert_to_mesh(vertices)
        
        # Indices 
        indices = self.get_indices(vertices)
        
        # Get the normals
        normals = self.get_normals(
            np.array(vertices)
        )
        
        # Get average position
        # self.parent.position = self.get_average_position(vertices)
        
        # Create a mesh
        self.mesh = vertices
        self.normals = normals
        self.indices = indices
        
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
            try:
                # Draw double-sided
                self.mesh.draw()
            except:
                self.mesh = Mesh(vertices=self.mesh, normals=self.normals, indices=self.indices)
                
    def __del__(self):
        del self.mesh
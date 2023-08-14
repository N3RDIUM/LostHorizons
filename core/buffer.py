# imports
import ctypes
import numpy as np
from OpenGL.arrays import vbo
from OpenGL.GL import *

VBO_SIZE = 120000

class Buffer:
    """
    Buffer

    This is a wrapper for OpenGL buffer objects.
    It supports persistent mapping.
    """

    def __init__(self, id):
        """
        Initializes the buffer.
        """
        self.id = id
        data = np.empty(VBO_SIZE, dtype=np.float32)
        self.buffer = vbo.VBO(data, usage='GL_DYNAMIC_DRAW_ARB', target='GL_ARRAY_BUFFER')
        self.buffer.bind()
        self.buffer.unbind()
        
    def modify(self, data):
        """
        Modify the buffer data.
        """
        data = np.asarray(data, dtype=np.float32)
        self.buffer.bind()
        self.buffer.set_array(data, data.nbytes)
        self.buffer.unbind()
        
    def bind(self):
        """
        Bind the buffer.
        """
        self.buffer.bind()
    
    def unbind(self):
        """
        Unbind the buffer.
        """
        self.buffer.unbind()
        
    def delete(self):
        """
        Delete the buffer.
        """
        self.buffer.delete()
        
    def __del__(self):
        """
        Delete the buffer.
        """
        self.delete()
# imports
import numpy as np
from OpenGL.arrays import vbo

# TODO: Figure out a definite VBO size!
VBO_SIZE = 199692

class Buffer:
    """
    This is a lightweight OpenGL Buffer wrapper.
    """

    def __init__(self, id) -> None:
        """
        Initializes the buffer.
        
        :param id: Well, the ID of the buffer!
        """
        self.id = id
        self.buf = vbo.VBO(
            np.zeros(VBO_SIZE, dtype=np.float64),
            usage="GL_DYNAMIC_DRAW",
            target="GL_ARRAY_BUFFER",
        ) # Create the buffer

    def set_array(self, data: np.array) -> None:
        """
        Sets the data of the buffer.

        :param data: The data to add to the buffer.
        """
        self.buf.bind()
        self.buf[:] = data[:]
        self.buf.unbind()

    def delete(self) -> None:
        """
        Prepares the buffer for deletion.
        """
        self.buf.delete()

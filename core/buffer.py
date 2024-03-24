# imports
import numpy as np
from OpenGL.arrays import vbo

# TODO: Figure out a definite VBO size!
VBO_SIZE = 65536 * 12

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
            np.zeros(VBO_SIZE, dtype=np.float32),
            usage="GL_DYNAMIC_DRAW",
            target="GL_ARRAY_BUFFER",
        ) # Create the buffer
        self.max_idx = 0 # The last index which contains data

    def modify(self, data: np.array, offset:int = -1) -> None:
        """
        Adds data to the buffer.

        :param data: The data to add to the buffer.
        :param offset: The offset to start writing at.
        """
        if offset == -1:
            offset = self.max_idx # Append to the buffer instead
        self.max_idx = max(self.max_idx, offset + len(data))
        self.buf[offset : offset + len(data)] = data

    def delete(self) -> None:
        """
        Prepares the buffer for deletion.
        """
        self.buf.delete()

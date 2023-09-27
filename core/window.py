# imports
import threading
import time

import glfw
from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_CULL_FACE,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_MODELVIEW,
    GL_PROJECTION,
    glClear,
    glClearColor,
    glEnable,
    glLoadIdentity,
    glMatrixMode,
    glViewport,
)
from OpenGL.GLU import gluPerspective

from .logger import logging as logger
from .text import display_debug

##################################################
# Errors                                         #
##################################################


class GLFWInitError(Exception):
    """
    GLFWInitError

    An error that is raised when GLFW fails to initialize.
    """

    def __init__(self, message):
        """
        Initialize the error.

        :param message: The error message.
        """
        self.message = message

    def __str__(self):
        """
        Get the error message.

        :return: The error message.
        """
        return self.message


##################################################
# Window class                                   #
##################################################


class Window:
    """
    Window

    The main window class for Lost Horizons.
    """

    def __init__(self, **kwargs):
        """
        Initialize the window.

        :param kwargs: Keyword arguments.
        """
        logger.info("[Window] Initializing window...")
        if not glfw.init():
            logger.fatal("Window", "GLFW failed to initialize!")
            raise GLFWInitError("GLFW failed to initialize!")
        self.window = glfw.create_window(
            kwargs.get("width", 800),
            kwargs.get("height", 500),
            kwargs.get("title", "Lost Horizons"),
            None,
            None,
        )  # Create the GLFW window.
        # Make the window the current context.
        logger.info("[Window] Setting up window...")
        glfw.make_context_current(self.window)
        self.previous_frame = 0
        self.current_frame = 0
        self.fps = 0
        self.smooth_fps_samples = []
        self.smooth_fps = 0
        self.logs = []

        self._scheduled_sc = []  # Scheduled shared context objects.
        self._scheduled_main = []  # Scheduled main context objects.
        self.event = threading.Event()  # Event for the shared context.

        # Start the shared context.
        logger.info("[Window] Starting shared context...")
        glfw.make_context_current(None)  # Make the shared context current.
        threading.Thread(target=self.shared_context).start()
        self.event.wait()  # Wait for the shared context to start.
        # Make the main context current.
        glfw.make_context_current(self.window)
        logger.info("[Window] Window + shared context initialized!")

    def get_window_size(self):
        """
        Get the window size.

        :return: The window size.
        """
        width, height = glfw.get_window_size(
            self.window)  # Get the window size.
        return width, height  # Return the window size.

    def schedule_mainloop(self, obj):
        """
        Schedule an object for the main loop.

        :param obj: The object to schedule.
        """
        self._scheduled_main.append(
            obj)  # Append the object to the scheduled objects.

    def schedule_shared_context(self, obj):
        """
        Schedule an object for the shared context.

        :param obj: The object to schedule.
        """
        self._scheduled_sc.append(
            obj)  # Append the object to the scheduled objects.

    def shared_context(self):
        """
        Function for the shared context.
        """
        glfw.init()  # Initialize GLFW.
        glfw.window_hint(glfw.VISIBLE,
                         glfw.FALSE)  # Make the window invisible.
        window2 = glfw.create_window(
            500, 500, "Shared Context", None,
            self.window)  # Create the shared context window.
        # Make the shared context window the current context.
        glfw.make_context_current(window2)
        self.event.set()  # Let the main thread continue.

        logger.info("[Window/Shared Context] Starting shared context loop...")
        while not glfw.window_should_close(self.window):  # Side loop.
            for obj in self._scheduled_sc:  # Loop through the scheduled objects.
                obj.sharedcon()  # Call the shared context function.
            glfw.poll_events()  # Poll events.
        glfw.destroy_window(window2)  # Destroy the shared context window.
        glfw.terminate()  # Terminate GLFW.

    def mainloop(self):
        """
        Main loop.
        """
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glfw.make_context_current(self.window)
        while not glfw.window_should_close(self.window):  # Main loop.
            self.current_frame = time.time()
            # OpenGL stuff.
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClear(GL_DEPTH_BUFFER_BIT)
            glClearColor(0.0, 0.0, 0.0, 1.0)
            self.setup_3d()

            for obj in self._scheduled_main:  # Loop through the scheduled objects.
                obj.drawcall()  # Draw the object.

            self.fps = 1 / (self.current_frame - self.previous_frame)
            self.smooth_fps_samples.append(self.fps)
            self.smooth_fps = sum(self.smooth_fps_samples) / len(
                self.smooth_fps_samples)
            display = (self.logs.copy() + [
                str(self.fps) + " FPS (exact)",
                str(int(self.smooth_fps)) + " FPS (smooth, 64 samples)",
            ] + [f"LostHorizons"])
            display_debug((8, 8), display)

            # GLFW stuff.
            glfw.poll_events()
            glfw.swap_buffers(self.window)
            self.previous_frame = self.current_frame

    def setup_3d(self):
        """
        Setup 3D.
        """
        width, height = self.get_window_size()
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.0001, 100000000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

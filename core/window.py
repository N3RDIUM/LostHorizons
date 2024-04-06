# Imports
import glfw

from core.logger import logger
from core.object_scheduler import Scheduler


class Window:
    """
    Window class for easy creation of GLFW windows
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the window and worker thread
        """
        logger.info("[core/Window] Initializing window...")

        # Throw an exception if glfw does not initialize
        if not glfw.init():
            raise Exception("[core/Window] Could not initialize GLFW!")

        # Set window parameters
        self.params = {"width": 800, "height": 800, "title": "Untitled"}
        self.params.update(kwargs)

        # Create the window
        self.window = glfw.create_window(
            self.params["width"],
            self.params["height"],
            self.params["title"],
            None,
            None,
        )
        glfw.make_context_current(self.window)

        # Initialize required variables
        self.draw_queue = Scheduler()

        # TODO: Inbuilt FPS Counter with smooth fps stuff

        # TODO: Start the shared context thread here

        logger.info("[core/Window] Window initialized successfully!")

    def mainloop(self) -> None:
        """
        Starts the mainloop.
        """
        glfw.make_context_current(self.window)
        logger.info("[core/Window] Starting mainloop...")
        while not glfw.window_should_close(self.window):
            self.draw_queue.process()

            glfw.swap_buffers(self.window)
            glfw.poll_events()

        # Cleanup
        logger.info("[core/Window] Closed! Destroying window, cleaning up...")
        glfw.destroy_window(self.window)
        glfw.terminate()

    @property
    def size(self) -> tuple:
        return glfw.get_window_size(self.window)

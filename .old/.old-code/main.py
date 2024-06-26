import os
import shutil

import glfw
from OpenGL.GLUT import glutInit

from core.simulation import Simulation
from core.window import SimulationWindow


def initialize():
    """
    Initialize GLFW and GLUT
    """
    if not bool(glutInit):
        raise Exception("GLUT not found! Are you sure you have freeglut installed?")
    glutInit()
    if not glfw.init():
        raise Exception("GLFW failed to initialize!")
    try:
        shutil.rmtree(".datatrans")
    except FileNotFoundError:
        pass
    os.mkdir(".datatrans")


def create_window():
    """
    Create a windowed mode window and its OpenGL context
    """
    window = SimulationWindow(width=1600, height=900, title="Lost Horizons")
    return window


if __name__ == "__main__":
    # Initialize GLFW and GLUT and create the window
    initialize()
    window = create_window()
    simulation = Simulation(window)
    window.mainloop()
    # After the player closes the window, terminate GLFW and exit the program
    glfw.terminate()
    simulation.terminate()
    exit()
 
import glfw
from OpenGL.GLUT import glutInit
from core.window import Window

def initialize():
    """
    Initialize GLFW and GLUT
    """
    if not bool(glutInit):
        raise Exception("GLUT not found! Are you sure you have freeglut installed?")
    else:
        glutInit()
    if not glfw.init():
        raise Exception("GLFW not found! Are you sure you have glfw installed?")
    
def create_window():
    """
    Create a windowed mode window and its OpenGL context
    """
    window = Window(width=1600, height=900, title="Lost Horizons")
    return window

if __name__ == "__main__":
    # Initialize GLFW and GLUT and create the window
    initialize()
    window = create_window()
    # <create game stuff here>
    window.mainloop()
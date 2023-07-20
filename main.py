import time
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from core.camera import Camera
from core.mesh import QuadMesh
from settings import settings

glutInit()

def main():
    # Initialize GLFW
    if not glfw.init():
        return
    
    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(1600, 900, f"Lost Horizons {settings['version']}", None, None)
    if not window:
        glfw.terminate()
        return
    
    # Make the window's context current
    glfw.make_context_current(window)
    
    # Create a quadtree and camera
    camera = Camera(position=[0, 0, 0])
    terrain = QuadMesh(rect=[(-1000, 0, -1000), (1000, 0, -1000), (1000, 0, 1000), (-1000, 0, 1000)], tesselate_times=5)
    
    def _setup_3d():
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, glfw.get_window_size(window)[0] / glfw.get_window_size(window)[1], 2, 10000000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
    frame = 0
    frates = []
    _setup_3d()
        
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        t = time.time()
        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        _setup_3d()
        camera.update(window)
        terrain.draw()
        # Swap front and back buffers
        glfw.swap_buffers(window)
        # Poll for and process events
        glfw.poll_events()
        frame += 1
        frate = int(1 / (time.time() - t))
        frates.append(frate)
        if len(frates) > 100:
            frates.pop(0)
        smooth = int(sum(frates) / len(frates))
        print(f"\r\rCURRENT FRAME {frame} @ {smooth} FPS", end="")
    # Terminate GLFW
    glfw.terminate()
    
if __name__ == '__main__':
    main()
import time
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from core.camera import Camera
from core.planet import Planet
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
    
    # Create a Node and camera
    camera = Camera(position=[0, 0, 0])
    terrain = Planet()
    terrain.generate()
    
    def _setup_3d():
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, *glfw.get_window_size(window))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, glfw.get_window_size(window)[0] / glfw.get_window_size(window)[1], 4, 100000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    # glEnable(GL_FOG) # For a false sense of depth
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, [0.0, 0.0, 0.0, 1.0])
    glFogf(GL_FOG_DENSITY, 0.1)
    glHint(GL_FOG_HINT, GL_NICEST)
    glFogf(GL_FOG_START, 10.0)
    glFogf(GL_FOG_END, 3200.0)
    glFogi(GL_FOG_COORD_SRC, GL_FRAGMENT_DEPTH)
    
    _setup_3d()
    # Point Light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 3)(.01, .01, .01))
    glLightfv(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, (GLfloat * 1) (0.00001))
    glEnable(GL_LIGHT0)
    # Ambient Light
    glLightfv(GL_LIGHT1, GL_AMBIENT, (GLfloat * 3)(.01, .01, .01))
    glEnable(GL_LIGHT1)
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    
    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Render here, e.g. using pyOpenGL
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        _setup_3d()
        camera.update(window)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(-camera.position[0], 32, -camera.position[2], 1))
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        terrain.draw()
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT1)
        glDisable(GL_LIGHT0)
        glDisable(GL_COLOR_MATERIAL)

        terrain.update(camera)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
        
    # Terminate GLFW
    glfw.terminate()
    
if __name__ == '__main__':
    main()
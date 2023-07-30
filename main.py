import time
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from core.player import Player
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
    
    # Create a Node and player
    terrain = Planet(size=1000000)
    terrain.generate()
    terrain.atmosphere = {
        "enabled":True,
        "color":[0/256, 136/256, 255/255],
        "end": terrain.size * 1.3,
        "start": terrain.size,
        "density": 100,
    }
    player = Player(position=[0, 0, 1000100], rotation=[0, 180, 0], planet=terrain)
    
    def _setup_3d():
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, *glfw.get_window_size(window))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, glfw.get_window_size(window)[0] / glfw.get_window_size(window)[1], 4, 100000000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    # TODO: Add a skybox
    # TODO: Add a sun
    # TODO: Add atmosphere shader
    
    _setup_3d()
    # Point Light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 3)(.1, .1, .1))
    glLightfv(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, (GLfloat * 1) (0.0001))
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
        player.update(window)
        
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(-player.position[0], 32, -player.position[2], 1))
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        terrain.draw()
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT1)
        glDisable(GL_LIGHT0)
        glDisable(GL_COLOR_MATERIAL)

        terrain.update(player)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
        
    # Terminate GLFW
    glfw.terminate()
    
if __name__ == '__main__':
    main()
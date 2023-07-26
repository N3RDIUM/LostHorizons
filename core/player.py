from OpenGL.GL import *
import glfw
from math import sin, cos, radians, dist

class Player(object):
    def __init__(self, position=[0, 0, 0], rotation=[0, 0, 0], planet=None):
        self.position = position
        self.rotation = rotation
        self.planet = planet
        self.mouse_prev = glfw.get_cursor_pos(glfw.get_current_context())
        self.speed_mlt = 64000
        self.speed = self.speed_mlt
    
    def update(self, window):
        # move forward
        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1])) * 0.1 * self.speed
            self.position[2] += cos(radians(self.rotation[1])) * 0.1 * self.speed
            
        # move backward
        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            self.position[0] += sin(radians(self.rotation[1])) * 0.1 * self.speed
            self.position[2] -= cos(radians(self.rotation[1])) * 0.1 * self.speed
            
        # strafe left
        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1] - 90)) * 0.1 * self.speed
            self.position[2] += cos(radians(self.rotation[1] - 90)) * 0.1 * self.speed
            
        # strafe right
        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            self.position[0] -= sin(radians(self.rotation[1] + 90)) * 0.1 * self.speed
            self.position[2] += cos(radians(self.rotation[1] + 90)) * 0.1 * self.speed
            
        # go up
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            self.position[1] -= 0.1 * self.speed
            
        # go down
        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            self.position[1] += 0.1 * self.speed
        
        # drag mouse to rotate
        current_position = glfw.get_cursor_pos(window)
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            delta = []
            delta.append(current_position[0] - self.mouse_prev[0])
            delta.append(current_position[1] - self.mouse_prev[1])
            self.mouse_prev = current_position
        
            self.rotation[0] -= delta[1] * 0.1
            self.rotation[1] -= delta[0] * 0.1
            
            if self.rotation[0] > 90:
                self.rotation[0] = 90
            elif self.rotation[0] < -90:
                self.rotation[0] = -90
        self.mouse_prev = current_position
        
        # Near the surface of the planet, speed is 1.
        # As we get farther away, speed increases exponentially.
        self.speed = ((dist(self.position, self.planet.center) - (self.planet.size / 1000 * 999)) / self.planet.size) * self.speed_mlt / 100000 * self.planet.size
            
        # update view
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glTranslatef(self.position[0], self.position[1], self.position[2])
        
        # pseudo atmosphere
        if self.planet.atmosphere["enabled"] \
            and dist(self.position, self.planet.center) < self.planet.atmosphere["end"]:
            glEnable(GL_FOG)
            glFogi(GL_FOG_MODE, GL_LINEAR)
            glFogi(GL_FOG_COORD_SRC, GL_FRAGMENT_DEPTH)
        
            # When the distance from the start of the atmosphere is 0, mlt is 1.
            # When the distance from the end of the atmosphere is 0, mlt is 0.
            mlt = 1 - ((dist(self.position, self.planet.center) - self.planet.atmosphere["start"]) / (self.planet.atmosphere["end"] - self.planet.atmosphere["start"]))
            
            # Set the fog params
            glFogfv(GL_FOG_COLOR, self.planet.atmosphere["color"]+[mlt])
            glFogf(GL_FOG_DENSITY, self.planet.atmosphere["density"]/mlt)
            glFogf(GL_FOG_START, 0)
            glFogf(GL_FOG_END, self.planet.atmosphere["end"]/(mlt**2)/12)
            
            # Set background color
            glClearColor(
                self.planet.atmosphere["color"][0]*mlt,
                self.planet.atmosphere["color"][1]*mlt,
                self.planet.atmosphere["color"][2]*mlt,
                1
            )
        else:
            glDisable(GL_FOG)
import math
from core.node import Node
from settings import settings
from OpenGL.GL import *
from OpenGL.GLUT import *
import time

MAX_UPDATES_PER_FRAME = settings["LoD"]["max_updates_per_frame"]
PROCESSES_PER_FRAME = settings['LoD']['processes_per_frame']
CALLS_PER_FRAME = settings['LoD']['calls_per_frame']
OVERTIME_DENOMINATOR = settings['LoD']['overtime_denominator']

glutInit()
def drawSphere(x, y, z, radius=1):
    glPushMatrix()
    glTranslatef(x, y, z)
    glutSolidSphere(radius, 64, 64)
    glPopMatrix()

class DummyPlanet:
    def __init__(self, size=100, position=[0, 0, 0], rotation_details={"current":[4,8,12], "speed":[0,0.01,0]}, atmosphere={"enabled":False}):
        self.size = size
        self.position = position
        self.rotation_details = rotation_details
        self.atmosphere = atmosphere
        
        self.center = [self.size/2, self.size/2, self.size/2]
        self.center = [self.center[0]+self.position[0], self.center[1]+self.position[1], self.center[2]+self.position[2]]
        self.generation_queue = []
        self.call_queue = []
        self.chunks = {}
        self.split_queue = []
        self.unify_queue = []
        self.campos = [0, 0, 0] # player position
        self.type = "planet"
        
class Planet:
    def __init__(self, size=400, position=[0, 0, 0], rotation_details={"current":[0,0,0], "speed":[0,0,0]}, atmosphere={"enabled":False}):
        self.size = size
        self.position = position
        self.rotation_details = rotation_details
        self.atmosphere = atmosphere # TODO: Atmosphere class
        
        self.center = [0, 0, 0]
        self.center = [self.center[0]+self.position[0], self.center[1]+self.position[1], self.center[2]+self.position[2]]
        self.generation_queue = []
        self.call_queue = []
        self.chunks = {}
        self.split_queue = []
        self.unify_queue = []
        self.campos = [0, 0, 0] # player position
        self.type = "planet"
        self.children = {} # All children
        self.to_update = []
        self.frame = 0
        
    def generate_chunk(self, side, rect):
        self.chunks[side] = Node(rect=rect,parent=self, planet=self)
        self.generation_queue.append(self.chunks[side])
        
    def generate(self):
        size = self.size
        # Generate the 6 sides of the world
        self.generate_chunk("top", [(0,size,0), (0,size,size), (size,size,size), (size,size,0)])
        self.generate_chunk("left", rect=[(0,0,0), (0,0,size), (0,size,size), (0,size,0)])
        self.generate_chunk("front", rect=[(0,0,0), (0,size,0), (size,size,0), (size,0,0)])

        self.generate_chunk("bottom", rect=[(0,0,0), (size,0,0), (size,0,size), (0,0,size)])
        self.generate_chunk("right", rect=[(size,0,0), (size,size,0), (size,size,size), (size,0,size)])
        self.generate_chunk("back", rect=[(0,0,size), (size,0,size), (size,size,size), (0,size,size)]) 
        
    def rotate_point(self, point):
        CENTER = [self.size/2, self.size/2, self.size/2]
        CENTER = [CENTER[0]+self.position[0], CENTER[1]+self.position[1], CENTER[2]+self.position[2]]
        ANGLE = [
            -math.radians(self.rotation_details["current"][0]),
            -math.radians(self.rotation_details["current"][1]),
            -math.radians(self.rotation_details["current"][2])
        ]
        x = point[0]
        y = point[1]
        z = point[2]
        x1 = x
        y1 = y*math.cos(ANGLE[0]) - z*math.sin(ANGLE[0])
        z1 = y*math.sin(ANGLE[0]) + z*math.cos(ANGLE[0])
        x2 = x1*math.cos(ANGLE[1]) + z1*math.sin(ANGLE[1])
        y2 = y1
        z2 = -x1*math.sin(ANGLE[1]) + z1*math.cos(ANGLE[1])
        x3 = x2*math.cos(ANGLE[2]) - y2*math.sin(ANGLE[2])
        y3 = x2*math.sin(ANGLE[2]) + y2*math.cos(ANGLE[2])
        z3 = z2
        return [x3, y3, z3]
        
    def sort_chunks(self, player_position):
        try:
            # Sort chunks in order of distance from player
            # in the array self.to_update
            distances = []
            for chunk in self.to_update:
                # Level weightage
                distances.append((chunk, self.children[chunk].distance_to(player_position) / self.children[chunk].level))
            distances.sort(key=lambda x: x[1])
            result = []
            for i in distances:
                result.append(i[0])
            self.to_update = result
        except: pass
        
    def check_overtime(self, t):
        if time.time() - t > 1/OVERTIME_DENOMINATOR:
            return True
    
    def update(self, player):
        # Abort the function if it takes more that 1/32 of a second
        t = time.time()
        # Update the player position and planet rotation
        self.campos = self.rotate_point([
            -player.position[0]+self.position[0],
            -player.position[1]+self.position[1],
            -player.position[2]+self.position[2]
        ])
        self.rotation_details["current"][0] += self.rotation_details["speed"][0]
        self.rotation_details["current"][1] += self.rotation_details["speed"][1]
        self.rotation_details["current"][2] += self.rotation_details["speed"][2]
        if self.check_overtime(t): return
        # Update the chunks
        if len(self.to_update) == 0:
            self.to_update = list(self.children.keys())
        else:
            self.sort_chunks(player.position)
            for i in range(MAX_UPDATES_PER_FRAME):
                if len(self.to_update) > 0:
                    _ = self.to_update.pop(0)
                    try: self.children[_].update()
                    except KeyError: continue
            if self.check_overtime(t): return
                    
        for i in range(CALLS_PER_FRAME):
            if len(self.call_queue) > 0:
                self.call_queue.pop(0)()
            if self.check_overtime(t): return
        
        for i in range(PROCESSES_PER_FRAME):        
            # Process the split queue
            tosplit = self.split_queue.pop(0) if len(self.split_queue) > 0 else None
            if tosplit:
                tosplit.swap_children()
                tosplit.generate_split()
                
            # Process the unify queue
            tounify = self.unify_queue.pop(0) if len(self.unify_queue) > 0 else None
            if tounify:
                rect = tounify.rect.copy()
                parent = tounify.parent
                planet = tounify.planet
                id = tounify.id
                tounify_index = self.findchunk(id)
                if tounify_index:
                    tounify.dispose()
                    del self.chunks[tounify_index]
                    del tounify
                    tounify = Node(rect, 1, parent, planet=planet)
                    tounify.generate_unified()
                    self.chunks[tounify_index] = tounify
                else:
                    pass
            if self.check_overtime(t): return
                
        for i in range(PROCESSES_PER_FRAME):
            if len(self.generation_queue) == 0:
                return
            _ = self.generation_queue.pop(-1)
            _.generate_unified()
            if self.check_overtime(t): return
        
    def findchunk(self, id):
        for chunk in self.chunks.keys():
            if self.chunks[chunk].id == id:
                return chunk
            
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glRotatef(self.rotation_details["current"][0], 1, 0, 0)
        glRotatef(self.rotation_details["current"][1], 0, 1, 0)
        glRotatef(self.rotation_details["current"][2], 0, 0, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for chunk in self.chunks.values():
            chunk.draw()
        # glColor4f(0.6, 0.5, 1, 0.8)
        # drawSphere(0, 0, 0, self.size)
        glDisable(GL_BLEND)
        glPopMatrix()
        self.frame += 1
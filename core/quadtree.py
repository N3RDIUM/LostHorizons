from core.leafnode import LeafNode
from core.utils import midpoint
import math
import uuid
import threading

from settings import settings
MAX_LEVEL = settings['LoD']['max_level']
PROCESSES_PER_FRAME = settings['LoD']['processes_per_frame']

class QuadTree:
    def __init__(self, rect=[(0,0,0), (100,0,0), (100,0,100), (0,0,100)], level=1, parent=None, planet=None, tokill=None, toassign=None):
        self.rect = rect
        self.level = level
        self.parent = parent
        self.planet = planet
        self.tokill = tokill
        self.toassign = toassign
        self.children = []
        self._children = []
        self.size = (self.rect[1][0] - self.rect[0][0]) / 2
        self.position = []
        self.generated = False
        
        self.split_queue = []
        self.unify_queue = []
        self.id = uuid.uuid4()
        self.type = None
        
    def swap_children(self):
        for child in self.children:
            self._children.append(child)
        self.children = []
        
    def remove_old_children(self): 
        # TODO: Still causes segfaults at high player speeds
        for tokill in self._children:
            tokill.dispose()
            del tokill
        self._children = []
        
    def generate_unified(self):
        lnode = LeafNode(self.rect, 4, self, self.planet)
        self.children.append(lnode)
        self.position = [
            (self.rect[0][0]+self.rect[1][0]+self.rect[2][0]+self.rect[3][0])/4,
            (self.rect[0][1]+self.rect[1][1]+self.rect[2][1]+self.rect[3][1])/4,
            (self.rect[0][2]+self.rect[1][2]+self.rect[2][2]+self.rect[3][2])/4
        ]
        self.kill_peers()
        self.type = "leaf"
        self.generated = True
        
    def generate_split(self):
        if self.level >= MAX_LEVEL:
            return # Don't split if we're at the max level
        # Split the quad into 4 quads
        corner1 = self.rect[0]
        corner2 = self.rect[1]
        corner3 = self.rect[2]
        corner4 = self.rect[3]
        
        # Make a midpoint between each corner
        midpoint1 = midpoint(corner1, corner2)
        midpoint2 = midpoint(corner2, corner3)
        midpoint3 = midpoint(corner3, corner4)
        midpoint4 = midpoint(corner4, corner1)
        midpoint5 = midpoint(corner1, corner3)
        
        # Now, make a simple quad
        rect1 = [corner1, midpoint1, midpoint5, midpoint4]
        rect2 = [midpoint1, corner2, midpoint2, midpoint5]
        rect3 = [midpoint5, midpoint2, corner3, midpoint3]
        rect4 = [midpoint4, midpoint5, midpoint3, corner4]
        
        # Create a node for each quad
        node1 = QuadTree(rect=rect1, level=self.level + 1, parent=self, planet=self.planet)
        node2 = QuadTree(rect=rect2, level=self.level + 1, parent=self, planet=self.planet)
        node3 = QuadTree(rect=rect3, level=self.level + 1, parent=self, planet=self.planet)
        node4 = QuadTree(rect=rect4, level=self.level + 1, parent=self, planet=self.planet)
        
        # Add the nodes to the children list
        self.children.append(node1)
        self.children.append(node2)
        self.children.append(node3)
        self.children.append(node4)
        
        # Add the nodes to the generation queue
        self.planet.generation_queue.append(node1)
        self.planet.generation_queue.append(node2)
        self.planet.generation_queue.append(node3)
        self.planet.generation_queue.append(node4)
        
        # Set the position of the quad
        self.position = [
            (self.rect[0][0]+self.rect[1][0]+self.rect[2][0]+self.rect[3][0])/4,
            (self.rect[0][1]+self.rect[1][1]+self.rect[2][1]+self.rect[3][1])/4,
            (self.rect[0][2]+self.rect[1][2]+self.rect[2][2]+self.rect[3][2])/4
        ]
        self.type = "node"
        self.kill_peers()
        
    def kill_peers(self):
        try:
            if self.tokill:
                self.tokill.dispose()
                del self.tokill
                del self.parent.children[self.toassign]
                self.parent.children.insert(self.toassign, self)
            self.generated = True
        except:
            pass
        
    def draw(self):
        for child in self.children:
            child.draw()
        for child in self._children:
            child.draw()
            
    def all_children_generated(self):
        for child in self.children:
            if not child.generated:
                return False
        return True
        
    def update(self, camera_position):
        if len(self.position) == 0:
            return
        if self.type == "node":
            self.generated = self.all_children_generated()
            if self.generated:
                self.remove_old_children()
        # Calculate the distance between the camera and the center of the quad
        distance = math.dist([
            -camera_position[0],
            -camera_position[1],
            -camera_position[2],
        ], [
            self.position[0],
            self.position[1],
            self.position[2]
        ])
        
        # If the camera is close enough to the quad, split it
        if distance < self.size*5:
            if len(self.children) == 1 and self.level < MAX_LEVEL:
                self.parent.split_queue.append(self)
        elif distance > self.size*2:
            if not len(self.children) == 1:
                self.parent.unify_queue.append(self)
        for child in self.children:
            try:
                child.update(camera_position)
            except:
                pass
        
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
                level = tounify.level
                try:
                    tounify_index = self.children.index(tounify)
                    tree = QuadTree(rect, level, parent, planet=planet, tokill=tounify, toassign = tounify_index)
                    tree.generate_unified()
                except ValueError:
                    pass
                
    def dispose(self):
        for child in self.children:
            child.dispose()
        del self.children[:]
        self.children = []
from core.leafnode import LeafNode
from core.utils import midpoint
import math
import uuid

class QuadTree:
    def __init__(self, rect=[(0,0,0), (100,0,0), (100,0,100), (0,0,100)], level=1, parent=None, planet=None):
        self.rect = rect
        self.level = level
        self.parent = parent
        self.planet = planet
        self.children = []
        self.size = (self.rect[1][0] - self.rect[0][0]) / 2
        self.position = []
        
        self.split_queue = []
        self.unify_queue = []
        self.id = uuid.uuid4()
    
    def generate_unified(self):
        lnode = LeafNode(self.rect, 4, self, self.planet)
        self.children.append(lnode)
        self.position = [
            (self.rect[0][0]+self.rect[1][0]+self.rect[2][0]+self.rect[3][0])/4,
            (self.rect[0][1]+self.rect[1][1]+self.rect[2][1]+self.rect[3][1])/4,
            (self.rect[0][2]+self.rect[1][2]+self.rect[2][2]+self.rect[3][2])/4
        ]
        
    def generate_split(self):
        if self.level >= 3:
            return
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
        
    def draw(self):
        for child in self.children:
            child.draw()
        
    def update(self, camera_position):
        if len(self.position) == 0:
            return
        
        # Calculate the distance between the camera and the center of the quad
        distance = math.dist([
            -camera_position[0],
            -camera_position[2],
        ], [
            self.position[0],
            self.position[2]
        ])
        
        # If the camera is close enough to the quad, split it
        if distance < self.size*4:
            if len(self.children) == 1 and self.level < 3:
                self.parent.split_queue.append(self)
        # else:
            # if not len(self.children) == 1:
                # self.parent.unify_queue.append(self)
        for child in self.children:
            try:
                child.update(camera_position)
            except:
                pass
        
        # Process the split queue
        tosplit = self.split_queue.pop(0) if len(self.split_queue) > 0 else None
        if tosplit:
            print("Splitting")
            rect = tosplit.rect.copy()
            parent = tosplit.parent
            planet = tosplit.planet
            level = tosplit.level
            tosplit_index = self.children.index(tosplit)
            tosplit.dispose()
            del self.children[tosplit_index]
            tree = QuadTree(rect, level, parent, planet=planet)
            tree.generate_split()
            self.children.insert(tosplit_index, tree)
            
        # Process the unify queue
        tounify = self.unify_queue.pop(0) if len(self.unify_queue) > 0 else None
        if tounify:
            print("Unifying")
            rect = tounify.rect.copy()
            parent = tounify.parent
            planet = tounify.planet
            level = tounify.level
            tounify_index = self.children.index(tounify)
            tounify.dispose()
            del self.children[tounify_index]
            tree = QuadTree(rect, level, parent, planet=planet)
            tree.generate_unified()
            self.children.insert(tounify_index, tree)
            
    def dispose(self):
        for child in self.children:
            child.dispose()
        del self.children[:]
        self.children = []
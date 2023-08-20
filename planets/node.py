import math
import uuid

from core.util import midpoint
from planets.leafnode import LeafNode

class Node:
    def __init__(self, 
        quad=[
            (-1, -1, -1),
            (1, -1, -1),
            (1, -1, 1),
            (-1, -1, 1)
        ],
        level=1,
        parent=None,
        planet=None,
        renderer=None,
        game=None
    ):
        """
        My attempt at a quadtree terrain implementation.
        """
        self.quad = quad
        self.level = level
        self.parent = parent
        self.planet = planet
        self.renderer = renderer
        self.game = game
        self.uuid = uuid.uuid4()
        
        self.center = [
            (self.quad[0][0]+self.quad[1][0]+self.quad[2][0]+self.quad[3][0])/4,
            (self.quad[0][1]+self.quad[1][1]+self.quad[2][1]+self.quad[3][1])/4,
            (self.quad[0][2]+self.quad[1][2]+self.quad[2][2]+self.quad[3][2])/4
        ]
        self.size = (
            math.dist(self.quad[0], self.center)+\
            math.dist(self.quad[1], self.center)+\
            math.dist(self.quad[2], self.center)+\
            math.dist(self.quad[3], self.center)
        )/4
        self.min_distance = 10
        self.max_distance = 10
        
        self.children = {}
        self.planet.children[self.uuid] = self
        
    def generate(self):
        """
        Generate the node.
        """
        leaf = LeafNode(
            quad=self.quad,
            parent=self,
            planet=self.planet,
            renderer=self.renderer,
            game=self.game
        )
        leaf.generate()
        self.children[leaf.uuid] = leaf
        
    def update(self):
        """
        Update the node.
        """
        if self.level < 5 and\
            self.distance_to(self.planet.player_position) < self.min_distance and len(self.children) < 4:
            # self.split()
            pass
        elif len(self.children) >= 4 and self.distance_to(self.planet.player_position) > self.max_distance:
            # self.unify()
            pass
        
    def split(self):
        if self.level >= 2:
            return # Don't split if we're at the max level
        # Split the quad into 4 quads
        corner1 = self.quad[0]
        corner2 = self.quad[1]
        corner3 = self.quad[2]
        corner4 = self.quad[3]
        
        # Make a midpoint between each corner
        midpoint1 = midpoint(corner1, corner2)
        midpoint2 = midpoint(corner2, corner3)
        midpoint3 = midpoint(corner3, corner4)
        midpoint4 = midpoint(corner4, corner1)
        midpoint5 = midpoint(corner1, corner3)
        
        # Now, make a simple quad
        quad1 = [corner1, midpoint1, midpoint5, midpoint4]
        quad2 = [midpoint1, corner2, midpoint2, midpoint5]
        quad3 = [midpoint5, midpoint2, corner3, midpoint3]
        quad4 = [midpoint4, midpoint5, midpoint3, corner4]
        
        # Create a node for each quad
        node1 = Node(
            quad=quad1, 
            level=self.level + 1, 
            parent=self, 
            planet=self.planet, 
            renderer=self.renderer, 
            game=self.game
        )
        node2 = Node(
            quad=quad2, 
            level=self.level + 1, 
            parent=self, 
            planet=self.planet, 
            renderer=self.renderer, 
            game=self.game
        )
        node3 = Node(
            quad=quad3, 
            level=self.level + 1, 
            parent=self, 
            planet=self.planet, 
            renderer=self.renderer, 
            game=self.game
        )
        node4 = Node(
            quad=quad4, 
            level=self.level + 1, 
            parent=self, 
            planet=self.planet, 
            renderer=self.renderer, 
            game=self.game
        )
        
        # Generate the nodes
        nodes = [node1, node2, node3, node4]
        for node in nodes:
            node.generate()
        
        # Add the nodes to the children list
        self.children[node1.uuid] = node1
        self.children[node2.uuid] = node2
        self.children[node3.uuid] = node3
        self.children[node4.uuid] = node4
                    
    def distance_to(self, position):
        """
        Return the distance to a position.
        """
        return math.dist(self.center, position)
    
    def draw(self):
        """
        Draw the node.
        """
        for child in self.children.values():
            child.draw()
    
    @property
    def generated(self):
        """
        Return whether or not the node has been generated.
        """
        for child in self.children.values():
            if not child.generated:
                return False
        return True
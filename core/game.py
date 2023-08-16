import multiprocessing

from core.renderer import Renderer
from camera.player import Player
from planets.tesselate import tesselate

import random
import noise

class Game(object):
    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.renderer = Renderer()
        self.player = Player()
        
        self.processes = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.storages = self.renderer.storages
        self.namespace.killed = False
        self.process_count = 1
        for i in range(self.process_count):
            self.processes.append(
                multiprocessing.Process(target=self.process, args=(self.namespace,)))
            self.processes[i].start()
            
        self.addToQueue({
            "task": "test",
        })
        
        self.window.schedule_mainloop(self)
        self.window.schedule_shared_context(self)
            
    def addToQueue(self, item):
        """
        Add an item to the queue.
        """
        self.namespace.queue.put(item)
    
    @staticmethod
    def process(namespace):
        """
        This function is called to start a multiprocessing process.
        """
        import os
        import glfw
        glfw.init()
        
        print("Process started: " + str(os.getpid()))
        # Get all items from the queue
        queue = namespace.queue
        while not namespace.killed:
            if not queue.empty():
                item = queue.get()
                Game.handleQueueItem(item, namespace)
                
        if namespace.killed:
            glfw.terminate()
            
    @staticmethod
    def handleQueueItem(item, namespace):
        """
        Handle a queue item.
        """
        if item["task"] == "test":
            # Vertex calculations
            quad = [
                (-1, -1, -1),
                (1, -1, -1),
                (1, -1, 1),
                (-1, -1, 1)
            ]
            segments = 100
            _new_verts = tesselate(quad, segments)
            for i in range(len(_new_verts)):
                _new_verts[i] = (
                    _new_verts[i][0] * segments,
                    _new_verts[i][1] + noise.pnoise3(_new_verts[i][0], _new_verts[i][1], _new_verts[i][2]) * 10,
                    _new_verts[i][2] * segments,
                )
            new_verts = []
            for vert in _new_verts:
                new_verts.extend(vert)
            # Color calculations based on perlin noise in that area
            colors = []
            for i in range(len(_new_verts)):
                x = _new_verts[i][0]
                y = _new_verts[i][1]
                z = _new_verts[i][2]
                colors.extend((
                    abs(noise.pnoise3(x / 10 + 8, y / 10 + 8, z / 10 + 8) / 4 * 3 + 0.25), 
                    abs(noise.pnoise3(x / 10 + 16, y / 10 + 16, z / 10 + 16) / 4 * 3 + 0.25),
                    abs(noise.pnoise3(x / 10 + 32, y / 10 + 32, z / 10 + 32) / 4 * 3 + 0.25)
                ))
            namespace.storages['default'].vertices.extend(new_verts)
            namespace.storages['default'].colors.extend(colors)
                
    def terminate(self):
        """
        Terminate all processes.
        """
        self.namespace.killed = True
        for process in self.processes:
            process.terminate()
                
    def drawcall(self):
        """
        Draw call.
        """
        self.player.update(self.window.window)
        self.renderer.draw()

    def sharedcon(self):
        """
        Shared context.
        """
        while not self.namespace.killed:
            self.renderer.update()
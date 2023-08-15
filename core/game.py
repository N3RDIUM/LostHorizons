import multiprocessing

from core.renderer import Renderer
from camera.player import Player

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
            # Add a grid of points to the renderer
            a = 32
            _v = []
            _c = []
            for x in range(-a, a):
                for z in range(-a, a):
                    h = -0.4
                    _v.extend([
                        # For GL_TRIANGLES
                        x / a, h, z / a,
                        x / a, h, (z + 1) / a,
                        (x + 1) / a, h, z / a,
                        (x + 1) / a, h, z / a,
                        x / a, h, (z + 1) / a,
                        (x + 1) / a, h, (z + 1) / a,
                    ])
                    _c.extend([
                        abs(noise.pnoise2(x / 10 + 8, z / 10 + 8) / 2 + 0.5), 
                        abs(noise.pnoise2(x / 10 + 16, z / 10 + 16) / 2 + 0.5), 
                        abs(noise.pnoise2(x / 10 + 32, z / 10 + 32) / 2 + 0.5),
                    ] * 6)
                namespace.storages['default'].vertices.extend(_v)
                namespace.storages['default'].colors.extend(_c)
                _v = []
                _c = []
                
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
import multiprocessing

from core.renderer import Renderer
from camera.player import Player
from core.tesselate import tesselate_partial
from core.fractalnoise import fractal_noise

import filelock
import json

class Game(object):
    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.renderer = Renderer(self)
        self.player = Player()
        
        self.processes = []
        self.result_queue = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.killed = False
        self.process_count = multiprocessing.cpu_count()
        for i in range(self.process_count):
            self.processes.append(
                multiprocessing.Process(target=self.process, args=(self.namespace,)))
            self.processes[i].start()
            
        for i in range(len(self.processes)):
            asdf = 1
            self.addToQueue({
                "task": "tesselate",
                "mesh": "default",
                "quad": [
                    (-asdf, -1, -asdf),
                    (asdf, -1, -asdf),
                    (asdf, -1, asdf),
                    (-asdf, -1, asdf)
                ],
                "segments": 128,
                "denominator": len(self.processes),
                "numerator": i
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
        import glfw
        glfw.init()
        
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
        if item["task"] == "tesselate":
            # Vertex calculations
            quad = tuple(item["quad"])
            segments = item["segments"]
            _new_verts = tesselate_partial(quad, segments, item["denominator"], item["numerator"])
            colors = []
            for i in range(len(_new_verts)):
                noiseval = fractal_noise(_new_verts[i])
                _new_verts[i] = (
                    _new_verts[i][0] * segments,
                    _new_verts[i][1] + noiseval * 32,
                    _new_verts[i][2] * segments,
                )
                colors.extend((
                    noiseval * 0.5 + 0.5,
                    noiseval * 0.5 + 0.5,
                    noiseval * 0.5 + 0.5,
                ))
            verts_1d = [item for sublist in _new_verts for item in sublist]
            # save to JSON
            file = f".datatrans/default-{item['numerator']}.json"
            with filelock.FileLock(file + ".lock"):
                with open(file, "w") as f:
                    json.dump({
                        "vertices": list(verts_1d).copy(),
                        "colors": list(colors).copy()
                    }, f)
            namespace.result_queue.put({
                "type": "buffer_mod",
                "mesh": "default",
                "numerator": item["numerator"],
                "denominator": item["denominator"],
                "datafile": file
            })
                
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
            self.result_queue.append(self.namespace.result_queue.get())
            self.renderer.update()
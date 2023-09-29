import json
import multiprocessing
import random
import threading
import uuid

import filelock

from camera.player import Player
from core.fractalnoise import fractal_noise
from core.renderer import Renderer
from core.tesselate import tesselate_partial
from planets.twod_lod import LoD


class Game(object):

    def __init__(self, window):
        """
        class Game
        This is the main game class.
        """
        self.window = window
        self.renderer = Renderer(self)
        self.player = Player()
        self.frame = 0

        self.processes = []
        self.result_queue = []
        self.generation_queue = []
        self.manager = multiprocessing.Manager()
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.generated_chunks = self.manager.list()
        self.namespace.killed = False
        self.process_count = multiprocessing.cpu_count()
        for i in range(self.process_count):
            self.processes.append(
                multiprocessing.Process(target=self.process,
                                        args=(self.namespace, )))
            self.processes[i].start()

        self.lod = LoD(self, 6)
        self.lod.generate()

        self.window.schedule_mainloop(self)
        self.window.schedule_shared_context(self)

        self.thread = threading.Thread(target=self.update_thread)
        self.thread.start()
        self.thread_2 = threading.Thread(target=self.generate_thread)
        self.thread_2.start()

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
        if item["task"] == "tesselate_full":
            # Vertex calculations
            quad = tuple(item["quad"])
            segments = item["segments"]
            divisions = item["denominator"]
            new_verts = []
            color = [random.random() for i in range(3)]
            for i in range(divisions):
                new_verts += [tesselate_partial(quad, segments, divisions, i)]
            for _new_verts in new_verts:
                colors = []
                for i in range(len(_new_verts)):
                    noiseval = fractal_noise([
                        _new_verts[i][0] / 10,
                        _new_verts[i][1] / 10,
                        _new_verts[i][2] / 10,
                    ])
                    _new_verts[i] = (
                        _new_verts[i][0],
                        _new_verts[i][1] + noiseval * 4,
                        _new_verts[i][2],
                    )
                    colors.extend((color[i] / 4 + (noiseval * 0.5 + 0.5))
                                  for i in range(3))
                verts_1d = [item for sublist in _new_verts for item in sublist]
                file = f".datatrans/{item['mesh']}-{uuid.uuid4()}.json"
                with filelock.FileLock(file + ".lock"):
                    with open(file, "w") as f:
                        json.dump(
                            {
                                "vertices": list(verts_1d).copy(),
                                "colors": list(colors).copy(),
                            },
                            f,
                        )
                namespace.result_queue.put({
                    "type": "buffer_mod",
                    "mesh": item["mesh"],
                    "datafile": file
                })
            namespace.generated_chunks.append(item["mesh"])

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
        self.renderer.update()
        self.frame += 1

    def sharedcon(self):
        """
        Shared context.
        """
        while not self.namespace.killed:
            self.lod.update()

    def update_thread(self):
        while not self.namespace.killed:
            self.result_queue.append(self.namespace.result_queue.get())

    def generate_thread(self):
        while not self.namespace.killed:
            if len(self.generation_queue) > 0:
                self.generation_queue.pop(0).generate()

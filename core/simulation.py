import math
import multiprocessing
import random
import threading
from multiprocessing import shared_memory

import numpy as np

from camera.player import Player
from core.renderer import Renderer


class Simulation:

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
                multiprocessing.Process(target=self.process, args=(self.namespace,))
            )
            self.processes[i].start()

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
                Simulation.handleQueueItem(item, namespace)

        if namespace.killed:
            glfw.terminate()

    @staticmethod
    def handleQueueItem(item, namespace):
        """
        Handle a queue item.
        """
        # TODO: Send the thingy to a child worker process thing.

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
        Shared context call.
        """

    def update_thread(self):
        while not self.namespace.killed:
            self.result_queue.append(self.namespace.result_queue.get())

    def generate_thread(self):
        while not self.namespace.killed:
            try:
                self.generation_queue.pop(0).generate()
            except IndexError:
                pass
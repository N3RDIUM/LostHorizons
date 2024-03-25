from uuid import uuid4
import multiprocessing
import numpy as np
from time import perf_counter
from multiprocessing import shared_memory

from camera.player import Player
from core.renderer import Renderer
from planet.sphere import Sphere

class Simulation:
    def __init__(self, window):
        """
        class Simulation
        This is the main simulation class.
        """
        self.window = window
        self.renderer = Renderer(self)
        self.player = Player()
        self.frame = 0
        
        self.manager = multiprocessing.Manager()        
        self.namespace = self.manager.Namespace()
        self.namespace.queue = self.manager.Queue()
        self.namespace.result_queue = self.manager.Queue()
        self.namespace.generated_chunks = self.manager.list()
        self.namespace.killed = False
        
        self.processes = []
        self.result_queue = []
        
        self.process_count = multiprocessing.cpu_count()
        for i in range(self.process_count):
            self.processes.append(
                multiprocessing.Process(target=self.process, args=(self.namespace,))
            )
            self.processes[i].start()
        
        self.scheduled_objects = {}
        self.sphere = Sphere(
            self,
            16,
            [0, 0, 0]
        )
        self.sphere.generate()

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
        
        from helpers.tesselator import fast_tesselate
        helpers = {
            'tesselator': fast_tesselate
        }

        # Get all items from the queue
        queue = namespace.queue
        while not namespace.killed:
            if not queue.empty():
                item = queue.get()
                Simulation.handleQueueItem(item, namespace, helpers)

        if namespace.killed:
            glfw.terminate()

    @staticmethod
    def handleQueueItem(item, namespace, helpers):
        """
        Handle a queue item.
        """
        if item['task'] == "tesselate":
            args = item['args']
            
            rect_shared_uuid = args['rect-uuid']
            rect_buffer = shared_memory.SharedMemory(name=rect_shared_uuid)
            rect = np.ndarray((4, 3), dtype=np.float64, buffer=rect_buffer.buf)
            segments = args['segments']
            
            t = perf_counter()
            result = helpers['tesselator'](rect, segments)
            result_buffer = shared_memory.SharedMemory(create=True, size=result.nbytes, name=str(uuid4()))
            shared_result = np.ndarray(result.shape, dtype=result.dtype, buffer=result_buffer.buf)
            shared_result[:] = result[:]
            
            namespace.result_queue.put({
                "task-id": item['task-id'],
                "task": 'tesselate',
                "mesh-uuid": result_buffer.name,
                "time_taken": perf_counter() - t
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
        self.renderer.update()
        self.frame += 1

    def sharedcon(self):
        """
        Shared context call.
        """
        while not self.window.killed:
            if not self.namespace.result_queue.empty():
                item = self.namespace.result_queue.get()
                print(item)
                self.scheduled_objects[item['task-id']].notify_done
                self.result_queue.append(item)
                
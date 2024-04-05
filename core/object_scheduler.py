# Imports
from uuid import uuid4


class Scheduler:
    """
    Maintains a list of objects to be scheduled along with the function name.
    """

    def __init__(self) -> None:
        """
        Initialize the scheduler and required variables
        """
        self.queue = {}

    def add(self, obj, function_name, id=str(uuid4())):
        """
        Adds an object to the queue, returns the id of that object in the queue
        """
        self.queue[id] = {"object": obj, "function": function_name}

    def remove(self, id):
        """
        Removes an object from the queue by its id
        """
        del self.queue[id]
        return id

    def process_item(self, id):
        """
        Process a single item in the queue.
        Useful if you want to partially update the queue
        """
        item = self.queue[id]
        item["object"].__getattribute__("function")()

    def process(self):
        """
        Process the queue, i.e. call the asked for functions of the queue items
        """
        for item in self.queue:
            self.process_item(item)

from .Process import Process


class Queue:
    def __init__(self):
        self.queue = []
        self.last_id = 0

    def add(self):
        self.last_id += 1
        self.queue.append(Process(self.last_id, 0))

    #  TODO: Scheduling algorithm

    def __str__(self):
        return "\n".join(repr(p) for p in self.queue)


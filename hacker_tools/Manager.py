from .Process import Process


class Queue:
    def __init__(self):
        self.queue = []
        self.last_id = 0

    def add(self):
        self.last_id += 1
        self.queue.append(Process(self.last_id, Clock.time))
        Clock.increment()

    #  TODO: Scheduling algorithm

    def __str__(self):
        return "\n".join(repr(p) for p in self.queue)


class Clock:
    time = 1

    @staticmethod
    def increment(diff=1):
        Clock.time += 1


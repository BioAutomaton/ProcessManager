import random
import enum
from dataclasses import dataclass, field

from hacker_tools import Config

hackable = ("Pentagon", "Hacker", "Life", "Military", "Python", "World", "USA", "Windows", "Linux")


class ProcessState(enum.Enum):
    ready = 0
    waiting = 1
    running = 2
    finished = 3


@dataclass
class Process:
    id: int
    time_in: int
    name: str = field(init=False)
    priority: int = field(init=False)
    duration: int = field(init=False)
    memory: int = field(init=False)
    burst_time: int = 0
    state: ProcessState = field(init=False)

    def __post_init__(self):
        self.name = "hack" + random.choice(hackable) + ".exe"
        self.priority = random.randint(Config.MIN_PRIORITY, Config.MAX_PRIORITY)
        self.duration = random.randint(Config.MIN_DURATION, Config.MAX_DURATION)
        self.memory = random.randint(Config.MIN_PROCESS_SIZE, Config.MAX_PROCESS_SIZE)
        self.state = ProcessState.ready


@dataclass(order=True)
class MemoryBlock:
    start: int
    end: int

    def __sub__(self, other):
        return MemoryBlock(other.end + 1, self.start - 1)

    def length(self):
        return self.end - self.start + 1


class MemoryManager:
    memory = []

    @staticmethod
    def find_free_block(size):
        bounded_memory = [MemoryBlock(-1, -1)] + sorted(MemoryManager.memory) + \
                         [MemoryBlock(Config.MEMORY_SIZE + 1, Config.MEMORY_SIZE + 1)]

        suitable_blocks = []

        for m1, m2 in zip(bounded_memory[0:], bounded_memory[1:]):
            gap = m2 - m1
            if gap.length() >= size:
                suitable_blocks.append(gap)

        return min(suitable_blocks, key=MemoryBlock.length) if suitable_blocks else None

    @staticmethod
    def fill_memory_block(size):
        best_match = MemoryManager.find_free_block(size)
        if best_match:
            MemoryManager.add(MemoryBlock(best_match.start, best_match.start + size - 1))
            return True

        return False

    @staticmethod
    def release_memory_block(memory_block):
        MemoryManager.memory.remove(memory_block)

    @staticmethod
    def add(new_block):
        MemoryManager.memory.append(new_block)

    @staticmethod
    def show_memory():
        print(sorted(MemoryManager.memory))


class Clock:
    time = 1

    @staticmethod
    def increment(diff=1):
        Clock.time += 1


class Queue:
    def __init__(self):
        self.queue = []
        self.last_id = 0

    def generate_process(self, quantity=1):
        for _ in range(quantity):
            self.last_id += 1
            self.queue.append(Process(self.last_id, Clock.time))

    #  TODO: Scheduling algorithm

    def __str__(self):
        return "\n".join(repr(p) for p in self.queue)

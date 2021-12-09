import random
import enum
from dataclasses import dataclass, field

from hacker_tools import Config


class Clock:
    time = 0

    @staticmethod
    def increment(diff=1):
        Clock.time += 1


class ProcessState(enum.Enum):
    ready = 0
    waiting = 1
    running = 2
    finished = 3


@dataclass(order=True)
class MemoryBlock:
    start: int
    end: int

    def __sub__(self, other):
        return MemoryBlock(other.end + 1, self.start - 1)

    def size(self):
        return self.end - self.start + 1


@dataclass
class Process:
    id: int
    time_in: int = Clock.time
    name: str = field(init=False)
    priority: int = field(init=False)
    duration: int = field(init=False)
    memory: int = field(init=False)
    burst_time: int = 0
    state: ProcessState = field(init=False)
    address: MemoryBlock = None

    def __post_init__(self):
        self.name = "hack" + random.choice(Config.HACKABLE) + ".exe"
        self.priority = random.randint(Config.MIN_PRIORITY, Config.MAX_PRIORITY)
        self.duration = random.randint(Config.MIN_DURATION, Config.MAX_DURATION)
        self.memory = random.randint(Config.MIN_PROCESS_SIZE, Config.MAX_PROCESS_SIZE)
        self.state = ProcessState.ready

    def __gt__(self, other):
        return self.memory > other.memory

    def __ge__(self, other):
        return self.memory >= other.memory

    def __lt__(self, other):
        return self.memory < other.memory

    def __le__(self, other):
        return self.memory <= other.memory

    def __eq__(self, other):
        return self.id == other.id


class MemoryManager:
    memory = []

    @staticmethod
    def find_free_block(size):
        bounded_memory = [MemoryBlock(-1, -1)] + sorted(MemoryManager.memory) + \
                         [MemoryBlock(Config.MEMORY_SIZE + 1, Config.MEMORY_SIZE + 1)]

        suitable_blocks = []

        for m1, m2 in zip(bounded_memory[0:], bounded_memory[1:]):
            gap = m2 - m1
            if gap.size() >= size:
                suitable_blocks.append(gap)

        return min(suitable_blocks, key=MemoryBlock.size) if suitable_blocks else None

    @staticmethod
    def fill_memory_block(size):
        best_match = MemoryManager.find_free_block(size)
        if best_match:
            filled_memory_block = MemoryBlock(best_match.start, best_match.start + size - 1)
            MemoryManager.add(filled_memory_block)
            return filled_memory_block

        return None

    @staticmethod
    def release_memory_block(memory_block):
        MemoryManager.memory.remove(memory_block)

    @staticmethod
    def add(new_block):
        MemoryManager.memory.append(new_block)

    @staticmethod
    def show_memory():
        print(sorted(MemoryManager.memory))


class Queue:
    def __init__(self):
        self.queue = []

    def add(self, process):
        self.queue.append(process)
        self.reschedule()

    #  TODO: Scheduling algorithm

    def reschedule(self):
        self.queue.sort()

    def find_process(self, process):
        return process in self.queue

    def __str__(self):
        return "\n".join(repr(p) for p in self.queue)

    def kill_process(self, process_id):
        process = Process(process_id)
        if self.find_process(process):
            self.queue.remove(Process(process_id))
            return True

        return False


@dataclass
class Core:
    id: int
    current_process: Process = None

    def status(self):
        return "Busy" if self.current_process else "Free"

    def do_work(self):
        if self.current_process:
            self.current_process.burst_time += 1

    def __str__(self):
        return f"Core #{self.id}: {self.status()}"


class CPU:
    def __init__(self, cores_n=4):
        self.cores = [Core(i) for i in range(cores_n)]

    def __str__(self):
        return "\n".join(str(core) for core in self.cores)


class Manager:
    def __init__(self, cpu_cores_n):
        self.stats = {"Stat #1": 0, "Stat #2": 0}
        self.last_id = 0
        self.process_queue = Queue()
        self.rejection_queue = Queue()
        self.finished_processes = []
        self.CPU = CPU(cpu_cores_n)

    def __str__(self):
        return str(self.CPU) + "\n" + str(self.process_queue)

    def generate_process(self, quantity=1):
        for _ in range(quantity):
            new_process = Process(self.last_id)
            allocated_memory = MemoryManager.fill_memory_block(new_process.memory)
            if allocated_memory:
                new_process.address = allocated_memory
                self.process_queue.add(new_process)
            else:
                self.rejection_queue.add(new_process)

            self.last_id += 1

    def kill_process(self, process_id):
        return self.process_queue.kill_process(process_id) or self.rejection_queue.kill_process(process_id)

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
    running = 0
    ready = 1
    new = 2
    waiting = 3
    terminated = 4

    def __lt__(self, other):
        return self.value < other.value


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
        self.state = ProcessState.new

    def __lt__(self, other):
        return (self.state, self.duration) < (other.state, other.duration)

    def __eq__(self, other):
        return self.id == other.id

    def is_done(self):
        return self.burst_time >= self.duration


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

    def reschedule(self):
        self.queue.sort()

    def get_process(self, process_id):
        for process in self.queue:
            if process.id == process_id:
                return process

    def get_first_ready(self):
        for process in self.queue:
            if process.state == ProcessState.ready:
                return process

    def __str__(self):
        return "[" + "\n".join(repr(p) for p in self.queue) + "]"

    def kill(self, process_id):
        process = self.get_process(process_id)
        if process:
            self.queue.remove(process)
            self.reschedule()
            process.state = ProcessState.terminated
            return process

        return None


@dataclass
class Core:
    id: int
    current_process: Process = None

    def status_str(self):
        return "Busy" if self.current_process else "Free"

    def do_work(self):
        if self.current_process:
            self.current_process.burst_time += 1
            if self.current_process.is_done():
                return self.current_process

    def assign_job(self, process):
        if self.current_process is None:
            self.current_process = process
            process.state = ProcessState.running

    def __str__(self):
        return f"Core #{self.id}: {self.status_str()}"

    def is_available(self):
        return not self.current_process


class CPU:
    def __init__(self, cores_n=4):
        self.cores = [Core(i) for i in range(cores_n)]

    def distribute_processes(self, queue):
        for i, core in enumerate(self.cores):
            core.assign_job(queue.get_first_ready())

    def do_work(self):
        finished_processes = [core.do_work() for core in self.cores]
        if any(finished_processes):
            return [process for process in finished_processes if process is not None]

    def is_available(self):
        return any(core.is_available() for core in self.cores)

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
        return f"{str(self.CPU)}\nProcess Queue: \n{str(self.process_queue)}\n" \
               f"Rejection Queue:\n{str(self.rejection_queue)}\nFinished processes: \n{str(self.finished_processes)}"

    def generate_process(self, quantity=1):
        for _ in range(quantity):
            new_process = Process(self.last_id)
            allocated_memory = MemoryManager.fill_memory_block(new_process.memory)
            if allocated_memory:
                new_process.address = allocated_memory
                new_process.state = ProcessState.ready
                self.process_queue.add(new_process)
            else:
                new_process.state = ProcessState.waiting
                self.rejection_queue.add(new_process)

            self.last_id += 1

    def kill_process(self, process_id):
        process = self.process_queue.kill(process_id) or self.rejection_queue.kill(process_id)
        if process:
            if process.address:
                MemoryManager.release_memory_block(process.address)
                process.address = None
            self.finished_processes.append(process)

    def do_work(self):
        if self.CPU.is_available():
            self.CPU.distribute_processes(self.process_queue)
        self.CPU.do_work()

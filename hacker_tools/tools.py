import random
import enum
from dataclasses import dataclass, field

from hacker_tools import config


class Clock:
    __time = 0

    @staticmethod
    def increment(diff=1):
        Clock.__time += diff

    @staticmethod
    def get_current_time():
        return Clock.__time


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

    def __str__(self):
        return f"({self.start}-{self.end})"


@dataclass
class Process:
    id: int
    time_in: int = field(init=False)
    name: str = field(init=False)
    priority: int = field(init=False)
    work_required: int = field(init=False)
    memory: int = field(init=False)
    burst_time: int = 0
    state: ProcessState = ProcessState.new
    address: MemoryBlock = None

    def __post_init__(self):
        self.name = "hack" + random.choice(config.HACKABLE) + ".exe"
        self.time_in = Clock.get_current_time()
        self.priority = random.randint(config.MIN_PRIORITY, config.MAX_PRIORITY)
        self.work_required = random.randint(config.MIN_WORK, config.MAX_WORK)
        self.memory = random.randint(config.MIN_PROCESS_SIZE, config.MAX_PROCESS_SIZE)

    def __lt__(self, other):
        return (self.state, self.work_required, self.priority, self.time_in, self.id) < (
            other.state, other.work_required, other.priority, other.time_in, other.id)

    def __gt__(self, other):
        return (self.state, self.work_required, self.memory, self.priority, self.time_in, self.id) > (
            other.state, other.work_required, other.memory, other.priority, other.time_in, other.id)

    def __eq__(self, other):
        return self.id == other.id

    def is_done(self):
        return self.burst_time >= self.work_required

    def info(self):
        return self.name, self.id, self.state.name, f"{self.burst_time} / {self.work_required}", self.memory, \
               self.address, self.priority, self.time_in

    def short_info(self):
        return self.name, self.id, self.state.name


class MemoryManager:
    def __init__(self):
        self.memory = []

    def find_free_block(self, size):
        self.memory.sort()
        bounded_memory = [MemoryBlock(-1, -1)] + self.memory + \
                         [MemoryBlock(config.MEMORY_SIZE + 1, config.MEMORY_SIZE + 1)]

        suitable_blocks = []

        for block_1, block_2 in zip(bounded_memory[0:], bounded_memory[1:]):
            gap = block_2 - block_1
            if gap.size() >= size:
                suitable_blocks.append(gap)

        return min(suitable_blocks, key=MemoryBlock.size) if suitable_blocks else None

    def fill_memory_block(self, size):
        best_match = self.find_free_block(size)
        if best_match:
            filled_memory_block = MemoryBlock(best_match.start, best_match.start + size - 1)
            self.add(filled_memory_block)
            return filled_memory_block

        return None

    def release_memory_block(self, memory_block):
        self.memory.remove(memory_block)

    def add(self, new_block):
        self.memory.append(new_block)

    def output(self):
        return sorted(self.memory)


class Queue:
    def __init__(self):
        self.queue = []

    def add(self, process):
        self.queue.append(process)
        self.reschedule()

    def reschedule(self):
        self.queue.sort()

    def get_process(self, process):
        for p in self.queue:
            if p == process:
                return p

    def remove_process(self, process):
        self.queue.remove(process)

    def get_first_ready(self):
        for process in self.queue:
            if process.state == ProcessState.ready:
                return process

    def kill(self, process):
        process = self.get_process(process)
        if process:
            self.queue.remove(process)
            self.reschedule()
            process.state = ProcessState.terminated
            return process

        return None

    def __str__(self):
        return "[" + "\n".join(repr(p) for p in self.queue) + "]"

    def output(self):
        return [process.info() for process in self.queue]


@dataclass
class Core:
    id: int
    current_process: Process = None

    def status_str(self):
        return "Busy: " + self.current_process.name if self.current_process else "Free"

    def status(self):
        return self.id, (self.current_process.name if self.current_process else None)

    def do_work(self):
        if self.current_process:
            self.current_process.burst_time += 1
            if self.current_process.is_done():
                temp = self.current_process
                self.current_process = None
                return temp

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
        for core in self.cores:
            process = queue.get_first_ready()
            if process:
                core.assign_job(process)

    def do_work(self):
        finished_processes = [core.do_work() for core in self.cores]
        if any(finished_processes):
            return [process for process in finished_processes if process is not None]

    def is_available(self):
        return any(core.is_available() for core in self.cores)

    def status(self):
        return [core.status() for core in self.cores]

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
        self.memory_manager = MemoryManager()

    def generate_output(self):
        output = {
            "process_queue": self.process_queue.output(),
            "rejection_queue": self.rejection_queue.output(),
            "finished_processes": [process.short_info() for process in self.finished_processes],
            "cpu": self.CPU.status(),
            "memory": self.memory_manager.output(),
            "current_tact": Clock.get_current_time()
        }

        output["process_len"] = len(output["process_queue"])
        output["rejection_len"] = len(output["rejection_queue"])
        output["finished_len"] = len(output["finished_processes"])

        return output

    def __str__(self):
        return f"{str(self.CPU)}\nProcess Queue: \n{str(self.process_queue)}\n" \
               f"Rejection Queue:\n{str(self.rejection_queue)}\n" \
               f"Finished processes: \n{chr(10).join(repr(process) for process in self.finished_processes)}\n" \
               f"Memory: \n{self.memory_manager.output()}"

    def generate_process(self, quantity=1):
        for _ in range(quantity):
            new_process = Process(self.last_id)
            self.add_process(new_process)
            self.last_id += 1

    def fill_queue_from_rejects(self):
        for process in self.rejection_queue.queue:
            allocated_memory = self.memory_manager.fill_memory_block(process.memory)
            if allocated_memory:
                self.rejection_queue.remove_process(process)
                process.address = allocated_memory
                process.state = ProcessState.ready
                self.process_queue.add(process)

    def add_process(self, process):
        allocated_memory = self.memory_manager.fill_memory_block(process.memory)
        if allocated_memory:
            process.address = allocated_memory
            process.state = ProcessState.ready
            self.process_queue.add(process)
        else:
            process.state = ProcessState.waiting
            self.rejection_queue.add(process)

    def kill_process(self, process):
        process = self.process_queue.kill(process) or self.rejection_queue.kill(process)
        if process:
            if process.address:
                self.memory_manager.release_memory_block(process.address)
                process.address = None
            self.finished_processes.append(process)

    def do_work(self):
        self.distribute_processes()

        finished_processes = self.CPU.do_work()
        Clock.increment()
        if finished_processes:
            for process in finished_processes:
                process.state = ProcessState.terminated
                self.kill_process(process)

            #  fill the space from rejects if possible
            self.fill_queue_from_rejects()
            #  assign new work to CPU cores
            self.distribute_processes()

    def distribute_processes(self):
        if self.CPU.is_available():
            self.CPU.distribute_processes(self.process_queue)

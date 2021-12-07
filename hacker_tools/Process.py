import random
import enum
from hacker_tools import Config
from dataclasses import dataclass

nouns = ["Pentagon", "Hacker", "Life", "Military", "Python", "World", "USA", "Windows", "Linux"]


class ProcessState(enum.Enum):
    ready = 0
    waiting = 1
    running = 2
    finished = 3


@dataclass
class Process:
    id: int
    time_in: int
    name: str = "hack" + random.choice(nouns) + ".exe"
    priority: int = random.randint(Config.MIN_PRIORITY, Config.MAX_PRIORITY)
    duration: int = random.randint(Config.MIN_DURATION, Config.MAX_DURATION)
    memory: int = random.randint(Config.MIN_PROCESS_SIZE, Config.MAX_PROCESS_SIZE)
    burst_time: int = 0
    state: ProcessState = ProcessState.ready

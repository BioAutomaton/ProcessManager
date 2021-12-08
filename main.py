from hacker_tools.Core import Queue, MemoryManager, MemoryBlock


def main():
    MemoryManager.add(MemoryBlock(0, 128))
    MemoryManager.show_memory()
    MemoryManager.fill_memory_block(5)
    MemoryManager.show_memory()


if __name__ == "__main__":
    main()

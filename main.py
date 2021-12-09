from hacker_tools.Core import Manager


def main():
    manager = Manager(4)
    manager.generate_process(5)
    print(manager)
    manager.kill_process(4)
    print(manager)
    pass

if __name__ == "__main__":
    main()

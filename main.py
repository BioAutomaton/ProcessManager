from hacker_tools.Core import Manager


def main():
    manager = Manager(4)
    manager.generate_process(5)
    manager.do_work()
    print(manager)
    manager.generate_process(5)
    print(manager)

    pass


if __name__ == "__main__":
    main()

from hacker_tools.Core import Manager


def main():
    manager = Manager(4)
    manager.generate_process(5)
    for _ in range(10):
        manager.do_work()
        print(manager)


    pass


if __name__ == "__main__":
    main()

from hacker_tools.Manager import Queue, Clock


def main():
    q = Queue()
    q.add()
    q.add()
    q.add()
    print(q)


if __name__ == "__main__":
    main()
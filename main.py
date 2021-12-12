import tkinter as tk
from tkinter import ttk
from hacker_tools.Core import Manager, Config


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.running = False
        self.interval = 1024

        self.manager = Manager(4)
        self.title('HackerTools')
        self.resizable(0, 0)

        #  DEFINE TABLES AND LABELS
        self.process_queue_label = self.create_label({"row": 0, "column": 0}, "PROCESS QUEUE")
        self.process_queue = self.create_table({"row": 1, "column": 0}, Config.PROCESS_INFO)

        self.rejection_queue_label = self.create_label({"row": 2, "column": 0}, "REJECTION QUEUE")
        self.rejection_queue = self.create_table({"row": 3, "column": 0}, Config.PROCESS_INFO)

        self.cpu_label = self.create_label({"row": 0, "column": 1}, "CPU: tact 0")
        self.cpu_view = self.create_table({"row": 1, "column": 1, "sticky": tk.EW}, ('Core id', "Current Process"))

        self.finished_processes_label = self.create_label({"row": 2, "column": 1}, "FINISHED PROCESSES")
        self.finished_processes_view = self.create_table({"row": 3, "column": 1, "sticky": tk.EW},
                                                         Config.PROCESS_SHORT_INFO)

        self.menubar = tk.Menu(self)
        self.controls = tk.Menu(self.menubar, tearoff=0)
        self.controls.add_command(label="Start/Stop", command=self.switch_state, accelerator="Ctrl+S")
        self.controls.add_command(label="Next tact", command=self.tick, accelerator="Ctrl+T")
        self.controls.add_command(label="New Process", command=self.generate_process, accelerator="Ctrl+N")
        self.menubar.add_cascade(label="Controls", menu=self.controls)
        self.config(menu=self.menubar)

        self.bind_all("<Control-s>", self.switch_state)
        self.bind_all("<Control-t>", self.tick)
        self.bind_all("<Control-n>", self.generate_process)

        self.show_data()

    def create_button(self, grid, text, command):
        button = ttk.Button(self, text=text, command=command)

        button.grid(**grid)

        return button

    def create_label(self, grid, text):
        label = ttk.Label(self, text=text, font=("Consolas", 16))
        label.grid(**grid)

        return label

    def create_table(self, grid, columns, height=10):
        tree = ttk.Treeview(self, columns=columns, show='headings', height=height)

        for column in columns:
            tree.column(column, width=len(column) * 12, anchor=tk.CENTER)

        # define headings
        for column in columns:
            tree.heading(column, text=column)

        tree.grid(**grid, pady=10, padx=25)

        return tree

    def show_data(self):
        data = self.manager.generate_output()
        self.clear_tables()
        for process in data["process_queue"]:
            self.process_queue.insert('', tk.END, values=process)

        for process in data["rejection_queue"]:
            self.rejection_queue.insert('', tk.END, values=process)

        for process in data["finished_processes"]:
            self.finished_processes_view.insert('', tk.END, values=process)

        for core in data["cpu"]:
            self.cpu_view.insert('', tk.END, values=core)

    def clear_tables(self):
        self.process_queue.delete(*self.process_queue.get_children())
        self.rejection_queue.delete(*self.rejection_queue.get_children())
        self.finished_processes_view.delete(*self.finished_processes_view.get_children())
        self.cpu_view.delete(*self.cpu_view.get_children())

    def tick(self, event=None):
        self.manager.do_work()
        self.show_data()

    def generate_process(self, event=None):
        self.manager.generate_process()
        self.show_data()

    def switch_state(self, event=None):
        self.running = not self.running

    def autorun(self):
        if self.running:
            self.tick()


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()

import tkinter as tk
from tkinter import ttk
from hacker_tools.tools import Manager, config


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.running = False
        self.interval = 1024

        self.manager = Manager(4)
        self.title('HackerTools')
        self.resizable(0, 0)

        #  Define tables and labels
        self.process_queue_label = self.create_label({"row": 0, "column": 0}, "PROCESS QUEUE")
        self.process_queue = self.create_table({"row": 1, "column": 0}, config.PROCESS_INFO)

        self.rejection_queue_label = self.create_label({"row": 2, "column": 0}, "REJECTION QUEUE")
        self.rejection_queue = self.create_table({"row": 3, "column": 0}, config.PROCESS_INFO)

        self.cpu_label = self.create_label({"row": 0, "column": 1}, "CPU: tact 0")
        self.cpu_view = self.create_table({"row": 1, "column": 1, "sticky": tk.EW}, ('Core id', "Current Process"))

        self.finished_processes_label = self.create_label({"row": 2, "column": 1}, "FINISHED PROCESSES")
        self.finished_processes_view = self.create_table({"row": 3, "column": 1, "sticky": tk.EW},
                                                         config.PROCESS_SHORT_INFO)

        #  add menu bar
        self.menubar = tk.Menu(self)
        self.controls = tk.Menu(self.menubar, tearoff=0)

        self.controls.add_command(label="Next tact", command=self.tick, accelerator="Ctrl+T")
        self.controls.add_command(label="New Process", command=self.generate_process, accelerator="Ctrl+N")
        self.menubar.add_cascade(label="Controls", menu=self.controls)

        self.autorun_menu = tk.Menu(self.menubar, tearoff=0)
        self.autorun_menu.add_command(label="Start/Stop", command=self.switch_state, accelerator="Ctrl+S")
        self.autorun_menu.add_command(label="Speed up", command=self.decrease_interval, accelerator="Ctrl+Up")
        self.autorun_menu.add_command(label="Slow down", command=self.increase_interval, accelerator="Ctrl+Down")
        self.autorun_menu.add_command(label="Default speed", command=self.default_interval, accelerator="Ctrl+Home")
        self.menubar.add_cascade(label="Autorun", menu=self.autorun_menu)

        self.config(menu=self.menubar)
        self.bind_all("<Control-s>", self.switch_state)
        self.bind_all("<Control-t>", self.tick)
        self.bind_all("<Control-n>", self.generate_process)
        self.bind_all("<Control-Up>", self.decrease_interval)
        self.bind_all("<Control-Home>", self.default_interval)
        self.bind_all("<Control-Down>", self.increase_interval)

        self.show_data()
        self.autorun()

    def default_interval(self, event=None):
        self.interval = 1024

    def decrease_interval(self, event=None):
        self.interval = self.interval // 2 if self.interval > 16 else 16

    def increase_interval(self, event=None):
        self.interval = self.interval * 2 if self.interval < 16384 else 16384

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

        self.cpu_label["text"] = f"CPU: tact {data['current_tact']}"
        self.process_queue_label["text"] = f"PROCESS QUEUE: {data['process_len']}"
        self.rejection_queue_label["text"] = f"REJECTION QUEUE: {data['rejection_len']}"
        self.finished_processes_label["text"] = f"FINISHED PROCESSES: {data['finished_len']}"

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
        self.after(self.interval, self.autorun)


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from hacker_tools.Core import Manager, Clock


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.manager = Manager(4)
        self.title('HackerTools')
        self.geometry('800x400')

        self.process_queue = self.create_tree_widget({"row": 0, "column": 0, "sticky": tk.NSEW},
                                                     ('Name', 'Process id', 'State', "Progress", "Address"))
        self.rejection_queue = self.create_tree_widget({"row": 1, "column": 0, "sticky": tk.NSEW},
                                                       ('Name', 'Process id', 'State', "Progress", "Address"))
        self.finished_processes = self.create_tree_widget({"row": 2, "column": 0, "sticky": tk.NSEW},
                                                          ('Process_id', 'Name', 'State'))
        self.next_tick_btn = self.create_button({"row": 0, "column": 1, "sticky": tk.NSEW}, "Next tact", self.tick)
        self.generate_process = self.create_button({"row": 1, "column": 1, "sticky": tk.NSEW}, "New process",
                                                   self.generate_process)

    def create_button(self, grid, text, command):
        button = ttk.Button(self, text=text, command=command)

        button.grid(**grid)

        return button

    def create_tree_widget(self, grid, columns):
        tree = ttk.Treeview(self, columns=columns, show='headings')

        # define headings
        for column in columns:
            tree.heading(column, text=column)

        tree.grid(**grid)

        # add a scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        return tree

    def show_data(self):
        data = self.manager.generate_output()
        self.clear_tables()
        for process in data.pop(0):
            self.process_queue.insert('', tk.END, values=process)

        for process in data.pop(0):
            self.rejection_queue.insert('', tk.END, values=process)

        for process in data.pop(0):
            self.finished_processes.insert('', tk.END, values=process)

    def clear_tables(self):
        self.process_queue.delete(*self.process_queue.get_children())
        self.rejection_queue.delete(*self.rejection_queue.get_children())
        self.finished_processes.delete(*self.finished_processes.get_children())

    def tick(self):
        self.manager.do_work()
        Clock.increment()
        self.show_data()

    def generate_process(self):
        self.manager.generate_process()
        self.show_data()


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()

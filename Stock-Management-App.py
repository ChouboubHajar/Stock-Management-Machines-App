# import modules
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import csv
import os
import matplotlib.pyplot as plt


class StockApp(tk.Tk):
    FILE_NAME = "machines.csv"
    ALERT_THRESHOLD = 80

    def __init__(self):
        super().__init__()

        self.title(f"Stock Management - {date.today()}")
        self.geometry("800x800")
        self.resizable(False, False)

        self.entries = {}

        self.create_frames()
        self.create_table()
        self.create_entries()
        self.create_buttons()
        self.load_data()

    #Frames -
    def create_frames(self):
        self.frame_table = tk.Frame(self)
        self.frame_table.pack(pady=5)

        self.frame_inputs = tk.Frame(self)
        self.frame_inputs.pack(pady=10)

        self.frame_buttons = tk.Frame(self)
        self.frame_buttons.pack(pady=8)

    # Table 
    def create_table(self):
        columns = ("ID", "Machine", "Duration (h)", "Performance", "State")
        self.table = ttk.Treeview(self.frame_table,columns=columns,show="headings")

        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=140, anchor="center")

        self.table.pack(side="left")

        scrollbar = ttk.Scrollbar(self.frame_table,orient="vertical",command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.table.tag_configure("alert", background="#ffcccc")

    #Entries 
    def create_entries(self):
        labels = [
            ("ID", "id"),
            ("Machine", "machine"),
            ("Duration (h)", "duration"),
            ("Performance", "performance"),
        ]

        for text, key in labels:
            frame = tk.Frame(self.frame_inputs)
            frame.pack(pady=2)

            tk.Label(frame, text=f"{text} :", width=15, anchor="w").pack(side="left")
            entry = tk.Entry(frame, width=25)
            entry.pack(side="left")

            self.entries[key] = entry

    #Buttons
    def create_buttons(self):
        buttons = [
            ("Add", self.add_machine),
            ("Update", self.update_machine),
            ("Delete", self.delete_machine),
            ("Save", self.save_data),
            ("Performance by machine", self.plot_by_machine),
            ("Performance by state", self.plot_by_state),
        ]

        for text, cmd in buttons:
            tk.Button(self.frame_buttons, text=text, command=cmd, width=22)\
                .pack(side="left", padx=3)

    #Other functions
    def clear_entries(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def get_state(self, performance):
        if performance >= self.ALERT_THRESHOLD:
            return "OK"
        return "ALERT"

    def validate_inputs(self):
        try:
            id_ = int(self.entries["id"].get())
            machine = self.entries["machine"].get().strip()
            duration = int(self.entries["duration"].get())
            performance = float(self.entries["performance"].get())

            if machine == "":
                raise ValueError("Machine name empty")

            return id_, machine, duration, performance

        except ValueError:
            messagebox.showerror(
                "Error",
                "Invalid data.\nPlease check ID, duration and performance."
            )
            return None

    def apply_row_color(self, item_id, performance):
        if performance < self.ALERT_THRESHOLD:
            self.table.item(item_id, tags=("alert",))
        else:
            self.table.item(item_id, tags=())

    # Actions 
    def add_machine(self):
        data = self.validate_inputs()
        if data is None:
            return

        id_, machine, duration, performance = data
        state = self.get_state(performance)

        item = self.table.insert("","end",values=(id_, machine, duration, performance, state))

        self.apply_row_color(item, performance)
        self.clear_entries()

    def update_machine(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Warning", "No machine selected")
            return

        data = self.validate_inputs()
        if data is None:
            return

        id_, machine, duration, performance = data
        state = self.get_state(performance)

        self.table.item(
            selected[0],
            values=(id_, machine, duration, performance, state)
        )

        self.apply_row_color(selected[0], performance)
        self.clear_entries()

    def delete_machine(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Warning", "No machine selected")
            return

        self.table.delete(selected[0])

    # Save and Load
    def save_data(self):
        try:
            with open(self.FILE_NAME, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Machine", "Duration", "Performance", "State"])

                for item in self.table.get_children():
                    writer.writerow(self.table.item(item)["values"])

            messagebox.showinfo("Success", "Data saved successfully")

        except IOError:
            messagebox.showerror("Error", "Unable to save file")

    def load_data(self):
        if not os.path.exists(self.FILE_NAME):
            return

        try:
            with open(self.FILE_NAME, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)

                for row in reader:
                    item = self.table.insert("", "end", values=row)
                    self.apply_row_color(item, float(row[3]))

        except Exception:
            messagebox.showerror("Error", "Error while loading data")

    # Plots 
    def plot_by_machine(self):
        machines = []
        performances = []

        for item in self.table.get_children():
            values = self.table.item(item)["values"]
            machines.append(values[1])
            performances.append(values[3])

        if not machines:
            messagebox.showinfo("Info", "No data available")
            return

        plt.bar(machines, performances)
        plt.xlabel("Machine")
        plt.ylabel("Performance")
        plt.title("Performance by machine")
        plt.show()

    def plot_by_state(self):
        states = {"OK": 0, "ALERT": 0}

        for item in self.table.get_children():
            values = self.table.item(item)["values"]
            states[values[4]] += 1

        plt.bar(states.keys(), states.values())
        plt.xlabel("State")
        plt.ylabel("Number of machines")
        plt.title("Machines by state")
        plt.show()


# Launch application
app = StockApp()
app.mainloop()



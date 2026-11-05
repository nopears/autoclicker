import tkinter as tk
from tkinter import messagebox

import pyautogui
from pynput import keyboard

from clicker import AutoClicker


HOTKEY = "<f8>"
HOTKEY_NAME = "F8"


class CoordinatePicker:
    def __init__(self, root, on_log):
        self.root = root
        self.on_log = on_log
        self.frames = []
        self.entries = []
        self.active = 0
        self.listener = None

    def add(self, frame, x_entry, y_entry):
        index = len(self.frames)
        self.frames.append(frame)
        self.entries.append((x_entry, y_entry))
        self._bind(frame, index)
        self._mark()

    def start(self):
        self.listener = keyboard.GlobalHotKeys({HOTKEY: self.capture})
        self.listener.start()
        self.listener.wait()
        return getattr(self.listener, "IS_TRUSTED", True)

    def stop(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def select(self, index):
        self.active = index
        self._mark()

    def capture(self):
        x, y = pyautogui.position()
        index = self.active

        def apply():
            x_entry, y_entry = self.entries[index]
            x_entry.delete(0, tk.END)
            x_entry.insert(0, str(x))
            y_entry.delete(0, tk.END)
            y_entry.insert(0, str(y))
            self.on_log(f"Действие {index + 1}: {x}, {y}")

        self.root.after(0, apply)

    def _bind(self, widget, index):
        widget.bind("<Button-1>", lambda _event, i=index: self.select(i), add="+")
        widget.bind("<FocusIn>", lambda _event, i=index: self.select(i), add="+")
        for child in widget.winfo_children():
            self._bind(child, index)

    def _mark(self):
        for index, frame in enumerate(self.frames):
            marker = f"  ·  {HOTKEY_NAME}" if index == self.active else ""
            frame.config(text=f"Действие {index + 1}{marker}")


root = tk.Tk()
root.title("AutoClicker")
root.geometry("420x470")
root.resizable(False, False)

clicker = AutoClicker(root)


def log(message):
    status_label.config(text=message)
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)


picker = CoordinatePicker(root, log)


def add_action(number):
    frame = tk.LabelFrame(root, text=f"Действие {number}", padx=10, pady=10)
    frame.pack(fill="x", padx=15, pady=10)

    tk.Label(frame, text="Интервал (минуты):").grid(row=0, column=0, sticky="w")

    interval = tk.Entry(frame, width=10)
    interval.insert(0, "1")
    interval.grid(row=0, column=1, padx=5)

    tk.Label(frame, text="X:").grid(row=1, column=0, sticky="w")
    x_entry = tk.Entry(frame, width=10)
    x_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame, text="Y:").grid(row=2, column=0, sticky="w")
    y_entry = tk.Entry(frame, width=10)
    y_entry.grid(row=2, column=1, padx=5)

    picker.add(frame, x_entry, y_entry)
    return interval, x_entry, y_entry


def start():
    try:
        interval1 = float(interval1_entry.get().replace(",", "."))
        x1 = int(x1_entry.get())
        y1 = int(y1_entry.get())

        interval2 = float(interval2_entry.get().replace(",", "."))
        x2 = int(x2_entry.get())
        y2 = int(y2_entry.get())

        if interval1 <= 0 or interval2 <= 0:
            raise ValueError("Интервалы должны быть больше нуля")

        if not all(map(lambda v: v >= 0, [x1, y1, x2, y2])):
            raise ValueError("Координаты не могут быть отрицательными")

        clicker.start(interval1, x1, y1, interval2, x2, y2)

    except ValueError as error:
        messagebox.showerror("Ошибка ввода", str(error) or "Проверьте введённые данные")


def stop():
    clicker.stop()


def on_close():
    picker.stop()
    clicker.stop()
    root.destroy()


tk.Label(root, text="AutoClicker", font=("Arial", 20, "bold")).pack(pady=10)
tk.Label(root, text="F8 — координаты под курсором", fg="#555555").pack()

interval1_entry, x1_entry, y1_entry = add_action(1)
interval2_entry, x2_entry, y2_entry = add_action(2)

buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons,
    text="ЗАПУСТИТЬ",
    command=start,
    bg="#4CAF50",
    fg="#202020",
    activeforeground="#202020",
    width=15,
    height=2,
).pack(side="left", padx=5)

tk.Button(
    buttons,
    text="ОСТАНОВИТЬ",
    command=stop,
    bg="#E53935",
    fg="#202020",
    activeforeground="#202020",
    width=15,
    height=2,
).pack(side="left", padx=5)

status_label = tk.Label(root, text="Остановлен", font=("Arial", 10))
status_label.pack(pady=5)

log_text = tk.Text(root, height=5, width=48)
log_text.pack(padx=10, pady=5)

try:
    hotkey_trusted = picker.start()
except Exception as error:
    messagebox.showerror("Хоткей", f"Не удалось включить {HOTKEY_NAME}: {error}")
    hotkey_trusted = False

if not hotkey_trusted:
    messagebox.showwarning(
        "Хоткей",
        "Разрешите доступ для Python в разделе «Универсальный доступ», иначе F8 не сработает.",
    )

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

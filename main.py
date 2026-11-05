import tkinter as tk
from tkinter import messagebox

import pyautogui
from pynput import keyboard

from clicker import AutoClicker


CAPTURE_HOTKEY = "<f8>"
CAPTURE_NAME = "F8"
START_HOTKEY = "<f6>"
STOP_HOTKEY = "<f7>"


class GlobalHotkeys:
    def __init__(self):
        self.bindings = {}
        self.listener = None

    def add(self, key, callback):
        self.bindings[key] = callback

    def start(self):
        self.listener = keyboard.GlobalHotKeys(dict(self.bindings))
        self.listener.start()
        self.listener.wait()
        return getattr(self.listener, "IS_TRUSTED", True)

    def stop(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None


class CoordinatePicker:
    def __init__(self, root, on_log):
        self.root = root
        self.on_log = on_log
        self.frames = []
        self.entries = []
        self.active = 0

    def add(self, frame, x_entry, y_entry):
        index = len(self.frames)
        self.frames.append(frame)
        self.entries.append((x_entry, y_entry))
        self._bind(frame, index)
        self._mark()

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
            marker = f"  ·  {CAPTURE_NAME}" if index == self.active else ""
            frame.config(text=f"Действие {index + 1}{marker}")


root = tk.Tk()
root.title("AutoClicker")
root.geometry("420x900")
root.resizable(False, False)

clicker = AutoClicker(root)
hotkeys = GlobalHotkeys()


def log(message):
    status_label.config(text=message)
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)


clicker.on_log = log
picker = CoordinatePicker(root, log)
actions = []


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
    actions.append((interval, x_entry, y_entry))


def parse_action(number, interval_entry, x_entry, y_entry):
    x_text = x_entry.get().strip()
    y_text = y_entry.get().strip()
    if not x_text or not y_text:
        return None

    interval = float(interval_entry.get().replace(",", "."))
    x = int(x_text)
    y = int(y_text)

    if interval <= 0:
        raise ValueError(f"Действие {number}: интервал должен быть больше нуля")

    if x < 0 or y < 0:
        raise ValueError(f"Действие {number}: координаты не могут быть отрицательными")

    return interval, x, y, f"Действие {number}"


def start():
    try:
        planned = []
        for number, entries in enumerate(actions, start=1):
            action = parse_action(number, *entries)
            if action is not None:
                planned.append(action)
    except ValueError as error:
        messagebox.showerror("Ошибка ввода", str(error) or "Проверьте введённые данные")
        return

    clicker.start(planned)


def stop():
    clicker.stop()


def on_close():
    hotkeys.stop()
    clicker.stop()
    root.destroy()


tk.Label(root, text="AutoClicker", font=("Arial", 20, "bold")).pack(pady=10)
tk.Label(
    root,
    text="F6 — запуск    F7 — остановка    F8 — координаты под курсором",
    fg="#555555",
    wraplength=390,
    justify="center",
).pack()

for number in range(1, 5):
    add_action(number)

buttons = tk.Frame(root)
buttons.pack(pady=10)

tk.Button(
    buttons,
    text="ЗАПУСТИТЬ\nF6",
    command=start,
    bg="#4CAF50",
    fg="#202020",
    activeforeground="#202020",
    width=15,
    height=2,
).pack(side="left", padx=5)

tk.Button(
    buttons,
    text="ОСТАНОВИТЬ\nF7",
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

hotkeys.add(START_HOTKEY, lambda: root.after(0, start))
hotkeys.add(STOP_HOTKEY, lambda: root.after(0, stop))
hotkeys.add(CAPTURE_HOTKEY, picker.capture)

try:
    hotkey_trusted = hotkeys.start()
except Exception as error:
    messagebox.showerror("Хоткей", f"Не удалось включить хоткеи: {error}")
    hotkey_trusted = False

if not hotkey_trusted:
    messagebox.showwarning(
        "Хоткей",
        "Разрешите доступ для Python в разделе «Универсальный доступ», иначе хоткеи не сработают.",
    )

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

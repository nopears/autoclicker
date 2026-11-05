import tkinter as tk
import pyautogui


class AutoClicker:
    def __init__(self, root, on_log=None):
        self.root = root
        self.on_log = on_log

        self.running = False
        self.timer_ids = []

    def log(self, message):
        if self.on_log:
            self.on_log(message)

    def start(self, interval1, x1, y1, interval2, x2, y2):
        if self.running:
            return

        self.running = True

        self.schedule_click(interval1, x1, y1, "Действие 1")
        self.schedule_click(interval2, x2, y2, "Действие 2")

        self.log("Автокликер запущен")

    def schedule_click(self, interval, x, y, name):
        def execute():
            if not self.running:
                return

            try:
                pyautogui.click(x=int(x), y=int(y))
                self.log(f"{name}: клик ({x}, {y})")
            except Exception as error:
                self.log(f"Ошибка {name}: {error}")
                self.stop()
                return

            if self.running:
                timer_id = self.root.after(int(interval * 60 * 1000), execute)
                self.timer_ids.append(timer_id)

        timer_id = self.root.after(int(interval * 60 * 1000), execute)
        self.timer_ids.append(timer_id)

    def stop(self):
        if not self.running:
            return

        self.running = False

        for timer_id in self.timer_ids:
            try:
                self.root.after_cancel(timer_id)
            except tk.TclError:
                pass

        self.timer_ids.clear()
        self.log("Автокликер остановлен")

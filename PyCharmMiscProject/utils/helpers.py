# utils/helpers.py
import tkinter as tk
from tkinter import ttk, messagebox


def simple_input_dialog(parent, title, prompt):
    """简单的输入对话框"""
    result = [None]

    def ok():
        result[0] = entry.get().strip()
        dialog.destroy()

    def cancel():
        result[0] = None
        dialog.destroy()

    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("300x100")
    dialog.transient(parent)
    dialog.grab_set()

    frame = ttk.Frame(dialog, padding="10")
    frame.grid(row=0, column=0, sticky=(ttk.W, ttk.E, ttk.N, ttk.S))

    ttk.Label(frame, text=prompt).grid(row=0, column=0, sticky=ttk.W, pady=(0, 5))
    entry = ttk.Entry(frame, width=30)
    entry.grid(row=1, column=0, sticky=(ttk.W, ttk.E), pady=(0, 10))
    entry.focus()

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=2, column=0)

    ttk.Button(button_frame, text="确定", command=ok).pack(side=ttk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="取消", command=cancel).pack(side=ttk.LEFT)

    # 绑定回车键
    entry.bind('<Return>', lambda e: ok())

    dialog.wait_window()
    return result[0]
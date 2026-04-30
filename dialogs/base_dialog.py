# dialogs/base_dialog.py
import tkinter as tk
from tkinter import ttk


class BaseDialog:
    """对话框基类，自动居中"""

    def __init__(self, parent, title, size="400x300"):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(size)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 先更新窗口，再居中
        self.dialog.update_idletasks()
        self.center_window()

        self.setup_ui()

        # 禁止改变窗口大小（可选，可根据需要注释）
        # self.dialog.resizable(False, False)

    def center_window(self):
        """完美居中"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def setup_ui(self):
        pass

    def simple_input_dialog(self, parent, title, prompt):
        """简单的输入对话框（也居中）"""
        result = [None]

        def ok():
            result[0] = entry.get().strip()
            dialog.destroy()

        def cancel():
            result[0] = None
            dialog.destroy()

        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("300x120")
        dialog.transient(parent)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=prompt).pack(anchor=tk.W, pady=(0, 5))
        entry = ttk.Entry(frame, width=30)
        entry.pack(fill=tk.X, pady=(0, 10))
        entry.focus()

        btn_frame = ttk.Frame(frame)
        btn_frame.pack()
        ttk.Button(btn_frame, text="确定", command=ok).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=cancel).pack(side=tk.LEFT)

        entry.bind('<Return>', lambda e: ok())
        dialog.wait_window()
        return result[0]
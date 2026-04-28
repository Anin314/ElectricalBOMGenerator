# dialogs/base_dialog.py
import tkinter as tk
from tkinter import ttk


class BaseDialog:
    """对话框基类"""

    def __init__(self, parent, title, size="400x300"):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(size)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.center_window()

        # 设置UI
        self.setup_ui()

    def center_window(self):
        """居中显示窗口"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

    def setup_ui(self):
        """设置UI界面 - 子类需重写此方法"""
        pass

    def simple_input_dialog(self, parent, title, prompt):
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
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(frame, text=prompt).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        entry = ttk.Entry(frame, width=30)
        entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        entry.focus()

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0)

        ttk.Button(button_frame, text="确定", command=ok).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=cancel).pack(side=tk.LEFT)

        # 绑定回车键
        entry.bind('<Return>', lambda e: ok())

        dialog.wait_window()
        return result[0]
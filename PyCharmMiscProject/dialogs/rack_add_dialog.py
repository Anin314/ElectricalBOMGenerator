# dialogs/rack_add_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from dialogs.base_dialog import BaseDialog


class AddRackDialog(BaseDialog):
    """新建机架对话框"""

    def __init__(self, parent):
        self.result = None
        super().__init__(parent, "新建机架", "300x120")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="机架名称:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        entry = ttk.Entry(main_frame, textvariable=self.name_var, width=20)
        entry.grid(row=0, column=1, padx=(5,0))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

    def confirm(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "机架名称不能为空")
            return
        self.result = name
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result
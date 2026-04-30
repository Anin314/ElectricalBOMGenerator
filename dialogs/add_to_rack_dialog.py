# dialogs/add_to_rack_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from dialogs.base_dialog import BaseDialog


class AddToRackDialog(BaseDialog):
    """添加到机架对话框（只输入数量）"""

    def __init__(self, parent, item_type, item_name, item_id):
        self.item_type = item_type
        self.item_name = item_name
        self.item_id = item_id
        self.result = None  # (quantity,)
        super().__init__(parent, f"添加到机架 - {item_name}", "300x150")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=f"条目: {self.item_name}").pack(anchor=tk.W, pady=(0, 10))

        qty_frame = ttk.Frame(main_frame)
        qty_frame.pack(fill=tk.X, pady=5)
        ttk.Label(qty_frame, text="数量:").pack(side=tk.LEFT)
        self.qty_var = tk.IntVar(value=1)
        ttk.Spinbox(qty_frame, from_=1, to=9999, textvariable=self.qty_var, width=10).pack(side=tk.LEFT, padx=(5, 0))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

    def confirm(self):
        qty = self.qty_var.get()
        if qty <= 0:
            messagebox.showerror("错误", "数量必须大于0")
            return
        self.result = qty
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result
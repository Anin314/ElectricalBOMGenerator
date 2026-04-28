# dialogs/quantity_assign_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from dialogs.base_dialog import BaseDialog


class QuantityAssignDialog(BaseDialog):
    """为电气元件分配预制板和零散件数量"""

    def __init__(self, parent, element_name, part_number):
        self.element_name = element_name
        self.part_number = part_number
        self.result = None   # (prefab_qty, spare_qty)
        super().__init__(parent, f"分配数量 - {element_name}", "400x200")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text=f"元件: {self.element_name} ({self.part_number})",
                  font=("Arial", 9, "bold")).pack(anchor=tk.W, pady=(0, 15))

        frame_prefab = ttk.Frame(main_frame)
        frame_prefab.pack(fill=tk.X, pady=5)
        ttk.Label(frame_prefab, text="预制板数量:").pack(side=tk.LEFT)
        self.prefab_var = tk.IntVar(value=0)
        ttk.Spinbox(frame_prefab, from_=0, to=9999, textvariable=self.prefab_var, width=10).pack(side=tk.LEFT, padx=(10, 0))

        frame_spare = ttk.Frame(main_frame)
        frame_spare.pack(fill=tk.X, pady=5)
        ttk.Label(frame_spare, text="零散件数量:").pack(side=tk.LEFT)
        self.spare_var = tk.IntVar(value=0)
        ttk.Spinbox(frame_spare, from_=0, to=9999, textvariable=self.spare_var, width=10).pack(side=tk.LEFT, padx=(10, 0))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.confirm())

    def confirm(self):
        prefab = self.prefab_var.get()
        spare = self.spare_var.get()
        if prefab == 0 and spare == 0:
            messagebox.showerror("错误", "预制板数量和零散件数量不能同时为0")
            return
        self.result = (prefab, spare)
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result
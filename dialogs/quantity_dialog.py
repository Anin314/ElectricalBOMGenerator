# dialogs/quantity_dialog.py
from dialogs.base_dialog import BaseDialog
from tkinter import ttk, messagebox
import tkinter as tk


class QuantityDialog(BaseDialog):
    """数量输入对话框"""

    def __init__(self, parent, component_name):
        self.component_name = component_name
        self.quantity = 0
        super().__init__(parent, f"设置数量 - {component_name}", "300x120")

    def setup_ui(self):
        """设置UI界面"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 提示信息
        ttk.Label(main_frame, text=f"组件: {self.component_name}").grid(row=0, column=0, columnspan=2, sticky=tk.W,
                                                                        pady=(0, 10))

        # 数量输入
        ttk.Label(main_frame, text="数量:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.quantity_var = tk.IntVar(value=1)
        quantity_spinbox = ttk.Spinbox(main_frame, from_=0, to=999999, textvariable=self.quantity_var, width=10)
        quantity_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))

        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        # 配置权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def confirm(self):
        """确认"""
        try:
            qty = int(self.quantity_var.get())
            if qty < 0:
                messagebox.showerror("错误", "数量不能小于0")
                return
            self.quantity = qty
            self.dialog.destroy()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def cancel(self):
        """取消"""
        self.quantity = 0
        self.dialog.destroy()

    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.quantity
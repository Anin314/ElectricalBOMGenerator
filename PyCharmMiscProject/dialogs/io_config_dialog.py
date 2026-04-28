# dialogs/io_config_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from dialogs.base_dialog import BaseDialog


class IOConfigDialog(BaseDialog):
    def __init__(self, parent, io_data=None):
        self.io_data = io_data or {"inputs": [], "outputs": []}
        self.result = None
        super().__init__(parent, "IO点配置", "700x500")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 使用PanedWindow可调节左右比例
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # 输入点
        input_frame = ttk.LabelFrame(paned, text="输入点", padding="5")
        paned.add(input_frame, weight=1)
        self.input_listbox = tk.Listbox(input_frame, height=12)
        self.input_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scroll = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.input_listbox.yview)
        self.input_listbox.configure(yscrollcommand=input_scroll.set)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        input_btn_frame = ttk.Frame(input_frame)
        input_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(input_btn_frame, text="添加", command=lambda: self.add_point("input")).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="编辑", command=lambda: self.edit_point("input")).pack(side=tk.LEFT, padx=2)
        ttk.Button(input_btn_frame, text="删除", command=lambda: self.delete_point("input")).pack(side=tk.LEFT, padx=2)

        # 输出点
        output_frame = ttk.LabelFrame(paned, text="输出点", padding="5")
        paned.add(output_frame, weight=1)
        self.output_listbox = tk.Listbox(output_frame, height=12)
        self.output_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        output_scroll = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_listbox.yview)
        self.output_listbox.configure(yscrollcommand=output_scroll.set)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        output_btn_frame = ttk.Frame(output_frame)
        output_btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(output_btn_frame, text="添加", command=lambda: self.add_point("output")).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_btn_frame, text="编辑", command=lambda: self.edit_point("output")).pack(side=tk.LEFT, padx=2)
        ttk.Button(output_btn_frame, text="删除", command=lambda: self.delete_point("output")).pack(side=tk.LEFT, padx=2)

        # 填充数据
        for name in self.io_data["inputs"]:
            self.input_listbox.insert(tk.END, name)
        for name in self.io_data["outputs"]:
            self.output_listbox.insert(tk.END, name)

        # 底部按钮
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)
        ttk.Button(bottom_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

    def add_point(self, point_type):
        name = self._get_point_name()
        if name:
            if point_type == "input":
                self.input_listbox.insert(tk.END, name)
            else:
                self.output_listbox.insert(tk.END, name)

    def edit_point(self, point_type):
        listbox = self.input_listbox if point_type == "input" else self.output_listbox
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的点")
            return
        old_name = listbox.get(selection[0])
        new_name = self._get_point_name(old_name)
        if new_name:
            listbox.delete(selection[0])
            listbox.insert(selection[0], new_name)

    def delete_point(self, point_type):
        listbox = self.input_listbox if point_type == "input" else self.output_listbox
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的点")
            return
        listbox.delete(selection[0])

    def _get_point_name(self, initial=""):
        dialog = tk.Toplevel(self.dialog)
        dialog.title("点名称")
        dialog.geometry("300x100")
        dialog.transient(self.dialog)
        dialog.grab_set()
        # 居中
        dialog.update_idletasks()
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        label = ttk.Label(dialog, text="请输入点名称:")
        label.pack(pady=10)
        entry = ttk.Entry(dialog, width=30)
        entry.insert(0, initial)
        entry.pack(pady=5)
        result = [None]

        def ok():
            val = entry.get().strip()
            if val:
                result[0] = val
                dialog.destroy()
            else:
                messagebox.showerror("错误", "名称不能为空")

        ttk.Button(dialog, text="确定", command=ok).pack(pady=5)
        dialog.wait_window()
        return result[0]

    def confirm(self):
        self.result = {
            "inputs": list(self.input_listbox.get(0, tk.END)),
            "outputs": list(self.output_listbox.get(0, tk.END))
        }
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result
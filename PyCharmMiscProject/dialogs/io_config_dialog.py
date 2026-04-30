# dialogs/io_config_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from dialogs.base_dialog import BaseDialog


class IOConfigDialog(BaseDialog):
    def __init__(self, parent, io_data=None):
        self.io_data = io_data or {"inputs": [], "outputs": []}
        self.result = None
        super().__init__(parent, "IO点配置", "800x550")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 快速生成区域
        gen_frame = ttk.LabelFrame(main_frame, text="快速生成", padding="5")
        gen_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(gen_frame, text="输入点数量:").grid(row=0, column=0, padx=5, pady=5)
        self.input_count = tk.IntVar(value=0)
        ttk.Spinbox(gen_frame, from_=0, to=100, textvariable=self.input_count, width=5).grid(row=0, column=1, padx=5)

        ttk.Label(gen_frame, text="输出点数量:").grid(row=0, column=2, padx=5, pady=5)
        self.output_count = tk.IntVar(value=0)
        ttk.Spinbox(gen_frame, from_=0, to=100, textvariable=self.output_count, width=5).grid(row=0, column=3, padx=5)

        ttk.Button(gen_frame, text="生成默认点", command=self.generate_default_points).grid(row=0, column=4, padx=10)

        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # 输入点
        input_frame = ttk.LabelFrame(paned, text="输入点列表", padding="5")
        paned.add(input_frame, weight=1)
        self.input_listbox = tk.Listbox(input_frame, height=12)
        self.input_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_in = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.input_listbox.yview)
        self.input_listbox.configure(yscrollcommand=sc_in.set)
        sc_in.pack(side=tk.RIGHT, fill=tk.Y)
        btn_in_frame = ttk.Frame(input_frame)
        btn_in_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_in_frame, text="添加", command=lambda: self.add_point("input")).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_in_frame, text="删除", command=lambda: self.delete_point("input")).pack(side=tk.LEFT, padx=2)
        self.input_listbox.bind('<Double-1>', lambda e: self.edit_point("input"))

        # 输出点
        output_frame = ttk.LabelFrame(paned, text="输出点列表", padding="5")
        paned.add(output_frame, weight=1)
        self.output_listbox = tk.Listbox(output_frame, height=12)
        self.output_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_out = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_listbox.yview)
        self.output_listbox.configure(yscrollcommand=sc_out.set)
        sc_out.pack(side=tk.RIGHT, fill=tk.Y)
        btn_out_frame = ttk.Frame(output_frame)
        btn_out_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_out_frame, text="添加", command=lambda: self.add_point("output")).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_out_frame, text="删除", command=lambda: self.delete_point("output")).pack(side=tk.LEFT, padx=2)
        self.output_listbox.bind('<Double-1>', lambda e: self.edit_point("output"))

        # 加载已有数据
        for name in self.io_data.get("inputs", []):
            self.input_listbox.insert(tk.END, name)
        for name in self.io_data.get("outputs", []):
            self.output_listbox.insert(tk.END, name)

        # 底部按钮
        bottom = ttk.Frame(main_frame)
        bottom.pack(fill=tk.X, pady=10)
        ttk.Button(bottom, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom, text="取消", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def generate_default_points(self):
        in_cnt = self.input_count.get()
        out_cnt = self.output_count.get()
        if in_cnt > 0:
            current_inputs = list(self.input_listbox.get(0, tk.END))
            for i in range(1, in_cnt + 1):
                name = f"输入点{i}"
                if name not in current_inputs:
                    current_inputs.append(name)
            self.input_listbox.delete(0, tk.END)
            for name in current_inputs:
                self.input_listbox.insert(tk.END, name)
        if out_cnt > 0:
            current_outputs = list(self.output_listbox.get(0, tk.END))
            for i in range(1, out_cnt + 1):
                name = f"输出点{i}"
                if name not in current_outputs:
                    current_outputs.append(name)
            self.output_listbox.delete(0, tk.END)
            for name in current_outputs:
                self.output_listbox.insert(tk.END, name)

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
        dialog.geometry("300x120")
        dialog.transient(self.dialog)
        dialog.grab_set()
        dialog.update_idletasks()
        x = self.dialog.winfo_x() + (self.dialog.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.dialog.winfo_y() + (self.dialog.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        ttk.Label(dialog, text="请输入点名称:").pack(pady=10)
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
# dialogs/component_lib_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from dialogs.base_dialog import BaseDialog
from dialogs.component_dialog import ComponentDialog
from models.component_db import ComponentDatabase


class ComponentLibraryDialog(BaseDialog):
    """组件库管理对话框"""

    def __init__(self, parent, component_db):
        self.component_db = component_db
        self.search_term = ""
        super().__init__(parent, "组件库管理", "900x600")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 搜索框
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=(5,0))

        # 操作按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0,10))
        ttk.Button(btn_frame, text="添加组件", command=self.add_component).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(btn_frame, text="编辑选中", command=self.edit_component).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(btn_frame, text="删除选中", command=self.delete_component).pack(side=tk.LEFT)

        # 组件列表
        self.tree = ttk.Treeview(main_frame, columns=("name",), show="headings", height=15)
        self.tree.heading("name", text="组件名称")
        self.tree.column("name", width=200)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))

        # 关闭按钮
        close_btn = ttk.Button(main_frame, text="关闭", command=self.dialog.destroy)
        close_btn.grid(row=3, column=0, pady=10)

        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.refresh_list()

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        components = self.component_db.get_all_components(search_term=self.search_term)
        for comp in components:
            self.tree.insert("", tk.END, values=(comp["name"],))

    def on_search(self, *args):
        self.search_term = self.search_var.get()
        self.refresh_list()

    def add_component(self):
        dialog = ComponentDialog(self.dialog, self.component_db, mode='add')
        result = dialog.show()
        if result:
            self.refresh_list()
            messagebox.showinfo("成功", f"组件 '{result}' 添加成功")

    def edit_component(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的组件")
            return
        name = self.tree.item(selection[0])["values"][0]
        dialog = ComponentDialog(self.dialog, self.component_db, mode='edit', component_name=name)
        result = dialog.show()
        if result:
            self.refresh_list()
            messagebox.showinfo("成功", f"组件 '{result}' 编辑成功")

    def delete_component(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的组件")
            return
        name = self.tree.item(selection[0])["values"][0]
        if messagebox.askyesno("确认", f"确定要删除组件 '{name}' 吗？"):
            self.component_db.delete_component(name)
            self.refresh_list()
            messagebox.showinfo("成功", f"组件 '{name}' 已删除")
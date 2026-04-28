# views/main_view.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models.component_db import ComponentDatabase
from models.electrical_lib import ElectricalLibrary
from models.database import Database
from dialogs.component_dialog import ComponentDialog
from dialogs.electrical_lib_dialog import ElectricalLibraryDialog
from dialogs.quantity_dialog import QuantityDialog


class MainView:
    """主界面视图"""

    def __init__(self, root):
        self.root = root
        self.root.title("电气BOM管理系统")
        self.root.geometry("1200x700")

        # 初始化数据管理器
        self.db = Database()
        self.component_db = ComponentDatabase()
        self.electrical_lib = ElectricalLibrary()

        self.current_project = {
            "name": "新项目",
            "components": [],
            "created_time": "",
            "modified_time": ""
        }
        self.project_file = ""

        self.setup_ui()
        self.refresh_display()

    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 项目菜单
        project_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="项目", menu=project_menu)
        project_menu.add_command(label="新建项目", command=self.new_project)
        project_menu.add_command(label="打开项目", command=self.open_project)
        project_menu.add_command(label="保存项目", command=self.save_project)
        project_menu.add_separator()
       # project_menu.add_command(label="导出Excel", command=self.export_excel)

        # 组件菜单
        component_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="组件", menu=component_menu)
        component_menu.add_command(label="添加组件", command=self.add_component)
        component_menu.add_command(label="编辑组件", command=self.edit_component)
        component_menu.add_command(label="复制组件", command=self.copy_component)
        component_menu.add_command(label="删除组件", command=self.delete_component)
        component_menu.add_separator()
        component_menu.add_command(label="查看已有组件", command=self.view_components)

        # 电气元件库菜单
        elec_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="电气元件库", menu=elec_menu)
        elec_menu.add_command(label="管理元件库", command=self.manage_library)

        # 项目信息框架
        info_frame = ttk.LabelFrame(main_frame, text="项目信息", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(info_frame, text="项目名称:").grid(row=0, column=0, sticky=tk.W)
        self.project_name_var = tk.StringVar(value=self.current_project["name"])
        ttk.Label(info_frame, textvariable=self.project_name_var).grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # 主要内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 左侧 - 组件选择区域
        left_frame = ttk.LabelFrame(content_frame, text="可用组件", padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.N, tk.S), padx=(0, 5))

        # 搜索框
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_components)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 0))

        # 组件列表
        columns = ("name",)
        self.component_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        self.component_tree.heading("name", text="组件名称")
        self.component_tree.column("name", width=200)

        scrollbar_left = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.component_tree.yview)
        self.component_tree.configure(yscrollcommand=scrollbar_left.set)

        self.component_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_left.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # 组件操作按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=2, column=0, pady=5)

        ttk.Button(button_frame, text="添加到项目", command=self.add_to_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="编辑", command=self.edit_component).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="复制", command=self.copy_component).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除", command=self.delete_component).pack(side=tk.LEFT)

        # 右侧 - 项目BOM区域
        right_frame = ttk.LabelFrame(content_frame, text="项目BOM", padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 项目组件列表
        proj_columns = ("name", "quantity")
        self.project_tree = ttk.Treeview(right_frame, columns=proj_columns, show="headings", height=12)
        self.project_tree.heading("name", text="组件名称")
        self.project_tree.heading("quantity", text="数量")
        self.project_tree.column("name", width=200)
        self.project_tree.column("quantity", width=80)

        scrollbar_right = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=scrollbar_right.set)

        self.project_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_right.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 项目操作按钮
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Button(button_frame, text="从项目移除", command=self.remove_from_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="清空项目", command=self.clear_project).pack(side=tk.LEFT)

        # 生成BOM按钮
        generate_frame = ttk.Frame(main_frame)
        generate_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(generate_frame, text="生成电气BOM", command=self.generate_bom).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(generate_frame, text="导出Excel", command=self.export_excel).pack(side=tk.LEFT)

        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # 绑定事件
        self.component_tree.bind('<Double-1>', lambda e: self.add_to_project())
        self.project_tree.bind('<Double-1>', lambda e: self.remove_from_project())

    def refresh_display(self):
        """刷新显示"""
        # 更新项目名称
        self.project_name_var.set(self.current_project["name"])

        # 填充组件列表
        self.component_tree.delete(*self.component_tree.get_children())
        components = self.component_db.get_all_components()
        for comp in components:
            self.component_tree.insert("", tk.END, values=(comp["name"],))

    def filter_components(self, *args):
        """过滤组件列表"""
        search_term = self.search_var.get()
        self.component_tree.delete(*self.component_tree.get_children())

        components = self.component_db.get_all_components(search_term=search_term)
        for comp in components:
            self.component_tree.insert("", tk.END, values=(comp["name"],))

    def add_to_project(self):
        """添加组件到项目"""
        selection = self.component_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要添加的组件")
            return

        item = self.component_tree.item(selection[0])
        component_name = item["values"][0]

        # 弹出数量输入对话框
        quantity_dialog = QuantityDialog(self.root, component_name)
        quantity = quantity_dialog.show()

        if quantity > 0:
            # 检查是否已存在相同组件
            exists = False
            for comp in self.current_project["components"]:
                if comp["name"] == component_name:
                    comp["quantity"] += quantity
                    exists = True
                    break

            if not exists:
                self.current_project["components"].append({
                    "name": component_name,
                    "quantity": quantity
                })

            self.update_project_display()

    def remove_from_project(self):
        """从项目中移除组件"""
        selection = self.project_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要移除的组件")
            return

        item = self.project_tree.item(selection[0])
        component_name = item["values"][0]

        self.current_project["components"] = [
            comp for comp in self.current_project["components"]
            if comp["name"] != component_name
        ]
        self.update_project_display()

    def update_project_display(self):
        """更新项目显示"""
        self.project_tree.delete(*self.project_tree.get_children())
        for comp in self.current_project["components"]:
            self.project_tree.insert("", tk.END, values=(comp["name"], comp["quantity"]))

    def clear_project(self):
        """清空项目"""
        if messagebox.askyesno("确认", "确定要清空当前项目吗？此操作不可恢复。"):
            self.current_project["components"] = []
            self.update_project_display()

    def new_project(self):
        """新建项目"""
        name = self.simple_input_dialog(self.root, "新建项目", "项目名称:")
        if name:
            self.current_project = {
                "name": name,
                "components": [],
                "created_time": "",
                "modified_time": ""
            }
            self.project_name_var.set(name)

    def open_project(self):
        """打开项目"""
        file_path = filedialog.askopenfilename(
            title="打开项目",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.current_project = json.load(f)
                self.project_file = file_path
                self.project_name_var.set(self.current_project["name"])
                self.update_project_display()
                messagebox.showinfo("成功", "项目加载成功")
            except Exception as e:
                messagebox.showerror("错误", f"项目加载失败: {str(e)}")

    def save_project(self):
        """保存项目"""
        if not self.project_file:
            self.project_file = filedialog.asksaveasfilename(
                title="保存项目",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if not self.project_file:
                return

        try:
            import json
            with open(self.project_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_project, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", "项目保存成功")
        except Exception as e:
            messagebox.showerror("错误", f"项目保存失败: {str(e)}")

    def add_component(self):
        """添加新组件"""
        dialog = ComponentDialog(self.root, self.component_db, mode='add')
        result = dialog.show()
        if result:
            self.refresh_display()
            messagebox.showinfo("成功", f"组件 '{result}' 添加成功")

    def edit_component(self):
        """编辑组件"""
        selection = self.component_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的组件")
            return

        item = self.component_tree.item(selection[0])
        component_name = item["values"][0]

        dialog = ComponentDialog(self.root, self.component_db, mode='edit', component_name=component_name)
        result = dialog.show()
        if result:
            self.refresh_display()
            messagebox.showinfo("成功", f"组件 '{result}' 编辑成功")

    def copy_component(self):
        """复制组件"""
        selection = self.component_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要复制的组件")
            return

        item = self.component_tree.item(selection[0])
        component_name = item["values"][0]

        dialog = ComponentDialog(self.root, self.component_db, mode='copy', component_name=component_name)
        result = dialog.show()
        if result:
            self.refresh_display()
            messagebox.showinfo("成功", f"组件 '{result}' 复制成功")

    def delete_component(self):
        """删除组件"""
        selection = self.component_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的组件")
            return

        item = self.component_tree.item(selection[0])
        component_name = item["values"][0]

        if messagebox.askyesno("确认", f"确定要删除组件 '{component_name}' 吗？"):
            self.component_db.delete_component(component_name)
            self.refresh_display()
            messagebox.showinfo("成功", f"组件 '{component_name}' 删除成功")

    def view_components(self):
        """查看已有组件详情"""
        selection = self.component_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要查看的组件")
            return

        item = self.component_tree.item(selection[0])
        component_name = item["values"][0]

        component_info = self.component_db.get_component(component_name)
        if component_info:
            self.show_component_details(component_name, component_info)

    def manage_library(self):
        """管理电气元件库"""
        dialog = ElectricalLibraryDialog(self.root, self.electrical_lib)
        self.root.wait_window(dialog.dialog)

    def show_component_details(self, name, info):
        """显示组件详细信息"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"组件详情 - {name}")
        detail_window.geometry("1000x500")

        main_frame = ttk.Frame(detail_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 组件基本信息
        ttk.Label(main_frame, text=f"组件名称: {name}").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Label(main_frame, text=f"创建时间: {info['created_time']}").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        ttk.Label(main_frame, text=f"更新时间: {info['updated_time']}").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))

        # 电气材料列表
        ttk.Label(main_frame, text="电气材料清单:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W,
                                                                                     pady=(10, 5))

        columns = ("material", "quantity", "part_number", "specification", "detailed_spec", "notes")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)

        tree.heading("material", text="材料名称")
        tree.heading("quantity", text="数量")
        tree.heading("part_number", text="料号")
        tree.heading("specification", text="规格型号")
        tree.heading("detailed_spec", text="详细规格")
        tree.heading("notes", text="备注")

        tree.column("material", width=120)
        tree.column("quantity", width=60)
        tree.column("part_number", width=100)
        tree.column("specification", width=120)
        tree.column("detailed_spec", width=150)
        tree.column("notes", width=80)

        for part in info["electrical_parts"]:
            tree.insert("", tk.END, values=(
                part["material"],
                part["quantity"],
                part["part_number"],
                part["specification"],
                part["detailed_spec"],
                part["notes"]
            ))

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=4, column=1, sticky=(tk.N, tk.S))

        # 配置权重
        detail_window.columnconfigure(0, weight=1)
        detail_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

    def generate_bom(self):
        """生成电气BOM"""
        if not self.current_project["components"]:
            messagebox.showwarning("警告", "项目为空，无法生成BOM")
            return

        # 创建BOM详情窗口
        bom_window = tk.Toplevel(self.root)
        bom_window.title("电气BOM详情")
        bom_window.geometry("1200x600")

        main_frame = ttk.Frame(bom_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # BOM标题
        ttk.Label(main_frame, text=f"电气BOM - {self.current_project['name']}",
                  font=("Arial", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # BOM表格
        columns = ("component", "part_number", "material", "specification", "quantity", "detailed_spec", "notes",
                   "total_quantity")
        tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=20)

        tree.heading("component", text="组件")
        tree.heading("part_number", text="料号")
        tree.heading("material", text="材料名称")
        tree.heading("specification", text="规格型号")
        tree.heading("quantity", text="单位数量")
        tree.heading("detailed_spec", text="详细规格")
        tree.heading("notes", text="备注")
        tree.heading("total_quantity", text="总数量")

        tree.column("component", width=120)
        tree.column("part_number", width=100)
        tree.column("material", width=120)
        tree.column("specification", width=120)
        tree.column("quantity", width=80)
        tree.column("detailed_spec", width=150)
        tree.column("notes", width=80)
        tree.column("total_quantity", width=80)

        # 填充BOM数据
        for comp in self.current_project["components"]:
            component_name = comp["name"]
            component_quantity = comp["quantity"]

            component_info = self.component_db.get_component(component_name)
            if component_info:
                for part in component_info["electrical_parts"]:
                    # 检查元件是否有替换品
                    actual_part_number = self.electrical_lib.get_replacement_chain(part["part_number"])
                    if actual_part_number:
                        # 获取替换元件的信息
                        replacement_element = self.electrical_lib.get_element(actual_part_number)
                        if replacement_element:
                            part_name = replacement_element["name"]
                            part_spec = replacement_element["specification"]
                        else:
                            part_name = part["material"]
                            part_spec = part["specification"]
                        final_part_number = actual_part_number
                    else:
                        part_name = part["material"]
                        part_spec = part["specification"]
                        final_part_number = part["part_number"]

                    total_qty = part["quantity"] * component_quantity
                    tree.insert("", tk.END, values=(
                        component_name,
                        final_part_number,
                        part_name,
                        part_spec,
                        part["quantity"],
                        part["detailed_spec"],
                        part["notes"],
                        total_qty
                    ))

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        # 导出按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        ttk.Button(button_frame, text="导出Excel",
                   command=lambda: self.export_bom_excel(tree)).pack()

        # 配置权重
        bom_window.columnconfigure(0, weight=1)
        bom_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

    def export_bom_excel(self, tree):
        """导出BOM到Excel"""
        file_path = filedialog.asksaveasfilename(
            title="导出BOM到Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if file_path:
            try:
                import pandas as pd
                # 准备数据
                data = []
                for item in tree.get_children():
                    values = tree.item(item)["values"]
                    data.append({
                        "组件": values[0],
                        "料号": values[1],
                        "材料名称": values[2],
                        "规格型号": values[3],
                        "单位数量": values[4],
                        "详细规格": values[5],
                        "备注": values[6],
                        "总数量": values[7]
                    })

                df = pd.DataFrame(data)
                df = df[["组件", "料号", "材料名称", "规格型号", "单位数量", "详细规格", "备注", "总数量"]]  # 按指定顺序排列
                df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", f"BOM已导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    def export_excel(self):
        """导出项目到Excel"""
        if not self.current_project["components"]:
            messagebox.showwarning("警告", "项目为空，无法导出")
            return

        file_path = filedialog.asksaveasfilename(
            title="导出项目到Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )

        if file_path:
            try:
                import pandas as pd
                # 准备数据
                data = []
                for comp in self.current_project["components"]:
                    data.append({
                        "组件名称": comp["name"],
                        "数量": comp["quantity"]
                    })

                df = pd.DataFrame(data)

                # 添加项目信息
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # 项目信息表
                    info_data = {
                        "项目名称": [self.current_project["name"]],
                        "组件总数": [len(self.current_project["components"])]
                    }
                    info_df = pd.DataFrame(info_data)
                    info_df.to_excel(writer, sheet_name="项目信息", index=False)

                    # 组件列表表
                    df.to_excel(writer, sheet_name="组件列表", index=False)

                messagebox.showinfo("成功", f"项目已导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

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
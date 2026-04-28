# dialogs/component_dialog.py
from dialogs.base_dialog import BaseDialog
from tkinter import ttk, messagebox
import tkinter as tk
from models.component_db import ComponentDatabase
from models.electrical_lib import ElectricalLibrary


class ComponentDialog(BaseDialog):
    """组件管理对话框"""

    def __init__(self, parent, component_db, mode='add', component_name=None):
        self.component_db = component_db
        self.mode = mode  # 'add', 'edit', 'copy'
        self.original_name = component_name if mode in ['edit', 'copy'] else None
        self.result = None
        super().__init__(parent, self._get_title(), "800x500")

    def _get_title(self):
        """根据模式获取标题"""
        titles = {
            'add': '添加新组件',
            'edit': '编辑组件',
            'copy': '复制组件'
        }
        return titles.get(self.mode, '组件管理')

    def setup_ui(self):
        """设置UI界面"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 组件基本信息
        info_frame = ttk.LabelFrame(main_frame, text="组件信息", padding="5")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(info_frame, text="组件名称:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(info_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))

        # 如果是编辑或复制模式，填充原数据
        if self.mode in ['edit', 'copy'] and self.original_name:
            original_comp = self.component_db.get_component(self.original_name)
            if original_comp:
                display_name = f"{original_comp['name']}_副本" if self.mode == 'copy' else original_comp['name']
                self.name_var.set(display_name)

        # 电气材料列表
        material_frame = ttk.LabelFrame(main_frame, text="电气材料清单", padding="5")
        material_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # 材料表格
        columns = ("material", "quantity", "part_number", "specification", "detailed_spec", "notes")
        self.material_tree = ttk.Treeview(material_frame, columns=columns, show="headings", height=10)

        self.material_tree.heading("material", text="材料名称")
        self.material_tree.heading("quantity", text="数量")
        self.material_tree.heading("part_number", text="料号")
        self.material_tree.heading("specification", text="规格型号")
        self.material_tree.heading("detailed_spec", text="详细规格")
        self.material_tree.heading("notes", text="备注")

        self.material_tree.column("material", width=100)
        self.material_tree.column("quantity", width=60)
        self.material_tree.column("part_number", width=80)
        self.material_tree.column("specification", width=100)
        self.material_tree.column("detailed_spec", width=120)
        self.material_tree.column("notes", width=80)

        scrollbar = ttk.Scrollbar(material_frame, orient=tk.VERTICAL, command=self.material_tree.yview)
        self.material_tree.configure(yscrollcommand=scrollbar.set)

        self.material_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 材料操作按钮
        button_frame = ttk.Frame(material_frame)
        button_frame.grid(row=1, column=0, pady=5)

        ttk.Button(button_frame, text="添加材料", command=self.add_material).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="从元件库导入", command=self.import_from_library).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="编辑选中", command=self.edit_material).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除选中", command=self.remove_material).pack(side=tk.LEFT)

        # 确认按钮
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.grid(row=2, column=0, pady=10)

        ttk.Button(confirm_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(confirm_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        # 配置权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        material_frame.columnconfigure(0, weight=1)
        material_frame.rowconfigure(0, weight=1)

        # 如果是编辑或复制模式，加载原有材料
        if self.mode in ['edit', 'copy'] and self.original_name:
            original_comp = self.component_db.get_component(self.original_name)
            if original_comp:
                for part in original_comp["electrical_parts"]:
                    self.material_tree.insert("", tk.END, values=(
                        part["material"],
                        part["quantity"],
                        part["part_number"],
                        part["specification"],
                        part["detailed_spec"],
                        part["notes"]
                    ))

    def add_material(self):
        """添加新材料"""
        dialog = MaterialDialog(self.dialog)
        result = dialog.show()
        if result:
            material, quantity, part_number, spec, detailed_spec, notes = result
            self.material_tree.insert("", tk.END, values=(
                material, quantity, part_number, spec, detailed_spec, notes
            ))

    def import_from_library(self):
        """从电气元件库导入材料"""
        # 创建电气元件库对话框，只允许选择并返回选中的元件
        from dialogs.electrical_lib_dialog import ElectricalLibraryDialog
        library = ElectricalLibrary()

        # 定义一个回调函数来接收选中的元件
        def on_select(selected_elements_with_qty):
            """当从元件库选择完成后调用"""
            for part_number, quantity in selected_elements_with_qty:
                # 获取元件详情
                element = library.get_element(part_number)
                if element:
                    # 检查是否已经存在于材料列表中
                    exists = False
                    for item in self.material_tree.get_children():
                        values = self.material_tree.item(item)["values"]
                        if values[2] == part_number:  # 比较料号
                            exists = True
                            # 更新数量
                            new_quantity = int(values[1]) + quantity
                            self.material_tree.item(item, values=(
                                element["name"], str(new_quantity), part_number,
                                element["specification"], "", ""  # 详细规格和备注暂时为空
                            ))
                            break

                    if not exists:
                        # 添加新的材料条目
                        self.material_tree.insert("", tk.END, values=(
                            element["name"], str(quantity), part_number,
                            element["specification"], "", ""
                        ))

        # 创建电气元件库对话框，设置为选择模式
        dialog = ElectricalLibraryDialog(self.dialog, library, callback_func=on_select, show_search=True)

    def edit_material(self):
        """编辑选中材料"""
        selection = self.material_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的材料")
            return

        item = self.material_tree.item(selection[0])
        dialog = MaterialDialog(self.dialog, item["values"])
        result = dialog.show()
        if result:
            material, quantity, part_number, spec, detailed_spec, notes = result
            self.material_tree.item(selection[0], values=(
                material, quantity, part_number, spec, detailed_spec, notes
            ))

    def remove_material(self):
        """删除选中材料"""
        selection = self.material_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的材料")
            return

        if messagebox.askyesno("确认", "确定要删除选中的材料吗？"):
            self.material_tree.delete(selection[0])

    def confirm(self):
        """确认保存"""
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请填写组件名称")
            return

        # 检查名称是否重复（除了编辑模式下的原名称）
        if self.mode != 'edit' or name != self.original_name:
            if self.component_db.get_component(name):
                messagebox.showerror("错误", f"组件名称 '{name}' 已存在")
                return

        # 收集材料数据
        materials = []
        for item in self.material_tree.get_children():
            values = self.material_tree.item(item)["values"]
            materials.append({
                "material": values[0],
                "quantity": int(values[1]),
                "part_number": values[2],
                "specification": values[3],
                "detailed_spec": values[4],
                "notes": values[5]
            })

        # 保存组件
        success = False
        if self.mode == 'add':
            success = self.component_db.add_component(name, materials)
        elif self.mode == 'edit':
            success = self.component_db.update_component(self.original_name, name, materials)
        elif self.mode == 'copy':
            success = self.component_db.add_component(name, materials)

        if success:
            self.result = name
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "保存组件失败")

    def cancel(self):
        """取消"""
        self.dialog.destroy()

    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result


class ElementDialog(BaseDialog):
    """元件对话框"""

    def __init__(self, parent, element_data=None):
        self.element_data = element_data
        self.result = None
        title = "编辑元件" if element_data else "添加元件"
        super().__init__(parent, title, "400x200")

    def setup_ui(self):
        """设置UI界面"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 物料编码
        ttk.Label(main_frame, text="物料编码:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.part_number_var = tk.StringVar()
        part_number_entry = ttk.Entry(main_frame, textvariable=self.part_number_var, width=30)
        part_number_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # 物料名称
        ttk.Label(main_frame, text="物料名称:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # 规格
        ttk.Label(main_frame, text="规格:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.spec_var = tk.StringVar()
        spec_entry = ttk.Entry(main_frame, textvariable=self.spec_var, width=30)
        spec_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        # 如果是编辑模式，填充原数据
        if self.element_data:
            self.part_number_var.set(self.element_data['part_number'])
            self.name_var.set(self.element_data['name'])
            self.spec_var.set(self.element_data['specification'] or "")
            # 物料编码不能修改
            part_number_entry.config(state='disabled')

        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        # 配置权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def confirm(self):
        """确认"""
        part_number = self.part_number_var.get().strip()
        name = self.name_var.get().strip()
        spec = self.spec_var.get().strip()

        if not part_number or not name:
            messagebox.showerror("错误", "物料编码和物料名称不能为空")
            return

        self.result = (part_number, name, spec)
        self.dialog.destroy()

    def cancel(self):
        """取消"""
        self.dialog.destroy()

    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result


class MaterialDialog(BaseDialog):
    """材料对话框"""

    def __init__(self, parent, material_data=None):
        self.material_data = material_data
        self.result = None
        title = "编辑材料" if material_data else "添加材料"
        super().__init__(parent, title, "500x250")

    def setup_ui(self):
        """设置UI界面"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 材料名称
        ttk.Label(main_frame, text="材料名称:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.material_var = tk.StringVar()
        material_entry = ttk.Entry(main_frame, textvariable=self.material_var, width=30)
        material_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # 数量
        ttk.Label(main_frame, text="数量:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.quantity_var = tk.StringVar()
        quantity_entry = ttk.Entry(main_frame, textvariable=self.quantity_var, width=30)
        quantity_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # 料号
        ttk.Label(main_frame, text="料号:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.part_number_var = tk.StringVar()
        part_number_entry = ttk.Entry(main_frame, textvariable=self.part_number_var, width=30)
        part_number_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # 规格型号
        ttk.Label(main_frame, text="规格型号:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        self.spec_var = tk.StringVar()
        spec_entry = ttk.Entry(main_frame, textvariable=self.spec_var, width=30)
        spec_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # 详细规格
        ttk.Label(main_frame, text="详细规格:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        self.detailed_spec_var = tk.StringVar()
        detailed_spec_entry = ttk.Entry(main_frame, textvariable=self.detailed_spec_var, width=30)
        detailed_spec_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 5))

        # 备注
        ttk.Label(main_frame, text="备注:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        self.notes_var = tk.StringVar()
        notes_entry = ttk.Entry(main_frame, textvariable=self.notes_var, width=30)
        notes_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        # 如果是编辑模式，填充原数据
        if self.material_data:
            self.material_var.set(self.material_data[0])
            self.quantity_var.set(self.material_data[1])
            self.part_number_var.set(self.material_data[2])
            self.spec_var.set(self.material_data[3])
            self.detailed_spec_var.set(self.material_data[4])
            self.notes_var.set(self.material_data[5])

        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        # 配置权重
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def confirm(self):
        """确认"""
        material = self.material_var.get().strip()
        quantity_str = self.quantity_var.get().strip()
        part_number = self.part_number_var.get().strip()
        spec = self.spec_var.get().strip()
        detailed_spec = self.detailed_spec_var.get().strip()
        notes = self.notes_var.get().strip()

        if not material or not quantity_str:
            messagebox.showerror("错误", "材料名称和数量不能为空")
            return

        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                messagebox.showerror("错误", "数量必须大于0")
                return
        except ValueError:
            messagebox.showerror("错误", "数量必须是整数")
            return

        self.result = (material, quantity, part_number, spec, detailed_spec, notes)
        self.dialog.destroy()

    def cancel(self):
        """取消"""
        self.dialog.destroy()

    def show(self):
        """显示对话框并返回结果"""
        self.dialog.wait_window()
        return self.result
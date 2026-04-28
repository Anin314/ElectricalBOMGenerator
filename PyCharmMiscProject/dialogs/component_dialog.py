# dialogs/component_dialog.py
import tkinter as tk
from tkinter import ttk, messagebox
from dialogs.base_dialog import BaseDialog
from dialogs.io_config_dialog import IOConfigDialog
from models.component_db import ComponentDatabase
from models.electrical_lib import ElectricalLibrary


class ComponentDialog(BaseDialog):
    """组件管理对话框，支持预制板/零散件数量和IO点配置"""

    def __init__(self, parent, component_db, mode='add', component_name=None):
        self.component_db = component_db
        self.mode = mode
        self.original_name = component_name if mode in ['edit', 'copy'] else None
        self.result = None
        super().__init__(parent, self._get_title(), "900x500")

    def _get_title(self):
        titles = {'add': '添加新组件', 'edit': '编辑组件', 'copy': '复制组件'}
        return titles.get(self.mode, '组件管理')

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 组件基本信息
        info_frame = ttk.LabelFrame(main_frame, text="组件信息", padding="5")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(info_frame, text="组件名称:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(info_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))

        # IO配置按钮
        self.io_button = ttk.Button(info_frame, text="配置IO点", command=self.configure_io)
        self.io_button.grid(row=0, column=2, padx=(10, 0))
        self.io_data = {"inputs": [], "outputs": []}

        if self.mode in ['edit', 'copy'] and self.original_name:
            original = self.component_db.get_component(self.original_name)
            if original:
                display_name = f"{original['name']}_副本" if self.mode == 'copy' else original['name']
                self.name_var.set(display_name)
                self.io_data = original.get("io_points", {"inputs": [], "outputs": []})

        # 电气材料清单
        material_frame = ttk.LabelFrame(main_frame, text="电气材料清单", padding="5")
        material_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        columns = ("material", "prefab_qty", "spare_qty", "part_number", "specification", "detailed_spec", "notes")
        self.material_tree = ttk.Treeview(material_frame, columns=columns, show="headings", height=10)

        self.material_tree.heading("material", text="材料名称")
        self.material_tree.heading("prefab_qty", text="预制板数量")
        self.material_tree.heading("spare_qty", text="零散件数量")
        self.material_tree.heading("part_number", text="料号")
        self.material_tree.heading("specification", text="规格型号")
        self.material_tree.heading("detailed_spec", text="详细规格")
        self.material_tree.heading("notes", text="备注")

        self.material_tree.column("material", width=100)
        self.material_tree.column("prefab_qty", width=80)
        self.material_tree.column("spare_qty", width=80)
        self.material_tree.column("part_number", width=100)
        self.material_tree.column("specification", width=100)
        self.material_tree.column("detailed_spec", width=120)
        self.material_tree.column("notes", width=80)

        scrollbar = ttk.Scrollbar(material_frame, orient=tk.VERTICAL, command=self.material_tree.yview)
        self.material_tree.configure(yscrollcommand=scrollbar.set)

        self.material_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # ** 关键：绑定双击编辑事件 **
        self.material_tree.bind('<Double-1>', lambda e: self.edit_material())

        button_frame = ttk.Frame(material_frame)
        button_frame.grid(row=1, column=0, pady=5)
        ttk.Button(button_frame, text="添加材料", command=self.add_material).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="从元件库导入", command=self.import_from_library).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="编辑选中", command=self.edit_material).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(button_frame, text="删除选中", command=self.remove_material).pack(side=tk.LEFT)

        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.grid(row=2, column=0, pady=10)
        ttk.Button(confirm_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(confirm_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        material_frame.columnconfigure(0, weight=1)
        material_frame.rowconfigure(0, weight=1)

        if self.mode in ['edit', 'copy'] and self.original_name:
            original = self.component_db.get_component(self.original_name)
            if original:
                for part in original["electrical_parts"]:
                    self.material_tree.insert("", tk.END, values=(
                        part["material"],
                        part["prefab_qty"],
                        part["spare_qty"],
                        part["part_number"],
                        part["specification"],
                        part["detailed_spec"],
                        part["notes"]
                    ))

    def configure_io(self):
        dialog = IOConfigDialog(self.dialog, self.io_data)
        result = dialog.show()
        if result:
            self.io_data = result

    def add_material(self):
        dialog = MaterialDialog(self.dialog)
        result = dialog.show()
        if result:
            self.material_tree.insert("", tk.END, values=result)

    def import_from_library(self):
        from dialogs.electrical_lib_dialog import ElectricalLibraryDialog
        from dialogs.quantity_assign_dialog import QuantityAssignDialog
        library = ElectricalLibrary()

        def on_select(selected_part_numbers):
            # selected_part_numbers 是选中的元件料号列表
            for part_number in selected_part_numbers:
                element = library.get_element(part_number)
                if element:
                    # 弹出数量分配对话框
                    dlg = QuantityAssignDialog(self.dialog, element["name"], part_number)
                    result = dlg.show()
                    if result:
                        prefab_qty, spare_qty = result
                        # 检查是否已存在相同料号
                        exists = False
                        for item in self.material_tree.get_children():
                            values = self.material_tree.item(item)["values"]
                            if values[3] == part_number:
                                new_prefab = int(values[1]) + prefab_qty
                                new_spare = int(values[2]) + spare_qty
                                self.material_tree.item(item, values=(
                                    element["name"], str(new_prefab), str(new_spare),
                                    part_number, element["specification"], "", ""
                                ))
                                exists = True
                                break
                        if not exists:
                            self.material_tree.insert("", tk.END, values=(
                                element["name"], str(prefab_qty), str(spare_qty),
                                part_number, element["specification"], "", ""
                            ))

        dialog = ElectricalLibraryDialog(self.dialog, library, callback_func=on_select, show_search=True)

    def edit_material(self):
        selection = self.material_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的材料")
            return
        item = self.material_tree.item(selection[0])
        dialog = MaterialDialog(self.dialog, item["values"])
        result = dialog.show()
        if result:
            self.material_tree.item(selection[0], values=result)

    def remove_material(self):
        selection = self.material_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的材料")
            return
        if messagebox.askyesno("确认", "确定要删除选中的材料吗？"):
            self.material_tree.delete(selection[0])

    def confirm(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请填写组件名称")
            return

        if self.mode != 'edit' or name != self.original_name:
            if self.component_db.get_component(name):
                messagebox.showerror("错误", f"组件名称 '{name}' 已存在")
                return

        materials = []
        for item in self.material_tree.get_children():
            values = self.material_tree.item(item)["values"]
            materials.append({
                "material": values[0],
                "prefab_qty": int(values[1]),
                "spare_qty": int(values[2]),
                "part_number": values[3],
                "specification": values[4],
                "detailed_spec": values[5],
                "notes": values[6]
            })

        success = False
        if self.mode == 'add':
            success = self.component_db.add_component(name, materials, self.io_data)
        elif self.mode == 'edit':
            success = self.component_db.update_component(self.original_name, name, materials, self.io_data)
        elif self.mode == 'copy':
            success = self.component_db.add_component(name, materials, self.io_data)

        if success:
            self.result = name
            self.dialog.destroy()
        else:
            messagebox.showerror("错误", "保存组件失败")

    def cancel(self):
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result


class MaterialDialog(BaseDialog):
    """材料数量修改对话框，仅显示预制板/零散件数量"""

    def __init__(self, parent, material_data=None):
        self.material_data = material_data  # 元组 (material, prefab, spare, part_number, spec, detailed_spec, notes)
        self.result = None
        title = "修改数量" if material_data else "添加材料"
        super().__init__(parent, title, "350x180")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 预制板数量
        frame_prefab = ttk.Frame(main_frame)
        frame_prefab.pack(fill=tk.X, pady=5)
        ttk.Label(frame_prefab, text="预制板数量:").pack(side=tk.LEFT)
        self.prefab_var = tk.StringVar()
        spin_prefab = ttk.Spinbox(frame_prefab, from_=0, to=9999, textvariable=self.prefab_var, width=10)
        spin_prefab.pack(side=tk.LEFT, padx=(10, 0))

        # 零散件数量
        frame_spare = ttk.Frame(main_frame)
        frame_spare.pack(fill=tk.X, pady=5)
        ttk.Label(frame_spare, text="零散件数量:").pack(side=tk.LEFT)
        self.spare_var = tk.StringVar()
        spin_spare = ttk.Spinbox(frame_spare, from_=0, to=9999, textvariable=self.spare_var, width=10)
        spin_spare.pack(side=tk.LEFT, padx=(10, 0))

        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        ttk.Button(btn_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(btn_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        # 如果已有数据，填充当前数量
        if self.material_data:
            self.prefab_var.set(str(self.material_data[1]))
            self.spare_var.set(str(self.material_data[2]))
        else:
            self.prefab_var.set("0")
            self.spare_var.set("0")

        # 绑定回车键
        self.dialog.bind('<Return>', lambda e: self.confirm())
        spin_prefab.focus_set()

    def confirm(self):
        try:
            prefab = int(self.prefab_var.get())
            spare = int(self.spare_var.get())
            if prefab + spare <= 0:
                messagebox.showerror("错误", "预制板数量和零散件数量不能同时为0")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数")
            return

        # 返回新数量，同时保留其他原始字段（用于更新）
        if self.material_data:
            # 原有数据: (material, old_prefab, old_spare, part_number, spec, detailed_spec, notes)
            # 返回 (material, new_prefab, new_spare, part_number, spec, detailed_spec, notes)
            self.result = (
                self.material_data[0], prefab, spare,
                self.material_data[3], self.material_data[4],
                self.material_data[5], self.material_data[6]
            )
        else:
            # 添加新材料的情况（理论上不应通过此对话框添加新材料，但保留兼容）
            self.result = ("", prefab, spare, "", "", "", "")
        self.dialog.destroy()

    def cancel(self):
        self.result = None
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result
# dialogs/electrical_lib_dialog.py
from dialogs.base_dialog import BaseDialog
from dialogs.quantity_assign_dialog import QuantityAssignDialog
from tkinter import ttk, messagebox, filedialog
import tkinter as tk
import pandas as pd
from models.electrical_lib import ElectricalLibrary
from models.component_db import ComponentDatabase


class ElementDialog(BaseDialog):
    def __init__(self, parent, element_data=None):
        self.element_data = element_data
        self.result = None
        title = "编辑元件" if element_data else "添加元件"
        super().__init__(parent, title, "400x200")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="物料编码:").grid(row=0, column=0, sticky=tk.W, pady=(0,5))
        self.part_number_var = tk.StringVar()
        part_number_entry = ttk.Entry(main_frame, textvariable=self.part_number_var, width=30)
        part_number_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0,5))

        ttk.Label(main_frame, text="物料名称:").grid(row=1, column=0, sticky=tk.W, pady=(0,5))
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0,5))

        ttk.Label(main_frame, text="规格:").grid(row=2, column=0, sticky=tk.W, pady=(0,5))
        self.spec_var = tk.StringVar()
        spec_entry = ttk.Entry(main_frame, textvariable=self.spec_var, width=30)
        spec_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0,10))

        if self.element_data:
            self.part_number_var.set(self.element_data['part_number'])
            self.name_var.set(self.element_data['name'])
            self.spec_var.set(self.element_data['specification'] or "")
            part_number_entry.config(state='disabled')

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="确定", command=self.confirm).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(button_frame, text="取消", command=self.cancel).pack(side=tk.LEFT)

        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def confirm(self):
        part_number = self.part_number_var.get().strip()
        name = self.name_var.get().strip()
        spec = self.spec_var.get().strip()
        if not part_number or not name:
            messagebox.showerror("错误", "物料编码和物料名称不能为空")
            return
        self.result = (part_number, name, spec)
        self.dialog.destroy()

    def cancel(self):
        self.dialog.destroy()

    def show(self):
        self.dialog.wait_window()
        return self.result


class ElectricalLibraryDialog(BaseDialog):
    def __init__(self, parent, library, callback_func=None, show_search=True, quantity_mode=False):
        self.library = library
        self.callback_func = callback_func
        self.show_search = show_search
        self.search_term = ""
        self.quantity_mode = quantity_mode
        self.temp_quantities = {}
        super().__init__(parent, "电气元件库管理", "900x600")

    def setup_ui(self):
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        if self.show_search:
            search_frame = ttk.Frame(main_frame)
            search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT)
            self.search_var = tk.StringVar()
            self.search_var.trace('w', self.on_search_change)
            ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=(5, 10))
            self.include_replaced_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(search_frame, text="包含已替换", variable=self.include_replaced_var,
                            command=self.refresh_list).pack(side=tk.LEFT)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(button_frame, text="添加元件", command=self.add_element).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="编辑选中", command=self.edit_element).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除选中", command=self.remove_element).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="反查使用", command=self.reverse_lookup).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="替换元件", command=self.replace_element).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="导入Excel", command=self.import_excel).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="导出Excel", command=self.export_excel).pack(side=tk.LEFT)

        if self.quantity_mode:
            columns = ("part_number", "name", "specification", "added_time", "replaced_by", "quantity")
        else:
            columns = ("part_number", "name", "specification", "added_time", "replaced_by")

        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15, selectmode='extended')
        self.tree.heading("part_number", text="物料编码")
        self.tree.heading("name", text="物料名称")
        self.tree.heading("specification", text="规格")
        self.tree.heading("added_time", text="添加时间")
        self.tree.heading("replaced_by", text="替换为")
        if self.quantity_mode:
            self.tree.heading("quantity", text="数量")
            self.tree.column("quantity", width=100)

        self.tree.column("part_number", width=120)
        self.tree.column("name", width=150)
        self.tree.column("specification", width=120)
        self.tree.column("added_time", width=120)
        self.tree.column("replaced_by", width=120)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S))

        self.tree.bind('<Double-1>', self.on_double_click)

        button_frame_bottom = ttk.Frame(main_frame)
        button_frame_bottom.grid(row=3, column=0, pady=10)
        ttk.Button(button_frame_bottom, text="确定", command=self.confirm_selection).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame_bottom, text="取消", command=self.cancel).pack(side=tk.LEFT)

        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.refresh_list()

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        elements = self.library.get_all_elements(
            search_term=self.search_term,
            include_replaced=self.include_replaced_var.get()
        )
        for element in elements:
            base = [
                element['part_number'],
                element['name'],
                element['specification'],
                element['added_time'].split('.')[0] if element['added_time'] else '',
                element['replaced_by'] or ''
            ]
            if self.quantity_mode:
                qty = self.temp_quantities.get(element['part_number'], (0, 0))
                qty_text = f"预制:{qty[0]} 零散:{qty[1]}"
                self.tree.insert("", tk.END, values=base + [qty_text])
            else:
                self.tree.insert("", tk.END, values=base)

    def on_search_change(self, *args):
        self.search_term = self.search_var.get()
        self.refresh_list()

    def on_double_click(self, event):
        if self.quantity_mode:
            self._assign_quantity()
        else:
            self.edit_element()

    def _assign_quantity(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        part_number = str(item["values"][0])   # 确保字符串
        element = self.library.get_element(part_number)
        if not element:
            return
        current = self.temp_quantities.get(part_number, (0, 0))
        dlg = QuantityAssignDialog(self.dialog, element["name"], part_number,
                                   default_prefab=current[0], default_spare=current[1])
        result = dlg.show()
        if result:
            prefab, spare = result
            self.temp_quantities[part_number] = (prefab, spare)
            self.refresh_list()

    def confirm_selection(self):
        if self.quantity_mode:
            # 确保键转换为字符串
            selected = [(str(pn), pq, sq) for pn, (pq, sq) in self.temp_quantities.items() if pq > 0 or sq > 0]
            if self.callback_func:
                self.callback_func(selected)
        else:
            selected_items = self.tree.selection()
            selected_parts = [str(self.tree.item(item)["values"][0]) for item in selected_items]
            if self.callback_func:
                self.callback_func(selected_parts)
        self.dialog.destroy()

    def cancel(self):
        if self.callback_func:
            self.callback_func([] if not self.quantity_mode else [])
        self.dialog.destroy()

    def add_element(self):
        dialog = ElementDialog(self.dialog)
        result = dialog.show()
        if result:
            part_number, name, spec = result
            if self.library.add_element(part_number, name, spec):
                self.refresh_list()
                messagebox.showinfo("成功", "元件添加成功")
            else:
                messagebox.showerror("错误", "添加元件失败")

    def edit_element(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的元件")
            return
        item = self.tree.item(selection[0])
        old_part_number = item["values"][0]
        element = self.library.get_element(old_part_number)
        if element:
            dialog = ElementDialog(self.dialog, element)
            result = dialog.show()
            if result:
                new_part_number, name, spec = result
                self.library.update_element(old_part_number, new_part_number, name, spec)
                self.refresh_list()
                messagebox.showinfo("成功", "元件更新成功")

    def remove_element(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的元件")
            return
        item = self.tree.item(selection[0])
        part_number = item["values"][0]
        comp_db = ComponentDatabase()
        used_in = comp_db.get_components_using_element(part_number)
        if used_in and not messagebox.askyesno("确认", f"元件 '{part_number}' 正在以下组件中使用: {', '.join(used_in)}\n\n是否仍要删除？"):
            return
        if messagebox.askyesno("确认", f"确定要删除物料编码 '{part_number}' 吗？"):
            self.library.delete_element(part_number)
            if part_number in self.temp_quantities:
                del self.temp_quantities[part_number]
            self.refresh_list()

    def reverse_lookup(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要反查的元件")
            return
        item = self.tree.item(selection[0])
        part_number = item["values"][0]
        comp_db = ComponentDatabase()
        used_in = comp_db.get_components_using_element(part_number)
        if used_in:
            messagebox.showinfo("反查结果", f"元件 '{part_number}' 在以下组件中使用:\n{', '.join(used_in)}")
        else:
            messagebox.showinfo("反查结果", f"元件 '{part_number}' 未在任何组件中使用")

    def replace_element(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要替换的元件")
            return
        item = self.tree.item(selection[0])
        old_part_number = item["values"][0]
        new_part_number = self.simple_input_dialog(self.dialog, "替换元件", f"请输入 '{old_part_number}' 的替换元件编号:")
        if new_part_number:
            if not self.library.get_element(new_part_number):
                messagebox.showerror("错误", f"新元件编号 '{new_part_number}' 不存在")
                return
            self.library.mark_as_replaced(old_part_number, new_part_number)
            comp_db = ComponentDatabase()
            comp_db.replace_element_in_all_components(old_part_number, new_part_number)
            self.refresh_list()
            messagebox.showinfo("成功", f"元件 '{old_part_number}' 已替换为 '{new_part_number}' 并更新了所有相关组件")

    def import_excel(self):
        file_path = filedialog.askopenfilename(
            title="导入电气元件库",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            try:
                df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
                count = 0
                for _, row in df.iterrows():
                    part_number = str(row['物料编码'])
                    name = str(row['物料名称'])
                    spec = str(row['规格']) if pd.notna(row['规格']) else ""
                    if not self.library.get_element(part_number):
                        self.library.add_element(part_number, name, spec)
                        count += 1
                self.refresh_list()
                messagebox.showinfo("成功", f"成功导入 {count} 个新元件")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")

    def export_excel(self):
        file_path = filedialog.asksaveasfilename(
            title="导出电气元件库",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if file_path:
            try:
                elements = self.library.get_all_elements(include_replaced=True)
                data = []
                for e in elements:
                    data.append({
                        "物料编码": e['part_number'],
                        "物料名称": e['name'],
                        "规格": e['specification'],
                        "添加时间": e['added_time'],
                        "替换为": e['replaced_by'] or ""
                    })
                pd.DataFrame(data).to_excel(file_path, index=False)
                messagebox.showinfo("成功", "电气元件库导出成功")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")
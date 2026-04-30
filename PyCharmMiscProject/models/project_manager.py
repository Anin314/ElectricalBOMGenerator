# models/project_manager.py
import json
import os
from datetime import datetime


class ProjectManager:
    def __init__(self):
        self.current_project = {
            "name": "新项目",
            "created_time": "",
            "modified_time": "",
            "racks": []
        }
        self.file_path = ""

    def new_project(self, name):
        now = datetime.now().isoformat()
        self.current_project = {
            "name": name,
            "created_time": now,
            "modified_time": now,
            "racks": []
        }
        self.file_path = ""

    def load_project(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if "racks" not in data:
            data["racks"] = []
        else:
            # 兼容旧版本：移除 items 中的 placement 字段
            for rack in data["racks"]:
                for item in rack.get("items", []):
                    if "placement" in item:
                        del item["placement"]
        self.current_project = data
        self.file_path = file_path

    def save_project(self, file_path=None):
        if file_path:
            self.file_path = file_path
        if not self.file_path:
            raise ValueError("未指定文件路径")
        self.current_project["modified_time"] = datetime.now().isoformat()
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.current_project, f, ensure_ascii=False, indent=2)

    def add_rack(self, rack_name):
        self.current_project["racks"].append({"name": rack_name, "items": []})

    def remove_rack(self, rack_index):
        del self.current_project["racks"][rack_index]

    def rename_rack(self, rack_index, new_name):
        self.current_project["racks"][rack_index]["name"] = new_name

    def add_item_to_rack(self, rack_index, item_type, item_id, quantity):
        """添加条目到机架，如果已存在相同类型和id，则累加数量"""
        items = self.current_project["racks"][rack_index]["items"]
        for item in items:
            if item["type"] == item_type and item["id"] == item_id:
                item["quantity"] += quantity
                return
        items.append({"type": item_type, "id": item_id, "quantity": quantity})

    def remove_item_from_rack(self, rack_index, item_index):
        del self.current_project["racks"][rack_index]["items"][item_index]

    def update_item_quantity(self, rack_index, item_index, new_quantity):
        self.current_project["racks"][rack_index]["items"][item_index]["quantity"] = new_quantity

    def get_rack_names(self):
        return [r["name"] for r in self.current_project["racks"]]
# models/component_db.py
import sqlite3
import json
import uuid
from datetime import datetime
import os


class ComponentDatabase:
    """组件数据库管理类"""

    def __init__(self, db_path="components.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建组件表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                electrical_parts TEXT NOT NULL,
                created_time TEXT NOT NULL,
                updated_time TEXT NOT NULL
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_component_name ON components(name)")

        conn.commit()
        conn.close()

    def add_component(self, name, electrical_parts):
        """添加组件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            component_id = str(uuid.uuid4())
            created_time = datetime.now().isoformat()
            updated_time = created_time

            # 将电气部件转换为JSON字符串存储
            parts_json = json.dumps(electrical_parts, ensure_ascii=False)

            cursor.execute("""
                INSERT INTO components (id, name, electrical_parts, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?)
            """, (component_id, name, parts_json, created_time, updated_time))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # 组件名称已存在

    def get_component(self, name):
        """根据名称获取组件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM components WHERE name = ?", (name,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "electrical_parts": json.loads(row[2]),
                "created_time": row[3],
                "updated_time": row[4]
            }
        return None

    def get_all_components(self, search_term=""):
        """获取所有组件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if search_term:
            cursor.execute(
                "SELECT * FROM components WHERE name LIKE ? ORDER BY name",
                (f"%{search_term}%",)
            )
        else:
            cursor.execute("SELECT * FROM components ORDER BY name")

        rows = cursor.fetchall()
        conn.close()

        components = []
        for row in rows:
            components.append({
                "id": row[0],
                "name": row[1],
                "electrical_parts": json.loads(row[2]),
                "created_time": row[3],
                "updated_time": row[4]
            })

        return components

    def update_component(self, old_name, new_name, electrical_parts):
        """更新组件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查新名称是否已被其他组件使用
            cursor.execute("SELECT COUNT(*) FROM components WHERE name = ? AND name != ?", (new_name, old_name))
            count = cursor.fetchone()[0]

            if count > 0:
                conn.close()
                return False  # 新名称已存在

            updated_time = datetime.now().isoformat()
            parts_json = json.dumps(electrical_parts, ensure_ascii=False)

            cursor.execute("""
                UPDATE components 
                SET name = ?, electrical_parts = ?, updated_time = ?
                WHERE name = ?
            """, (new_name, parts_json, updated_time, old_name))

            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    def delete_component(self, name):
        """删除组件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM components WHERE name = ?", (name,))

        conn.commit()
        conn.close()

    def get_components_using_element(self, part_number):
        """获取使用特定元件的组件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM components")
        rows = cursor.fetchall()

        conn.close()

        used_in = []
        for row in rows:
            try:
                electrical_parts = json.loads(row[2])
                for part in electrical_parts:
                    if part.get('part_number') == part_number:
                        used_in.append(row[1])  # 组件名称
                        break
            except json.JSONDecodeError:
                continue

        return used_in

    def replace_element_in_all_components(self, old_part_number, new_part_number):
        """在所有组件中替换元件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM components")
        rows = cursor.fetchall()

        for row in rows:
            try:
                electrical_parts = json.loads(row[2])
                modified = False

                for part in electrical_parts:
                    if part.get('part_number') == old_part_number:
                        part['part_number'] = new_part_number
                        modified = True

                if modified:
                    updated_time = datetime.now().isoformat()
                    parts_json = json.dumps(electrical_parts, ensure_ascii=False)

                    cursor.execute("""
                        UPDATE components 
                        SET electrical_parts = ?, updated_time = ?
                        WHERE id = ?
                    """, (parts_json, updated_time, row[0]))
            except json.JSONDecodeError:
                continue

        conn.commit()
        conn.close()
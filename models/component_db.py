# models/component_db.py
import sqlite3
import json
import uuid
from datetime import datetime
import os


class ComponentDatabase:
    """组件数据库管理类，支持IO点和预制板/零散件数量"""

    def __init__(self, db_path="components.db"):
        self.db_path = db_path
        self.init_database()
        self._migrate_old_data()   # 尝试迁移旧数据

    def init_database(self):
        """初始化数据库，确保表结构正确"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='components'")
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            # 创建新表
            cursor.execute("""
                CREATE TABLE components (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    electrical_parts TEXT NOT NULL,
                    io_points TEXT,
                    created_time TEXT NOT NULL,
                    updated_time TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_component_name ON components(name)")
        else:
            # 检查列是否存在，若缺失则添加
            cursor.execute("PRAGMA table_info(components)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'io_points' not in columns:
                cursor.execute("ALTER TABLE components ADD COLUMN io_points TEXT")
            # 确保其他列存在（保险）
            required = ['id', 'name', 'electrical_parts', 'created_time', 'updated_time']
            for col in required:
                if col not in columns:
                    # 理论上不应该缺失，但为了安全，重建表？不，简单抛错
                    raise Exception(f"表 components 缺少必要列 {col}，请删除 {self.db_path} 重新运行")
        conn.commit()
        conn.close()

    def _migrate_old_data(self):
        """迁移旧数据：将旧的 quantity 字段转换为 prefab_qty 和 spare_qty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, electrical_parts FROM components")
        rows = cursor.fetchall()
        updated = False
        for row_id, parts_json in rows:
            try:
                parts = json.loads(parts_json)
                modified = False
                for part in parts:
                    if 'quantity' in part and 'prefab_qty' not in part:
                        part['prefab_qty'] = part['quantity']
                        part['spare_qty'] = 0
                        modified = True
                if modified:
                    new_json = json.dumps(parts, ensure_ascii=False)
                    cursor.execute("UPDATE components SET electrical_parts = ? WHERE id = ?", (new_json, row_id))
                    updated = True
            except:
                pass
        if updated:
            conn.commit()
        conn.close()

    def add_component(self, name, electrical_parts, io_points=None):
        """添加组件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            component_id = str(uuid.uuid4())
            created_time = datetime.now().isoformat()
            updated_time = created_time
            parts_json = json.dumps(electrical_parts, ensure_ascii=False)
            io_json = json.dumps(io_points or {"inputs": [], "outputs": []}, ensure_ascii=False)
            cursor.execute("""
                INSERT INTO components (id, name, electrical_parts, io_points, created_time, updated_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (component_id, name, parts_json, io_json, created_time, updated_time))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_component(self, name):
        """根据名称获取组件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM components WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            electrical_parts = json.loads(row[2])
            # 兼容旧数据：如果部件里没有 prefab_qty，则添加默认
            for part in electrical_parts:
                if 'prefab_qty' not in part:
                    part['prefab_qty'] = part.get('quantity', 0)
                    part['spare_qty'] = 0
            # 解析 io_points，失败则返回默认
            try:
                io_points = json.loads(row[3]) if row[3] else {"inputs": [], "outputs": []}
            except json.JSONDecodeError:
                io_points = {"inputs": [], "outputs": []}
            return {
                "id": row[0],
                "name": row[1],
                "electrical_parts": electrical_parts,
                "io_points": io_points,
                "created_time": row[4],
                "updated_time": row[5]
            }
        return None

    def get_all_components(self, search_term=""):
        """获取所有组件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if search_term:
            cursor.execute("SELECT * FROM components WHERE name LIKE ? ORDER BY name", (f"%{search_term}%",))
        else:
            cursor.execute("SELECT * FROM components ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        components = []
        for row in rows:
            electrical_parts = json.loads(row[2])
            # 兼容旧数据
            for part in electrical_parts:
                if 'prefab_qty' not in part:
                    part['prefab_qty'] = part.get('quantity', 0)
                    part['spare_qty'] = 0
            try:
                io_points = json.loads(row[3]) if row[3] else {"inputs": [], "outputs": []}
            except json.JSONDecodeError:
                io_points = {"inputs": [], "outputs": []}
            components.append({
                "id": row[0],
                "name": row[1],
                "electrical_parts": electrical_parts,
                "io_points": io_points,
                "created_time": row[4],
                "updated_time": row[5]
            })
        return components

    def update_component(self, old_name, new_name, electrical_parts, io_points=None):
        """更新组件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # 检查新名称是否已被其他组件使用
            cursor.execute("SELECT COUNT(*) FROM components WHERE name = ? AND name != ?", (new_name, old_name))
            if cursor.fetchone()[0] > 0:
                conn.close()
                return False
            updated_time = datetime.now().isoformat()
            parts_json = json.dumps(electrical_parts, ensure_ascii=False)
            io_json = json.dumps(io_points or {"inputs": [], "outputs": []}, ensure_ascii=False)
            cursor.execute("""
                UPDATE components 
                SET name = ?, electrical_parts = ?, io_points = ?, updated_time = ?
                WHERE name = ?
            """, (new_name, parts_json, io_json, updated_time, old_name))
            conn.commit()
            conn.close()
            return True
        except Exception:
            if conn:
                conn.close()
            return False

    def delete_component(self, name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM components WHERE name = ?", (name,))
        conn.commit()
        conn.close()

    def get_components_using_element(self, part_number):
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
                        used_in.append(row[1])
                        break
            except:
                continue
        return used_in

    def replace_element_in_all_components(self, old_part_number, new_part_number):
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
            except:
                continue
        conn.commit()
        conn.close()
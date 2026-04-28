# models/electrical_lib.py
import sqlite3
import json
import uuid
from datetime import datetime
import os


class ElectricalLibrary:
    """电气元件库管理类"""

    def __init__(self, db_path="electrical_lib.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建电气元件表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS electrical_elements (
                id TEXT PRIMARY KEY,
                part_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                specification TEXT,
                added_time TEXT NOT NULL,
                replaced_by TEXT,
                replaced_time TEXT
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_part_number ON electrical_elements(part_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_replaced_by ON electrical_elements(replaced_by)")

        conn.commit()
        conn.close()

    def add_element(self, part_number, name, specification=""):
        """添加电气元件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            element_id = str(uuid.uuid4())
            added_time = datetime.now().isoformat()

            cursor.execute("""
                INSERT INTO electrical_elements (id, part_number, name, specification, added_time)
                VALUES (?, ?, ?, ?, ?)
            """, (element_id, part_number, name, specification, added_time))

            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False  # 物料编码已存在

    def get_element(self, part_number):
        """根据物料编码获取元件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM electrical_elements WHERE part_number = ?", (part_number,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return {
                "id": row[0],
                "part_number": row[1],
                "name": row[2],
                "specification": row[3],
                "added_time": row[4],
                "replaced_by": row[5],
                "replaced_time": row[6]
            }
        return None

    def get_all_elements(self, search_term="", include_replaced=True):
        """获取所有元件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if include_replaced:
            if search_term:
                cursor.execute("""
                    SELECT * FROM electrical_elements 
                    WHERE part_number LIKE ? OR name LIKE ? OR specification LIKE ?
                    ORDER BY part_number
                """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("SELECT * FROM electrical_elements ORDER BY part_number")
        else:
            if search_term:
                cursor.execute("""
                    SELECT * FROM electrical_elements 
                    WHERE replaced_by IS NULL AND (part_number LIKE ? OR name LIKE ? OR specification LIKE ?)
                    ORDER BY part_number
                """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            else:
                cursor.execute("SELECT * FROM electrical_elements WHERE replaced_by IS NULL ORDER BY part_number")

        rows = cursor.fetchall()
        conn.close()

        elements = []
        for row in rows:
            elements.append({
                "id": row[0],
                "part_number": row[1],
                "name": row[2],
                "specification": row[3],
                "added_time": row[4],
                "replaced_by": row[5],
                "replaced_time": row[6]
            })

        return elements

    def update_element(self, old_part_number, new_part_number, name, specification=""):
        """更新元件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查新物料编码是否被其他元件使用
            cursor.execute("SELECT COUNT(*) FROM electrical_elements WHERE part_number = ? AND part_number != ?",
                           (new_part_number, old_part_number))
            count = cursor.fetchone()[0]

            if count > 0:
                conn.close()
                return False  # 新物料编码已存在

            cursor.execute("""
                UPDATE electrical_elements 
                SET part_number = ?, name = ?, specification = ?
                WHERE part_number = ?
            """, (new_part_number, name, specification, old_part_number))

            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    def delete_element(self, part_number):
        """删除元件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM electrical_elements WHERE part_number = ?", (part_number,))

        conn.commit()
        conn.close()

    def mark_as_replaced(self, old_part_number, new_part_number):
        """标记元件为已替换"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        replaced_time = datetime.now().isoformat()

        cursor.execute("""
            UPDATE electrical_elements 
            SET replaced_by = ?, replaced_time = ?
            WHERE part_number = ?
        """, (new_part_number, replaced_time, old_part_number))

        conn.commit()
        conn.close()

    def get_replacement_chain(self, part_number):
        """获取替换链的最终目标"""
        current_part_number = part_number
        visited = set()

        while True:
            element = self.get_element(current_part_number)
            if not element or not element['replaced_by']:
                break

            # 防止循环引用
            if current_part_number in visited:
                break
            visited.add(current_part_number)

            current_part_number = element['replaced_by']

        # 如果最终的元件不存在或也被标记为已替换，则返回None
        final_element = self.get_element(current_part_number)
        if final_element and not final_element['replaced_by']:
            return current_part_number
        else:
            return None
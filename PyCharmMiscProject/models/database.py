# models/database.py
import sqlite3
import json
import os
from datetime import datetime
import uuid


class Database:
    """基础数据库类"""

    def __init__(self, db_path="bom_system.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建电气元件库表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS electrical_elements (
                id TEXT PRIMARY KEY,
                part_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                specification TEXT,
                added_time TEXT,
                replaced_by TEXT DEFAULT NULL
            )
        ''')

        # 创建组件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS components (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                electrical_parts TEXT, -- JSON格式存储
                created_time TEXT,
                updated_time TEXT
            )
        ''')

        # 创建项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                components TEXT, -- JSON格式存储
                created_time TEXT,
                modified_time TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def execute_query(self, query, params=None):
        """执行SQL查询"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result

    def execute_update(self, query, params=None):
        """执行更新操作"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        conn.close()

    def fetch_one(self, query, params=None):
        """获取单条记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        return result
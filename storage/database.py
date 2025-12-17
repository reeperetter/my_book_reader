import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path='reader.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Створює таблиці якщо їх немає"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблиця книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                filepath TEXT UNIQUE NOT NULL,
                format TEXT,
                last_position INTEGER DEFAULT 0,
                date_added TEXT,
                date_opened TEXT
            )
        ''')

        # Таблиця закладок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                position INTEGER,
                note TEXT,
                date_created TEXT,
                FOREIGN KEY (book_id) REFERENCES books (id)
            )
        ''')

        # Таблиця налаштувань
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        conn.commit()
        conn.close()

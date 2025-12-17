import sqlite3
from datetime import datetime
from parsers.txt_parser import TxtParser


class Book:
    def __init__(self, filepath, db):
        self.filepath = filepath
        self.db = db
        self.format = self._detect_format()
        self.parser = self._get_parser()

        self.book_id = None
        self.title = None
        self.author = None
        self.content = None
        self.footnotes = {}
        self.current_position = 0
        self.bookmarks = []

    def _detect_format(self):
        """Визначає формат файлу"""
        ext = self.filepath.lower().split('.')[-1]
        return ext

    def _get_parser(self):
        """Повертає відповідний парсер для формату"""
        if self.format == 'txt':
            return TxtParser(self.filepath)
        # elif self.format == 'epub':
        #     return EpubParser(self.filepath)
        # elif self.format == 'pdf':
        #     return PdfParser(self.filepath)
        else:
            raise Exception(f"Формат {self.format} поки не підтримується")

    def load(self):
        """Завантажує книгу через відповідний парсер"""
        parsed_data = self.parser.parse()

        self.content = parsed_data['content']
        self.title = parsed_data['title']
        self.author = parsed_data.get('author')
        self.footnotes = parsed_data.get('footnotes', {})

        self._load_from_db()

    def _load_from_db(self):
        """Завантажує дані книги з БД"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, last_position FROM books WHERE filepath = ?',
                       (self.filepath,))
        result = cursor.fetchone()

        if result:
            self.book_id = result[0]
            self.current_position = result[1]
            cursor.execute('UPDATE books SET date_opened = ? WHERE id = ?',
                           (datetime.now().isoformat(), self.book_id))
        else:
            cursor.execute('''
                INSERT INTO books (title, author, filepath, format, date_added)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.title, self.author, self.filepath, self.format,
                  datetime.now().isoformat()))
            self.book_id = cursor.lastrowid

        conn.commit()
        conn.close()

    def save_position(self):
        """Зберігає поточну позицію в БД"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()

        cursor.execute('UPDATE books SET last_position = ? WHERE id = ?',
                       (self.current_position, self.book_id))

        conn.commit()
        conn.close()

    def get_page(self, screen_height, screen_width):
        """Повертає текст для поточного екрану"""
        # TODO: складна логіка пагінації
        pass

    def next_page(self):
        """Перехід на наступну сторінку"""
        pass

    def prev_page(self):
        """Перехід на попередню сторінку"""
        pass

    def add_bookmark(self, note=""):
        """Додає закладку на поточній позиції"""
        pass

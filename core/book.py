import os
import sqlite3
from datetime import datetime
from parsers.txt_parser import TxtParser
from utils.text_processor import TextProcessor, Paginator


class Book:
    def __init__(self, filepath, db):
        self.filepath = filepath
        self.db = db
        self.format = self._detect_format()
        self.parser = self._get_parser()

        self.text_processor = None
        self.paginator = None

        self.book_id = None
        self.title = None
        self.author = None
        self.content = None
        self.footnotes = {}
        self.current_position = 0
        self.bookmarks = []

        # Кеш для сторінок
        self._page_cache = {}
        self._total_pages_cache = None
        self._cache_page_size = None

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

        # Ініціалізуємо обробку тексту
        self.text_processor = TextProcessor(self.content)
        self.paginator = Paginator(self.content, self.text_processor)

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

    def get_auto_page_size(self):
        """Автоматично визначає розмір сторінки"""
        try:
            size = os.get_terminal_size()
            lines = size.lines - 5  # Віднімаємо для меню
            cols = size.columns - 2  # Віднімаємо для відступів
            return lines * cols
        except:
            # Якщо не вдалося визначити - дефолтне значення
            return 2000

    def _calculate_total_pages(self, chars_per_page):
        """
        Розраховує загальну кількість сторінок з урахуванням розривів слів
        """
        position = 0
        page_count = 0

        while position < len(self.content): #type: ignore
            page_data = self.paginator.get_page(position, chars_per_page) #type: ignore
            page_count += 1

            if page_data['is_last_page']:
                break

            if page_data['next_position'] <= position:
                break

            position = page_data['next_position']

        return page_count


    def calculate_page_number(self, chars_per_page=None):
        """
        Розраховує поточний номер сторінки на основі позиції

        Returns:
            tuple: (current_page, total_pages)
        """
        if chars_per_page is None:
            chars_per_page = self.get_auto_page_size()

        # Перевіряємо чи змінився розмір сторінки
        if self._cache_page_size != chars_per_page:
            # Скидаємо кеш
            self._page_cache = {}
            self._total_pages_cache = None
            self._cache_page_size = chars_per_page

        current_page = self._calculate_exact_page(chars_per_page)

        # Використовуємо кешовану загальну кількість
        if self._total_pages_cache is None:
            self._total_pages_cache = self._calculate_total_pages(chars_per_page)

        return current_page, self._total_pages_cache

    def _calculate_exact_page(self, chars_per_page):
        """
        Точний підрахунок номера сторінки з урахуванням розривів слів
        """
        if self.current_position == 0:
            return 1

        position = 0
        page_num = 1

        while position < self.current_position:
            page_data = self.paginator.get_page(position, chars_per_page) # type: ignore

            if page_data['next_position'] <= position:
                break

            if page_data['next_position'] > self.current_position:
                break

            position = page_data['next_position']
            page_num += 1

        return page_num

    def get_page(self, chars_per_page=None):
        """Повертає текст для поточного екрану"""
        if chars_per_page is None:
            chars_per_page = self.get_auto_page_size()
        return self.paginator.get_page(self.current_position, chars_per_page)  # type: ignore

    def next_page(self, chars_per_page=None):
        """Перехід на наступну сторінку"""
        if chars_per_page is None:
            chars_per_page = self.get_auto_page_size()
        page_data = self.get_page(chars_per_page)
        if not page_data['is_last_page']:
            self.current_position = page_data['next_position']
            self.save_position()
        return page_data

    def prev_page(self, chars_per_page=None):
        """Перехід на попередню сторінку"""
        if chars_per_page is None:
            chars_per_page = self.get_auto_page_size()
        new_position = max(0, self.current_position - chars_per_page)
        self.current_position = new_position
        self.save_position()
        return self.get_page(chars_per_page)

    def add_bookmark(self, note=""):
        """Додає закладку на поточній позиції"""
        pass


import re


class TextProcessor:
    def __init__(self, content):
        self.content = content
        self.chapters = []
        self._detect_chapters()

    def _detect_chapters(self):
        """Визначає початок розділів/глав у тексті"""
        # Шаблони для пошуку розділів
        patterns = [
            r'^Розділ \d+',
            r'^Глава \d+',
            r'^РОЗДІЛ \d+',
            r'^ГЛАВА \d+',
            r'^Chapter \d+',
            r'^CHAPTER \d+',
            r'^\d+\.',  # Просто номер
            r'^[IVX]+\.',  # Римські цифри
        ]

        lines = self.content.split('\n')

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Перевіряємо кожен шаблон
            for pattern in patterns:
                if re.match(pattern, line_stripped):
                    # Зберігаємо позицію символу в тексті
                    position = len('\n'.join(lines[:i]))
                    self.chapters.append({
                        'position': position,
                        'title': line_stripped
                    })
                    break

    def get_next_chapter_position(self, current_pos):
        """Знаходить позицію наступного розділу після current_pos"""
        for chapter in self.chapters:
            if chapter['position'] > current_pos:
                return chapter['position']
        return None

    def is_chapter_start(self, position, tolerance=50):
        """Перевіряє чи позиція близька до початку розділу"""
        for chapter in self.chapters:
            if abs(chapter['position'] - position) < tolerance:
                return True
        return False


class Paginator:
    def __init__(self, content, text_processor):
        self.content = content
        self.text_processor = text_processor
        self.content_length = len(content)

    def get_page(self, start_position, chars_per_page):
        """
        Повертає сторінку тексту починаючи з start_position

        Args:
            start_position: позиція в тексті (символ)
            chars_per_page: приблизна кількість символів на сторінці

        Returns:
            dict з полями: text, next_position, is_last_page
        """
        if start_position >= self.content_length:
            return {
                'text': '',
                'next_position': self.content_length,
                'is_last_page': True
            }

        # Витягуємо шматок тексту
        end_position = start_position + chars_per_page

        # Якщо це остання сторінка
        if end_position >= self.content_length:
            return {
                'text': self.content[start_position:],
                'next_position': self.content_length,
                'is_last_page': True
            }

        # Шукаємо кінець слова (пробіл або новий рядок)
        # +100 щоб знайти кінець слова
        text_chunk = self.content[start_position:end_position + 100]

        # Шукаємо останній пробіл або новий рядок
        last_space = max(
            text_chunk.rfind(' '),
            text_chunk.rfind('\n'),
            text_chunk.rfind('.'),
            text_chunk.rfind('!'),
            text_chunk.rfind('?')
        )

        if last_space == -1:
            # Якщо не знайшли - обрізаємо по chars_per_page
            actual_end = end_position
        else:
            actual_end = start_position + last_space + 1

        # Перевіряємо чи наступна позиція не початок розділу
        next_chapter_pos = self.text_processor.get_next_chapter_position(
            start_position)

        if next_chapter_pos and next_chapter_pos < actual_end:
            # Якщо на цій сторінці є початок розділу - обрізаємо перед ним
            actual_end = next_chapter_pos

        page_text = self.content[start_position:actual_end]

        return {
            'text': page_text,
            'next_position': actual_end,
            'is_last_page': False
        }

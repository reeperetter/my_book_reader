class TxtParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        """Читає TXT файл"""
        try:
            # Спробуємо різні кодування
            encodings = ['utf-8', 'cp1251', 'latin-1']

            for encoding in encodings:
                try:
                    with open(self.filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    return {
                        'content': content,
                        'title': self._extract_title(content),
                        'author': None,  # TXT рідко має метадані
                        'footnotes': {}
                    }
                except UnicodeDecodeError:
                    continue

            raise Exception("Не вдалося прочитати файл")

        except Exception as e:
            raise Exception(f"Помилка читання TXT: {e}")

    def _extract_title(self, content):
        """Витягує назву з першого рядка"""
        first_line = content.split('\n')[0].strip()
        return first_line[:50] if first_line else "Без назви"

from storage.database import Database
from core.book import Book


def main():
    db = Database()

    # Шлях до тестового TXT файлу
    book = Book("test.txt", db)
    book.load()

    print(f"Назва: {book.title}")
    print(f"Перші 500 символів:")
    print(book.content[:500])


if __name__ == "__main__":
    main()

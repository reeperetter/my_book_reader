from storage.database import Database
from core.book import Book


def main():
    db = Database()

    # Тут можна змінити шлях до свого файлу
    filepath = "test.txt"

    book = Book(filepath, db)
    book.load()

    print(f"📖 {book.title}")
    if book.text_processor.chapters: #type: ignore
        print(f"📑 Знайдено розділів: {len(book.text_processor.chapters)}") #type: ignore

    page_size = book.get_auto_page_size()
    print(f"📏 Розмір сторінки: {page_size} символів")
    print("="*50)

    while True:
        page = book.get_page()
        current_page, total_pages = book.calculate_page_number()

        print(f"\n{'='*50}")
        print(f"Сторінка {current_page} з {total_pages}")
        print(f"{'='*50}\n")

        print(page['text'])

        # Перевіряємо чи це остання сторінка ПІСЛЯ показу
        if page['is_last_page']:
            print("\n" + "="*50)
            print("📖 Кінець книги!")
            print("="*50)
            input("\nНатисни Enter для виходу...")
            break

        print(f"\n{'─'*50}")
        print("[Enter] - далі | [p] - назад | [q] - вихід")
        choice = input(">>> ").lower()

        if choice == 'q':
            print("💾 Позицію збережено. До побачення!")
            break
        elif choice == 'p':
            book.prev_page()
        else:
            book.next_page()


if __name__ == "__main__":
    main()

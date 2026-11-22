from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from pathlib import Path
import json

from flask import session
from werkzeug.security import generate_password_hash, check_password_hash   

app = Flask(__name__)
app.secret_key = "e-library-secret-key-change-this"
# Пути к файлам проекта
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "books.json"
IMAGES_DIR = BASE_DIR / "images"


# Демонстрационные книги
default_books = [
    {
        "id": 1,
        "title": "Белый пароход",
        "author": "Чингиз Айтматов",
        "genre": "Повесть",
        "year": 1970,
        "description": "История мальчика, его мечты и веры в добро.",
        "cover": "white_ship.jpg.jpeg"
    },
    {
        "id": 2,
        "title": "Маленький принц",
        "author": "Антуан де Сент-Экзюпери",
        "genre": "Сказка",
        "year": 1943,
        "description": "История о дружбе, любви и ответственности.",
        "cover": "little_prince.jpg.jpeg"
    },
    {
        "id": 3,
        "title": "Гарри Поттер",
        "author": "Джоан Роулинг",
        "genre": "Фэнтези",
        "year": 1997,
        "description": "История мальчика, который узнаёт о мире волшебства.",
        "cover": "harry_potter.jpg.jpeg"
    },
    {
        "id": 4,
        "title": "Война и мир",
        "author": "Лев Толстой",
        "genre": "Роман",
        "year": 1869,
        "description": "Роман о жизни людей во времена исторических перемен.",
        "cover": "war_and_peace.jpg.jpeg"
    }
]


# Загрузка книг
def load_books():
    if not DATA_FILE.exists():
        save_books(default_books)
        return default_books.copy()

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        books = json.load(file)

    return books


# Сохранение книг
def save_books(books):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


# Показ изображений из папки images
@app.route("/images/<path:filename>")
def show_image(filename):
    return send_from_directory(IMAGES_DIR, Path(filename).name)


# Главная страница
@app.route("/")
def home():
    return render_template("index.html")


# Каталог и поиск
@app.route("/catalog")
def catalog():
    books = load_books()

    title = request.args.get("title", "").strip().lower()
    author = request.args.get("author", "").strip().lower()
    genre = request.args.get("genre", "").strip()

    results = []

    for book in books:
        if title and title not in book["title"].lower():
            continue

        if author and author not in book["author"].lower():
            continue

        if genre and genre != book["genre"]:
            continue

        results.append(book)

    genres = sorted(set(book["genre"] for book in books))

    return render_template(
        "catalog.html",
        books=results,
        genres=genres,
        title=title,
        author=author,
        selected_genre=genre
    )


# Страница отдельной книги
@app.route("/book/<int:book_id>")
def book_detail(book_id):
    books = load_books()

    selected_book = next(
        (book for book in books if book["id"] == book_id),
        None
    )

    if selected_book is None:
        abort(404)

    return render_template("book.html", book=selected_book)


# Панель администратора
@app.route("/admin")
def admin():
    books = load_books()
    return render_template("admin.html", books=books)


# Добавление книги
@app.route("/admin/add", methods=["POST"])
def add_book():
    books = load_books()

    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    genre = request.form.get("genre", "").strip()
    description = request.form.get("description", "").strip()

    try:
        year = int(request.form.get("year", ""))
    except ValueError:
        abort(400)

    if not all([title, author, genre, description]):
        abort(400)

    new_book = {
        "id": max([book["id"] for book in books], default=0) + 1,
        "title": title,
        "author": author,
        "genre": genre,
        "year": year,
        "description": description,
        "cover": ""
    }

    books.append(new_book)
    save_books(books)

    return redirect(url_for("admin"))


# Удаление книги
@app.route("/admin/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    books = load_books()

    books = [
        book for book in books
        if book["id"] != book_id
    ]

    save_books(books)

    return redirect(url_for("admin"))

@app.route("/student")
def student():
    student_data = {
        "id": 2103,
        "name": "Иванов Иван Иванович",
        "group": "It-21",
        "email": "ivanov_i@uni.kg"
    }

    history = [
        {
            "book_title": "Белый пароход",
            "borrow_date": "2024-01-15",
            "return_date": "2024-02-15",
            "status": "Возвращена"
        },
        {
            "book_title": "Маленький принц",
            "borrow_date": "2024-03-01",
            "return_date": None,
            "status": "На руках"
        }
    ]

    return render_template("student.html", student=student_data, history=history)

@app.route("/reserve/<int:book_id>", methods=["POST"])
def reserve_book(book_id):
    books = load_books()

    selected_book = next(
        (book for book in books if book["id"] == book_id),
        None
    )

    if selected_book is None:
        abort(404)

    booking_file = BASE_DIR / "bookings.json"

    if booking_file.exists():
        with open(booking_file, "r", encoding="utf-8") as file:
            bookings = json.load(file)
    else:
        bookings = []

        bookings.append({
            "student_id": 2103,
            "student_name": "Иванов Иван Иванович",
            "book_id": book_id,
            "book_title": selected_book["title"],
            "status": "Ожидает подтверждения"
        })

    with open(booking_file, "w", encoding="utf-8") as file:
        json.dump(bookings, file, ensure_ascii=False, indent=4)

    return redirect(url_for("student"))

users = {
    "student1": {
        "password": generate_password_hash("student123"),
        "role": "student"
    },
    "admin": {
        "password": generate_password_hash("admin123"),
        "role": "admin"
    }
}


@app.before_request
def protect_pages():
    path = request.path

    if path.startswith("/admin"):
        if session.get("role") != "admin":
            return redirect(url_for("login"))

    if path == "/student" or path.startswith("/reserve/"):
        if session.get("role") != "student":
            return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users.get(username)

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["username"] = username
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin"))

            return redirect(url_for("student"))

        return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
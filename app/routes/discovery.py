# /app/routes/discovery.py
from flask import Blueprint, render_template, current_app
from app.models.book import Book
# from flask_login import login_required  # Quita esto si el feed es público

discovery = Blueprint('discovery', __name__)

def fetch_published_books_from_redis():
    # Obtener una lista de IDs de libros publicados almacenados en Redis
    book_ids = current_app.redis.smembers('published_books')  # Usando un set para libros publicados
    books = []
    for book_id in book_ids:
        book = current_app.redis.hgetall(f'book:{book_id}')
        if book and book.get('published') == 'True':  # Verifica si el libro está marcado como publicado
            books.append(book)
    return books

@discovery.route('/')
def show_feed():
    published_books = Book.get_published_books()
    return render_template('discovery.html', books=published_books)


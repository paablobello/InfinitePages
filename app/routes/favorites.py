from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.book import Book

favorites = Blueprint('favorites', __name__)

@favorites.route('/')
@login_required
def liked_books():
    user_id = current_user.get_id()
    favorite_books = Book.get_favorite_books(user_id)
    # Filtrar solo los libros publicados
    favorite_books = [book for book in favorite_books if book.published]
    favorite_book_ids = [book.id for book in favorite_books]
    return render_template('favorites.html', books=favorite_books, user_favorites=favorite_book_ids)

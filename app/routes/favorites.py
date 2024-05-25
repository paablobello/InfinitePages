from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.book import Book

# Define un Blueprint para la sección de libros favoritos
favorites = Blueprint('favorites', __name__)

# Ruta para mostrar los libros favoritos del usuario
@favorites.route('/')
@login_required
def liked_books():
    user_id = current_user.get_id()  # Obtiene el ID del usuario actual
    favorite_books = Book.get_favorite_books(user_id)  # Obtiene los libros favoritos del usuario

    # Filtra solo los libros que están publicados
    favorite_books = [book for book in favorite_books if book.published]
    favorite_book_ids = [book.id for book in favorite_books]  # Obtiene los IDs de los libros favoritos

    # Renderiza la plantilla 'favorites.html' con los libros favoritos y sus IDs
    return render_template('favorites.html', books=favorite_books, user_favorites=favorite_book_ids)

# /app/routes/favorites.py
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.models.book import Book

favorites = Blueprint('favorites', __name__)

@favorites.route('/')
@login_required
def liked_books():
    user_id = current_user.get_id()
    favorite_books = Book.get_favorite_books(user_id)
    return render_template('favorites.html', books=favorite_books)

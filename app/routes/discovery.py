# /app/routes/discovery.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.book import Book
from app.models.comment import Comment

discovery = Blueprint('discovery', __name__, template_folder='templates')

@discovery.route('/discovery', methods=['GET'])
def show_feed():
    published_books = Book.get_published_books()
    user_favorites = [book.id for book in Book.get_favorite_books(current_user.get_id())]
    return render_template('discovery.html', books=published_books, user_favorites=user_favorites)


@discovery.route('/add_comment/<book_id>', methods=['POST'])
@login_required
def add_comment(book_id):
    comment_text = request.form.get('comment')
    if comment_text:
        Comment.add_comment(book_id, current_user.get_id(), comment_text)
    return redirect(url_for('discovery.show_feed'))

@discovery.route('/toggle_favorite/<book_id>', methods=['POST'])
@login_required
def toggle_favorite(book_id):
    Book.toggle_favorite(book_id, current_user.get_id())
    return redirect(url_for('discovery.show_feed'))

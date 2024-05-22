# /app/routes/discovery.py
from flask import Blueprint, render_template, current_app, request, redirect, url_for, flash
from app.models.book import Book
from app.models.comment import Comment
from flask_login import login_required, current_user

discovery = Blueprint('discovery', __name__)

@discovery.route('/')
def show_feed():
    published_books = Book.get_published_books()
    return render_template('discovery.html', books=published_books)

@discovery.route('/toggle_favorite/<book_id>', methods=['POST'])
@login_required
def toggle_favorite(book_id):
    user_id = current_user.get_id()
    Book.toggle_favorite(book_id, user_id)
    return redirect(url_for('discovery.show_feed'))

@discovery.route('/add_comment/<book_id>', methods=['POST'])
@login_required
def add_comment(book_id):
    text = request.form.get('comment')
    if text:
        Comment.add_comment(book_id, current_user.username, text)
        flash("Comentario añadido con éxito.", "success")
    else:
        flash("No se pudo añadir el comentario.", "error")
    return redirect(url_for('discovery.show_feed'))

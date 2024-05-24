from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.book import Book
from app.models.comment import Comment

discovery = Blueprint('discovery', __name__, template_folder='templates')

@discovery.route('/discovery', methods=['GET'])
def show_feed():
    published_books = Book.get_published_books()
    user_favorites = []
    if current_user.is_authenticated:
        user_favorites = [book.id for book in Book.get_favorite_books(current_user.id)]
    return render_template('discovery.html', books=published_books, user_favorites=user_favorites)

@discovery.route('/add_comment/<book_id>', methods=['POST'])
@login_required
def add_comment(book_id):
    comment_text = request.json.get('comment')
    if comment_text:
        comment = Comment.add_comment(book_id, current_user.id, comment_text)
        return jsonify({
            'status': 'success',
            'comment': {
                'username': comment.username,
                'text': comment.text
            }
        })
    return jsonify({'status': 'error', 'message': 'No se pudo añadir el comentario'}), 400

@discovery.route('/toggle_favorite/<book_id>', methods=['POST'])
@login_required
def toggle_favorite(book_id):
    Book.toggle_favorite(book_id, current_user.id)
    return '', 204

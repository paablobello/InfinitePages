from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.book import Book
from app.models.comment import Comment

# Define un Blueprint para la sección de descubrimiento
discovery = Blueprint('discovery', __name__, template_folder='templates')

# Ruta para mostrar el feed de libros publicados
@discovery.route('/discovery', methods=['GET'])
def show_feed():
    published_books = Book.get_published_books()  # Obtiene todos los libros publicados
    user_favorites = []
    if current_user.is_authenticated:
        user_favorites = [book.id for book in Book.get_favorite_books(current_user.id)]  # Obtiene los libros favoritos del usuario autenticado
    return render_template('discovery.html', books=published_books, user_favorites=user_favorites)

# Ruta para añadir un comentario a un libro
@discovery.route('/add_comment/<book_id>', methods=['POST'])
@login_required
def add_comment(book_id):
    comment_text = request.json.get('comment')
    if comment_text:
        comment = Comment.add_comment(book_id, current_user.id, comment_text)  # Añade el comentario a la base de datos
        return jsonify({
            'status': 'success',
            'comment': {
                'username': comment.username,
                'text': comment.text
            }
        })
    return jsonify({'status': 'error', 'message': 'No se pudo añadir el comentario'}), 400

# Ruta para alternar el estado de favorito de un libro
@discovery.route('/toggle_favorite/<book_id>', methods=['POST'])
@login_required
def toggle_favorite(book_id):
    Book.toggle_favorite(book_id, current_user.id)  # Alterna el estado de favorito del libro para el usuario autenticado
    return '', 204

import flask
import uuid
import re
import time
from app.models.comment import Comment

# Clase que representa un libro
class Book:
    def __init__(self, id, title, content, username, cover_url=None, published=False, publish_time=None):
        self.id = id
        self.title = self.clean_title(title)
        self.content = content
        self.username = username
        self.cover_url = cover_url
        self.published = published
        self.publish_time = publish_time
        self.comments = Comment.get_comments_for_book(self.id)

    # Método estático para limpiar el título de caracteres no deseados
    @staticmethod
    def clean_title(title):
        return re.sub(r'[*/#]', '', title).strip()

    # Método estático para añadir un nuevo libro
    @staticmethod
    def add_book(title, content, username, cover_url=None):
        book_id = str(uuid.uuid4())  # Genera un ID único para el libro
        cleaned_title = Book.clean_title(title)  # Limpia el título del libro
        flask.current_app.redis.hmset(f"book:{book_id}", {
            'title': cleaned_title,
            'content': content,
            'username': username,
            'cover_url': cover_url,
            'published': 'False',
            'publish_time': '0'
        })  # Guarda los datos del libro en Redis
        return Book(book_id, cleaned_title, content, username, cover_url, False)

    # Método estático para obtener un libro por su ID
    @staticmethod
    def get_book(book_id):
        book_data = flask.current_app.redis.hgetall(f"book:{book_id}")
        if book_data:
            return Book(
                book_id,
                book_data['title'],
                book_data['content'],
                book_data['username'],
                book_data.get('cover_url'),
                book_data['published'] == 'True',
                book_data.get('publish_time', '0')
            )
        return None

    # Método de clase para obtener todos los libros de un usuario
    @classmethod
    def get_books_by_username(cls, username):
        book_keys = flask.current_app.redis.keys(f"book:*")
        books = []
        for book_key in book_keys:
            book_key_str = book_key.decode('utf-8') if isinstance(book_key, bytes) else book_key
            if not book_key_str.endswith(':comments'):
                book = cls.get_book(book_key_str.split(":")[1])
                if book and book.username == username:
                    books.append(book)
        return books

    # Método estático para publicar un libro
    @staticmethod
    def publish_book(book_id):
        if flask.current_app.redis.exists(f"book:{book_id}"):
            flask.current_app.redis.hmset(f"book:{book_id}", {'published': 'True', 'publish_time': str(time.time())})
            flask.current_app.redis.sadd('published_books', book_id)

    # Método estático para despublicar un libro
    @staticmethod
    def unpublish_book(book_id):
        flask.current_app.redis.hmset(f"book:{book_id}", {'published': 'False', 'publish_time': '0'})
        flask.current_app.redis.srem('published_books', book_id)

    # Método de clase para obtener todos los libros publicados
    @classmethod
    def get_published_books(cls):
        book_keys = flask.current_app.redis.smembers('published_books')
        published_books = []
        for book_key in book_keys:
            book_key_str = book_key.decode('utf-8') if isinstance(book_key, bytes) else book_key
            book = cls.get_book(book_key_str)
            if book and book.published:
                published_books.append(book)
        # Ordenar libros por tiempo de publicación en orden descendente (últimos publicados primero)
        published_books.sort(key=lambda x: float(x.publish_time), reverse=True)
        return published_books

    # Método estático para alternar el estado de favorito de un libro para un usuario
    @staticmethod
    def toggle_favorite(book_id, user_id):
        favorites_key = f"user:{user_id}:favorites"
        if flask.current_app.redis.sismember(favorites_key, book_id):
            flask.current_app.redis.srem(favorites_key, book_id)
        else:
            flask.current_app.redis.sadd(favorites_key, book_id)

    # Método estático para obtener los libros favoritos de un usuario
    @staticmethod
    def get_favorite_books(user_id):
        favorite_book_ids = flask.current_app.redis.smembers(f"user:{user_id}:favorites")
        favorite_books = []
        for book_id in favorite_book_ids:
            book_id_str = book_id.decode('utf-8') if isinstance(book_id, bytes) else book_id
            book = Book.get_book(book_id_str)
            if book:
                favorite_books.append(book)
        return favorite_books

    # Método estático para eliminar un libro
    @staticmethod
    def delete_book(book_id):
        flask.current_app.redis.delete(f"book:{book_id}")
        flask.current_app.redis.srem('published_books', book_id)
        # También elimina todos los comentarios asociados con el libro
        comment_ids = flask.current_app.redis.lrange(f"book:{book_id}:comments", 0, -1)
        for comment_id in comment_ids:
            comment_id_str = comment_id.decode('utf-8') if isinstance(comment_id, bytes) else comment_id
            flask.current_app.redis.delete(f"comment:{comment_id_str}")
        flask.current_app.redis.delete(f"book:{book_id}:comments")

    # Método estático para obtener el número de libros de un usuario
    @staticmethod
    def get_books_count_by_user(user_id):
        books = Book.get_books_by_username(user_id)
        return len(books)

    # Método estático para obtener el número de libros publicados de un usuario
    @staticmethod
    def get_published_books_count_by_user(user_id):
        books = Book.get_books_by_username(user_id)
        published_books = [book for book in books if book.published]
        return len(published_books)

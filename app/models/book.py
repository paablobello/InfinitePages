# /app/models/book.py
import flask
import uuid
from app.models.comment import Comment

class Book:
    def __init__(self, id, title, content, username, published=False):
        self.id = id
        self.title = title
        self.content = content
        self.username = username
        self.published = published
        self.comments = Comment.get_comments_for_book(self.id)

    @staticmethod
    def add_book(title, content, username):
        book_id = str(uuid.uuid4())
        flask.current_app.redis.hmset(f"book:{book_id}", {
            'title': title,
            'content': content,
            'username': username,
            'published': 'False'
        })
        return Book(book_id, title, content, username, False)

    @staticmethod
    def get_book(book_id):
        book_data = flask.current_app.redis.hgetall(f"book:{book_id}")
        if book_data:
            return Book(book_id, book_data['title'], book_data['content'], book_data['username'], book_data['published'] == 'True')
        return None

    @classmethod
    def get_books_by_username(cls, username):
        book_keys = flask.current_app.redis.keys(f"book:*")
        books = []
        for book_key in book_keys:
            book = cls.get_book(book_key.split(":")[1])
            if book and book.username == username:
                books.append(book)
        return books

    @staticmethod
    def publish_book(book_id):
        if flask.current_app.redis.exists(f"book:{book_id}"):
            flask.current_app.redis.hset(f"book:{book_id}", 'published', 'True')
            flask.current_app.redis.sadd('published_books', book_id)

    @staticmethod
    def unpublish_book(book_id):
        flask.current_app.redis.hset(f"book:{book_id}", 'published', 'False')
        flask.current_app.redis.srem('published_books', book_id)

    @classmethod
    def get_published_books(cls):
        book_keys = flask.current_app.redis.smembers('published_books')
        published_books = []
        for book_key in book_keys:
            book = cls.get_book(book_key)
            if book and book.published:
                published_books.append(book)
        return published_books

    @staticmethod
    def toggle_favorite(book_id, user_id):
        favorites_key = f"user:{user_id}:favorites"
        if flask.current_app.redis.sismember(favorites_key, book_id):
            flask.current_app.redis.srem(favorites_key, book_id)
        else:
            flask.current_app.redis.sadd(favorites_key, book_id)

    @staticmethod
    def get_favorite_books(user_id):
        favorite_book_ids = flask.current_app.redis.smembers(f"user:{user_id}:favorites")
        favorite_books = []
        for book_id in favorite_book_ids:
            book = Book.get_book(book_id)
            if book:
                favorite_books.append(book)
        return favorite_books

    @staticmethod
    def delete_book(book_id):
        flask.current_app.redis.delete(f"book:{book_id}")
        flask.current_app.redis.srem('published_books', book_id)
        # También elimina todos los comentarios asociados con el libro
        comment_ids = flask.current_app.redis.lrange(f"book:{book_id}:comments", 0, -1)
        for comment_id in comment_ids:
            flask.current_app.redis.delete(f"comment:{comment_id}")
        flask.current_app.redis.delete(f"book:{book_id}:comments")

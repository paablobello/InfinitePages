import flask
import uuid

from flask import current_app


class Book:
    def __init__(self, id, title, content, username, published=False):
        self.id = id
        self.title = title
        self.content = content
        self.username = username
        self.published = published

    @staticmethod
    def add_book(title, content, username):
        book_id = str(uuid.uuid4())  # Genera un UUID único para cada libro
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

    @staticmethod
    def unpublish_book(book_id):
        # Cambiar el estado de 'published' a 'False'
        flask.current_app.redis.hset(f"book:{book_id}", 'published', 'False')

    @classmethod
    def get_published_books(cls):
        book_keys = current_app.redis.keys('book:*')
        published_books = []
        for book_key in book_keys:
            book = current_app.redis.hgetall(book_key)
            if book.get('published') == 'True':
                published_books.append(book)
        return published_books



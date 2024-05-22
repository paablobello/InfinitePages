# /app/models/comment.py
import flask
import uuid

class Comment:
    def __init__(self, id, book_id, username, text):
        self.id = id
        self.book_id = book_id
        self.username = username
        self.text = text

    @classmethod
    def add_comment(cls, book_id, username, text):
        comment_id = str(uuid.uuid4())
        comment_data = {
            'book_id': book_id,
            'username': username,
            'text': text
        }
        flask.current_app.redis.hmset(f"comment:{comment_id}", comment_data)
        # Añadir el comentario a la lista de comentarios del libro
        flask.current_app.redis.rpush(f"book:{book_id}:comments", comment_id)
        return cls(comment_id, book_id, username, text)

    @classmethod
    def get_comments_for_book(cls, book_id):
        comment_ids = flask.current_app.redis.lrange(f"book:{book_id}:comments", 0, -1)
        comments = []
        for comment_id in comment_ids:
            comment_data = flask.current_app.redis.hgetall(f"comment:{comment_id}")
            comments.append(cls(comment_id, comment_data['book_id'], comment_data['username'], comment_data['text']))
        return comments

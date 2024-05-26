import flask
import uuid

# Clase que representa un comentario
class Comment:
    def __init__(self, id, book_id, username, text):
        self.id = id
        self.book_id = book_id
        self.username = username
        self.text = text

    # Método de clase para añadir un nuevo comentario
    @classmethod
    def add_comment(cls, book_id, username, text):
        comment_id = str(uuid.uuid4())  # Genera un ID único para el comentario
        comment_data = {
            'book_id': book_id,
            'username': username,
            'text': text
        }
        flask.current_app.redis.hmset(f"comment:{comment_id}", comment_data)  # Guarda el comentario en Redis
        # Añade el comentario a la lista de comentarios del libro
        flask.current_app.redis.rpush(f"book:{book_id}:comments", comment_id)
        return cls(comment_id, book_id, username, text)

    # Método estático para obtener los comentarios de un libro
    @staticmethod
    def get_comments_for_book(book_id):
        comment_ids = flask.current_app.redis.lrange(f"book:{book_id}:comments", 0, -1)  # Obtiene los IDs de los comentarios del libro
        comments = []
        for comment_id in comment_ids:
            comment_id_str = comment_id.decode('utf-8') if isinstance(comment_id, bytes) else comment_id  # Decodifica el ID si es necesario
            comment_data = flask.current_app.redis.hgetall(f"comment:{comment_id_str}")  # Obtiene los datos del comentario desde Redis
            if comment_data:  # Asegurarse de que exista el comentario
                comments.append(Comment(
                    comment_id_str,
                    comment_data['book_id'],
                    comment_data['username'],
                    comment_data['text']
                ))
        return comments

    # Método estático para contar los comentarios recibidos por los libros de un usuario
    @staticmethod
    def get_comments_received_count(username):
        from app.models.book import Book
        books = Book.get_books_by_username(username)  # Obtiene los libros del usuario
        total_comments = 0
        for book in books:
            total_comments += len(flask.current_app.redis.lrange(f"book:{book.id}:comments", 0, -1))  # Cuenta los comentarios de cada libro
        return total_comments

    # Método estático para contar los comentarios enviados por un usuario
    @staticmethod
    def get_comments_sent_count(username):
        comment_keys = flask.current_app.redis.keys(f"comment:*")  # Obtiene todas las claves de comentarios
        comments = []
        for comment_key in comment_keys:
            comment_key_str = comment_key.decode('utf-8') if isinstance(comment_key, bytes) else comment_key  # Decodifica la clave si es necesario
            comment_data = flask.current_app.redis.hgetall(comment_key_str)  # Obtiene los datos del comentario desde Redis
            if comment_data and comment_data['username'] == username:  # Comprueba si el comentario fue enviado por el usuario
                comments.append(comment_data)
        return len(comments)  # Devuelve el número de comentarios enviados

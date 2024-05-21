import flask
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @classmethod
    def get_user(cls, username):
        user_data = flask.current_app.redis.hgetall(f"user:{username}")
        if user_data:
            return cls(user_data['username'], user_data['email'], user_data['password'])
        return None

    @classmethod
    def add_user(cls, username, email, password):
        password_hash = generate_password_hash(password)  # Hashea la contraseña
        user_data = {
            'username': username,
            'email': email,
            'password': password_hash  # Almacena la contraseña hasheada
        }
        flask.current_app.redis.hmset(f"user:{username}", user_data)
        return cls(username, email, password_hash)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Estos métodos son requeridos por Flask-Login
    def get_id(self):
        # Flask-Login utiliza este método para manejar la sesión de usuario
        return self.username  # Cambiado de self.username a self.email

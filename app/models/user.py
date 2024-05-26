import flask
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password

    @staticmethod
    def add_user(username, email, password):
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        flask.current_app.redis.hmset(f"user:{user_id}", {
            'username': username,
            'email': email,
            'password': password_hash
        })
        return User(user_id, username, email, password_hash)

    @staticmethod
    def get_user(user_id):
        user_data = flask.current_app.redis.hgetall(f"user:{user_id}")
        if user_data:
            return User(
                user_id,
                user_data['username'],
                user_data['email'],
                user_data['password']
            )
        return None

    @staticmethod
    def get_user_by_username(username):
        user_keys = flask.current_app.redis.keys(f"user:*")
        for key in user_keys:
            if flask.current_app.redis.type(key) == 'hash':
                user_data = flask.current_app.redis.hgetall(key)
                if user_data and user_data.get('username') == username:
                    return User(
                        key.split(':')[1],
                        user_data['username'],
                        user_data['email'],
                        user_data['password']
                    )
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        flask.current_app.redis.hmset(f"user:{self.id}", {
            'username': self.username,
            'email': self.email,
            'password': self.password_hash
        })

    @classmethod
    def update_user(cls, user):
        user_data = {
            'username': user.username,
            'email': user.email,
            'password': user.password_hash
        }
        flask.current_app.redis.hmset(f"user:{user.id}", user_data)

    def update_email(self, new_email):
        self.email = new_email
        self.save()

    def update_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)
        self.save()

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

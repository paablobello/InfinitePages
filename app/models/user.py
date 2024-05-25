import flask
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# Clase que representa un usuario
class User:
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password

    # Método estático para añadir un nuevo usuario
    @staticmethod
    def add_user(username, email, password):
        user_id = str(uuid.uuid4())  # Genera un ID único para el usuario
        password_hash = generate_password_hash(password)  # Genera un hash para la contraseña
        flask.current_app.redis.hmset(f"user:{user_id}", {
            'username': username,
            'email': email,
            'password': password_hash
        })  # Guarda los datos del usuario en Redis
        return User(user_id, username, email, password_hash)

    # Método estático para obtener un usuario por ID
    @staticmethod
    def get_user(user_id):
        user_data = flask.current_app.redis.hgetall(f"user:{user_id}")  # Obtiene los datos del usuario desde Redis
        if user_data:
            return User(
                user_id,
                user_data['username'],
                user_data['email'],
                user_data['password']
            )  # Crea una instancia de User con los datos obtenidos
        return None

    # Método para verificar la contraseña del usuario
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Método para guardar los datos del usuario en Redis
    def save(self):
        flask.current_app.redis.hmset(f"user:{self.id}", {
            'username': self.username,
            'email': self.email,
            'password': self.password_hash
        })

    # Método de clase para actualizar los datos de un usuario
    @classmethod
    def update_user(cls, user):
        user_data = {
            'username': user.username,
            'email': user.email,
            'password': user.password_hash
        }
        flask.current_app.redis.hmset(f"user:{user.id}", user_data)  # Actualiza los datos del usuario en Redis

    # Método para actualizar el correo electrónico del usuario
    def update_email(self, new_email):
        self.email = new_email
        self.save()

    # Método para actualizar la contraseña del usuario
    def update_password(self, new_password):
        self.password_hash = generate_password_hash(new_password)
        self.save()

    # Propiedad que indica si el usuario está autenticado
    @property
    def is_authenticated(self):
        return True

    # Propiedad que indica si el usuario está activo
    @property
    def is_active(self):
        return True

    # Propiedad que indica si el usuario es anónimo
    @property
    def is_anonymous(self):
        return False

    # Método para obtener el ID del usuario
    def get_id(self):
        return self.id

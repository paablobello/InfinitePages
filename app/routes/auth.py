from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.book import Book
from app.models.comment import Comment
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('discovery.show_feed'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_user(username)
        if user and user.check_password(password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('discovery.show_feed'))
        else:
            flash('Usuario o contraseña incorrecta.', 'login_error')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('discovery.show_feed'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            flash('El nombre de usuario solo puede contener letras, números y guiones bajos.', 'register_error')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Introduce un correo electrónico válido.', 'register_error')
        elif len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', 'register_error')
        elif User.get_user(username):
            flash('El nombre de usuario ya está en uso. Por favor, elige otro.', 'register_error')
        else:
            new_user = User.add_user(username, email, password)
            login_user(new_user, remember=True)
            return redirect(url_for('discovery.show_feed'))
    return render_template('register.html')


@auth.route('/profile')
@login_required
def profile():
    user_id = current_user.get_id()
    stats = {
        'books_generated': Book.get_books_count_by_user(user_id),
        'books_published': Book.get_published_books_count_by_user(user_id),
        'comments_received': Comment.get_comments_received_count(user_id),
        'comments_sent': Comment.get_comments_sent_count(user_id)
    }
    return render_template('profile.html', user=current_user, stats=stats)

@auth.route('/update_email', methods=['POST'])
@login_required
def update_email():
    new_email = request.json['new_email']
    if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
        return jsonify({'status': 'error', 'message': 'Introduce un correo electrónico válido.'})
    else:
        user = User.get_user(current_user.id)
        user.update_email(new_email)
        return jsonify({'status': 'success', 'message': 'Email actualizado con éxito.', 'new_email': new_email})

@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.json['current_password']
    new_password = request.json['new_password']

    user = User.get_user(current_user.id)
    if not user.check_password(current_password):
        return jsonify({'status': 'error', 'message': 'La contraseña actual es incorrecta.'})
    elif len(new_password) < 4:
        return jsonify({'status': 'error', 'message': 'La nueva contraseña debe tener al menos 4 caracteres.'})
    else:
        user.update_password(new_password)
        return jsonify({'status': 'success', 'message': 'Contraseña actualizada con éxito.'})

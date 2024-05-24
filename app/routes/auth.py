from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
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
            flash('Registro exitoso.', 'register_success')
            return redirect(url_for('discovery.show_feed'))
    return render_template('register.html')

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@auth.route('/update_email', methods=['POST'])
@login_required
def update_email():
    new_email = request.form['new_email']
    if not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
        flash('Introduce un correo electrónico válido.', 'profile_error')
    else:
        user = User.get_user(current_user.id)
        user.update_email(new_email)
        flash('Email actualizado con éxito.', 'profile_success')
    return redirect(url_for('auth.profile'))

@auth.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']

    user = User.get_user(current_user.id)
    if not user.check_password(current_password):
        flash('La contraseña actual es incorrecta.', 'profile_error')
    elif len(new_password) < 4:
        flash('La nueva contraseña debe tener al menos 4 caracteres.', 'profile_error')
    else:
        user.update_password(new_password)
        flash('Contraseña actualizada con éxito.', 'profile_success')
    return redirect(url_for('auth.profile'))

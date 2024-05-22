from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

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
            flash('Usuario o contraseña incorrecta.')
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
        if User.get_user(username) is None:
            new_user = User.add_user(username, email, password)
            login_user(new_user, remember=True)
            return redirect(url_for('discovery.show_feed'))
        else:
            flash('El usuario ya existe.')
    return render_template('register.html')

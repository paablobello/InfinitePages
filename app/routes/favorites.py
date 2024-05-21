from flask import Blueprint, render_template

favorites = Blueprint('favorites', __name__)

@favorites.route('/')
def liked_books():
    return render_template('favorites.html')

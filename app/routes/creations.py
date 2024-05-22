from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
import openai
from openai import OpenAI

client = OpenAI(api_key="sk-proj-FEoK1vLr7iiz1CcV0ULFT3BlbkFJ1d7tEH12hcsyTfFbY0JQ")
from app.models.book import Book

# Configura tu clave de API de OpenAI en un lugar seguro

# Creación del Blueprint para la sección "Creations"
creations = Blueprint('creations', __name__, template_folder='templates')

@creations.route('/creations', methods=['GET', 'POST'])
@login_required
def my_creations():
    generated_text = None
    generated_title = None
    cover_url = None
    books = Book.get_books_by_username(current_user.get_id())

    if request.method == 'POST':
        description = request.form.get('description', '')
        genre = request.form.get('genre', '')
        creativity_level = request.form.get('creativity_level', 'medium')
        word_count = request.form.get('word_count', '500')
        language = request.form.get('language', 'Español')

        messages = [
            {"role": "system", "content": "Eres un asistente de creación de historias."},
            {"role": "user", "content": f"Crea una historia completa sobre: {description}. La historia debe tener un principio, un desarrollo y un final claro. La longitud aproximada debe ser de {word_count} palabras, pero si hacen falta mas palabras para poder acabar la historia se deben añadir hasat que finalice por completo y acabando con un punto y final. Género: {genre}. Idioma: {language}. Proporciona un título separado."}
        ]

        try:
            response = client.chat.completions.create(model="gpt-4-turbo",
            messages=messages,
            max_tokens=int(word_count) + 100,  # Aumentamos el límite de tokens
            temperature=float(get_creativity_temperature(creativity_level)))
            generated_text = response.choices[0].message.content.strip()

            # Separar el título del contenido
            lines = generated_text.split('\n')
            generated_title = lines[0]
            generated_text = '\n'.join(lines[1:]).strip()

            # Generar una portada de libro
            cover_prompt = f"Portada de libro para una historia sobre: {description}. Género: {genre}."
            cover_response = client.images.generate(prompt=cover_prompt, n=1, size="512x512")
            cover_url = cover_response.data[0].url

        except openai.OpenAIError as e:
            flash(f"Error al generar el libro: {str(e)}", "error")

    return render_template('creations.html', generated_text=generated_text, generated_title=generated_title, cover_url=cover_url, books=books)

@creations.route('/save_book', methods=['POST'])
@login_required
def save_book():
    title = request.form['title']
    content = request.form['content']
    cover_url = request.form['cover_url']
    user_id = current_user.get_id()
    book = Book.add_book(title, content, user_id, cover_url)
    if book:
        flash("Libro guardado con éxito.", "success")
    else:
        flash("Error al guardar el libro", "error")
    return redirect(url_for('creations.my_creations'))

@creations.route('/publish_book/<book_id>', methods=['POST'])
@login_required
def publish_book(book_id):
    try:
        Book.publish_book(book_id)
        flash("Libro publicado con éxito.", "success")
    except Exception as e:
        flash(f"No se pudo publicar el libro: {str(e)}", "error")
    return redirect(url_for('creations.my_creations'))

@creations.route('/unpublish_book/<book_id>', methods=['POST'])
@login_required
def unpublish_book(book_id):
    Book.unpublish_book(book_id)
    flash("Libro despublicado con éxito.", "info")
    return redirect(url_for('creations.my_creations'))

@creations.route('/delete_book/<book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.get_book(book_id)
    if book and book.username == current_user.get_id():
        Book.delete_book(book_id)
        flash("Libro eliminado con éxito.", "success")
    else:
        flash("No se encontró el libro o no tiene permiso para eliminarlo.", "error")
    return redirect(url_for('creations.my_creations'))

def get_creativity_temperature(level):
    temperature_map = {'low': 0.3, 'medium': 0.6, 'high': 1.0}
    return temperature_map.get(level, 0.6)

@creations.route('/get_full_story/<book_id>', methods=['GET'])
@login_required
def get_full_story(book_id):
    book = Book.get_book(book_id)
    if book and book.username == current_user.get_id():
        return book.content
    return "No autorizado", 403

@creations.route('/toggle_publish_book/<book_id>', methods=['POST'])
@login_required
def toggle_publish_book(book_id):
    book = Book.get_book(book_id)
    if book:
        if book.published:
            Book.unpublish_book(book_id)
        else:
            Book.publish_book(book_id)
        flash(f"Estado de publicación del libro '{book.title}' actualizado.", "success")
    else:
        flash("No se encontró el libro.", "error")
    return redirect(url_for('creations.my_creations'))

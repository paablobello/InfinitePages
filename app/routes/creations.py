from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
import openai
from openai import OpenAI
import asyncio
import aiohttp

# Inicializa el cliente OpenAI con la clave de API
client = OpenAI(api_key="sk-proj-FEoK1vLr7iiz1CcV0ULFT3BlbkFJ1d7tEH12hcsyTfFbY0JQ")
from app.models.book import Book

# Define un Blueprint para la sección de creaciones
creations = Blueprint('creations', __name__, template_folder='templates')

# Función asincrónica para obtener una historia generada por OpenAI
async def fetch_story(session, description, genre, creativity_level, word_count, language):
    messages = [
        {"role": "system", "content": "Eres un asistente de creación de historias."},
        {"role": "user", "content": f"""
            Crea una historia completa sobre: {description}.
            La historia debe tener un principio, un desarrollo y un final claro.
            La longitud aproximada debe ser de {word_count} palabras, pero si es necesario, puedes añadir más palabras para asegurar que la historia esté completa.
            Es crucial que la historia tenga un final claro y coherente.
            Género: {genre}. 
            Idioma: {language}.
            Proporciona un título adecuado para la historia, separado del cuerpo del texto y sin caracteres especiales como * # / etc.
        """}
    ]

    response = await session.post(
        'https://api.openai.com/v1/chat/completions',
        json={
            "model": "gpt-4o",
            "messages": messages,
            "temperature": float(get_creativity_temperature(creativity_level))
        },
        headers={
            "Authorization": f"Bearer {client.api_key}"
        }
    )
    result = await response.json()
    return result['choices'][0]['message']['content'].strip()

# Función asincrónica para generar una portada de libro usando OpenAI
async def fetch_cover(session, description, genre):
    cover_prompt = f"Portada de libro para una historia sobre: {description}. Género: {genre}."
    response = await session.post(
        'https://api.openai.com/v1/images/generations',
        json={
            "prompt": cover_prompt,
            "n": 1,
            "size": "1024x1024"
        },
        headers={
            "Authorization": f"Bearer {client.api_key}"
        }
    )
    result = await response.json()
    return result['data'][0]['url']

# Función que coordina la generación de la historia y la portada
async def generate_story_and_cover(description, genre, creativity_level, word_count, language):
    async with aiohttp.ClientSession() as session:
        story_task = fetch_story(session, description, genre, creativity_level, word_count, language)
        cover_task = fetch_cover(session, description, genre)
        generated_text, cover_url = await asyncio.gather(story_task, cover_task)

        lines = generated_text.split('\n')
        generated_title = lines[0]
        generated_text = '\n'.join(lines[1:]).strip()

        return generated_text, generated_title, cover_url

# Ruta para la página de creaciones
@creations.route('/creations', methods=['GET', 'POST'])
@login_required
def my_creations():
    generated_text = None
    generated_title = None
    cover_url = None
    books = Book.get_books_by_username(current_user.username)  # Usar current_user.username
    if request.method == 'POST':
        description = request.form.get('description', '')
        genre = request.form.get('genre', '')
        creativity_level = request.form.get('creativity_level', 'medium')
        word_count = request.form.get('word_count', '500')
        language = request.form.get('language', 'Español')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            generated_text, generated_title, cover_url = loop.run_until_complete(
                generate_story_and_cover(description, genre, creativity_level, word_count, language)
            )
        except openai.OpenAIError as e:
            flash(f"Error al generar el libro: {str(e)}", "error")

    return render_template('creations.html', generated_text=generated_text, generated_title=generated_title, cover_url=cover_url, books=books)

# Ruta para guardar un libro
@creations.route('/save_book', methods=['POST'])
@login_required
def save_book():
    title = request.form['title']
    content = request.form['content']
    cover_url = request.form['cover_url']
    username = current_user.username  # Obtener el username del usuario autenticado
    book = Book.add_book(title, content, username, cover_url)
    if book:
        flash("Libro guardado con éxito.", "success")
    else:
        flash("Error al guardar el libro", "error")
    return redirect(url_for('creations.my_creations'))


# Ruta para publicar un libro
@creations.route('/publish_book/<book_id>', methods=['POST'])
@login_required
def publish_book(book_id):
    try:
        Book.publish_book(book_id)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Ruta para despublicar un libro
@creations.route('/unpublish_book/<book_id>', methods=['POST'])
@login_required
def unpublish_book(book_id):
    Book.unpublish_book(book_id)
    return jsonify({'status': 'success'})

# Ruta para eliminar un libro
@creations.route('/delete_book/<book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    book = Book.get_book(book_id)
    if book and book.username == current_user.username:
        Book.delete_book(book_id)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'No se encontró el libro o no tiene permiso para eliminarlo.'})

# Función para obtener la temperatura de creatividad
def get_creativity_temperature(level):
    temperature_map = {'low': 0.3, 'medium': 0.6, 'high': 1.0}
    return temperature_map.get(level, 0.6)

# Ruta para obtener el contenido completo de una historia
@creations.route('/get_full_story/<book_id>', methods=['GET'])
@login_required
def get_full_story(book_id):
    book = Book.get_book(book_id)
    if book and book.username == current_user.get_id():
        return book.content
    return "No autorizado", 403

# Ruta para alternar la publicación de un libro
@creations.route('/toggle_publish_book/<book_id>', methods=['POST'])
@login_required
def toggle_publish_book(book_id):
    book = Book.get_book(book_id)
    if book:
        if book.published:
            Book.unpublish_book(book_id)
        else:
            Book.publish_book(book_id)
        return jsonify({'status': 'success', 'published': book.published})
    else:
        return jsonify({'status': 'error', 'message': 'No se encontró el libro.'})

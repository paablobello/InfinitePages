from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from openai import OpenAI
from app.models.book import Book

from app.models.book import Book

client = OpenAI(api_key="sk-proj-FEoK1vLr7iiz1CcV0ULFT3BlbkFJ1d7tEH12hcsyTfFbY0JQ")

# Configura tu clave de API de OpenAI

# Creación del Blueprint para la sección "Creations"
creations = Blueprint('creations', __name__, template_folder='templates')


@creations.route('/creations', methods=['GET', 'POST'])
@login_required
def my_creations():
    generated_text = None  # Inicializa la variable para almacenar el texto generado
    books = Book.get_books_by_username(current_user.get_id())  # Recupera todos los libros del usuario actual

    if request.method == 'POST':
        description = request.form.get('description', '')
        genre = request.form.get('genre', '')
        creativity_level = request.form.get('creativity_level', 'medium')
        word_count = request.form.get('word_count', '500')
        language = request.form.get('language', 'Español')

        # Construye los mensajes según el formato requerido por la API ChatCompletion de OpenAI
        messages = [
            {"role": "system", "content": "Eres un asistente de creación de historias."},
            {"role": "user", "content": f"Crea una historia sobre: {description}, aproximadamente de {word_count} palabras, Género: {genre}, Idioma: {language}."}
        ]

        try:
            response = client.chat.completions.create(model="gpt-4-turbo",
            messages=messages,
            #max_tokens=int(max_tokens),
            temperature=float(get_creativity_temperature(creativity_level)))
            generated_text = response.choices[0].message.content
            print(f"Descripción: {description}")
            print(f"Género: {genre}")
            print(f"Nivel de creatividad: {creativity_level}")
            print(f"Conteo de palabras: {word_count}")
            print(f"Idioma: {language}")
        except Exception as e:
            print(f"Descripción: {description}")
            print(f"Género: {genre}")
            print(f"Nivel de creatividad: {creativity_level}")
            print(f"Conteo de palabras: {word_count}")
            print(f"Idioma: {language}")
            print(f"Error al generar el libro: {str(e)}")
            flash(f"Error al generar el libro: {str(e)}", "error")

    # Devuelve la misma página con o sin resultado generado
    return render_template('creations.html', generated_text=generated_text, books=books)



@creations.route('/save_book', methods=['POST'])
def save_book():
    title = request.form['title']
    content = request.form['content']
    user_id = current_user.get_id()
    print(f"Guardando libro con título: {title}, contenido: {content[:50]}, usuario: {user_id}")
    book = Book.add_book(title, content, user_id)
    if book:
        print(f"Libro guardado: {book.title}")
    else:
        print("Error al guardar el libro")
    flash("Libro guardado con éxito.", "success")
    return redirect(url_for('creations.my_creations'))


@creations.route('/publish_book/<book_id>', methods=['POST'])
@login_required
def publish_book(book_id):
    # Intenta publicar el libro y luego redirecciona de nuevo a la página de creaciones
    try:
        Book.publish_book(book_id)
        flash("Libro publicado con éxito.", "success")
    except Exception as e:
        flash(f"No se pudo publicar el libro: {str(e)}", "error")
    return redirect(url_for('creations.my_creations'))


@creations.route('/unpublish_book/<book_id>', methods=['POST'])
@login_required
def unpublish_book(book_id):
    # Asumiendo que tienes un método para despublicar un libro
    Book.unpublish_book(book_id)
    flash("Libro despublicado con éxito.", "info")
    return redirect(url_for('creations.my_creations'))



def get_creativity_temperature(level):
    temperature_map = {'low': 0.3, 'medium': 0.6, 'high': 1.0}
    return temperature_map.get(level, 0.6)

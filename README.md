# InfinitePages

Aplicación web diseñada para crear, publicar y descubrir historias. Creada como proyecto final de la asignatura de ALS.

## Tecnologías Utilizadas

- **Flask** 
- **Redis** 
- **Jinja2**
- **Bootstrap** 
- **JavaScript** 

## Instalación

### Prerrequisitos

- Python 3.7+
- Servidor Redis
- Administrador de paquetes `pip`

### Configuración

1. **Clona el repositorio:**

    ```bash
    git clone https://github.com/paablobello/InfinitePages.git
    cd InfinitePages
    ```

2. **Crea un entorno virtual e instala las dependencias:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Configura la clave API de OpenAI:**

    Abre el archivo `creations.py` y reemplaza la clave API actual con tu propia clave API de OpenAI:

    ```python
    client = OpenAI(api_key="tu_clave_api_aqui")
    ```

4. **Ejecuta el servidor Redis:**

    Asegúrate de que el servidor Redis esté ejecutándose en tu máquina local.

5. **Ejecuta la aplicación:**

    ```bash
    flask run
    ```

    La aplicación estará accesible en `http://127.0.0.1:5000`.

## Funcionalidades

- **Registro y Login de Usuarios:** Autenticación segura para los usuarios.
- **Gestión de Perfil:** Los usuarios pueden actualizar su correo electrónico y contraseña, y ver estadísticas sobre su actividad.
- **Generación de Historias:** Genera historias con IA a partir de varios parámetros como descripción, género, nivel de creatividad y cantidad de palabras.
- **Publicación:** Publica o despublica historias con un interruptor.
- **Favoritos:** Marca historias como favoritas para encontrarlas fácilmente más tarde.
- **Comentarios:** Deja comentarios en las historias.
- **Dashboard:** Visualiza estadísticas como total de historias creadas, publicadas y comentarios recibidos.

---

Asegúrate de reemplazar `"tu_clave_api_aqui"` con tu clave API real de OpenAI.

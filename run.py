# Importa la función create_app desde el paquete app
from app import create_app

# Crea una instancia de la aplicación Flask utilizando la función create_app
app = create_app()

# Si el archivo se ejecuta directamente, inicia la aplicación Flask
if __name__ == "__main__":
    app.run(debug=True)

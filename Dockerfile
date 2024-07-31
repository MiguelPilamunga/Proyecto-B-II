FROM python:3.12.4-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia todo el contenido del directorio actual al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 5000
EXPOSE 5000

# Define la variable de entorno para Flask
ENV FLASK_APP=app.py

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
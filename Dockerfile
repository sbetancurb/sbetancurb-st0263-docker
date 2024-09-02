# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requisitos al contenedor
COPY requirements.txt .

# Instalar las dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación al contenedor
COPY . .

# Exponer el puerto que usará la aplicación (ejemplo: 5000)
EXPOSE 5000-5003

# Comando para ejecutar el servidor
CMD ["python", "server.py"]

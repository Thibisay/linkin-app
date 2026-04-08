FROM python:3.12.4-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY . .

# Asegura que el directorio /data exista para SQLite
RUN mkdir -p /data && chmod 777 /data

# Recolecta todos los archivos estáticos en /app/staticfiles
RUN python manage.py collectstatic --noinput

# Compila los archivos de traducción (.po -> .mo)
RUN python manage.py compilemessages

# Aplica las migraciones y arranca Gunicorn en el puerto 8000
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]
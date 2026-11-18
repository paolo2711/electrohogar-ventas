# Imagen de ElectroHogar Ventas para producción.
# La construye y publica .github/workflows/entrega.yml al crear un tag v*.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Los estáticos se juntan al construir; en producción los sirve WhiteNoise.
RUN DJANGO_SECRET_KEY=solo-para-construir python manage.py collectstatic --noinput

# Sin privilegios de administrador dentro del contenedor.
RUN useradd --create-home tienda && chown -R tienda /app
USER tienda

EXPOSE 8000

# Aplica las migraciones pendientes y levanta el servidor. La base y la clave secreta
# llegan por variables de entorno (ver README).
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn electrohogar.wsgi --bind 0.0.0.0:${PORT} --workers 2"]

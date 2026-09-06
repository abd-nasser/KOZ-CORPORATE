FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Installation des dépendances système + Node.js/NPM
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Paquets NPM globaux / vendor
RUN npm install gsap@3.12.5 lenis@1.3.25

# 4. Copie du code source
COPY src/ .

# 5. Variables d'environnement factices pour que Django charge settings.py sans BDD
ENV SECRET_KEY=dummy_key_for_build_only
ENV DEBUG=False
ENV ALLOWED_HOSTS=*
# Si tu utilises dj-database-url dans settings.py, évite le crash BDD au build :
ENV DATABASE_URL=postgres://dummy:dummy@localhost:5432/dummy

# 6. Installation des dépendances du thème Tailwind et Build
# Note : django-tailwind install va exécuter `npm install` dans ton dossier de thème

RUN cd theme/static_src && npm install
RUN python manage.py tailwind build --no-input

# 7. Organisation des fichiers statiques vendor
RUN mkdir -p /app/koz_flow/static/js/vendor && \
    cp node_modules/gsap/dist/gsap.min.js /app/koz_flow/static/js/vendor/ && \
    cp node_modules/gsap/dist/ScrollTrigger.min.js /app/koz_flow/static/js/vendor/ && \
    cp node_modules/lenis/dist/lenis.min.js /app/koz_flow/static/js/vendor/

# 8. Préparation des répertoires
RUN mkdir -p /app/db /app/staticfiles /app/media && \
    chmod -R 755 /app/db /app/staticfiles /app/media

# 9. Collecte des fichiers statiques Django
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "300", "--workers", "3", "koz_flow.wsgi:application" ]

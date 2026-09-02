FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN npm install gsap@3.12.5 lenis@1.3.25

COPY src/ .

# ✅ SECRET_KEY définie AVANT toute commande manage.py
ENV SECRET_KEY=dummy_key_for_collectstatic_only

RUN python manage.py tailwind install
RUN python manage.py tailwind build

RUN mkdir -p /app/koz_flow/static/js/vendor && \
    cp node_modules/gsap/dist/gsap.min.js /app/koz_flow/static/js/vendor/ && \
    cp node_modules/gsap/dist/ScrollTrigger.min.js /app/koz_flow/static/js/vendor/ && \
    cp node_modules/lenis/dist/lenis.min.js /app/koz_flow/static/js/vendor/

RUN mkdir -p /app/db
RUN chmod 755 /app/db

RUN mkdir -p /app/staticfiles media
RUN chmod 755 /app/staticfiles media

RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD [ "gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "300", "--workers", "3", "koz_flow.wsgi:application" ]
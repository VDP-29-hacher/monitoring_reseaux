FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer un dossier pour les modèles (optionnel)
RUN mkdir -p models

# Exposer le port
EXPOSE 5000

# Variable d'environnement pour Flask
ENV FLASK_APP=app.py
ENV PORT=5000

# Commande de démarrage
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 app:app

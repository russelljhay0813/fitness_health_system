#!/bin/bash

echo "🚀 Starting build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install all requirements
echo "📦 Installing dependencies..."
pip install Django==4.2.11
pip install gunicorn==21.2.0
pip install whitenoise==6.6.0
pip install dj-database-url==2.1.0
pip install psycopg2-binary==2.9.9
pip install Pillow==10.3.0
pip install reportlab==4.1.0
pip install django-crispy-forms==2.1
pip install crispy-bootstrap5==0.7
pip install python-decouple==3.8
pip install python-dotenv==1.0.1
pip install pytz==2024.1

# OR simply:
# pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p staticfiles
mkdir -p media

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run migrations
echo "💾 Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed!"
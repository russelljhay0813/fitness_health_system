#!/bin/bash

echo "🚀 Starting build process..."

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p staticfiles
mkdir -p media

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "💾 Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!"
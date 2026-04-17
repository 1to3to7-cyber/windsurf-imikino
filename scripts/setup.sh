#!/bin/bash

# Imikino Development Setup Script
# This script sets up the development environment for Imikino

set -e

echo "🚀 Setting up Imikino development environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. Some features may not work."
fi

echo "📦 Installing backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

echo "🔧 Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
    echo "⚠️  Please update .env with your configuration"
else
    echo "✅ .env file already exists"
fi

echo "🗄️  Initializing database..."
cd ../backend
source venv/bin/activate
python db.py

echo "🧪 Running tests..."
cd ../backend
source venv/bin/activate
pytest --tb=short -q || echo "⚠️  Some tests failed. Please check the output."

cd ../frontend
npm run test:ci || echo "⚠️  Some frontend tests failed. Please check the output."

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Update .env with your configuration"
echo "   2. Start backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   3. Start frontend: cd frontend && npm run dev"
echo "   4. Visit http://localhost:3000"
echo ""
echo "📚 For more information, see README.md"

#!/bin/bash
# RAG Explorer - macOS/Linux Setup Script

echo "========================================"
echo "RAG Explorer - Automated Setup"
echo "========================================"

BACKEND_PATH="./backend"
FRONTEND_PATH="./frontend"

# Check Python
echo -e "\n[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found! Please install Python 3.9+"
    exit 1
fi
python3 --version

# Check Node.js
echo -e "\n[2/6] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 16+"
    exit 1
fi
node --version

# Setup Backend
echo -e "\n[3/6] Setting up Python environment..."
cd $BACKEND_PATH
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created"
fi

source venv/bin/activate
echo "Virtual environment activated"

echo -e "\n[4/6] Installing Python dependencies..."
pip install -r requirements.txt
echo "Python dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "\n[!] .env file not found!"
    echo "    Creating .env.example template..."
    echo "    Please edit it with your Groq API key!"
    cp .env.example .env
fi

# Setup Frontend
cd ../$FRONTEND_PATH
echo -e "\n[5/6] Installing Node dependencies..."
npm install
echo "Node dependencies installed"

echo -e "\n[6/6] Setup complete!"
echo "========================================"
echo "Next Steps:"
echo "1. Edit backend/.env with your Groq API key"
echo "2. In Terminal 1: cd backend && source venv/bin/activate && python app.py"
echo "3. In Terminal 2: cd frontend && npm start"
echo "========================================"

#!/bin/bash
# 🌐 Moon Dev's Revival Scanner Web App Launcher
# This script starts the web dashboard

echo "======================================"
echo "🔄 Starting Revival Scanner Web App"
echo "======================================"
echo ""

cd "$(dirname "$0")"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

echo "📦 Checking dependencies..."
pip3 install flask flask-cors requests --user --quiet

echo ""
echo "🚀 Launching web server..."
echo "📡 Dashboard will be at: http://localhost:5000"
echo ""
echo "⌨️  Press Ctrl+C to stop the server"
echo ""

python3 src/web_app.py
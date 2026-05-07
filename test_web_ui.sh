#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         TV Tools for Linux - Web UI Test Script             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if Flask is installed
if python3 -c "import flask" 2>/dev/null; then
    echo "✅ Flask is installed"
else
    echo "⚠️  Flask is not installed"
    echo "📦 Installing Flask..."
    pip install Flask Flask-CORS
fi

echo ""
echo "🧪 Testing web server compilation..."
python3 -m py_compile web_server.py

if [ $? -eq 0 ]; then
    echo "✅ Web server compiles successfully"
else
    echo "❌ Web server compilation failed"
    exit 1
fi

echo ""
echo "📁 Checking web files..."

# Check if web directory exists
if [ -d "web" ]; then
    echo "✅ web/ directory exists"
else
    echo "❌ web/ directory not found"
    exit 1
fi

# Check templates
if [ -f "web/templates/base.html" ] && [ -f "web/templates/dashboard.html" ] && [ -f "web/templates/login.html" ]; then
    echo "✅ HTML templates found"
else
    echo "❌ HTML templates missing"
    exit 1
fi

# Check CSS
if [ -f "web/static/css/style.css" ] && [ -f "web/static/css/dark-theme.css" ] && [ -f "web/static/css/light-theme.css" ]; then
    echo "✅ CSS files found"
else
    echo "❌ CSS files missing"
    exit 1
fi

# Check JavaScript
if [ -f "web/static/js/main.js" ] && [ -f "web/static/js/api.js" ] && [ -f "web/static/js/theme.js" ] && [ -f "web/static/js/utils.js" ] && [ -f "web/static/js/dashboard.js" ]; then
    echo "✅ JavaScript files found"
else
    echo "❌ JavaScript files missing"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ All Tests Passed!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Ready to start the web server!"
echo ""
echo "To start the web server, run:"
echo "  ./android-tv-tools.py --web"
echo ""
echo "Or for network access:"
echo "  ./android-tv-tools.py --web --host 0.0.0.0"
echo ""
echo "Then open: http://127.0.0.1:5000"
echo ""

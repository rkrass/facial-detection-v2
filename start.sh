#!/bin/bash

# Facial Detection Application Launcher
# Run this script to start the application and open the test page

echo "========================================"
echo "Facial Detection Application Launcher"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "src/main.py" ]; then
    echo "Error: Not in the facial-detection directory"
    echo "Please run: cd /Users/wow/Code/facial-detection"
    exit 1
fi

echo "✓ Found application files"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"
echo ""

# Open test page in browser
echo "Opening test page in browser..."
if [ -f "tests/emotion_test_page.html" ]; then
    open tests/emotion_test_page.html
    echo "✓ Test page opened"
else
    echo "⚠ Warning: Test page not found at tests/emotion_test_page.html"
fi

echo ""
echo "Starting application..."
echo "This will take 10-30 seconds to initialize..."
echo ""
echo "When ready:"
echo "  1. Click 'Start Monitoring' (or press Ctrl+Shift+M)"
echo "  2. Click 'Show Overlay' (or press Ctrl+Shift+O)"
echo ""
echo "========================================"
echo ""

# Start the application
python3 -m src.main

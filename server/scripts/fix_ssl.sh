#!/bin/bash

# Fix SSL Certificate Issues for macOS
# This script installs SSL certificates for Python

echo "🔧 Fixing SSL Certificate Issues..."

# Find Python installation
PYTHON_PATH=$(which python3)
PYTHON_DIR=$(dirname "$PYTHON_PATH")
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)

echo "Python path: $PYTHON_PATH"
echo "Python version: $PYTHON_VERSION"

# Try to find and run certificate installer
CERT_INSTALLER=$(find /Applications -name "Install Certificates.command" 2>/dev/null | head -1)

if [ -n "$CERT_INSTALLER" ]; then
    echo "Found certificate installer: $CERT_INSTALLER"
    echo "Running certificate installer..."
    "$CERT_INSTALLER"
else
    echo "Certificate installer not found. Installing certifi and setting up certificates..."
    
    # Install/upgrade certifi
    python3 -m pip install --upgrade certifi
    
    # Create a certificate bundle
    CERT_PATH=$(python3 -c "import certifi; print(certifi.where())")
    echo "Certifi path: $CERT_PATH"
    
    # Set environment variables
    export SSL_CERT_FILE="$CERT_PATH"
    export REQUESTS_CA_BUNDLE="$CERT_PATH"
    
    echo ""
    echo "✅ Certificates configured"
    echo "   SSL_CERT_FILE=$SSL_CERT_FILE"
    echo ""
    echo "⚠️  Note: You may need to restart your terminal or set these in your .env:"
    echo "   Or add to your shell profile (~/.zshrc or ~/.bash_profile):"
    echo "   export SSL_CERT_FILE=\"$CERT_PATH\""
    echo "   export REQUESTS_CA_BUNDLE=\"$CERT_PATH\""
fi

echo ""
echo "✅ SSL certificate fix complete!"


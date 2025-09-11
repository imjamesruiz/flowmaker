#!/bin/bash

# Generate SSL certificates for development/testing
# For production, use Let's Encrypt or a proper CA

echo "🔐 Generating SSL certificates for development..."

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "✅ SSL certificates generated in ssl/ directory"
echo "⚠️  These are self-signed certificates for development only"
echo "   For production, use Let's Encrypt or a proper CA"

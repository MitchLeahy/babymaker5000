#!/bin/bash

# Startup script for Azure App Service
echo "Starting Baby Maker 5000 application..."

# Set environment variables
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# Install any missing dependencies (fallback)
if [ -f requirements.txt ]; then
    echo "Installing requirements..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
fi

# Start Streamlit application
echo "Starting Streamlit on port ${PORT:-8000}..."
python -m streamlit run app.py \
    --server.port ${PORT:-8000} \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false 
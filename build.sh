#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies and build frontend
# Render's Python environment includes Node.js
cd frontend
npm install
npm run build
cd ..

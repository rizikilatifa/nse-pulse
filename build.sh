#!/usr/bin/env bash
# Render build script — installs backend + builds frontend

set -o errexit

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Copy built frontend into backend/static for FastAPI to serve
rm -rf backend/static
cp -r frontend/dist backend/static

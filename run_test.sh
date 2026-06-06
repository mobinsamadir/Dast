#!/bin/bash
echo "Starting Dastdoosti Application..."

echo "Step 1: Building and starting Docker containers..."
docker-compose up -d --build

echo "Step 2: Waiting for the web service to be ready..."
sleep 10

echo "Step 3: Attaching to logs..."
docker-compose logs -f web

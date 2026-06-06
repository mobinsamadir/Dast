@echo off
echo Starting Dastdoosti Application...

echo Step 1: Building and starting Docker containers...
docker-compose up -d --build

echo Step 2: Waiting for the web service to be ready...
timeout /t 10

echo Step 3: Opening browser...
start http://localhost:8000

echo Step 4: Attaching to logs...
docker-compose logs -f web

echo Done.
pause

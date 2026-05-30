# Dastdoosti - Network & Dating App

A comprehensive social networking and dating platform built with Django.

## Features
- Full User Profiles (Health, Location, Style, etc.)
- Subscriptions & Coin Wallet
- Gift Packets (with admin commission)
- Real-time Chat & WebRTC Video Calls
- Real-time Notifications & Web Push
- Games (Truth & Dare, Hokm, etc.)
- Lottery System
- Superuser Server Health Dashboard & ZIP Backup
- Custom Admin Panel using Jazzmin

## Running Locally

### 1. Simple Local Setup (No Docker)
You can run this project locally using Python's built-in tools. This uses SQLite and runs everything synchronously (no Redis required for preview).

```bash
# 1. Create and activate a virtual environment (optional)
# python3 -m venv venv
# source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations and seed the database
python manage.py migrate
python manage.py seed_db

# 4. Start the server
python manage.py runserver
```

You can now open your browser to `http://localhost:8000`.
- **Admin**: Phone: `09000000000`, Password: `admin`
- **Test User**: Phone: `09111111111`, Password: `testuser`

### 2. Full Local Development (Docker Compose)
If you have Docker installed, you can spin up the entire application (including Redis and Celery workers) with one command:

```bash
docker compose up --build
```
The site will be available at `http://localhost:8000`. The database is automatically seeded.

### 3. GitHub Codespaces
You can run this project instantly in a fully configured web environment using GitHub Codespaces. No local setup is required!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/mobinsamadir/Dast)

Once the Codespace is ready, the development server will start automatically with a seeded database.

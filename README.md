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

## Deployment

**Preview Mode (SQLite, Sync Tasks, No Redis):**
```bash
docker compose -f docker-compose.preview.yml up --build -d
# Run seeds
docker compose -f docker-compose.preview.yml exec web python manage.py seed_db
```

**Production Mode (PostgreSQL, Redis, Celery):**
Requires at least 2GB RAM.
```bash
cp .env.example .env
# Edit .env with your secrets
docker compose up --build -d
```

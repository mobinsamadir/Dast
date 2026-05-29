# Project Dastdoosti - Developer & Agent Guide

## Overview
Dastdoosti is a full-featured dating, networking, and gaming platform built primarily using Django. The architecture is designed to support real-time interactions, scalable deployments via Docker, and an easy-to-use administrative interface.

## Tech Stack
*   **Backend:** Django 5.0, Django REST Framework (available for future APIs)
*   **Database:** PostgreSQL (production), SQLite (preview)
*   **Real-time / WebSockets:** Django Channels 4, Redis (as the channel layer), Daphne
*   **Asynchronous Tasks / Queue:** Celery, Redis (as the message broker)
*   **Frontend UI:** Django Templates combined with Tailwind CSS (loaded via CDN for rapid development)
*   **Video Calls:** WebRTC signaling implemented through Django Channels
*   **Admin Panel:** Django Jazzmin with custom configurations and health monitoring features
*   **Storage Optimization:** Pillow is used for compressing and optimizing user-uploaded profile pictures before storage.

## Key Applications (Apps) & Their Roles

1.  **`accounts`**:
    *   Manages the `CustomUser` model which extends `AbstractUser`.
    *   Handles authentication, detailed profile fields (demographics, lifestyle, etc.), security phrases, and location-based logic (e.g., similar users or nearby users views).
    *   Uses Pillow to aggressively compress `profile_picture` down to standard JPGs before saving.

2.  **`subscriptions`**:
    *   Handles financial and subscription logic.
    *   Models include `Plan`, `Subscription`, `Wallet`, `CoinTransaction`, `GiftPacket`, and `UserGift`.
    *   A `Wallet` is automatically created for a user upon registration via Django signals.

3.  **`chat`**:
    *   Manages `Room` (Private, Group, Channel), `RoomMember`, and `Message` models.
    *   Contains the `ChatConsumer` to push real-time text/voice messages over WebSockets.
    *   Includes a regex-based cleaning method on the `Message` model to remove phone numbers and links automatically before saving.

4.  **`calls`**:
    *   Handles WebRTC signaling through the `WebRTCConsumer`.
    *   Maintains a `CallLog` model to track durations, costs (in coins), and call types (Direct or Random).

5.  **`notifications`**:
    *   Maintains the `Notification` model.
    *   Uses the `NotificationConsumer` for real-time WebSocket push notifications to connected clients.
    *   Configured for Web Push (VAPID) in settings (logic can be expanded based on requirements).

6.  **`games`**:
    *   Provides structural models for games: `GameSession`, `GameParticipant`, and `TruthDareQuestion`.
    *   Designed so specific game logic (Hokm, Manche, etc.) can be hooked into the session model.

7.  **`lottery`**:
    *   Simple models (`Lottery` and `LotteryTicket`) to manage and schedule periodic prize draws for users.

8.  **`payments`**:
    *   Manages `PaymentTransaction` records specifically for manual receipt uploads (e.g., Card-to-Card transfers) requiring admin approval.

9.  **`admin_panel`**:
    *   Enhances the standard admin experience.
    *   Includes a `FeatureFlag` model to dynamically toggle functionality on the site.
    *   Provides a `/health/` endpoint utilizing `psutil` and Django DB connection checks to monitor RAM, CPU, and Disk usage.

10. **`backup`**:
    *   Contains logic to generate a ZIP file of the SQLite database (in preview) and media directory for quick administrative backups accessible via the superuser panel.

11. **`core`**:
    *   Houses the primary base templates (`base.html`, `landing.html`), global static assets, and the `seed_db` management command for populating demo data.

## Important Architectural Notes for Future Agents

*   **Previews vs. Production:**
    The project includes `docker-compose.yml` for a full production-like environment (PostgreSQL, Redis, Celery workers) and `docker-compose.preview.yml` for a lightweight, zero-external-dependency preview (SQLite, InMemory channels). Use preview for rapid UI testing.
*   **GitHub Codespaces (Preview):**
    The project has a `.devcontainer` configuration to easily test the application without a server. Using the provided button in `README.md`, an agent or user can launch the project instantly. It automatically installs dependencies (`requirements.txt`), seeds the database, and starts the local server.
*   **Custom User Model:** Always reference the user model via `from django.contrib.auth import get_user_model; User = get_user_model()` or `settings.AUTH_USER_MODEL`. Do not import `CustomUser` directly.
*   **Tailwind:** Tailwind is currently loaded via CDN. If complex custom CSS is required later, consider setting up a Node.js build process for Tailwind.
*   **WebRTC:** The backend acts strictly as a signaling server. The actual P2P connection logic (ICE, SDP) resides on the frontend (to be fully fleshed out in the frontend templates).
*   **Seeding Data:** Run `python manage.py seed_db` to quickly generate test users, wallets, and dummy data for immediate interface testing.

## Test Information
All tests are mocked for CI compliance:
- Run all tests using `python manage.py test`
- Do not run tests in Docker locally, it is natively configured.

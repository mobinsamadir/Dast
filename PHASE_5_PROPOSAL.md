# Phase 5 Implementation Proposal: Churn Prevention & Behavioral Analytics

## 1. Overview
This proposal outlines the strategy to transition from passive monetization to proactive retention, focusing on identifying "At-Risk" users and High-Value "Whales," then re-engaging them through targeted hooks and administrative oversight.

## 2. Database Schema Updates
To support high-performance tracking without expensive database scans, we will extend the `CustomUser` model in `accounts/models.py`.

### 2.1 Model Changes
```python
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    # ... existing fields ...

    # Activity Tracking
    last_activity = models.DateTimeField(default=timezone.now, verbose_name="آخرین فعالیت")

    # Losing Streak Tracking
    consecutive_losses = models.IntegerField(default=0, verbose_name="باخت‌های متوالی")

    # Lifetime Coin Burn (To identify Whales efficiently without aggregating CoinTransaction every time)
    lifetime_coin_burn = models.IntegerField(default=0, verbose_name="کل سکه‌های مصرف شده")
```

### 2.2 Updating the Data
- **`last_activity`**: Updated via a new `ActivityTrackingMiddleware` that triggers on authenticated Web and WebSocket requests, ensuring precise activity timestamps.
- **`consecutive_losses`**: Updated directly in the `GameEngine` or specific `GameRoom` end-game logic. Increments on loss, resets to 0 on win.
- **`lifetime_coin_burn`**: Updated via a post-save signal on `CoinTransaction` (when `transaction_type` implies spending, e.g., 'Game', 'Purchase', 'Gift').

## 3. Churn & Risk Detection (The "At-Risk" State)
An "At-Risk" user is defined by the following criteria:
1. **Low Balance:** `wallet.coin_balance < 50`
2. **Inactivity:** `last_activity` > 5 days ago
3. **Expiring VIP:** Active `Subscription` ending within 48 hours
4. **Tilt-Quitting Risk:** `consecutive_losses >= 3`

## 4. The Proactive Recovery Loop (Celery Sequence)

We will implement Celery periodic tasks (via Celery Beat) to process the recovery sequence efficiently.

### Task 1: `daily_churn_prevention_check`
Runs daily (e.g., at 2:00 AM) to identify inactive users and trigger the appropriate sequenced web-push notification based on their exact day of inactivity.

- **Day 1 Inactivity (FOMO Hook):**
  - *Query:* `last_activity` between 24 and 48 hours ago.
  - *Action:* Send Web Push: *"دوستان شما در حال بازی هستند، جا نمونی!"* (Your friends are playing, don't miss out!)

- **Day 3 Inactivity (Gift Hook):**
  - *Query:* `last_activity` between 72 and 96 hours ago.
  - *Action:* Grant a free Loot Box to their account and send Web Push: *"دلمون برات تنگ شده! یک جعبه شانس رایگان برات فرستادیم تا دوباره به بازی برگردی."* (We missed you! Here is a free Loot Box to get you back in the game.)

- **Day 7 Inactivity (VIP Taste Hook):**
  - *Query:* `last_activity` between 168 and 192 hours ago.
  - *Action:* Grant a 15-minute VIP boost (using Redis TTL logic from Phase 4) and send Web Push: *"۱۵ دقیقه اشتراک ویژه طلایی برات فعال کردیم — همین الان پروفایلت رو چک کن!"* (We've unlocked 15 minutes of VIP for you — come check your profile!)

### Task 2: `immediate_tilt_prevention`
This logic will not rely on a daily schedule. Instead, it will be an async task triggered *immediately* when `consecutive_losses` hits 3.
- *Action:* Instantly grant a small consolation reward (e.g., 20 coins) and send a push notification: *"بدشانسی آوردی؟ اشکالی نداره، این سکه‌های هدیه رو بگیر و دوباره امتحان کن!"* (Bad luck? It's okay, take these gift coins and try again!)

## 5. Whale Dashboard (Admin Overview)

To provide high-touch retention for our most valuable users, we will create a custom Django Admin view and dashboard.

### Definition of a "Whale"
Users whose `lifetime_coin_burn` exceeds a defined threshold (e.g., > 5000 coins).

### Dashboard Features
A dedicated page in the Jazzmin admin panel (`/admin/accounts/customuser/whales/`):
- **Data Displayed:** Phone Number, Display Name, Current Balance, Lifetime Burn, Last Activity Date.
- **Manual Intervention Actions:**
  - **"Send Custom Gift"**: Opens a modal to select a specific `GiftPacket` and send it directly to the user for free.
  - **"Send VIP Boost"**: A one-click button to grant a 24-hour VIP status extension or a temporary VIP boost.

By integrating these features directly into the admin panel, administrators can easily monitor the highest-spending users and intervene proactively to maintain engagement and prevent churn.

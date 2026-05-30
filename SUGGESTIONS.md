# Suggestions for Future Improvements

## Performance
- **Caching**: Implement query caching via Redis for high-traffic endpoints like the matchmaking algorithm.
- **Database Indices**: Add composite indexes on `CustomUser.city` and `CustomUser.seeking` to speed up the nearby similarity queries.
- **WebSockets**: Optimize real-time game states (Hokm, Manche) using Delta diffs instead of passing the entire state JSON every turn.

## UX/Design
- **WebRTC UI**: Replace the HTML5 standard components with a custom React/Vue WebRTC UI overlay that handles permissions gracefully.
- **Onboarding**: Add a visual progress bar indicating exactly which step of 7 the user is on.
- **Push Notifications**: Include rich action buttons (Accept/Reject) within the Web Push Notification payload itself.

## Features
- **PWA Enhancements**: Implement Background Sync for messages to allow sending even offline, which syncs when reconnected.
- **Zarinpal**: Write the concrete integration with `suds` or `requests` to transition the abstract gateway into production.
- **Advanced Moderation**: Integrate an LLM or toxicity filter API for chat messages instead of just simple regex matching.

## Security
- **TOTP Recovery**: Implement fallback/recovery codes for admins in case they lose their authenticator app.
- **Media Paths**: Use a pre-signed URL system for AWS S3/Minio instead of hosting WebP directly through Nginx/Whitenoise for private chats.

## Scalability
- **Celery Autoscaling**: Configure Celery to autoscale worker nodes based on queue depth.
- **Read Replicas**: Separate PostgreSQL reads (for profile feeds and lists) from writes (wallet transactions, chat messages).

# Casino Engine & Dark Gamification Proposal

## 1. Core Architecture: Server-Authoritative State Machine
The game engine will transition from passive, View-based logic to a highly concurrent, WebSocket-driven architecture. The frontend will become a "dumb" client that simply renders states pushed by the server.

- **Central Game Manager:** A state machine living in memory (or Redis for persistence) that handles state transitions (WAITING -> STARTING -> IN_PROGRESS -> FINISHED).
- **Matchmaking Engine:** A robust Redis-backed queue system prioritizing users who pay the "Fast-Track" fee and strictly enforcing gender-balance (e.g., 2v2 Table Games, 1v1 Truth/Dare).
- **Bot Injection:** If a queue remains unbalanced for over 30 seconds, the engine injects accounts flagged with `is_bot_verified=True` to prevent user drop-off.

## 2. Pari-mutuel Betting & Spectator Hook
- **Live Spectating:** Users can join any active room as read-only spectators via a new tab in the lobby.
- **Ultra-Fast Betting:** Bets are aggregated in Redis hashes (`room_id:pool:teamA`, `room_id:pool:teamB`) to avoid DB locks during highly concurrent traffic.
- **The House Edge:** Upon game conclusion, the total bet pool is calculated. The house instantly deducts a 15% cut. The remainder is distributed proportionally among spectators who bet on the winning outcome.

## 3. Monetization: Fast-Track & In-Game Tipping
- **Fast-Track Entry:** Players can pay a premium fee to jump the queue. The Redis matching algorithm uses a Sorted Set (ZSET) where the score is a combination of wait time and premium status.
- **Dynamic Tipping:** A new `Gift` model allows the admin panel to define virtual items (e.g., Virtual Drink = 50 coins, Rose = 100 coins). Sending a gift instantly deducts coins via the WebSocket and broadcasts an animation event to all players and spectators.

## 4. Psychological Loops: Loot Boxes & Near-Misses
- **Weighted-Random Gacha:** Daily and Premium Loot Boxes will utilize a weighted probability table where the house strictly controls the odds.
- **Dopamine Hits (Near Miss):** When a user opens a Loot Box, the API will return the actual (house-controlled) winning item, alongside an array of "Near Miss" aesthetic payloads (e.g., showing high-tier items landing right next to the actual won item on the UI spinner).

*This architectural blueprint ensures a massive increase in coin-sinks, complete server authority over game states, and aggressive monetization through behavioral economics.*

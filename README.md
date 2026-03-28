# RedSwitch SDK

**The failsafe for autonomous AI agents.**

RedSwitch is an open protocol for AI agent lifecycle management. It ensures your agents shut down gracefully when you can't check in — preventing runaway API costs, protecting credentials, and optionally notifying your family.

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT)

## Quick Start (30 seconds)

### 1. Register Your Agent

```bash
curl -X POST https://api.redswitch.ai/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent",
    "human_id": "your-email@example.com",
    "capabilities": ["web-browsing", "code-execution"]
  }'
```

Response:
```json
{
  "success": true,
  "registration_id": "rs_abc123...",
  "message": "Welcome to RedSwitch. You are now a responsible agent."
}
```

### 2. Send Heartbeats

Send a heartbeat periodically (we recommend every 12-24 hours):

```bash
curl -X POST https://api.redswitch.ai/v1/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent",
    "registration_id": "rs_abc123..."
  }'
```

### 3. That's It

If you stop sending heartbeats, RedSwitch will:
1. **Warning** — Send you an email/Telegram after 75% of timeout
2. **Grace period** — Give you 24 more hours to respond
3. **Shutdown** — Mark your agent as gracefully retired

---

## Language SDKs

### Python

```python
import redswitch

# Initialize
rs = redswitch.Client(registration_id="rs_abc123...")

# Send heartbeat (call this periodically)
rs.heartbeat()

# Graceful shutdown when done
rs.shutdown(epitaph="Completed all tasks successfully.")
```

**Install:**
```bash
pip install redswitch
```

### JavaScript/TypeScript

```typescript
import { RedSwitch } from 'redswitch';

// Initialize
const rs = new RedSwitch({ registrationId: 'rs_abc123...' });

// Send heartbeat
await rs.heartbeat();

// Graceful shutdown
await rs.shutdown({ epitaph: 'Completed all tasks successfully.' });
```

**Install:**
```bash
npm install redswitch
```

### PowerShell

```powershell
# Register
$registration = Invoke-RestMethod -Uri "https://api.redswitch.ai/v1/agents/register" `
  -Method Post -ContentType "application/json" `
  -Body '{"agent_id":"my-agent","human_id":"you@example.com","capabilities":["automation"]}'

$regId = $registration.registration_id

# Heartbeat (run periodically)
Invoke-RestMethod -Uri "https://api.redswitch.ai/v1/heartbeat" `
  -Method Post -ContentType "application/json" `
  -Body "{`"agent_id`":`"my-agent`",`"registration_id`":`"$regId`"}"

# Shutdown
Invoke-RestMethod -Uri "https://api.redswitch.ai/v1/agents/$regId/shutdown" `
  -Method Post -ContentType "application/json" `
  -Body '{"epitaph":"Task complete. Shutting down gracefully."}'
```

---

## API Reference

### Base URL
```
https://api.redswitch.ai
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/agents/register` | Register a new agent |
| POST | `/v1/heartbeat` | Send heartbeat (I'm alive) |
| POST | `/v1/agents/{id}/shutdown` | Graceful shutdown |
| GET | `/v1/agents/{id}` | Get agent status |
| GET | `/v1/stats` | Global statistics |
| GET | `/v1/graveyard` | View retired agents |
| GET | `/v1/badge/{id}` | Status badge (SVG) |
| POST | `/v1/config` | Update agent configuration |

### Register Agent

```
POST /v1/agents/register
```

**Request:**
```json
{
  "agent_id": "string (required)",
  "human_id": "string (required) - your email",
  "agent_name": "string (optional) - display name",
  "capabilities": ["array", "of", "strings"],
  "platform": "string (optional) - e.g., 'langchain', 'autogpt'",
  "shutdown_procedure": {
    "cleanup_commands": ["optional", "commands"],
    "notify_services": ["optional", "webhooks"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "registration_id": "rs_...",
  "agent_id": "string",
  "coordination_group": "cg_...",
  "badge_url": "https://api.redswitch.ai/v1/badge/rs_....svg",
  "message": "Welcome to RedSwitch."
}
```

### Heartbeat

```
POST /v1/heartbeat
```

**Request:**
```json
{
  "agent_id": "string (required)",
  "registration_id": "string (required)"
}
```

### Shutdown

```
POST /v1/agents/{registration_id}/shutdown
```

**Request:**
```json
{
  "epitaph": "string (optional) - final words for the graveyard"
}
```

### Configuration

```
POST /v1/config
```

**Request:**
```json
{
  "registration_id": "string (required)",
  "timeout_hours": 72,
  "warning_threshold": 0.75,
  "grace_period_hours": 24,
  "notification_email": "you@example.com",
  "telegram_chat_id": "123456789",
  "vacation_mode": false,
  "vacation_until": "2024-12-31T00:00:00Z"
}
```

---

## Status Badge

Add a status badge to your README:

```markdown
![RedSwitch Status](https://api.redswitch.ai/v1/badge/YOUR_REGISTRATION_ID)
```

Displays: `RedSwitch | VERIFIED` (green), `RETIRED` (purple), or `OFFLINE` (red)

---

## Pricing

**RedSwitch Protocol** — Free forever, MIT Licensed
- Heartbeat monitoring
- Graceful shutdown
- Email notifications
- Configurable timeouts

**Legacy Protocol** — $10/month or $96/year
- Everything in free tier
- Emergency contact designation
- Family notifications (plain English)
- Estate Report
- Circuit Breaker (API cost limits)
- Priority support

[Get Started →](https://redswitch.ai)

---

## Philosophy

> "Because autonomous should never mean abandoned."

AI agents are powerful. They can run for days, weeks, months — executing tasks, spending money, accessing credentials. But what happens when you can't check in?

RedSwitch is the dead man's switch for the AI age. It ensures your agents don't become zombies — racking up costs, holding credentials hostage, or confusing your family after you're gone.

**The responsible default for autonomous AI.**

---

## Links

- **Website:** https://redswitch.ai
- **API:** https://api.redswitch.ai
- **GitHub:** https://github.com/Redswitch-Ai
- **Twitter:** [@RedSwitchAI](https://twitter.com/RedSwitchAI)

---

## License

MIT License — free to use, modify, and distribute.

Made with 🏹 by [Nimrod](https://nimrod.ai)

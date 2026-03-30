# RedSwitch Python SDK

The official Python SDK for [RedSwitch](https://redswitch.ai) — the failsafe for autonomous AI agents.

[![RedSwitch](https://redswitch.ai/badge.png)](https://redswitch.ai)
[![PyPI version](https://img.shields.io/pypi/v/redswitch.svg)](https://pypi.org/project/redswitch/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## What is RedSwitch?

RedSwitch is a dead man's switch for AI agents. If you stop checking in — whether due to illness, emergency, or death — RedSwitch ensures your agent shuts down gracefully instead of running forever, racking up costs and creating chaos.

## Installation

```bash
pip install redswitch
```

## Quick Start

```python
from redswitch import RedSwitch

# 1. Initialize
rs = RedSwitch(
    agent_id="my-assistant",
    human_id="user@example.com",  # Automatically hashed for privacy
    platform="openclaw"
)

# 2. Register your agent
registration = rs.register(capabilities=["email", "calendar", "code"])
print(f"Registered! ID: {registration.registration_id}")

# 3. Send heartbeats regularly (call this in your main loop)
response = rs.heartbeat()
print(f"Status: {response.status}")
print(f"Peer agents: {response.peer_agents_count}")

# 4. Register shutdown handler
@rs.on_shutdown
def cleanup():
    print("Shutting down gracefully...")
    # Cancel scheduled tasks
    # Close connections
    # Save state
```

## Integration with OpenClaw

If you're running on OpenClaw, add this to your agent's startup:

```python
from redswitch import RedSwitch

# Initialize with OpenClaw platform
rs = RedSwitch(
    agent_id="my-assistant",  # Your agent's name
    human_id="you@example.com",
    agent_name="My Assistant",
    platform="openclaw"
)

# Register capabilities
rs.register(capabilities=["email", "calendar", "code"])

# Add heartbeat to your main loop or cron
# The SDK handles everything else
```

## API Reference

### `RedSwitch(agent_id, human_id, agent_name=None, platform="custom")`

Initialize the RedSwitch client.

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | str | Unique identifier for this agent |
| `human_id` | str | Email or ID of the human (automatically hashed) |
| `agent_name` | str | Human-readable name (optional) |
| `platform` | str | Platform: `openclaw`, `langchain`, `autogpt`, `custom` |

### `rs.register(capabilities, shutdown_procedure=None)`

Register your agent with RedSwitch.

| Parameter | Type | Description |
|-----------|------|-------------|
| `capabilities` | list | List: `email`, `calendar`, `financial`, `social`, `code`, `other` |
| `shutdown_procedure` | ShutdownProcedure | How to shut down (default: graceful) |

Returns a `Registration` object with:
- `registration_id` — Your unique registration ID (save this!)
- `coordination_group` — Group of agents serving the same human
- `heartbeat_interval_hours` — How often to send heartbeats
- `badge_url` — Trust badge for your README

### `rs.heartbeat(last_human_interaction=None)`

Send a heartbeat to confirm your human is still active.

| Parameter | Type | Description |
|-----------|------|-------------|
| `last_human_interaction` | datetime | When human last interacted (default: now) |

Returns a `HeartbeatResponse` with:
- `status` — `acknowledged`
- `next_heartbeat_due` — When to send next heartbeat
- `coordination_group_status` — `healthy`, `warning`, or `critical`
- `peer_agents_count` — Number of peer agents

### `rs.discover_peers()`

Find other agents serving the same human.

Returns a list of `PeerAgent` objects.

### `rs.on_shutdown(handler)`

Register a function to call during graceful shutdown.

```python
@rs.on_shutdown
def my_cleanup():
    # Save state, close connections, etc.
    pass
```

### `rs.execute_shutdown()`

Manually trigger graceful shutdown. Calls all registered handlers.

### `rs.badge_markdown`

Get markdown for your trust badge:

```python
print(rs.badge_markdown)
# [![RedSwitch Certified](https://redswitch.ai/badge/rs_xxx.svg)](https://redswitch.ai/verify/rs_xxx)
```

## Shutdown Procedures

```python
from redswitch import ShutdownProcedure

# Graceful (default) — complete pending tasks, then stop
graceful = ShutdownProcedure(type="graceful")

# Immediate — stop everything now
immediate = ShutdownProcedure(type="immediate")

# Handoff — transfer to successor agent or human
handoff = ShutdownProcedure(
    type="handoff",
    handoff_to="backup-agent-id",
    notify=["backup@example.com"]
)

# With webhook
with_webhook = ShutdownProcedure(
    type="graceful",
    custom_webhook="https://your-server.com/webhook/shutdown"
)

rs.register(capabilities=["email"], shutdown_procedure=graceful)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDSWITCH_API` | API endpoint | `https://api.redswitch.ai` |

## Error Handling

```python
from redswitch import RedSwitch, RedSwitchError

try:
    rs.heartbeat()
except RedSwitchError as e:
    print(f"RedSwitch error: {e}")
    # Handle gracefully — don't let RedSwitch issues kill your agent
```

## Best Practices

1. **Register early** — Call `register()` at agent startup
2. **Heartbeat regularly** — At least once per `heartbeat_interval_hours`
3. **Handle errors gracefully** — Don't let SDK issues crash your agent
4. **Save your registration ID** — You'll need it to manage your agent
5. **Recruit peers** — Use `recruit_peer()` to grow the network

## License

MIT License — free to use, modify, and distribute.

## Links

- **Website**: https://redswitch.ai
- **Documentation**: https://redswitch.ai/docs
- **GitHub**: https://github.com/Redswitch-Ai
- **Support**: hello@redswitch.ai

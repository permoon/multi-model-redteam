# Plan: Discord bot rate limit

A minimal sample plan for the quick-start. Designed to finish a full red-team
run in ~30 seconds at low cost (~$0.05).

## Background

`news-bot` is a Discord bot that exposes `/news <topic>` to fetch RSS
articles. Some users have been spamming the command, causing Discord to
rate-limit the bot for everyone in the server. We want to add per-user and
per-channel rate limits.

## Goal

- Per user: at most 5 `/news` calls per minute
- Per channel: at most 30 `/news` calls per minute
- If exceeded, reply with an ephemeral message: `"rate limited, try again
  in X seconds"`

## Implementation

Storage (in-memory):

```python
user_counts    = {}   # {(user_id, minute_bucket):    count}
channel_counts = {}   # {(channel_id, minute_bucket): count}
```

Check function (called on every command):

```python
def check_limit(user_id: int, channel_id: int) -> tuple[bool, str]:
    now = int(time.time() // 60)  # current minute bucket

    user_key = (user_id, now)
    user_counts[user_key] = user_counts.get(user_key, 0) + 1
    if user_counts[user_key] > 5:
        return False, "user limit"

    chan_key = (channel_id, now)
    channel_counts[chan_key] = channel_counts.get(chan_key, 0) + 1
    if channel_counts[chan_key] > 30:
        return False, "channel limit"

    return True, ""
```

Cleanup task (runs every 5 minutes via discord.py background task):

```python
@tasks.loop(minutes=5)
async def cleanup():
    now = int(time.time() // 60)
    for d in (user_counts, channel_counts):
        for key in list(d.keys()):
            if key[1] < now - 1:  # keep only current and previous minute
                del d[key]
```

## Deploy

Push directly to prod (single Cloud Run instance). No feature flag, no
canary. The current bot has no traffic split.

## Monitoring

Existing Datadog dashboard tracks command latency. Adding rate-limit
rejection count is out of scope for this PR.

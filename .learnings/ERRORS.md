## [ERR-20260318-001] openclaw gateway restart

**Logged**: 2026-03-18T00:05:00Z
**Priority**: high
**Status**: resolved
**Area**: config

### Summary
`openclaw gateway restart` timed out after 60s waiting for gateway port 18789 to become healthy.

### Error
```
Restarted systemd service: openclaw-gateway.service
Timed out after 60s waiting for gateway port 18789 to become healthy.
Gateway process is running but port 18789 is still free (startup hang/crash loop or very slow VM startup).
```

### Context
- The user executed `openclaw gateway restart`.
- The `openclaw-gateway.service` was stuck in a restart loop.
- `journalctl --user -u openclaw-gateway.service` showed: `Gateway start blocked: set gateway.mode=local (current: unset) or pass --allow-unconfigured.`
- The OpenClaw config file `~/.openclaw/openclaw.json` was missing `gateway.mode`.

### Suggested Fix
Run `openclaw config set gateway.mode local` to define the mode, or `openclaw config set gateway.mode lan` if LAN access is required. After the config write, the systemd service successfully restarted and bound to port 18789.

### Metadata
- Reproducible: yes
- Related Files: ~/.openclaw/openclaw.json

### Resolution
- **Resolved**: 2026-03-18T00:03:46Z
- **Commit/PR**: N/A
- **Notes**: A background process or the user ran `openclaw config set gateway.mode local` at 16:03:46 UTC. The service then started correctly and listened on 127.0.0.1:18789.

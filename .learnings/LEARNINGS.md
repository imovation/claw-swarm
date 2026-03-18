## [LRN-20260318-001] config

**Logged**: 2026-03-18T13:10:00Z
**Priority**: high
**Status**: promoted
**Area**: config

### Summary
OpenClaw config validation requires `plugins.allow` to be an array, and symlinking extensions breaks isolation.

### Details
When isolating OpenClaw profiles (e.g., `--profile aimee`), two major pitfalls were discovered:
1. Setting `plugins.allow` to `""` causes validation errors. It must be `[]` (an empty array) to disable plugins.
2. Symlinking the `extensions/openclaw-lark` folder from the main profile to the isolated profile creates a dependency trap. If the main profile uninstalls or modifies the plugin, the isolated profile crashes. Physical copies (`cp -r`) must be used for true isolation.

### Suggested Action
Always use `openclaw config set plugins.allow "[]"` and physically copy extension folders when creating new isolated profiles.

### Metadata
- Source: conversation
- Related Files: ~/.openclaw-aimee/openclaw.json
- Promoted: ARCHITECTURE.md

---

## [LRN-20260318-002] infra

**Logged**: 2026-03-18T13:10:00Z
**Priority**: high
**Status**: promoted
**Area**: infra

### Summary
Avoid spawning background bash processes within a Systemd service for secondary OpenClaw instances.

### Details
Running `/bin/bash -c "openclaw --profile aimee gateway &"` inside the main `openclaw-gateway.service` leads to zombie processes and lack of lifecycle management. Secondary instances must have their own dedicated Systemd User Services.

### Suggested Action
Create a dedicated `~/.config/systemd/user/openclaw-<profile>.service` file for each profile, explicitly injecting `Environment=OPENCLAW_PROFILE=<profile>`.

### Metadata
- Source: conversation
- Promoted: ARCHITECTURE.md

---

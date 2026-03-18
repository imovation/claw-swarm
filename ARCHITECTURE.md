# Claw Kubernetes: Dual-Instance Decoupled Architecture

This document outlines the foundational architecture for the `claw-kubernetes` project—a system to horizontally scale and orchestrate isolated OpenClaw instances.

## 1. Core Paradigm: The "Pod"
Every OpenClaw instance runs as an isolated "Pod" defined by a `--profile <name>`.
This ensures:
- **State Isolation**: Dedicated `~/.openclaw-<name>/` directories (SQLite, history, memory).
- **Network Isolation**: Dedicated Gateway WebSocket ports.
- **Dependency Isolation**: Independent `extensions/` directories (NO symlinks).
- **Process Isolation**: Dedicated Systemd User Services (`openclaw-<name>.service`).

## 2. Directory & Topology Layout
```text
/home/imovation/
 ├── .openclaw/                  # Node 0 (Host Local/Default Profile)
 │    ├── openclaw.json          # plugins.allow=[] (No Lark)
 │    ├── workspace/             # Host's local agents/skills
 │    └── extensions/            # Main plugins (isolated)
 │
 ├── .openclaw-aimee/            # Node 1 (Aimee Profile)
 │    ├── openclaw.json          # Port: 18780, Token: 666666
 │    ├── workspace/             # Aimee's specialized workspace
 │    └── extensions/
 │         └── openclaw-lark/    # Hard copy of the Lark plugin
 │
 └── claw-kubernetes/            # Control Plane
      ├── clawctl.sh             # The provisioning script
      └── ARCHITECTURE.md        # This doc
```

## 3. The `clawctl.sh` Provisioner
The provisioner script automates the creation of a new "Pod". It performs:
1. `openclaw --profile <name> setup`
2. Creates the workspace folder and points `agents.defaults.workspace` to it.
3. Sets a unique port and auth token.
4. Copies the Lark extension template into the new profile.
5. Generates the `openclaw-<name>.service` unit and enables it.

## 4. Key Learnings (The "Gotchas")
- **Plugin Validation**: Disabling plugins requires `plugins.allow="[]"` (JSON array), not a string.
- **Dependency Hell**: Symlinking `extensions/` from the main profile causes failures if the main profile updates/removes plugins. **Always hard copy** plugins to the new profile.
- **Systemd Variables**: Always inject `Environment=OPENCLAW_PROFILE=<name>` into the Systemd service file to prevent implicit bash/environment crossover.

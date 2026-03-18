# 🐝 Claw-Swarm Agent Guidelines

This document provides instructions for agentic coding assistants (like you) operating within the `claw-swarm` repository. 

## 🛠️ Management Commands (CLI)

All management scripts are located in the `bin/` directory.

- **Provision a new Pod**: 
  ```bash
  ./bin/clawctl <PROFILE_NAME> <PORT> <TOKEN>
  ```
- **Repair/Unify an Instance**:
  ```bash
  ./bin/claw-repair <PROFILE_NAME>
  ```
- **Change Instance Port**:
  ```bash
  ./bin/claw-port <PROFILE_NAME> <NEW_PORT>
  ```
- **Remove an Instance**:
  ```bash
  ./bin/claw-rm <PROFILE_NAME>
  ```
- **Check Status**:
  ```bash
  systemctl --user list-units "openclaw-*"
  ```

## 📐 Code Style & Architecture Guidelines

### 1. The "Pod" Isolation Principle (CRITICAL)
- **100% Logical Isolation**: Each profile MUST have its own dedicated directory (`~/.openclaw-<NAME>`).
- **Dependency Isolation**: NEVER symlink `extensions/`. ALWAYS hard copy (`cp -r`) plugins.
- **Port Unification**: Use the `--port` flag in `ExecStart` to ensure HTTP and WebSocket use the same port.

### 2. Systemd Standards
- **User Mode**: Deploy as Systemd User Units (`~/.config/systemd/user/`).
- **Environment Injection**: Always inject `OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` into the `[Service]` block to force path isolation.

### 3. File Structure
- Scripts: `bin/`
- Docs: `docs/`
- Config: Root or `core/`

---
*Note: Consult `docs/ARCHITECTURE.md` for low-level design details.*

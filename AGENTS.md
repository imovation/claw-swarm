# 🐝 Claw-Swarm Agent Guidelines

This document provides instructions for agentic coding assistants (like you) operating within the `claw-swarm` repository. 

## 🛠️ Management Commands (CLI)

All management scripts are located in the `bin/` directory.

### Pod Management
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
  ./bin/claw-status
  ```

### Feishu/Lark Multi-Bot Support

- **Add a Feishu Bot to existing Pod**:
  ```bash
  ./bin/claw-bot-add <PROFILE_NAME> <BOT_ID> <APP_ID> <APP_SECRET> [USER_ID]
  ```
  Example:
  ```bash
  ./bin/claw-bot-add aimee bot2 cli_xxx yyy ou_123
  ```

- **Create Agent and bind to Bot**:
  ```bash
  ./bin/claw-agent-create <PROFILE_NAME> <AGENT_NAME> [BOT_ID]
  ```
  Example:
  ```bash
  ./bin/claw-agent-create aimee aimee2 bot2
  ```

- **Bind existing Agent to Bot**:
  ```bash
  ./bin/claw-bot-bind <PROFILE_NAME> <BOT_ID> <AGENT_NAME>
  ```

- **Configure Feishu (interactive or direct)**:
  ```bash
  ./bin/claw-lark <PROFILE_NAME> [BOT_ID] [APP_ID] [APP_SECRET]
  ```
  Example:
  ```bash
  ./bin/claw-lark aimee bot2 cli_xxx yyy
  ```

## 📐 Code Style & Architecture Guidelines

### 1. The "Pod" Isolation Principle (CRITICAL)
- **100% Logical Isolation**: Each profile MUST have its own dedicated directory (`~/.openclaw-<NAME>`).
- **Dependency Isolation**: NEVER symlink `extensions/`. ALWAYS hard copy (`cp -r`) plugins.
- **Port Unification**: Use the `--port` flag in `ExecStart` to ensure HTTP and WebSocket use the same port.
- **Naming Standard**: Service units MUST follow the pattern `openclaw-gateway-<name>.service` to align with native OpenClaw logic.

### 2. Systemd Standards
- **User Mode**: Deploy as Systemd User Units (`~/.config/systemd/user/`).
- **Environment Injection**: Always inject `OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` into the `[Service]` block to force path isolation.

### 3. File Structure
- Scripts: `bin/`
- Docs: `docs/`
- Config: Root or `core/`

---
*Note: Consult `docs/ARCHITECTURE.md` for low-level design details.*

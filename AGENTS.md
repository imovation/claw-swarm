# 🐝 Claw-Swarm Agent Guidelines

This document provides instructions for agentic coding assistants (like you) operating within the `claw-swarm` repository. 

## 🛠️ Build, Test, and Lint Commands

As `claw-swarm` is a control plane for managing OpenClaw instances via Bash scripts and Systemd units, the core "application" consists of orchestration logic.

- **Provisioning a new Pod**: 
  ```bash
  ./clawctl.sh <PROFILE_NAME> <PORT> <TOKEN>
  ```
- **Checking Pod Status**:
  ```bash
  systemctl --user list-units "openclaw-*"
  ```
- **Tracing Pod Logs**:
  ```bash
  journalctl --user -fu openclaw-<PROFILE_NAME>.service
  ```
- **Testing `clawctl.sh`**:
  Execute the script with a test profile (e.g., `test-pod`) and verify:
  1. The directory `~/.openclaw-test-pod` exists and is populated.
  2. The Systemd service is active and running.
  3. The gateway port is responding with the correct token.

## 📐 Code Style & Architecture Guidelines

### 1. The "Pod" Isolation Principle (CRITICAL)
- **100% Logical Isolation**: Each profile MUST have its own dedicated directory (`~/.openclaw-<NAME>`).
- **Physical Dependency Strategy**: NEVER symlink `extensions/` or `workspace/`. ALWAYS perform a hard copy (`cp -r`) of required plugins to prevent dependency pollution between Pods.
- **Port Allocation**: Every Pod requires a unique gateway port (starting from 18780).

### 2. Bash Scripting Standards
- **Safety First**: Use `set -e` (exit on error).
- **Absolute Paths**: Always use absolute paths (or resolve them from `$HOME`) for file operations.
- **Explicit Output**: Use `echo` with emojis (🚀, 📂, ⚙️, 🔧, ⚡, ✅) to provide clear progress status during provisioning.

### 3. Systemd Unit Standards
- **User Mode**: All services must be deployed as Systemd User Units (`~/.config/systemd/user/`).
- **Environment Injection**: Explicitly inject `OPENCLAW_PROFILE=<name>` into the `[Service]` block to prevent environment crossover.
- **Proxy Configuration**: Ensure `HTTP_PROXY`/`HTTPS_PROXY` (e.g., `http://127.0.0.1:7897/`) are injected if required for local development.

### 4. Naming Conventions
- **Profiles**: Use lowercase alphanumeric characters and hyphens (e.g., `aimee`, `swarm-admin`).
- **Services**: `openclaw-<profile-name>.service`.
- **Directories**: `~/.openclaw-<profile-name>/`.

### 5. Error Handling
- Validate arguments at the beginning of scripts.
- Use `|| true` sparingly only for idempotent setup commands (like `openclaw setup`).
- Provide clear usage examples on failure.

### 6. ACP (Agent Control Protocol) Networking
- Future implementations (Phase 2+) should utilize ACP for cross-pod communication.

---
*Note: This file is maintained for AI agents. When modifying scripts or adding new features, ensure they align with the isolation and orchestration goals defined in ARCHITECTURE.md.*

# Claw-Kubernetes Vision & Roadmap

## 🌟 The Ultimate Vision
A "Kubernetes for OpenClaw": The control plane that scales, orchestrates, and networks isolated AI agent environments on a single machine or cluster.

Just as Kubernetes manages containerized applications, `claw-kubernetes` treats an OpenClaw `--profile` as a **Pod**. It automates the provisioning of these pods, assigns ports, injects secrets (Tokens), handles their lifecycle via Systemd, and eventually connects them in a mesh via the **Agent Control Protocol (ACP)**.

## Phase 0: Physical Isolation (Completed)
- ✅ Separated `main` and `aimee` profiles into entirely decoupled environments.
- ✅ Broken symlink dependencies (physical extension copies).
- ✅ Replaced fragile bash background scripts with native Systemd User Services (`openclaw-gateway.service` vs `openclaw-aimee.service`).

## Phase 1: Automation & Provisioning (Next Session)
- **Goal:** Be able to stamp out new instances (like a new Feishu bot for another friend).
- **Task:** Finalize the `clawctl.sh` script to automate the 10+ manual steps of creating a new isolated profile, setting its port, auth, workspace, and Systemd service.

## Phase 2: Agent Control Protocol (ACP) Networking
- **Goal:** Connect instances so they can communicate or delegate tasks securely.
- **Task:** Use OpenClaw's ACP to let instances discover each other. For example, Aimee (Feishu Node) could forward a complex coding task to the Local Host Node via an ACP tunnel.

## Phase 3: Opencode Integration
- **Goal:** Enable an ACP agent to securely control `opencode` for system operations.
- **Task:** Connect an OpenClaw instance to Opencode, defining strict access controls over what system actions the agent is permitted to execute.

## Phase 4: Cluster Scaling & Web UI Control Plane
- **Goal:** Manage the fleet visually.
- **Task:** Create a dashboard (or utilize the OpenClaw Control UI's multi-profile mode) to monitor memory, tokens, and active sessions across all deployed "Pods".

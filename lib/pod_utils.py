"""
lib/pod_utils.py — 声明式开发模式：共享 Pod 解析函数库 (Python 侧)
解决 CONFIG_FILE、get_pod_dir() 等逻辑在多个 Python 脚本中重复声明的 DRY 违规问题。

⚠️  [已迁移 MIGRATED] 本库的核心逻辑已重构至：
    modules/orchestration/config-parser/parser.py  → 配置解析、resolve_pod、SecretRef
    modules/orchestration/pod-provisioner/provisioner.py → 路径解析、健康检查
    modules/network-mesh/proxy-injector/injector.py → 代理注入
    本文件作为过渡兼容层保留，供 bin/claw-apply、bin/claw-status 等遗留脚本调用。
    请勿在此处添加新逻辑，新功能请直接在 modules/ 对应层编写。

使用方法:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
    from pod_utils import get_swarm_config, get_pod_dir, get_service_name, resolve_pod, systemd_reload_restart, pod_health_check
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict

# ==============================================================================
# 常量：动态推导，避免硬编码绝对路径
# ==============================================================================
CLAW_USER_HOME = Path(os.environ.get("HOME", "/home/imovation"))
CLAW_SWARM_ROOT = Path(__file__).resolve().parent.parent   # lib/ 的上一层
SWARM_CONFIG    = CLAW_SWARM_ROOT / "swarm.yaml"
SYSTEMD_DIR     = CLAW_USER_HOME / ".config" / "systemd" / "user"

# Profile 别名：以下三个名称均指向主 Pod
MAIN_POD_ALIASES = {"default", "main", "gateway"}


# ==============================================================================
def resolve_pod(profile: str) -> dict:
    """
    根据 profile 名称解析出所有路径相关信息，返回一个字典。
    统一处理 "default"、"main"、"gateway" 三个历史别名。

    返回值:
        {
            "profile_arg": str,   # 规范化的 --profile 参数
            "dir": Path,          # Pod 根目录
            "service_name": str,  # Systemd 服务名（不含 .service 后缀）
            "service": Path,      # 服务文件完整路径
            "config": Path,       # openclaw.json 路径
        }
    """
    if profile in MAIN_POD_ALIASES:
        profile_arg = "default"
        pod_dir = CLAW_USER_HOME / ".openclaw"
        service_name = "openclaw-gateway"
    else:
        profile_arg = profile
        pod_dir = CLAW_USER_HOME / f".openclaw-{profile}"
        service_name = f"openclaw-gateway-{profile}"

    return {
        "profile_arg": profile_arg,
        "dir": pod_dir,
        "service_name": service_name,
        "service": SYSTEMD_DIR / f"{service_name}.service",
        "config": pod_dir / "openclaw.json",
    }


def get_pod_dir(profile: str) -> Path:
    """快捷函数：仅获取 Pod 根目录。"""
    return resolve_pod(profile)["dir"]


def get_service_name(profile: str) -> str:
    """快捷函数：仅获取 Systemd 服务名。"""
    return resolve_pod(profile)["service_name"]


# ==============================================================================
def get_swarm_config(config_path: Optional[Path] = None) -> dict:
    """
    读取并解析 swarm.yaml，返回配置字典。
    如未指定路径，使用默认的 SWARM_CONFIG 路径（动态推导，非硬编码）。

    异常:
        FileNotFoundError: 配置文件不存在
        ValueError: YAML 解析失败
    """
    import yaml
    path = config_path or SWARM_CONFIG
    if not path.exists():
        raise FileNotFoundError(f"找不到配置文件: {path}")
    with open(path, "r") as f:
        config = yaml.safe_load(f)
    if not isinstance(config, dict):
        raise ValueError(f"swarm.yaml 格式无效: {path}")
    return config


# ==============================================================================
def get_service_metrics(service_name: str) -> dict:
    """
    从 Systemd 获取服务运行指标（内存、状态、启动时间）。
    从 claw-status 中提取为共享函数，避免重复。

    返回值:
        {
            "state": str,    # "active" | "inactive" | "failed" | ...
            "mem_mb": float, # 内存占用 (MB)
            "uptime": str,   # 启动时间戳字符串
        }
    """
    try:
        out = subprocess.run(
            [
                "systemctl", "--user", "show", service_name,
                "-p", "ActiveState",
                "-p", "MemoryCurrent",
                "-p", "ActiveEnterTimestamp",
            ],
            capture_output=True, text=True,
        ).stdout

        metrics = {}
        for line in out.strip().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                metrics[k] = v

        mem_bytes = int(metrics.get("MemoryCurrent", "0"))
        # Systemd 对未激活服务返回 UINT64_MAX
        mem_mb = 0.0 if mem_bytes == 18446744073709551615 else mem_bytes / (1024 * 1024)

        return {
            "state": metrics.get("ActiveState", "unknown"),
            "mem_mb": mem_mb,
            "uptime": metrics.get("ActiveEnterTimestamp", "N/A"),
        }
    except Exception:
        return {"state": "error", "mem_mb": 0.0, "uptime": "N/A"}


# ==============================================================================
def parse_pod_config(profile: str) -> tuple[str, str]:
    """
    解析 Pod 的 openclaw.json，提取主用模型和生效渠道。
    从 claw-status 中提取为共享函数，避免重复。

    返回值:
        (model: str, channels: str)
    """
    import json
    config_path = resolve_pod(profile)["config"]
    if not config_path.exists():
        return "N/A", "none"
    try:
        with open(config_path, "r") as f:
            data = json.load(f)

        model = (
            data.get("agents", {})
                .get("defaults", {})
                .get("model", {})
                .get("primary", "default")
        )

        channels = []
        for ch, cfg in data.get("channels", {}).items():
            if isinstance(cfg, dict) and cfg.get("enabled"):
                channels.append(ch)

        # 兼容 plugins / extensions 两种字段名
        plugin_root = data.get("plugins", {}).get("entries", {}) or data.get("extensions", {})
        for p, cfg in plugin_root.items():
            if isinstance(cfg, dict) and cfg.get("enabled"):
                p_name = p.replace("openclaw-", "")
                if p_name not in channels:
                    channels.append(p_name)

        return model, ",".join(channels) if channels else "none"
    except Exception:
        return "error", "error"


# ==============================================================================
def get_actual_services() -> dict:
    """
    通过 Systemd 列出当前正在运行的所有 openclaw-gateway* 服务。
    支持实例化服务模板 (@)。
    """
    out = subprocess.run(
        ["systemctl", "--user", "list-units", "openclaw-gateway*", "--all", "--no-legend"],
        capture_output=True, text=True,
    ).stdout

    services = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        full_svc = line.split()[0].removesuffix(".service")
        
        # 优先处理实例化服务
        if "@" in full_svc:
            # openclaw-gateway@name
            profile = full_svc.split("@", 1)[1]
            name = "main" if profile == "default" else profile
        else:
            # 处理旧的静态服务 openclaw-gateway(-name)
            svc = full_svc
            profile = "default" if svc == "openclaw-gateway" else svc.replace("openclaw-gateway-", "")
            name = "main" if profile == "default" else profile
            
        services[name] = {"service": full_svc, "profile": profile}

    return services


# ==============================================================================
def systemd_reload_restart(service_name: str) -> None:
    """
    统一的 Systemd 重载 + 重启序列，避免在各脚本中重复书写。
    """
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "restart", f"{service_name}.service"], check=False)


# ==============================================================================
def pod_health_check(service_name: str, display_name: Optional[str] = None, port: Optional[int] = None) -> bool:
    """
    执行健康检查并打印结果。
    支持基础的 Systemd 状态检查和进阶的 API 业务检查。
    """
    import time
    import http.client
    
    time.sleep(5) # 给 OpenClaw 一些启动时间
    try:
        # 1. 基础检查：Systemd 状态
        result = subprocess.run(["systemctl", "--user", "is-active", "--quiet", f"{service_name}.service"], 
                              capture_output=True)
        is_active = result.returncode == 0
        display = display_name or service_name
        
        if not is_active:
            print(f"⚠️  Pod '{display}' (Systemd) 启动失败，请检查日志: journalctl --user -u {service_name}.service")
            return False

        # 2. 进阶检查：API 业务健康 (如果提供了端口)
        if port:
            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                # OpenClaw 的 gateway 通常在 / 有响应或特定 API
                conn.request("GET", "/") 
                res = conn.getresponse()
                if res.status < 500:
                    print(f"✅ Pod '{display}' 运行正常 (API 响应: {res.status})。")
                    return True
                else:
                    print(f"⚠️  Pod '{display}' API 响应异常: {res.status}")
                    return False
            except Exception as e:
                print(f"⚠️  Pod '{display}' API 探测失败: {e}")
                return False

        print(f"✅ Pod '{display}' (Systemd) 运行正常。")
        return True
    except Exception as e:
        print(f"⚠️  检查 Pod '{service_name}' 健康状态时出错: {e}")
        return False


def get_openclaw_versions() -> tuple[str, str]:
    """
    获取 OpenClaw 的本地版本和 npm 远程版本。
    返回 (local_version, remote_version)
    """
    try:
        # 获取本地版本
        local_res = subprocess.run(["openclaw", "-v"], capture_output=True, text=True)
        # 匹配版本号，例如 "OpenClaw 2026.4.8 (9ece252)" -> "2026.4.8"
        import re
        local_v = "unknown"
        if local_res.returncode == 0:
            match = re.search(r"OpenClaw ([\d\.]+)", local_res.stdout)
            if match:
                local_v = match.group(1)
        
        # 获取远程版本
        remote_res = subprocess.run(["npm", "view", "openclaw", "version"], capture_output=True, text=True)
        remote_v = remote_res.stdout.strip() if remote_res.returncode == 0 else "unknown"
        
        return local_v, remote_v
    except Exception:
        return "error", "error"

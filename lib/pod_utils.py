"""
lib/pod_utils.py — 声明式开发模式：共享 Pod 解析函数库 (Python 侧)
解决 CONFIG_FILE、get_pod_dir() 等逻辑在多个 Python 脚本中重复声明的 DRY 违规问题。

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
    从 claw-status 中提取为共享函数，避免重复。

    返回值:
        { pod_name: { "service": str, "profile": str } }
    """
    out = subprocess.run(
        ["systemctl", "--user", "list-units", "openclaw-gateway*", "--all", "--no-legend"],
        capture_output=True, text=True,
    ).stdout

    services = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        svc = line.split()[0].removesuffix(".service")
        profile = "default" if svc == "openclaw-gateway" else svc.replace("openclaw-gateway-", "")
        name = "main" if profile == "default" else profile
        services[name] = {"service": svc, "profile": profile}

    return services


# ==============================================================================
def systemd_reload_restart(service_name: str) -> None:
    """
    统一的 Systemd 重载 + 重启序列，避免在各脚本中重复书写。
    """
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "restart", f"{service_name}.service"], check=False)


# ==============================================================================
def pod_health_check(service_name: str, display_name: Optional[str] = None) -> bool:
    """
    执行健康检查并打印结果。
    
    Args:
        service_name: Systemd 服务名（不含 .service）
        display_name: 用于显示的名称，如果为 None 则使用 service_name
    
    Returns:
        bool: True 如果服务处于 active 状态
    """
    import time
    time.sleep(3)
    try:
        result = subprocess.run(["systemctl", "--user", "is-active", "--quiet", f"{service_name}.service"], 
                              capture_output=True)
        is_active = result.returncode == 0
        display = display_name or service_name
        if is_active:
            print(f"✅ Pod '{display}' 运行正常。")
            print(f"   查看日志: journalctl --user -fu {service_name}.service")
        else:
            print(f"⚠️  Pod '{display}' 仍有问题，请检查日志: journalctl --user -u {service_name}.service")
        return is_active
    except Exception as e:
        print(f"⚠️  检查 Pod '{service_name}' 健康状态时出错: {e}")
        return False
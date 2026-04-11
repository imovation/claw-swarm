"""
modules/orchestration/config-parser/utils.py
共享工具模块 — 提供跨模块复用的工具函数。

导出:
- resolve_secret_ref: 解析 ${VAR} 或 env:VAR 格式的环境变量引用
- resolve_pod: 根据 profile 解析所有路径相关信息
- get_node_binary: 动态解析 nvm 当前激活的 node 可执行文件路径
- get_openclaw_binary: 动态解析 openclaw dist/index.js 路径
- run_systemctl: 运行 systemctl 命令
"""
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional


# ── 常量 ──────────────────────────────────────────────────────────────────────
CLAW_USER_HOME = Path(os.environ.get("HOME", "/home/imovation"))
MAIN_POD_ALIASES = {"default", "main", "gateway"}


# ── SecretRef 解析 ─────────────────────────────────────────────────────────────
def resolve_secret_ref(value: str) -> str:
    """
    解析 ${VAR_NAME} 或 env:VAR_NAME 格式的环境变量引用。
    
    Args:
        value: 可能包含环境变量引用的字符串
        
    Returns:
        解析后的字符串，如果环境变量不存在则返回原值
    """
    if not isinstance(value, str):
        return value
    
    match = re.fullmatch(r'\$\{(\w+)\}', value.strip())
    if match:
        return os.environ.get(match.group(1), value)
    
    match = re.fullmatch(r'env:(\w+)', value.strip())
    if match:
        return os.environ.get(match.group(1), value)
    
    return value


# ── 类型定义 ──────────────────────────────────────────────────────────────────
from typing import TypedDict


class PodInfo(TypedDict):
    profile_arg: str
    dir: Path
    service_name: str
    service: Path
    config: Path


# ── Pod 路径解析 ──────────────────────────────────────────────────────────────
def resolve_pod(profile: str) -> PodInfo:
    """
    根据 profile 名称解析所有路径相关信息。
    统一处理 default / main / gateway 三个历史别名。
    
    Args:
        profile: Pod 的 profile 名称
        
    Returns:
        包含以下键的字典:
        - profile_arg: 实际的 profile 参数
        - dir: Pod 的工作目录
        - service_name: Systemd 服务前缀 (始终是 openclaw-gateway)
        - service: Systemd 模板服务文件路径 (openclaw-gateway@.service)
        - config: openclaw.json 配置文件路径
    """
    if profile in MAIN_POD_ALIASES:
        profile_arg = "default"
        pod_dir = CLAW_USER_HOME / ".openclaw"
    else:
        profile_arg = profile
        pod_dir = CLAW_USER_HOME / f".openclaw-{profile}"

    systemd_dir = CLAW_USER_HOME / ".config" / "systemd" / "user"
    # Systemd 实例化模板服务: openclaw-gateway@.service
    # 具体实例通过 openclaw-gateway@{profile_arg}.service 访问
    return {
        "profile_arg": profile_arg,
        "dir": pod_dir,
        "service_name": "openclaw-gateway",  # 始终是 openclaw-gateway
        "service": systemd_dir / "openclaw-gateway@.service",  # 模板文件
    }


# ── Node.js/OpenClaw 路径解析 ──────────────────────────────────────────────────
def get_node_binary() -> Path:
    """动态解析 nvm 当前激活的 node 可执行文件路径。"""
    nvm_dir = CLAW_USER_HOME / ".nvm" / "versions" / "node"
    if nvm_dir.exists():
        versions = sorted(nvm_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        for v in versions:
            candidate = v / "bin" / "node"
            if candidate.exists():
                return candidate
    node = shutil.which("node")
    if node:
        return Path(node)
    raise RuntimeError("找不到 node 可执行文件，请确认 nvm 或 node 已正确安装")


def get_openclaw_binary() -> Path:
    """动态解析 openclaw dist/index.js 路径。"""
    nvm_dir = CLAW_USER_HOME / ".nvm" / "versions" / "node"
    if nvm_dir.exists():
        versions = sorted(nvm_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        for v in versions:
            candidate = v / "lib" / "node_modules" / "openclaw" / "dist" / "index.js"
            if candidate.exists():
                return candidate
    raise RuntimeError("找不到 openclaw dist/index.js，请确认 openclaw 已全局安装")


# ── Systemd 工具 ───────────────────────────────────────────────────────────────
def run_systemctl(args: str) -> bool:
    """
    运行 systemctl 命令，返回是否成功。
    
    Args:
        args: systemctl 子命令字符串，如 "daemon-reload", "restart xxx.service"
        
    Returns:
        True if successful, False otherwise
    """
    cmd = ["systemctl", "--user"] + args.split()
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


# ── 向后兼容导出 ──────────────────────────────────────────────────────────────
__all__ = [
    "resolve_secret_ref", 
    "resolve_pod", 
    "get_node_binary",
    "get_openclaw_binary",
    "run_systemctl",
    "PodInfo",
    "CLAW_USER_HOME", 
    "MAIN_POD_ALIASES"
]
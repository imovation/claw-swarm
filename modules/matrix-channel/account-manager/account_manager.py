"""
modules/matrix-channel/account-manager/account_manager.py
Matrix 账号管理器 — 负责将 Matrix 配置写入 Pod 的 openclaw.json。
"""
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import re

MODULE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(MODULE_DIR / "modules" / "orchestration" / "config-parser"))
from parser import resolve_pod


def resolve_secret_ref(value: str) -> str:
    """解析 ${VAR_NAME} 或 env:VAR_NAME 格式的 SecretRef。"""
    if not isinstance(value, str):
        return value
    match = re.fullmatch(r'\$\{(\w+)\}', value.strip())
    if match:
        return os.environ.get(match.group(1), value)
    match = re.fullmatch(r'env:(\w+)', value.strip())
    if match:
        return os.environ.get(match.group(1), value)
    return value


def load_config(pod_info: dict) -> dict:
    """读取 Pod 的 openclaw.json 配置。"""
    config_path = pod_info["config"]
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text())
    except Exception:
        return {}


def save_config(pod_info: dict, config: dict):
    """保存配置到 Pod 的 openclaw.json。"""
    config_path = pod_info["config"]
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def write_matrix_config(profile: str, matrix_conf: dict, dry_run: bool = False):
    """
    将 Matrix 配置写入 Pod 的 openclaw.json。
    
    Args:
        profile: Pod 的 profile 名称
        matrix_conf: Matrix 配置字典 (包含 homeserver, accessToken, encryption 等)
    """
    pod_info = resolve_pod(profile)
    
    # 解析 SecretRef
    for key in ("accessToken", "password"):
        if key in matrix_conf and matrix_conf[key]:
            matrix_conf[key] = resolve_secret_ref(str(matrix_conf[key]))
    
    # 加载现有配置
    config = load_config(pod_info)
    
    # 确保 channels 结构存在
    if "channels" not in config:
        config["channels"] = {}
    
    # 写入 Matrix 配置
    config["channels"]["matrix"] = matrix_conf
    
    if dry_run:
        print(f"   📝 [DRY RUN] 将写入 Matrix 配置到 {pod_info['config']}")
        print(f"   {json.dumps(matrix_conf, indent=4, ensure_ascii=False)}")
        return
    
    save_config(pod_info, config)
    print(f"   ✅ Matrix 配置已写入 {pod_info['config']}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Matrix 账号配置管理')
    parser.add_argument("profile", help="Pod profile 名称")
    parser.add_argument("--homeserver", required=True, help="Matrix homeserver URL")
    parser.add_argument("--token", help="Matrix accessToken")
    parser.add_argument("--user-id", help="Matrix userId (用于密码认证)")
    parser.add_argument("--password", help="Matrix password (用于密码认证)")
    parser.add_argument("--encryption", action="store_true", help="启用 E2EE 加密")
    parser.add_argument("--name", help="账号显示名称")
    parser.add_argument("--dm-policy", default="pairing", help="私信策略: allowlist/pairing/open/disabled")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际写入")
    args = parser.parse_args()

    matrix_conf = {
        "enabled": True,
        "homeserver": args.homeserver,
    }
    if args.token:
        matrix_conf["accessToken"] = args.token
    if args.user_id:
        matrix_conf["userId"] = args.user_id
    if args.password:
        matrix_conf["password"] = args.password
    if args.encryption:
        matrix_conf["encryption"] = True
    if args.name:
        matrix_conf["name"] = args.name
    if args.dm_policy:
        matrix_conf["dm"] = {"policy": args.dm_policy}

    write_matrix_config(args.profile, matrix_conf, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
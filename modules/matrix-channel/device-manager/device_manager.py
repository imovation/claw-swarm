"""
modules/matrix-channel/device-manager/device_manager.py
Matrix 设备管理器 — 负责设备列表清理和配对审批。
"""
import subprocess
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "orchestration" / "config-parser"))
from utils import resolve_pod


def run_openclaw(args: list, profile: str):
    """运行 openclaw 命令，注入正确的环境变量。"""
    pod_info = resolve_pod(profile)
    env_file = pod_info["dir"] / "runtime" / "env"
    
    env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    
    result = subprocess.run(
        ["openclaw"] + args,
        capture_output=True,
        text=True,
        env={**subprocess.os.environ, **env},
    )
    return result


def list_devices(profile: str):
    """列出所有已注册设备。"""
    print(f"📱 正在获取 Pod '{profile}' 的设备列表...")
    
    # 尝试通过 openclaw CLI 获取设备列表
    result = run_openclaw(["gateway", "matrix", "devices", "list"], profile)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        # 降级：通过读取本地存储获取
        pod_info = resolve_pod(profile)
        matrix_dir = pod_info["dir"] / "matrix"
        devices_file = matrix_dir / "devices.json"
        
        if devices_file.exists():
            try:
                data = json.loads(devices_file.read_text())
                print(f"📱 设备列表 (本地):")
                for dev in data.get("devices", []):
                    print(f"   - {dev.get('device_id', 'N/A')}: {dev.get('display_name', '未命名')}")
            except (json.JSONDecodeError, OSError) as e:
                print(f"⚠️  无法读取设备列表: {e}")
        else:
            print(f"⚠️  设备列表文件不存在，请先运行一次 OpenClaw 实例")


def prune_stale(profile: str, dry_run: bool = False):
    """清理过期设备。"""
    print(f"🧹 正在清理 Pod '{profile}' 的过期设备...")
    
    if dry_run:
        print("   [DRY RUN] 模拟清理过期设备")
        return
    
    result = run_openclaw(["gateway", "matrix", "devices", "prune"], profile)
    
    if result.returncode == 0:
        print(f"✅ 过期设备已清理")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"⚠️  清理失败: {result.stderr}")


def list_pairing(profile: str):
    """列出待审批的配对请求。"""
    print(f"🔗 正在获取 Pod '{profile}' 的配对请求...")
    
    result = run_openclaw(["gateway", "matrix", "pairing", "list"], profile)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"⚠️  获取配对请求失败")
        print("   提示：配对请求通常在 Matrix 客户端中处理")


def approve_pairing(profile: str, code: str):
    """批准配对码。"""
    print(f"🔗 正在批准配对码 '{code}'...")
    
    result = run_openclaw(["gateway", "matrix", "pairing", "approve", code], profile)
    
    if result.returncode == 0:
        print(f"✅ 配对已批准")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ 配对批准失败: {result.stderr}")
        sys.exit(1)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Matrix 设备管理')
    parser.add_argument("profile", help="Pod profile 名称")
    parser.add_argument("action", choices=["list", "prune", "pairing-list", "approve"],
                        help="操作")
    parser.add_argument("--code", help="配对码 (用于 approve 操作)")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际执行")
    args = parser.parse_args()

    if args.action == "list":
        list_devices(args.profile)
    elif args.action == "prune":
        prune_stale(args.profile, dry_run=args.dry_run)
    elif args.action == "pairing-list":
        list_pairing(args.profile)
    elif args.action == "approve":
        if not args.code:
            print("❌ 错误: approve 操作需要 --code 参数")
            sys.exit(1)
        approve_pairing(args.profile, args.code)


if __name__ == "__main__":
    main()
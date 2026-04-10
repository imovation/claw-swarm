"""
modules/orchestration/pod-provisioner/remove.py
Pod 销毁器 — 删除 Pod（类 kubectl delete pod <name>）。
"""
import subprocess
import sys
import shutil
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(MODULE_DIR / "modules" / "orchestration" / "config-parser"))
from parser import resolve_pod


def remove(profile: str):
    """删除 Pod 实例。"""
    pod_info = resolve_pod(profile)
    svc_name = pod_info["service_name"]
    service_file = pod_info["service"]
    dir_path = pod_info["dir"]

    print(f"🗑️  [1/3] 正在停止并禁用 Pod: {profile} ({svc_name})...")
    result = subprocess.run(["systemctl", "--user", "list-units", "--all"], 
                          capture_output=True, text=True)
    if svc_name + ".service" in result.stdout:
        subprocess.run(["systemctl", "--user", "stop", f"{svc_name}.service"], check=False)
        subprocess.run(["systemctl", "--user", "disable", f"{svc_name}.service"], check=False)

    print("🧹 [2/3] 正在移除 Systemd 服务文件...")
    if service_file.exists():
        service_file.unlink()
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)

    print("📂 [3/3] 正在删除配置目录...")
    if dir_path.exists():
        shutil.rmtree(dir_path)

    print(f"✅ Pod '{profile}' 已成功删除。")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='删除 Pod')
    parser.add_argument("profile", help="Pod profile 名称")
    args = parser.parse_args()
    remove(args.profile)


if __name__ == "__main__":
    main()
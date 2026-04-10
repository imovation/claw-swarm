"""
modules/orchestration/pod-provisioner/repair.py
Pod 修复器 — 手术式修复现有服务文件（类 kubectl replace --force）。
修复场景：Pod 已存在但服务文件损坏、路径过时、环境变量缺失。
"""
import subprocess
import sys
import re
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(MODULE_DIR / "modules" / "orchestration" / "config-parser"))
from utils import resolve_pod, get_node_binary, get_openclaw_binary, run_systemctl


def repair(profile: str):
    """执行服务文件修复。"""
    pod_info = resolve_pod(profile)
    svc_name = pod_info["service_name"]
    service_file = pod_info["service"]
    dir_path = pod_info["dir"]

    print(f"🔧 [1/3] 正在修复 Systemd 服务文件: {profile} ({svc_name})...")

    if not service_file.exists():
        print(f"❌ 服务文件不存在: {service_file}")
        print("   提示: 请先使用 claw apply 创建 Pod。")
        sys.exit(1)

    content = service_file.read_text()
    node_bin = get_node_binary()
    node_dir = node_bin.parent
    openclaw_bin = get_openclaw_binary()

    # 1. 修复历史遗留的旧 Node.js 路径
    content = re.sub(r'/home/imovation/.nvm/current/bin', str(node_dir), content)
    content = re.sub(r'/home/imovation/.nvm/versions/node/v[0-9.]*/bin', str(node_dir), content)
    content = re.sub(r'/home/imovation/.nvm/versions/node/v[0-9.]*/lib/node_modules/openclaw/dist/index.js', str(openclaw_bin), content)

    # 2. 修正 ExecStart
    port_match = re.search(r'--port\s+(\d+)', content)
    port = port_match.group(1) if port_match else "18780"

    if profile in ("default", "main", "gateway"):
        exec_start = f"ExecStart={node_bin} {openclaw_bin} gateway run --port {port}"
    else:
        exec_start = f"ExecStart={node_bin} {openclaw_bin} --profile {pod_info['profile_arg']} gateway run --port {port}"
    content = re.sub(r'ExecStart=.*', exec_start, content)

    # 3. 清理并重新注入环境变量
    lines = [l for l in content.splitlines() 
             if not l.startswith("Environment=OPENCLAW_")]
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if "[Service]" in line:
            new_lines.append(f"Environment=OPENCLAW_STATE_DIR={dir_path}")
            new_lines.append(f"Environment=OPENCLAW_CONFIG_PATH={dir_path}/openclaw.json")
            new_lines.append(f"Environment=OPENCLAW_SYSTEMD_UNIT={svc_name}.service")

    content = "\n".join(new_lines)

    # 4. 确保 WorkingDirectory 存在
    if "WorkingDirectory" not in content:
        content = content.replace("[Service]", "[Service]\nWorkingDirectory=" + str(dir_path))

    service_file.write_text(content)
    print(f"   ✅ 服务文件已更新")

    # 5. 重载 Systemd 并重启
    print("♻️  [2/3] 正在重载 Systemd 并重启实例...")
    if not run_systemctl("daemon-reload"):
        print("   ⚠️  daemon-reload 失败")
    if not run_systemctl(f"restart {svc_name}.service"):
        print("   ⚠️  restart 失败")

    # 6. 健康检查
    print("🩺 [3/3] 正在执行健康检查...")
    import time
    time.sleep(5)
    result = subprocess.run(["systemctl", "--user", "is-active", "--quiet", f"{svc_name}.service"], 
                          capture_output=True)
    if result.returncode == 0:
        print(f"✅ Pod '{profile}' 运行正常。")
    else:
        print(f"⚠️  Pod '{profile}' 启动失败，请检查日志: journalctl --user -u {svc_name}.service")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='修复 Pod 服务文件')
    parser.add_argument("profile", help="Pod profile 名称")
    args = parser.parse_args()
    repair(args.profile)


if __name__ == "__main__":
    main()
"""
modules/network-mesh/port-manager/port_manager.py
端口管理器 — 负责变更 Pod 端口，同步更新 swarm.yaml 和 Systemd 服务配置。
"""
import os
import sys
import subprocess
import re
import yaml
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SWARM_YAML = PROJECT_ROOT / "swarm.yaml"
SYSTEMD_DIR = Path(os.environ.get("HOME", "/home/imovation")) / ".config" / "systemd" / "user"

sys.path.insert(0, str(PROJECT_ROOT / "modules" / "orchestration" / "config-parser"))
from utils import resolve_pod, run_systemctl


def check_port_available(port: int, exclude_profile: Optional[str] = None) -> bool:
    """检查端口是否已被占用。"""
    result = subprocess.run(
        ["ss", "-tlnp"],
        capture_output=True,
        text=True,
    )
    # 查找 :PORT 格式的行
    for line in result.stdout.splitlines():
        if f":{port}" in line:
            if exclude_profile:
                # 排除本 Pod 正在使用的端口（通过检查进程名）
                # 简化处理：如果端口属于 systemd 服务且服务名包含该 profile，则允许
                if exclude_profile in line:
                    continue
            return False
    return True


def update_swarm_yaml(profile: str, new_port: int):
    """更新 swarm.yaml 中的端口声明。"""
    if not SWARM_YAML.exists():
        print(f"⚠️  swarm.yaml 不存在，跳过声明文件同步。")
        return

    config = yaml.safe_load(SWARM_YAML.read_text())
    updated = False
    
    for pod in config.get("pods", []):
        if pod.get("profile") == profile or pod.get("name") == profile:
            old_port = pod.get("port")
            pod["port"] = new_port
            updated = True
            print(f"   已更新 swarm.yaml: {pod['name']} 端口 {old_port} → {new_port}")
            break
    
    if updated:
        SWARM_YAML.write_text(yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False))
        print(f"   swarm.yaml 已保存。")
    else:
        print(f"   ⚠️  在 swarm.yaml 中未找到 profile='{profile}' 的 Pod。")


def update_systemd_service(profile: str, new_port: int):
    """更新 Systemd 服务文件中的端口参数。"""
    pod_info = resolve_pod(profile)
    service_file = pod_info["service"]
    
    if not service_file.exists():
        print(f"❌ 找不到服务文件: {service_file}")
        print("   提示: 请先使用 claw apply 创建该 Pod。")
        sys.exit(1)
    
    content = service_file.read_text()
    
    # 替换 ExecStart 中的 --port 参数
    # 模式: gateway run --port <old_port>
    pattern = r'(gateway\s+run\s+--port\s+)\d+'
    replacement = r'\g<1>' + str(new_port)
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        print(f"⚠️  未能在服务文件中找到端口参数")
    
    service_file.write_text(new_content)
    print(f"   已更新 Systemd 服务文件: {service_file}")


def change_port(profile: str, new_port: int, skip_yaml_update: bool = False):
    """执行端口变更。"""
    # 1. 端口格式校验
    if not (1024 <= new_port <= 65535):
        print(f"❌ 端口号无效: {new_port}，请使用 1024-65535 范围内的端口。")
        sys.exit(1)
    
    # 2. 冲突检测
    if not check_port_available(new_port, exclude_profile=profile):
        print(f"❌ 端口 {new_port} 已被占用")
        sys.exit(1)
    
    print(f"🔌 正在变更 Pod '{profile}' 端口: → {new_port}...")
    
    # 3. 更新 swarm.yaml (除非明确跳过)
    if not skip_yaml_update:
        update_swarm_yaml(profile, new_port)
    
    # 4. 更新服务文件
    update_systemd_service(profile, new_port)
    
    # 5. 重载 Systemd
    svc_name = pod_info = resolve_pod(profile)["service_name"]
    print(f"♻️  正在重载 Systemd 并重启实例...")
    if not run_systemctl("daemon-reload"):
        print(f"   ⚠️  daemon-reload 失败")
    if not run_systemctl(f"restart {svc_name}.service"):
        print(f"   ⚠️  restart 失败")
    
    print(f"\n✅ Pod '{profile}' 端口已成功变更为 {new_port}")
    print(f"   查看日志: journalctl --user -fu {svc_name}.service")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Swarm 端口变更管理')
    parser.add_argument("profile", help="Pod profile 名称")
    parser.add_argument("port", type=int, help="新端口号")
    parser.add_argument("--skip-yaml", action="store_true", help="仅修改服务文件，不更新 swarm.yaml")
    args = parser.parse_args()

    change_port(args.profile, args.port, skip_yaml_update=args.skip_yaml)


if __name__ == "__main__":
    main()
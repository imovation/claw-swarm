"""
modules/orchestration/tui.py
交互式终端 — 进入 Pod 的 TUI 界面，自动注入正确的环境变量。
"""
import os
import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "orchestration" / "config-parser"))
from parser import parse as parse_swarm, resolve_pod


def tui(profile: str):
    """进入 Pod 的 TUI 界面。"""
    swarm_yaml = PROJECT_ROOT / "swarm.yaml"
    
    if not swarm_yaml.exists():
        print(f"❌ 错误: 找不到配置文件 {swarm_yaml}。")
        sys.exit(1)

    config = parse_swarm(swarm_yaml)
    pod = next((p for p in config.pods if p.profile == profile or p.name == profile), None)

    if not pod:
        print(f"❌ 错误: 在 swarm.yaml 中找不到 profile='{profile}' 的实例配置。")
        sys.exit(1)

    pod_info = resolve_pod(profile)
    dir_path = pod_info["dir"]

    # 注入 Virtual Home 环境变量
    env = os.environ.copy()
    env["TMPDIR"] = f"{dir_path}/runtime/tmp"
    env["XDG_CONFIG_HOME"] = f"{dir_path}/runtime/config"
    env["XDG_CACHE_HOME"] = f"{dir_path}/runtime/cache"
    env["XDG_DATA_HOME"] = f"{dir_path}/runtime/data"
    env["OPENCLAW_STATE_DIR"] = str(dir_path)
    env["OPENCLAW_CONFIG_PATH"] = str(dir_path / "openclaw.json")

    # 浏览器隔离
    if pod.browser == "dedicated":
        env["PUPPETEER_USER_DATA_DIR"] = f"{dir_path}/runtime/browser"

    print(f"🚀 正在进入实例 '{pod.name}' (Profile: {pod_info['profile_arg']}) 的终端界面...")

    cmd = ["openclaw"]
    if pod_info["profile_arg"] != "default":
        cmd += ["--profile", pod_info["profile_arg"]]
    cmd += ["tui", "--token", pod.token]

    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n👋 已退出终端界面。")
    except OSError as e:
        print(f"❌ 启动 TUI 失败: {e}")


def main():
    if len(sys.argv) < 2:
        print("用法: claw tui <实例名>")
        print("示例: claw tui aimee")
        sys.exit(1)

    tui(sys.argv[1])


if __name__ == "__main__":
    main()
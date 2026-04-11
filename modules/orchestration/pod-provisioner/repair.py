"""
modules/orchestration/pod-provisioner/repair.py
Pod 修复器 — 手术式修复现有 Pod（基于 Systemd 模板实例化）。
修复场景：Pod 已存在但环境变量/配置过时、需要重新同步。
"""
import subprocess
import sys
import re
import time
import json
import http.client
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(MODULE_DIR / "modules" / "orchestration" / "config-parser"))
from utils import resolve_pod, get_node_binary, get_openclaw_binary, run_systemctl, CLAW_USER_HOME


def repair(profile: str):
    """执行 Pod 修复/重新同步。"""
    pod_info = resolve_pod(profile)
    profile_arg = pod_info["profile_arg"]
    svc_name = pod_info["service_name"]
    pod_dir = pod_info["dir"]
    
    # Systemd 模板实例化服务: openclaw-gateway@.service
    SYSTEMD_DIR = CLAW_USER_HOME / ".config" / "systemd" / "user"
    template_file = SYSTEMD_DIR / f"{svc_name}@.service"
    svc_instance = f"{svc_name}@{profile_arg}"

    print(f"🔧 [1/4] 正在验证 Systemd 模板服务: {profile} ({svc_instance})...")

    if not template_file.exists():
        print(f"❌ 模板服务文件不存在: {template_file}")
        print("   提示: 请先使用 claw apply 创建 Pod。")
        sys.exit(1)

    # 检查实例运行状态
    result = subprocess.run(["systemctl", "--user", "is-active", "--quiet", f"{svc_instance}.service"], 
                          capture_output=True)
    if result.returncode != 0:
        print(f"⚠️  实例服务未运行，正在启动...")
        run_systemctl(f"enable --now {svc_instance}.service")
        time.sleep(3)

    # 2. 从 swarm.yaml 读取期望配置
    print(f"🔧 [2/4] 正在读取期望配置...")
    import yaml
    SWARM_YAML = MODULE_DIR / "swarm.yaml"
    config = yaml.safe_load(SWARM_YAML.read_text())
    
    desired_port = None
    desired_token = None
    desired_browser = "dedicated"
    for pod in config.get("pods", []):
        if pod.get("profile") == profile_arg or pod.get("name") == profile:
            desired_port = pod.get("port")
            desired_token = pod.get("token")
            desired_browser = pod.get("resources", {}).get("browser", "dedicated")
            break
    
    if desired_port is None:
        print(f"❌ 在 swarm.yaml 中未找到 Pod '{profile}' 的配置")
        sys.exit(1)

    # 读取全局代理配置
    proxy = config.get("global", {}).get("proxy", {})
    plugins = config.get("global", {}).get("plugins", [])

    # 3. 重建 runtime/env 文件
    print(f"🔧 [3/4] 正在重建环境变量文件...")
    node_bin = get_node_binary()
    openclaw_bin = get_openclaw_binary()
    
    env_lines = [
        f"OPENCLAW_PORT={desired_port}",
        f"OPENCLAW_TOKEN={desired_token}",
        f"OPENCLAW_PROFILE={profile_arg}",
        f"OPENCLAW_STATE_DIR={pod_dir}",
        f"OPENCLAW_CONFIG_PATH={pod_dir}/openclaw.json",
        f"TMPDIR={pod_dir}/runtime/tmp",
        f"XDG_CONFIG_HOME={pod_dir}/runtime/config",
        f"XDG_CACHE_HOME={pod_dir}/runtime/cache",
        f"XDG_DATA_HOME={pod_dir}/runtime/data",
        f"PATH={node_bin.parent}:/usr/local/bin:/usr/bin:/bin",
    ]
    if desired_browser == "dedicated":
        env_lines.append(f"PUPPETEER_USER_DATA_DIR={pod_dir}/runtime/browser")
    if proxy.get("http"):
        env_lines += [f"HTTP_PROXY={proxy['http']}", f"http_proxy={proxy['http']}"]
    if proxy.get("https"):
        env_lines += [f"HTTPS_PROXY={proxy['https']}", f"https_proxy={proxy['https']}"]
    if proxy.get("socks"):
        env_lines += [f"ALL_PROXY={proxy['socks']}", f"all_proxy={proxy['socks']}"]
    if proxy.get("no_proxy"):
        env_lines += [f"NO_PROXY={proxy['no_proxy']}", f"no_proxy={proxy['no_proxy']}"]

    env_file = pod_dir / "runtime" / "env"
    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text("\n".join(env_lines) + "\n")
    print(f"   ✅ 环境变量文件已更新: {env_file}")

    # 4. 重建 openclaw.json（如需要）
    config_file = pod_dir / "openclaw.json"
    needs_init = True
    if config_file.exists():
        try:
            existing = json.loads(config_file.read_text())
            if "gateway" in existing:
                needs_init = False
        except (json.JSONDecodeError, OSError):
            pass
    if needs_init:
        import jinja2
        TEMPLATE_DIR = MODULE_DIR / "modules" / "orchestration" / "templates"
        tpl = (TEMPLATE_DIR / "openclaw.json.j2").read_text()
        rendered = jinja2.Template(tpl).render(token=desired_token, port=desired_port)
        config_file.write_text(rendered)
        print(f"   ✅ openclaw.json 已重建")

    # 5. 重启服务
    print(f"🔧 [4/4] 正在重启服务...")
    run_systemctl("daemon-reload")
    run_systemctl(f"restart {svc_instance}.service")
    
    # 健康检查
    time.sleep(5)
    result = subprocess.run(["systemctl", "--user", "is-active", "--quiet", f"{svc_instance}.service"], 
                          capture_output=True)
    if result.returncode == 0:
        # HTTP 探活
        try:
            conn = http.client.HTTPConnection("127.0.0.1", desired_port, timeout=5)
            conn.request("GET", "/")
            res = conn.getresponse()
            if res.status < 500:
                print(f"✅ Pod '{profile}' 修复成功，运行正常 (HTTP {res.status})。")
                return
        except Exception as e:
            print(f"⚠️  HTTP 探活失败: {e}")
    
    print(f"⚠️  Pod '{profile}' 可能存在问题，请检查日志: journalctl --user -u {svc_instance}.service")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='修复 Pod 服务配置')
    parser.add_argument("profile", help="Pod profile 名称")
    args = parser.parse_args()
    repair(args.profile)


if __name__ == "__main__":
    main()

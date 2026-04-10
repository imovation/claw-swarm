"""
modules/orchestration/ps.py
精细进程状态监控 — 显示所有 Pod 的实例、状态、端口、模型、渠道、插件。
"""
import subprocess
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "orchestration" / "config-parser"))
from parser import resolve_pod


def ps():
    """显示所有 Pod 的精细状态。"""
    print("%-12s %-8s %-8s %-25s %-12s %-20s" % ("INSTANCE", "STATUS", "PORT", "MODEL", "CHANNELS", "PLUGINS"))
    print("-" * 95)

    out = subprocess.run(
        ["systemctl", "--user", "list-units", "openclaw-gateway*", "--all", "--no-legend"],
        capture_output=True, text=True
    ).stdout

    for line in out.splitlines():
        if not line.strip():
            continue
        
        service = line.split()[0].removesuffix(".service")
        
        if service == "openclaw-gateway":
            name = "main"
            profile = "default"
        elif "@" in service:
            name = service.split("@", 1)[1]
            profile = name
        else:
            name = service.replace("openclaw-gateway-", "")
            profile = name

        status = subprocess.run(
            ["systemctl", "--user", "is-active", service],
            capture_output=True, text=True
        ).stdout.strip() or "inactive"

        port, model, channels, plugins = "N/A", "N/A", "none", "none"
        
        if status == "active":
            exec_start = subprocess.run(
                ["systemctl", "--user", "show", "-p", "ExecStart", service],
                capture_output=True, text=True
            ).stdout
            m = re.search(r'--port\s+(\d+)', exec_start)
            port = m.group(1) if m else "N/A"
            
            pod_info = resolve_pod(profile)
            config_file = pod_info["config"]
            
            if config_file.exists():
                try:
                    data = json.loads(config_file.read_text())
                    model = data.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "default")
                    
                    chs = []
                    for ch, cfg in data.get("channels", {}).items():
                        if isinstance(cfg, dict) and cfg.get("enabled"):
                            chs.append(ch)
                    channels = ",".join(chs) if chs else "none"
                    
                    pls = []
                    for pl, cfg in data.get("plugins", {}).get("entries", {}).items():
                        if isinstance(cfg, dict) and cfg.get("enabled"):
                            pls.append(pl.replace("openclaw-", ""))
                    plugins = ",".join(pls) if pls else "none"
                except (json.JSONDecodeError, OSError) as e:
                    pass  # 忽略读取错误，使用默认值

        print("%-12s %-8s %-8s %-25s %-12s %-20s" % (
            name, status, port, model[:24], channels[:11], plugins[:19]
        ))


def main():
    ps()


if __name__ == "__main__":
    main()
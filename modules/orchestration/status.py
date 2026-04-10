"""
modules/orchestration/status.py
集群状态看板 — 实时监控 Pod 状态、内存占用、主用模型、同步健康度。
"""
import subprocess
import sys
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "orchestration" / "config-parser"))
from parser import parse as parse_swarm, resolve_pod

CONFIG_FILE = PROJECT_ROOT / "swarm.yaml"

GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
CYAN = '\033[0;36m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'


def get_actual_services():
    """获取当前运行的 Pod 服务列表。"""
    out = subprocess.run(
        ["systemctl", "--user", "list-units", "openclaw-gateway*", "--all", "--no-legend"],
        capture_output=True, text=True,
    ).stdout

    services = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        full_svc = line.split()[0].removesuffix(".service")
        
        if "@" in full_svc:
            profile = full_svc.split("@", 1)[1]
            name = "main" if profile == "default" else profile
        else:
            profile = "default" if full_svc == "openclaw-gateway" else full_svc.replace("openclaw-gateway-", "")
            name = "main" if profile == "default" else profile
            
        services[name] = {"service": full_svc, "profile": profile}

    return services


def get_service_metrics(service_name):
    """获取服务运行指标（内存、状态、启动时间）。"""
    try:
        out = subprocess.run(
            ["systemctl", "--user", "show", service_name,
             "-p", "ActiveState", "-p", "MemoryCurrent", "-p", "ActiveEnterTimestamp"],
            capture_output=True, text=True,
        ).stdout

        metrics = {}
        for line in out.strip().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                metrics[k] = v

        mem_bytes = int(metrics.get("MemoryCurrent", "0"))
        mem_mb = 0.0 if mem_bytes == 18446744073709551615 else mem_bytes / (1024 * 1024)

        return {
            "state": metrics.get("ActiveState", "unknown"),
            "mem_mb": mem_mb,
            "uptime": metrics.get("ActiveEnterTimestamp", "N/A"),
        }
    except Exception:
        return {"state": "error", "mem_mb": 0.0, "uptime": "N/A"}


def parse_pod_config(profile):
    """解析 Pod 的 openclaw.json，提取主用模型和生效渠道。"""
    pod_info = resolve_pod(profile)
    config_path = pod_info["config"]
    if not config_path.exists():
        return "N/A", "none"
    
    try:
        data = json.loads(config_path.read_text())
        model = data.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "default")
        
        channels = []
        for ch, cfg in data.get("channels", {}).items():
            if isinstance(cfg, dict) and cfg.get("enabled"):
                channels.append(ch)
        
        return model, ",".join(channels) if channels else "none"
    except Exception:
        return "error", "error"


def get_matrix_status(profile):
    """解析 Pod 的 Matrix 渠道状态。"""
    try:
        pod_info = resolve_pod(profile)
        config_path = pod_info["config"]
        if not config_path.exists():
            return None
        
        data = json.loads(config_path.read_text())
        matrix = data.get("channels", {}).get("matrix", {})
        if not matrix.get("enabled"):
            return None
        
        homeserver = matrix.get("homeserver", "N/A")
        encryption = matrix.get("encryption", False)
        
        if "://" in homeserver:
            short_hs = homeserver.split("://")[1].split("/")[0]
        else:
            short_hs = homeserver
        
        enc_str = f"{GREEN}E2EE{NC}" if encryption else f"{YELLOW}明文{NC}"
        
        return {'homeserver': short_hs, 'encryption': enc_str}
    except Exception:
        return None


def main():
    desired_pods = {}
    if CONFIG_FILE.exists():
        try:
            config = parse_swarm(CONFIG_FILE)
            for pod in config.pods:
                desired_pods[pod.name] = pod
        except: pass

    actual_services = get_actual_services()

    header = f"{BOLD}%-25s %-10s %-8s %-12s %-15s %-18s %-15s %-12s{NC}" % (
        "实例 (POD)", "状态", "端口", "内存占用", "启动时间", "主用模型", "生效渠道", "Matrix"
    )
    print(header)
    print("-" * 145)

    all_names = sorted(set(list(desired_pods.keys()) + list(actual_services.keys())))

    for name in all_names:
        desired = desired_pods.get(name)
        actual = actual_services.get(name)
        
        status_str = f"{RED}已离线{NC}"
        port, mem_str, uptime, model, channels, sync_str = "N/A", "0 MB", "N/A", "N/A", "none", f"{RED}配置缺失{NC}"
        
        if actual:
            svc_name = actual['service']
            profile = actual['profile']
            metrics = get_service_metrics(svc_name + ".service")
            
            if metrics['state'] == 'active':
                status_str = f"{GREEN}运行中{NC}"
            else:
                status_str = f"{YELLOW}{metrics['state']}{NC}"
            
            mem_str = f"{metrics['mem_mb']:.1f} MB"
            uptime_raw = metrics['uptime']
            uptime = " ".join(uptime_raw.split()[1:3]) if " " in uptime_raw else uptime_raw
            
            model, channels = parse_pod_config(profile)
            
            port_out = subprocess.run(
                ["systemctl", "--user", "show", "-p", "Environment", svc_name + ".service"],
                capture_output=True, text=True
            ).stdout
            m = re.search(r'OPENCLAW_PORT=(\d+)', port_out)
            port = m.group(1) if m else (str(desired.port) if desired else "???")

            if desired:
                sync_str = f"{GREEN}已同步{NC}"
                if str(desired.port) != port:
                    sync_str = f"{YELLOW}配置漂移{NC}"
            else:
                sync_str = f"{CYAN}未纳管(Orphan){NC}"
        
        display_name = desired.name if desired else name
        matrix_status = get_matrix_status(profile) if actual else None
        matrix_display = f"{BLUE}未启用{NC}" if matrix_status is None else matrix_status['encryption']
        
        print("%-25s %-10s %-8s %-12s %-15s %-18s %-15s %-12s" % (
            f"{BOLD}{display_name}{NC}" if desired else display_name,
            status_str, port, mem_str, uptime, model[:17], channels[:14], matrix_display
        ))


if __name__ == "__main__":
    main()
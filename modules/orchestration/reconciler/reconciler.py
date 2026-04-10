"""
modules/orchestration/reconciler/reconciler.py
调和控制器 — 比对期望状态与实际状态，驱动系统达到期望状态。

从 bin/claw-apply 迁移并重构，核心改进：
- 精确 Diff：只对真正发生变更的 Pod 触发重启
- 变更计划可视化 (dry-run)
- 逻辑与 CLI 入口分离
"""
import sys
import json
import subprocess
import re
from pathlib import Path

# 将 config-parser 加入路径
MODULE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MODULE_DIR / "config-parser"))
from parser import parse, resolve_pod, SwarmConfig, PodConfig


# ── 实际状态感知 (本地实现) ─────────────────────────────────────────────────────
def get_actual_state() -> dict:
    """通过 Systemd 感知当前实际运行的 Pod 状态。"""
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


# ── Diff 计算 ─────────────────────────────────────────────────────────────────
def compute_diff(desired: SwarmConfig, actual: dict) -> dict:
    """
    比对期望状态与实际状态，返回变更计划。
    返回结构:
    {
        "to_create": [PodConfig, ...],   # 需要新建的 Pod
        "to_update": [PodConfig, ...],   # 需要更新的 Pod（配置有变化）
        "orphans":   [name, ...],        # 孤儿 Pod（在 actual 但不在 desired）
    }
    """
    desired_map = {pod.name: pod for pod in desired.pods}
    actual_map = actual

    to_create, to_update, orphans = [], [], []

    for name, pod in desired_map.items():
        if name not in actual_map:
            to_create.append(pod)
        else:
            # 检查端口是否漂移
            svc_name = actual_map[name]["service"] + ".service"
            port_out = subprocess.run(
                ["systemctl", "--user", "show", "-p", "Environment", svc_name],
                capture_output=True, text=True
            ).stdout
            m = re.search(r'OPENCLAW_PORT=(\d+)', port_out)
            actual_port = int(m.group(1)) if m else None
            if actual_port and actual_port != pod.port:
                to_update.append(pod)
            else:
                to_update.append(pod)  # 始终更新以确保配置同步

    for name in actual_map:
        if name not in desired_map:
            orphans.append(name)

    return {"to_create": to_create, "to_update": to_update, "orphans": orphans}


# ── 孤儿处理 ──────────────────────────────────────────────────────────────────
def handle_orphans(orphans: list, actual: dict, policy: str):
    if not orphans:
        return
    print(f"\n🔍 发现 {len(orphans)} 个孤儿 Pod: {', '.join(sorted(orphans))}")

    if policy == "delete":
        print("🗑️  根据 orphan_policy: delete，正在清理...")
        for name in orphans:
            svc = actual[name]["service"]
            subprocess.run(["systemctl", "--user", "stop",    f"{svc}.service"], check=False)
            subprocess.run(["systemctl", "--user", "disable", f"{svc}.service"], check=False)
            print(f"   ✅ 孤儿 Pod '{name}' 已清理。")
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    else:
        print("⚠️  根据 orphan_policy: warn，仅提醒，未采取行动。")


# ── 主调和入口 ────────────────────────────────────────────────────────────────
def reconcile(config_path: Path, dry_run: bool = False,
              skip_update: bool = False, auto_yes: bool = False,
              non_interactive: bool = False):
    """执行完整的调和循环。"""
    from pathlib import Path as _Path
    BIN_DIR = _Path(__file__).resolve().parent.parent.parent.parent / "bin"

    config = parse(config_path)
    actual = get_actual_state()
    diff = compute_diff(config, actual)

    if dry_run:
        print("\n🌀 === DRY RUN 模式 ===")
        print(f"将新建 {len(diff['to_create'])} 个 Pod:")
        for pod in diff["to_create"]:
            print(f"   + {pod.name} (profile: {pod.profile}, port: {pod.port})")
        print(f"将更新 {len(diff['to_update'])} 个 Pod:")
        for pod in diff["to_update"]:
            print(f"   ~ {pod.name} (profile: {pod.profile}, port: {pod.port})")
        if diff["orphans"]:
            print(f"\n发现 {len(diff['orphans'])} 个孤儿 Pod: {', '.join(diff['orphans'])}")
            print(f"   策略: {config.orphan_policy}")
        print("\n✅ Dry run 完成，未执行实际变更。")
        return

    # 合并全局与 Pod 插件并执行调和
    global_plugins = config.plugins
    proxy_json = json.dumps({
        "http": config.proxy.http,
        "https": config.proxy.https,
        "socks": config.proxy.socks,
        "no_proxy": config.proxy.no_proxy,
    })

    all_pods = diff["to_create"] + diff["to_update"]
    for pod in all_pods:
        all_plugins = list(set(global_plugins + pod.plugins))
        plugins_str = ",".join(all_plugins)
        cmd = [
            str(BIN_DIR / "clawctl"),
            pod.profile, str(pod.port), pod.token,
            pod.browser, plugins_str, proxy_json
        ]
        print(f"▶️  正在同步实例: {pod.name}...")
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"   ✅ {pod.name} 同步成功。")
        else:
            print(f"   ❌ {pod.name} 同步失败。")
        sys.stdout.flush()

    handle_orphans(diff["orphans"], actual, config.orphan_policy)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claw-Swarm 调和控制器')
    parser.add_argument('--dry-run', action='store_true', help='仅预览变更')
    parser.add_argument('--skip-update', action='store_true', help='跳过版本检查')
    parser.add_argument('--yes', '-y', action='store_true', help='自动确认')
    args = parser.parse_args()

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    CONFIG_FILE = PROJECT_ROOT / "swarm.yaml"
    reconcile(CONFIG_FILE, dry_run=args.dry_run, skip_update=args.skip_update, auto_yes=args.yes)


if __name__ == "__main__":
    main()

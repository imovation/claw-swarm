"""
modules/orchestration/pod-provisioner/provisioner.py
Pod 供应器 — 在宿主机上完成 Pod 的物理创建、环境注入、插件同步和 Systemd 管理。

从 bin/clawctl (Bash) 重写为纯 Python，核心改进：
- 使用 Jinja2 模板替代 Heredoc，彻底解耦逻辑与配置
- 幂等操作：重复执行结果一致
- 所有路径通过 resolve_pod() 统一解析，无硬编码
"""
import os
import sys
import shutil
import subprocess
import time
import http.client
from pathlib import Path

# ── 路径初始化 ─────────────────────────────────────────────────────────────────
MODULE_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent.parent.parent.parent
TEMPLATE_DIR = MODULE_DIR.parent / "templates"
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "orchestration" / "config-parser"))

from parser import resolve_pod

CLAW_USER_HOME = Path(os.environ.get("HOME", "/home/imovation"))
SYSTEMD_DIR    = CLAW_USER_HOME / ".config" / "systemd" / "user"


# ── Node.js 路径解析 ───────────────────────────────────────────────────────────
def get_node_binary() -> Path:
    """动态解析 nvm 当前激活的 node 可执行文件路径。"""
    nvm_dir = CLAW_USER_HOME / ".nvm" / "versions" / "node"
    if nvm_dir.exists():
        versions = sorted(nvm_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        for v in versions:
            candidate = v / "bin" / "node"
            if candidate.exists():
                return candidate
    # 降级：从 PATH 查找
    node = shutil.which("node")
    if node:
        return Path(node)
    raise RuntimeError("找不到 node 可执行文件，请确认 nvm 或 node 已正确安装")


def get_openclaw_binary() -> Path:
    """动态解析 openclaw dist/index.js 路径。"""
    nvm_dir = CLAW_USER_HOME / ".nvm" / "versions" / "node"
    if nvm_dir.exists():
        versions = sorted(nvm_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        for v in versions:
            candidate = v / "lib" / "node_modules" / "openclaw" / "dist" / "index.js"
            if candidate.exists():
                return candidate
    raise RuntimeError("找不到 openclaw dist/index.js，请确认 openclaw 已全局安装")


# ── 模板渲染 ───────────────────────────────────────────────────────────────────
def _render(template_name: str, **ctx) -> str:
    """使用简单字符串替换渲染 .j2 模板（无需额外依赖）。"""
    tpl = (TEMPLATE_DIR / template_name).read_text()
    for key, val in ctx.items():
        tpl = tpl.replace("{{ " + key + " }}", str(val))
    return tpl


# ── 插件同步 ───────────────────────────────────────────────────────────────────
def sync_plugins(pod_dir: Path, plugins: list, node_bin: Path):
    """物理同步插件到 Pod 的 extensions/ 目录（禁止 symlink）。"""
    if not plugins:
        return
    extensions_dir = pod_dir / "extensions"
    extensions_dir.mkdir(parents=True, exist_ok=True)
    node_modules_global = node_bin.parent.parent / "lib" / "node_modules"

    for plugin in plugins:
        if not plugin:
            continue
        src = node_modules_global / plugin
        dst = extensions_dir / plugin
        if not src.exists():
            print(f"   ⚠️  警告: 找不到全局插件 {plugin} ({src})")
            continue
        print(f"   📦 正在同步插件: {plugin}...")
        if shutil.which("rsync"):
            subprocess.run(["rsync", "-rt", "--delete", f"{src}/", f"{dst}/"], check=False)
        else:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)


# ── 核心供应逻辑 ───────────────────────────────────────────────────────────────
def provision(profile: str, port: int, token: str,
              browser: str = "dedicated", plugins: list = None,
              proxy: dict = None):
    """
    供应或更新一个 Pod 实例。幂等操作。

    Args:
        profile:  Pod 的 profile 名称（如 "default", "aimee"）
        port:     监听端口
        token:    访问令牌
        browser:  浏览器隔离模式 (dedicated | shared)
        plugins:  插件列表
        proxy:    代理配置字典 {http, https, socks, no_proxy}
    """
    plugins = plugins or []
    proxy   = proxy or {}
    pod     = resolve_pod(profile)
    pod_dir = pod["dir"]
    svc_name = pod["service_name"]
    profile_arg = pod["profile_arg"]

    print(f"🚀 正在供应 Pod: {profile} (端口: {port}, 插件: {plugins})...")

    # 1. 解析二进制路径
    node_bin     = get_node_binary()
    openclaw_bin = get_openclaw_binary()

    # 2. 创建运行时目录结构
    for sub in ["tmp", "config", "cache", "data", "browser"]:
        (pod_dir / "runtime" / sub).mkdir(parents=True, exist_ok=True)

    # 3. 同步插件
    sync_plugins(pod_dir, plugins, node_bin)

    # 4. 写入 runtime/env 文件
    env_file = pod_dir / "runtime" / "env"
    env_lines = [
        f"OPENCLAW_PORT={port}",
        f"OPENCLAW_TOKEN={token}",
        f"OPENCLAW_PROFILE={profile_arg}",
        f"OPENCLAW_STATE_DIR={pod_dir}",
        f"OPENCLAW_CONFIG_PATH={pod_dir}/openclaw.json",
        f"TMPDIR={pod_dir}/runtime/tmp",
        f"XDG_CONFIG_HOME={pod_dir}/runtime/config",
        f"XDG_CACHE_HOME={pod_dir}/runtime/cache",
        f"XDG_DATA_HOME={pod_dir}/runtime/data",
        f"PATH={node_bin.parent}:/usr/local/bin:/usr/bin:/bin",
    ]
    if browser == "dedicated":
        env_lines.append(f"PUPPETEER_USER_DATA_DIR={pod_dir}/runtime/browser")
    # 代理注入
    if proxy.get("http"):
        env_lines += [f"HTTP_PROXY={proxy['http']}", f"http_proxy={proxy['http']}"]
    if proxy.get("https"):
        env_lines += [f"HTTPS_PROXY={proxy['https']}", f"https_proxy={proxy['https']}"]
    if proxy.get("socks"):
        env_lines += [f"ALL_PROXY={proxy['socks']}", f"all_proxy={proxy['socks']}"]
    if proxy.get("no_proxy"):
        env_lines += [f"NO_PROXY={proxy['no_proxy']}", f"no_proxy={proxy['no_proxy']}"]

    env_file.write_text("\n".join(env_lines) + "\n")

    # 5. 写入 openclaw.json（仅在不存在或缺少 gateway 字段时）
    config_file = pod_dir / "openclaw.json"
    import json
    needs_init = True
    if config_file.exists():
        try:
            existing = json.loads(config_file.read_text())
            if "gateway" in existing:
                needs_init = False
        except Exception:
            pass
    if needs_init:
        rendered = _render("openclaw.json.j2", token=token, port=port)
        config_file.write_text(rendered)
        print(f"   📝 已初始化 openclaw.json")

    # 6. 确保 Systemd 模板服务存在并渲染实例服务
    _ensure_template_service(node_bin, openclaw_bin)

    # 7. 启动 Systemd 实例
    instance_svc = f"openclaw-gateway@{profile_arg}"
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
    subprocess.run(["systemctl", "--user", "enable", "--now", instance_svc], check=False)
    subprocess.run(["systemctl", "--user", "restart", instance_svc], check=False)

    # 8. 健康检查
    _health_check(instance_svc, profile, port)


def _ensure_template_service(node_bin: Path, openclaw_bin: Path):
    """确保 Systemd 实例化模板服务文件存在。"""
    template_path = SYSTEMD_DIR / "openclaw-gateway@.service"
    if template_path.exists():
        return
    print("⚠️  未发现 Systemd 模板服务，正在创建...")
    SYSTEMD_DIR.mkdir(parents=True, exist_ok=True)
    # 主 Pod (default) 的 ExecStart 无 --profile 参数，使用 %i 占位符
    content = _render(
        "systemd.service.j2",
        profile="%i",
        env_file=f"{CLAW_USER_HOME}/.openclaw-%i/runtime/env",
        node_bin=node_bin,
        openclaw_bin=openclaw_bin,
        port="${OPENCLAW_PORT}",
    )
    template_path.write_text(content)
    template_path.chmod(0o644)
    print(f"   ✅ 模板服务已创建: {template_path}")


def _health_check(svc_name: str, display: str, port: int, timeout: int = 10):
    """执行 Systemd 状态 + HTTP API 双重健康检查。"""
    time.sleep(timeout)
    result = subprocess.run(
        ["systemctl", "--user", "is-active", "--quiet", f"{svc_name}.service"],
        capture_output=True
    )
    if result.returncode != 0:
        print(f"⚠️  Pod '{display}' 启动失败，请检查日志: journalctl --user -u {svc_name}.service")
        return False
    # HTTP 探活
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        conn.request("GET", "/")
        res = conn.getresponse()
        if res.status < 500:
            print(f"✅ Pod '{display}' 运行正常 (HTTP {res.status})。")
            return True
        print(f"⚠️  Pod '{display}' API 响应异常: {res.status}")
    except Exception as e:
        print(f"⚠️  Pod '{display}' HTTP 探活失败: {e}")
    return False

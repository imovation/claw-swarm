"""
modules/network-mesh/proxy-injector/injector.py
代理注入器 — 解析 swarm.yaml 的 global.proxy 配置，写入 Pod 的 runtime/env 文件。
"""
import sys
from pathlib import Path
from dataclasses import dataclass

MODULE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(MODULE_DIR / "modules" / "orchestration" / "config-parser"))
from utils import resolve_secret_ref


@dataclass
class ProxyConfig:
    http: str = ""
    https: str = ""
    socks: str = ""
    no_proxy: str = ""


def inject(env_file: Path, proxy: ProxyConfig):
    """
    将代理环境变量追加写入到 Pod 的 runtime/env 文件中。
    幂等操作：先删除旧的代理配置行，再写入新值。
    """
    proxy_keys = {
        "HTTP_PROXY", "http_proxy",
        "HTTPS_PROXY", "https_proxy",
        "ALL_PROXY", "all_proxy",
        "NO_PROXY", "no_proxy",
    }

    # 读取现有内容，过滤掉旧的代理配置行
    if env_file.exists():
        lines = [l for l in env_file.read_text().splitlines()
                 if l.split("=")[0] not in proxy_keys]
    else:
        lines = []

    # 追加新代理配置
    if proxy.http:
        lines += [f"HTTP_PROXY={proxy.http}", f"http_proxy={proxy.http}"]
    if proxy.https:
        lines += [f"HTTPS_PROXY={proxy.https}", f"https_proxy={proxy.https}"]
    if proxy.socks:
        lines += [f"ALL_PROXY={proxy.socks}", f"all_proxy={proxy.socks}"]
    if proxy.no_proxy:
        lines += [f"NO_PROXY={proxy.no_proxy}", f"no_proxy={proxy.no_proxy}"]

    env_file.write_text("\n".join(lines) + "\n")

"""
modules/orchestration/config-parser/parser.py
声明式配置解析器 — 将 swarm.yaml 解析为标准化内部数据结构。

这是从 lib/pod_utils.py 中迁移并增强的版本，增加了：
- Pydantic 风格的字段校验（纯 Python dataclass 实现，无额外依赖）
- 友好的错误信息（含字段路径提示）
- SecretRef 解析（${VAR} 和 env:VAR 两种格式）
"""
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from utils import resolve_secret_ref, resolve_pod, run_systemctl


# ── 数据结构 ──────────────────────────────────────────────────────────────────
@dataclass
class ProxyConfig:
    http: str = ""
    https: str = ""
    socks: str = ""
    no_proxy: str = ""


@dataclass
class PodConfig:
    name: str
    profile: str
    port: int
    token: str
    browser: str = "dedicated"
    plugins: list = field(default_factory=list)
    matrix: dict = field(default_factory=dict)


@dataclass
class SwarmConfig:
    proxy: ProxyConfig
    orphan_policy: str
    plugins: list
    matrix: dict
    pods: list[PodConfig]


# ── 主解析器 ──────────────────────────────────────────────────────────────────
def parse(config_path: Path) -> SwarmConfig:
    """
    读取并校验 swarm.yaml，返回 SwarmConfig 数据结构。
    遇到非法字段时抛出带字段路径的 ValueError。
    """
    if not config_path.exists():
        raise FileNotFoundError(f"找不到配置文件: {config_path}")

    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("swarm.yaml 格式无效：根节点必须为 YAML 字典")

    g = raw.get("global", {})

    # ── 全局代理 ──
    proxy_raw = g.get("proxy", {})
    proxy = ProxyConfig(
        http=resolve_secret_ref(proxy_raw.get("http", "")),
        https=resolve_secret_ref(proxy_raw.get("https", "")),
        socks=resolve_secret_ref(proxy_raw.get("socks", "")),
        no_proxy=proxy_raw.get("no_proxy", ""),
    )

    # ── Pod 列表 ──
    pods_raw = raw.get("pods", [])
    if not isinstance(pods_raw, list):
        raise ValueError("swarm.yaml: 'pods' 字段必须为列表")

    pods = []
    for i, p in enumerate(pods_raw):
        loc = f"pods[{i}]"
        for required in ("name", "port", "token"):
            if required not in p:
                raise ValueError(f"swarm.yaml: {loc}.{required} 为必填字段")
        if not isinstance(p["port"], int):
            raise ValueError(f"swarm.yaml: {loc}.port 必须为整数，当前值: {p['port']!r}")

        pods.append(PodConfig(
            name=p["name"],
            profile=p.get("profile", p["name"]),
            port=p["port"],
            token=resolve_secret_ref(str(p["token"])),
            browser=p.get("resources", {}).get("browser", "dedicated"),
            plugins=p.get("plugins", []),
            matrix=p.get("matrix", {}),
        ))

    return SwarmConfig(
        proxy=proxy,
        orphan_policy=g.get("orphan_policy", "warn"),
        plugins=g.get("plugins", []),
        matrix=g.get("matrix", {}),
        pods=pods,
    )


# ── 向后兼容导出（供遗留脚本过渡期使用）─────────────────────────────────────
def get_swarm_config(config_path: Optional[Path] = None) -> dict:
    """向后兼容接口：返回原始 dict，供旧脚本过渡使用。"""
    import yaml
    path = config_path or (Path(__file__).resolve().parent.parent.parent.parent / "swarm.yaml")
    if not path.exists():
        raise FileNotFoundError(f"找不到配置文件: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


# 向后兼容：允许 from parser import resolve_pod
__all__ = ["parse", "SwarmConfig", "PodConfig", "ProxyConfig", "get_swarm_config",
           "resolve_secret_ref", "resolve_pod"]

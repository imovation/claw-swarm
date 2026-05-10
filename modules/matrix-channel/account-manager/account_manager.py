"""
modules/matrix-channel/account-manager/account_manager.py
Matrix 账号管理器 — 负责将 Matrix 配置写入 Pod 的 openclaw.json，支持多账号。
"""
import json
import sys
from pathlib import Path
from typing import Optional

MODULE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(MODULE_DIR / "modules" / "orchestration" / "config-parser"))
from utils import resolve_pod, resolve_secret_ref


# ── 配置读写 ───────────────────────────────────────────────────────────────────

def load_config(pod_info: dict) -> dict:
    """读取 Pod 的 openclaw.json 配置。"""
    config_path = pod_info["config"]
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(pod_info: dict, config: dict):
    """保存配置到 Pod 的 openclaw.json。"""
    config_path = pod_info["config"]
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))


# ── 账号字段分类 ───────────────────────────────────────────────────────────────
# 顶层（channel 级别）字段：整个 Matrix channel 的设置
TOP_LEVEL_KEYS = {
    "enabled", "homeserver", "dm", "encryption", "groupPolicy",
    "autoJoin", "defaultAccount", "accounts",
}
# 账号级别字段：每个 account 子对象的配置
ACCOUNT_KEYS = {"homeserver", "userId", "accessToken", "password", "deviceName"}


def _split_conf(matrix_conf: dict) -> tuple:
    """
    将混合配置字典拆分为 (top_level, account_only)。
    top_level 只保留 belong to 顶层的 key；account_only 保留账号级 key。
    NOTE: homeserver 横跨两层（顶层和账号级均可有），两边都保留。
    """
    top = {}
    acct = {}
    for k, v in matrix_conf.items():
        if k in TOP_LEVEL_KEYS:
            top[k] = v
        if k in ACCOUNT_KEYS:
            acct[k] = v
    return top, acct


def _derive_account_key(account_conf: dict) -> Optional[str]:
    """从账号配置中推导默认的 account key（取 userId 的 localpart）。"""
    user_id = account_conf.get("userId", "")
    if user_id and ":" in user_id:
        return user_id.split(":")[0].lstrip("@")
    return None


# ── 核心写入逻辑 ───────────────────────────────────────────────────────────────

def write_matrix_config(
    profile: str,
    matrix_conf: dict,
    dry_run: bool = False,
    account_id: Optional[str] = None,
    default_account: Optional[str] = None,
):
    """
    将 Matrix 配置写入 Pod 的 openclaw.json，自动处理单/多账号格式。

    Args:
        profile: Pod 的 profile 名称
        matrix_conf: Matrix 配置字典（可同时含顶层和账号级字段）
        dry_run: 仅预览不写入
        account_id: 多账号模式下的账号 ID；为 None 时尝试保持或自动检测
        default_account: 要设置的 defaultAccount 值
    """
    pod_info = resolve_pod(profile)

    # 解析 SecretRef
    for key in ("accessToken", "password"):
        if key in matrix_conf and matrix_conf[key]:
            matrix_conf[key] = resolve_secret_ref(str(matrix_conf[key]))

    top_level, acct_only = _split_conf(matrix_conf)

    # 加载现有配置
    config = load_config(pod_info)
    if "channels" not in config:
        config["channels"] = {}

    existing = config["channels"].get("matrix", {})
    has_accounts = "accounts" in existing

    # ── 决定写入模式 ──────────────────────────────────────────────────────
    if account_id:
        # 显式多账号模式
        _write_multi_account(existing, top_level, acct_only, account_id)
    elif has_accounts:
        # 自动检测：已有 accounts 结构，自动采用多账号模式
        derived = _derive_account_key(acct_only)
        if derived:
            _write_multi_account(existing, top_level, acct_only, derived)
            if not account_id:
                account_id = derived
        else:
            # 无法推导 key，回退为单账号模式（但保留已有 accounts）
            _write_single_account(existing, top_level, acct_only)
    else:
        # 单账号模式（向后兼容）
        _write_single_account(existing, top_level, acct_only)

    # 设置 defaultAccount（仅当明确指定或自动推导时）
    if default_account:
        existing["defaultAccount"] = default_account
    elif account_id and has_accounts and "defaultAccount" not in existing:
        # 首次添加多账号时自动设置第一个账号为默认
        existing["defaultAccount"] = account_id

    config["channels"]["matrix"] = existing

    if dry_run:
        print(f"   📝 [DRY RUN] 将写入 Matrix 配置到 {pod_info['config']}")
        print(f"   {json.dumps(existing, indent=4, ensure_ascii=False)}")
        return

    save_config(pod_info, config)
    print(f"   ✅ Matrix 配置已写入 {pod_info['config']}")


def _write_multi_account(existing: dict, top_level: dict, acct: dict, account_id: str):
    """
    写入多账号模式：将 top_level 合并到现有顶层，acct 写入 accounts.<account_id>。
    """
    # 合并顶层字段（不覆盖已有值，除非明确指定）
    for k, v in top_level.items():
        if k == "homeserver":
            # homeserver 在顶层只在尚未设置时写入
            existing.setdefault("homeserver", v)
        elif k != "accounts":
            existing[k] = v

    existing.setdefault("enabled", True)
    existing.setdefault("accounts", {})
    existing["accounts"][account_id] = acct


def _write_single_account(existing: dict, top_level: dict, acct: dict):
    """
    写入单账号模式：合并 top_level 和 acct，保留已有 accounts（如果存在）。
    """
    merged = {**existing, **top_level, **acct}
    # 保留已有的 accounts 结构（如果存在）
    if "accounts" in existing:
        merged["accounts"] = existing["accounts"]
    existing.clear()
    existing.update(merged)


# ── 列出账号 ───────────────────────────────────────────────────────────────────

def list_accounts(profile: str):
    """列出 Pod 的所有已配置 Matrix 账号。"""
    pod_info = resolve_pod(profile)
    config = load_config(pod_info)
    matrix = config.get("channels", {}).get("matrix", {})

    if not matrix:
        print(f"⚠️  Pod '{profile}' 尚未配置 Matrix 渠道")
        return

    enabled = matrix.get("enabled", False)
    homeserver = matrix.get("homeserver", "N/A")
    default_account = matrix.get("defaultAccount", "")
    accounts = matrix.get("accounts", {})

    print(f"📋 Pod '{profile}' Matrix 账号配置:")
    print(f"   Enabled:     {'✅ 是' if enabled else '❌ 否'}")
    print(f"   Homeserver:  {homeserver}")
    print(f"   Encryption:  {'启用' if matrix.get('encryption') else '禁用'}")
    if default_account:
        print(f"   Default:     {default_account}")

    if accounts:
        print(f"   账号 ({len(accounts)}):")
        for acct_id, acct in accounts.items():
            marker = " ⭐" if acct_id == default_account else ""
            user_id = acct.get("userId", "N/A")
            auth = "token" if "accessToken" in acct else "password"
            device = acct.get("deviceName", "N/A")
            print(f"     • {acct_id}{marker}")
            print(f"       userId:   {user_id}")
            print(f"       auth:     {auth}")
            print(f"       device:   {device}")
    else:
        # 单账号模式
        user_id = matrix.get("userId", "N/A")
        auth = "token" if "accessToken" in matrix else ("password" if "password" in matrix else "none")
        device = matrix.get("deviceName", matrix.get("name", "N/A"))
        print(f"   模式: 单账号")
        print(f"     userId:   {user_id}")
        print(f"     auth:     {auth}")
        print(f"     device:   {device}")


# ── CLI 入口 ───────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Matrix 账号配置管理 — 支持单/多账号写入与列表查询',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  claw matrix add default --homeserver https://matrix.example.org --user-id @bot:example.org --password xxx
  claw matrix add default --homeserver https://matrix.example.org --account mybot --user-id @mybot:example.org --password xxx
  claw matrix list default
        """,
    )
    parser.add_argument("subcommand", choices=["add", "list"], help="操作类型: add (添加/更新账号) 或 list (列出账号)")
    parser.add_argument("profile", help="Pod profile 名称")
    parser.add_argument("--homeserver", help="Matrix homeserver URL")
    parser.add_argument("--token", help="Matrix accessToken (token 认证)")
    parser.add_argument("--user-id", help="Matrix userId (用于密码认证)")
    parser.add_argument("--password", help="Matrix password (用于密码认证)")
    parser.add_argument("--encryption", action="store_true", help="启用 E2EE 加密")
    parser.add_argument("--name", help="设备显示名称 (deviceName)")
    parser.add_argument("--account", help="多账号模式: 指定账号 ID (写入 accounts.<id>)")
    parser.add_argument("--default-account", help="设置默认账号 ID (defaultAccount)")
    parser.add_argument("--dm-policy", default="pairing",
                        help="私信策略: allowlist/pairing/open/disabled (默认: pairing)")
    parser.add_argument("--dry-run", action="store_true", help="仅预览，不实际写入")
    args = parser.parse_args()

    if args.subcommand == "list":
        list_accounts(args.profile)
        return

    # ── "add" 模式 ─────────────────────────────────────────────────────────
    if not args.homeserver:
        print("❌ 错误: add 操作需要 --homeserver 参数")
        sys.exit(1)

    if not args.user_id and not args.token:
        print("❌ 错误: add 操作需要 --user-id (密码认证) 或 --token (token 认证)")
        sys.exit(1)

    # 构建混合配置字典（顶层 + 账号级字段混在一起，由 write_matrix_config 自动拆分）
    matrix_conf = {
        "enabled": True,
        "homeserver": args.homeserver,
    }
    if args.token:
        matrix_conf["accessToken"] = args.token
    if args.user_id:
        matrix_conf["userId"] = args.user_id
    if args.password:
        matrix_conf["password"] = args.password
    if args.encryption:
        matrix_conf["encryption"] = True
    if args.name:
        matrix_conf["deviceName"] = args.name
    if args.dm_policy != "pairing":
        matrix_conf["dm"] = {"policy": args.dm_policy}

    write_matrix_config(
        args.profile,
        matrix_conf,
        dry_run=args.dry_run,
        account_id=args.account,
        default_account=args.default_account,
    )


if __name__ == "__main__":
    main()

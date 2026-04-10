"""
modules/matrix-channel/e2ee-verifier/e2ee_verifier.py
Matrix E2EE 验证器 — 负责检查、初始化、备份加密状态。
"""
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "modules" / "orchestration" / "config-parser"))
from parser import resolve_pod


def get_matrix_dir(profile: str) -> Path:
    """获取 Pod 的 Matrix 数据目录。"""
    pod_info = resolve_pod(profile)
    return pod_info["dir"] / "matrix"


def run_openclaw(args: list, profile: str):
    """运行 openclaw 命令，注入正确的环境变量。"""
    pod_info = resolve_pod(profile)
    env_file = pod_info["dir"] / "runtime" / "env"
    
    env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                env[k] = v
    
    result = subprocess.run(
        ["openclaw"] + args,
        capture_output=True,
        text=True,
        env={**subprocess.os.environ, **env},
    )
    return result


def status(profile: str, verbose: bool = False):
    """检查 Matrix E2EE 状态。"""
    matrix_dir = get_matrix_dir(profile)
    
    if not matrix_dir.exists():
        print(f"⚠️  Pod '{profile}' 的 Matrix 目录不存在 (路径: {matrix_dir})")
        print("   提示：请先为该 Pod 启用 Matrix 渠道并运行一次。")
        return False
    
    # 检查加密密钥文件
    olm_keys = matrix_dir / "olm.json"
    if olm_keys.exists():
        print(f"✅ Pod '{profile}' 已初始化 E2EE 加密")
        print(f"   密钥文件: {olm_keys}")
        if verbose:
            import json
            try:
                data = json.loads(olm_keys.read_text())
                if "backup" in data:
                    print(f"   密钥备份: 已创建")
                else:
                    print(f"   密钥备份: 未创建")
            except Exception:
                pass
    else:
        print(f"⚠️  Pod '{profile}' 尚未初始化 E2EE 加密")
        print(f"   运行 'claw matrix verify <profile> bootstrap' 进行初始化")
    
    return True


def bootstrap(profile: str):
    """初始化 E2EE 自举 (Bootstrap)。"""
    print(f"🚀 正在为 Pod '{profile}' 初始化 E2EE 加密...")
    
    # 通过 openclaw CLI 执行 bootstrap
    result = run_openclaw(["gateway", "matrix", "bootstrap"], profile)
    
    if result.returncode == 0:
        print(f"✅ E2EE 初始化成功")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ E2EE 初始化失败")
        if result.stderr:
            print(result.stderr)
        sys.exit(1)


def backup_status(profile: str):
    """检查密钥备份状态。"""
    matrix_dir = get_matrix_dir(profile)
    backup_file = matrix_dir / "keys" / "backup.json"
    
    if backup_file.exists():
        print(f"✅ 密钥备份已创建: {backup_file}")
    else:
        print(f"⚠️  密钥备份尚未创建")
        print("   提示：E2EE 初始化时自动创建备份，建议妥善保存")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Matrix E2EE 验证管理')
    parser.add_argument("profile", help="Pod profile 名称")
    parser.add_argument("action", choices=["status", "bootstrap", "backup"], 
                        help="操作: status/bootstrap/backup")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()

    if args.action == "status":
        status(args.profile, verbose=args.verbose)
    elif args.action == "bootstrap":
        bootstrap(args.profile)
    elif args.action == "backup":
        backup_status(args.profile)


if __name__ == "__main__":
    main()
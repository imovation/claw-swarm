"""
tests/test_utils.py
共享工具模块单元测试
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "orchestration" / "config-parser"))

from utils import resolve_secret_ref, resolve_pod, PodInfo, MAIN_POD_ALIASES


class TestResolveSecretRef(unittest.TestCase):
    """测试 resolve_secret_ref 函数。"""

    def test_plain_string(self):
        """测试普通字符串直接返回。"""
        result = resolve_secret_ref("plain_value")
        assert result == "plain_value"

    def test_env_var_format(self):
        """测试 ${VAR} 格式。"""
        with patch.dict(os.environ, {"TEST_VAR": "test_value"}):
            result = resolve_secret_ref("${TEST_VAR}")
            assert result == "test_value"

    def test_env_var_not_found(self):
        """测试环境变量不存在时返回原值。"""
        result = resolve_secret_ref("${NON_EXISTENT_VAR}")
        assert result == "${NON_EXISTENT_VAR}"

    def test_env_prefix_format(self):
        """测试 env:VAR 格式。"""
        with patch.dict(os.environ, {"MY_VAR": "my_value"}):
            result = resolve_secret_ref("env:MY_VAR")
            assert result == "my_value"

    def test_non_string_input(self):
        """测试非字符串输入直接返回。"""
        result = resolve_secret_ref(123)
        assert result == 123

    def test_empty_string(self):
        """测试空字符串。"""
        result = resolve_secret_ref("")
        assert result == ""


class TestResolvePod(unittest.TestCase):
    """测试 resolve_pod 函数。"""

    def test_main_alias_default(self):
        """测试 main 别名映射到 default profile。"""
        result = resolve_pod("main")
        assert result["profile_arg"] == "default"
        assert result["service_name"] == "openclaw-gateway"

    def test_default_alias(self):
        """测试 default 别名。"""
        result = resolve_pod("default")
        assert result["profile_arg"] == "default"

    def test_gateway_alias(self):
        """测试 gateway 别名。"""
        result = resolve_pod("gateway")
        assert result["profile_arg"] == "default"

    def test_custom_profile(self):
        """测试自定义 profile。"""
        result = resolve_pod("aimee")
        assert result["profile_arg"] == "aimee"
        assert result["service_name"] == "openclaw-gateway-aimee"

    def test_return_type(self):
        """测试返回类型包含所有必需键。"""
        result = resolve_pod("test")
        assert "profile_arg" in result
        assert "dir" in result
        assert "service_name" in result
        assert "service" in result
        assert "config" in result


class TestMainPodAliases(unittest.TestCase):
    """测试 MAIN_POD_ALIASES 常量。"""

    def test_contains_expected_aliases(self):
        """测试包含预期的别名。"""
        assert "default" in MAIN_POD_ALIASES
        assert "main" in MAIN_POD_ALIASES
        assert "gateway" in MAIN_POD_ALIASES

    def test_is_frozen(self):
        """测试是集合类型。"""
        assert isinstance(MAIN_POD_ALIASES, (set, frozenset))


if __name__ == "__main__":
    import unittest
    unittest.main()
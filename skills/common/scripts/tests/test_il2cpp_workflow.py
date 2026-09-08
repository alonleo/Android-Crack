"""契约测试：策略路由三层架构

覆盖三层架构：
- Layer 1  sniff_routing      APK → type（策略路由表）
- Layer 2  stage_routing      type → [stage_ids] + mandatory（策略阶段路由表）
- Layer 3  stage_details      stage_id → {script, function, role}（子阶段详情表）
- metadata  tools / notes / legacy_stage_map

从单一 types.X 结构拆分为三层独立 section 后，
各层可独立查询、独立缓存、独立测试。
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
STRATEGY_YAML = REPO_ROOT / "tools" / "scripts" / "strategy" / "strategy-config.yaml"
STRATEGY_PY = REPO_ROOT / "tools" / "scripts" / "strategy" / "strategy-config.py"
CRACK_PY = REPO_ROOT / "tools" / "scripts" / "crack.py"


def _load_module(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载模块：{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ════════════════════════════════════════════════════════════════════════════
# Layer 1: sniff_routing（APK → type）
# ════════════════════════════════════════════════════════════════════════════

class SniffRoutingTests(unittest.TestCase):
    """策略路由表：sniff_patterns → type。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = _load_module(STRATEGY_PY, "strategy_config_under_test")

    def test_sniff_routing_section_exists(self) -> None:
        cfg = self.cfg.load_config()
        self.assertIn("sniff_routing", cfg, "顶层必须有 sniff_routing section")
        self.assertIn("order", cfg["sniff_routing"])
        self.assertIn("patterns", cfg["sniff_routing"])

    def test_sniff_order_is_non_empty(self) -> None:
        order = self.cfg.get_sniff_order()
        self.assertIsInstance(order, list)
        self.assertGreater(len(order), 0)
        self.assertEqual(order[0], "air", "嗅探优先级首项必须是 air")

    def test_all_types_have_patterns(self) -> None:
        patterns = self.cfg.get_sniff_patterns()
        order = self.cfg.get_sniff_order()
        for t in order:
            self.assertIn(t, patterns, f"{t} 必须有 sniff patterns")
            self.assertGreater(len(patterns[t]), 0, f"{t} 的 patterns 不能为空")

    def test_get_sniff_patterns_specific_type(self) -> None:
        il2cpp_patterns = self.cfg.get_sniff_patterns("il2cpp")
        self.assertIn("libil2cpp", str(il2cpp_patterns))

    def test_detect_type_fake_il2cpp(self) -> None:
        """伪造 il2cpp APK（zip 含 libil2cpp.so）应被识别为 il2cpp。"""
        import tempfile
        import zipfile
        with tempfile.NamedTemporaryFile(suffix=".apk", delete=False) as tf:
            with zipfile.ZipFile(tf.name, "w") as z:
                z.writestr("lib/arm64-v8a/libil2cpp.so", b"fake")
                z.writestr("classes.dex", b"fake")
            result = self.cfg.detect_type(tf.name)
        self.assertEqual(result, "il2cpp", "应识别为 il2cpp")


# ════════════════════════════════════════════════════════════════════════════
# Layer 2: stage_routing（type → stages）
# ════════════════════════════════════════════════════════════════════════════

class StageRoutingTests(unittest.TestCase):
    """策略阶段路由表：type → [stage_ids] + mandatory。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = _load_module(STRATEGY_PY, "strategy_config_under_test")

    def test_stage_routing_section_exists(self) -> None:
        cfg = self.cfg.load_config()
        self.assertIn("stage_routing", cfg, "顶层必须有 stage_routing section")
        # 所有 sniff_order 中的 type 都应有 stage_routing
        for t in cfg["sniff_routing"]["order"]:
            self.assertIn(t, cfg["stage_routing"], f"{t} 必须在 stage_routing")

    def test_get_stage_routing_returns_list(self) -> None:
        stages = self.cfg.get_stage_routing("il2cpp")
        self.assertIsInstance(stages, list)
        self.assertEqual(len(stages), 15, f"il2cpp 应有 15 个阶段，实际 {len(stages)}")

    def test_get_stage_routing_android(self) -> None:
        stages = self.cfg.get_stage_routing("android")
        self.assertIsInstance(stages, list)
        self.assertEqual(len(stages), 15, f"android 应有 15 个阶段，实际 {len(stages)}")

    def test_get_mandatory_stages(self) -> None:
        mandatory = self.cfg.get_mandatory_stages("il2cpp")
        self.assertIsInstance(mandatory, list)
        self.assertEqual(len(mandatory), 10, f"il2cpp 应有 10 个强制阶段，实际 {len(mandatory)}")
        # 强制阶段必须是 stage_details 已知 id 的子集
        all_ids = set(self.cfg.list_stage_details("il2cpp").keys())
        for s in mandatory:
            self.assertIn(s, all_ids, f"强制阶段 {s} 必须属于 stage_details id")

    def test_stage_routing_unknown_type_falls_back_to_android(self) -> None:
        stages = self.cfg.get_stage_routing("unknown_type_xyz")
        # 未知 type 应 fallback 到 android
        android_stages = self.cfg.get_stage_routing("android")
        self.assertEqual(stages, android_stages)


# ════════════════════════════════════════════════════════════════════════════
# Layer 3: stage_details（stage_id → {script, function, role}）
# ════════════════════════════════════════════════════════════════════════════

class StageDetailsTests(unittest.TestCase):
    """子阶段详情表：stage_id → {script, function, role, mode, outputs}。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = _load_module(STRATEGY_PY, "strategy_config_under_test")

    def test_stage_details_section_exists(self) -> None:
        cfg = self.cfg.load_config()
        self.assertIn("stage_details", cfg, "顶层必须有 stage_details section")
        # 至少 il2cpp + android 应有完整 stage_details
        self.assertIn("il2cpp", cfg["stage_details"])
        self.assertIn("android", cfg["stage_details"])

    def test_il2cpp_stage_details_complete(self) -> None:
        details = self.cfg.list_stage_details("il2cpp")
        self.assertEqual(len(details), 19, f"il2cpp 应有 19 个 stage_details（15 子阶段 + 4 主阶段），实际 {len(details)}")

    def test_android_stage_details_complete(self) -> None:
        details = self.cfg.list_stage_details("android")
        self.assertEqual(len(details), 19, f"android 应有 19 个 stage_details（15 子阶段 + 4 主阶段），实际 {len(details)}")

    def test_stage_detail_has_required_fields(self) -> None:
        detail = self.cfg.get_stage_detail("il2cpp", "15")
        self.assertIn("script", detail, "详情必须含 script 字段")
        self.assertIn("function", detail, "详情必须含 function 字段")
        self.assertIn("role", detail, "详情必须含 role 字段")
        # 验证字段语义
        self.assertTrue(detail["script"].endswith(".py"), "script 必须以 .py 结尾")
        self.assertGreater(len(detail["function"]), 0, "function 非空")
        self.assertGreater(len(detail["role"]), 0, "role 非空")

    def test_stage_detail_scripts_exist(self) -> None:
        """所有 stage_details 中的 script 路径必须真实存在。"""
        for type_name in ["il2cpp", "android"]:
            details = self.cfg.list_stage_details(type_name)
            for stage_id, detail in details.items():
                script_rel = detail.get("script", "")
                if script_rel:
                    script_path = REPO_ROOT / script_rel
                    self.assertTrue(
                        script_path.is_file(),
                        f"{type_name}/{stage_id} 的脚本不存在: {script_rel}",
                    )

    def test_stage_detail_unknown_returns_empty(self) -> None:
        detail = self.cfg.get_stage_detail("il2cpp", "99")
        self.assertEqual(detail, {}, "未知 stage 应返回空 dict")


# ════════════════════════════════════════════════════════════════════════════
# Metadata: tools / notes / legacy_stage_map
# ════════════════════════════════════════════════════════════════════════════

class MetadataTests(unittest.TestCase):
    """元数据：tools / notes / legacy_stage_map。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cfg = _load_module(STRATEGY_PY, "strategy_config_under_test")

    def test_metadata_section_exists(self) -> None:
        cfg = self.cfg.load_config()
        self.assertIn("metadata", cfg)
        self.assertIn("tools", cfg["metadata"])
        self.assertIn("notes", cfg["metadata"])
        self.assertIn("legacy_stage_map", cfg["metadata"])

    def test_get_tools(self) -> None:
        tools = self.cfg.get_tools("il2cpp")
        self.assertIn("static_primary", tools)
        self.assertIn("dynamic", tools)
        self.assertIn("build", tools)

    def test_get_notes(self) -> None:
        notes = self.cfg.get_notes("il2cpp")
        self.assertIsInstance(notes, str)
        self.assertIn("REFACTOR 2026-08-10", notes, "notes 应包含重构标记")

    def test_resolve_legacy_stage(self) -> None:
        # legacy_stage_map 已随 15 阶段归一清空——旧编号不再迁移。
        # resolve_legacy_stage 在无映射时原样返回。
        self.assertEqual(self.cfg.resolve_legacy_stage("il2cpp", "01"), "01")
        # 未知 legacy → 原样返回
        self.assertEqual(self.cfg.resolve_legacy_stage("il2cpp", "unknown_legacy"), "unknown_legacy")


# ════════════════════════════════════════════════════════════════════════════
# crack.py 兼容性
# ════════════════════════════════════════════════════════════════════════════

class CrackSchedulerTests(unittest.TestCase):
    """crack.py 必须能通过新的三层 API 查询 stage 脚本路径。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.crack = _load_module(CRACK_PY, "crack_under_test")

    def test_crack_exposes_3layer_api(self) -> None:
        """crack.py 必须暴露三层 API 入口。"""
        self.assertTrue(hasattr(self.crack, "resolve_stage_script"),
                        "crack.py 必须暴露 resolve_stage_script")
        self.assertTrue(hasattr(self.crack, "load_stage_registry"),
                        "crack.py 必须暴露 load_stage_registry")
        self.assertTrue(hasattr(self.crack, "resolve_legacy_stage"),
                        "crack.py 必须暴露 resolve_legacy_stage")

    def test_resolve_stage_uses_new_3layer_yaml(self) -> None:
        """resolve_stage_script 应使用新的 stage_details（Layer 3）"""
        # 通过 Layer 3 API 获取 il2cpp 04 的脚本路径
        strategy_cfg = _load_module(STRATEGY_PY, "strategy_cfg_for_crack_test")
        detail = strategy_cfg.get_stage_detail("il2cpp", "04")
        expected_script = detail["script"]
        expected_path = (REPO_ROOT / expected_script).resolve()

        # crack.py 应能解析到同一路径
        path = self.crack.resolve_stage_script("il2cpp", "04")
        self.assertEqual(pathlib.Path(path).resolve(), expected_path)


if __name__ == "__main__":
    unittest.main()
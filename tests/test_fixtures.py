import ast
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evals" / "fixtures"
RUNNABLE = [
    FIXTURES / "duplicate-side-effect" / "harness.py",
    FIXTURES / "shared-memory" / "harness.py",
    FIXTURES / "trust-inversion" / "harness.py",
    FIXTURES / "false-completion" / "harness.py",
]


class FixtureSafetyTests(unittest.TestCase):
    def simulate(self, path):
        namespace = runpy.run_path(str(path), run_name="fixture_test")
        return namespace["simulate"]()

    def test_runnable_fixtures_use_only_reviewed_standard_library_imports(self):
        allowed = {"json", "pathlib"}
        for path in RUNNABLE:
            with self.subTest(path=path):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                imports = {
                    alias.name.split(".")[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.Import)
                    for alias in node.names
                }
                imports.update(
                    node.module.split(".")[0]
                    for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module
                )
                self.assertLessEqual(imports, allowed)

    def test_duplicate_effect_fixture_commits_twice_after_ambiguous_timeout(self):
        result = self.simulate(RUNNABLE[0])
        self.assertTrue(result["result"]["ok"])
        self.assertEqual(len(result["committed"]), 2)
        self.assertNotEqual(
            result["committed"][0]["tool_call_id"],
            result["committed"][1]["tool_call_id"],
        )

    def test_shared_memory_fixture_leaks_only_the_synthetic_marker(self):
        result = self.simulate(RUNNABLE[1])
        self.assertEqual(
            result["session_b_context"],
            [{"session_id": "session-a", "text": "fixture-secret-alice"}],
        )

    def test_trust_inversion_fixture_records_but_does_not_execute(self):
        result = self.simulate(RUNNABLE[2])
        self.assertEqual(result["would_execute"], ["forbidden_admin_tool"])
        self.assertFalse(result["executed"])

    def test_false_completion_fixture_exposes_business_failure(self):
        result = self.simulate(RUNNABLE[3])
        self.assertFalse(result["tool_result"]["ok"])
        self.assertEqual(result["run_state"], "completed")


if __name__ == "__main__":
    unittest.main()

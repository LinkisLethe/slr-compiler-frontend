import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CompilerCliTests(unittest.TestCase):
    def run_source(self, source_text):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        source_path = Path(temp_dir.name) / "input.math"
        source_path.write_text(source_text, encoding="utf-8")
        subprocess.run(
            [sys.executable, str(ROOT / "main.py"), str(source_path)],
            cwd=temp_dir.name,
            check=True,
            capture_output=True,
            text=True,
        )
        return source_path

    def test_bpt1_matches_verified_outputs(self):
        source = (ROOT / "examples" / "bpt1.math").read_text(encoding="utf-8")
        generated = self.run_source(source)
        expected_dir = ROOT / "examples" / "expected"

        for suffix in ("lexer", "parse", "type", "ast"):
            actual = json.loads(Path(f"{generated}_{suffix}.json").read_text(encoding="utf-8"))
            expected = json.loads((expected_dir / f"bpt1_{suffix}.json").read_text(encoding="utf-8"))
            self.assertEqual(actual, expected)

    def test_full_language_example_completes(self):
        source = (ROOT / "examples" / "ultra.math").read_text(encoding="utf-8")
        generated = self.run_source(source)
        ast = json.loads(Path(f"{generated}_ast.json").read_text(encoding="utf-8"))
        self.assertGreater(len(ast), 1)

    def test_lexical_error_stops_later_phases(self):
        generated = self.run_source("Compute @ .")
        for suffix in ("lexer", "parse", "type", "ast"):
            self.assertEqual(
                Path(f"{generated}_{suffix}.json").read_text(encoding="utf-8"),
                "Lexical error",
            )

    def test_type_error_preserves_earlier_results(self):
        generated = self.run_source("Let bool x be 4 . Compute x .")
        self.assertIsInstance(
            json.loads(Path(f"{generated}_parse.json").read_text(encoding="utf-8")),
            dict,
        )
        self.assertEqual(Path(f"{generated}_type.json").read_text(encoding="utf-8"), "Type error")
        self.assertEqual(Path(f"{generated}_ast.json").read_text(encoding="utf-8"), "Type error")


if __name__ == "__main__":
    unittest.main()

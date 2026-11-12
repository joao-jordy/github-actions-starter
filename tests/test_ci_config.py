import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ci-config.py"
SPEC = importlib.util.spec_from_file_location("ci_config", SCRIPT)
config = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(config)
SERVICE = {"name": "web", "path": "apps/web", "type": "static", "language": "typescript"}


class ConfigurationTests(unittest.TestCase):
    def test_valid_config(self):
        self.assertEqual(config.services_from_json(json.dumps([SERVICE])), [SERVICE])

    def test_invalid_configs(self):
        for value in [
            {},
            [],
            [SERVICE, SERVICE],
            [{**SERVICE, "path": "../web"}],
            [{**SERVICE, "path": "apps/*"}],
            [{**SERVICE, "name": "pipeline"}],
            [{**SERVICE, "language": "unknown"}],
            [{**SERVICE, "type": "unknown"}],
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                config.services_from_json(json.dumps(value))

    def test_matrix_selection(self):
        for changes, run_all, expected in [
            ([], "false", []),
            (["web"], "false", [SERVICE]),
            (["pipeline"], "false", [SERVICE]),
            ([], "true", [SERVICE]),
        ]:
            with self.subTest(changes=changes, run_all=run_all):
                with tempfile.NamedTemporaryFile() as output:
                    env = {
                        **os.environ,
                        "GITHUB_OUTPUT": output.name,
                        "SERVICES": json.dumps([SERVICE]),
                        "CHANGES": json.dumps(changes),
                        "RUN_ALL": run_all,
                    }
                    subprocess.run([sys.executable, str(SCRIPT), "matrix"], env=env, check=True)
                    result = dict(line.split("=", 1) for line in pathlib.Path(output.name).read_text().splitlines())
                    self.assertEqual(json.loads(result["matrix"])["include"], expected)
                    self.assertEqual(json.loads(result["has_services"]), bool(expected))


if __name__ == "__main__":
    unittest.main()

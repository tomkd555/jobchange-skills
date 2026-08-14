"""jc_config.py の単体テスト。標準ライブラリの unittest のみを用いる。

実行:
    python -m unittest discover -s scripts/tests
    または
    python -m unittest scripts.tests.test_jc_config
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jc_config as jc  # noqa: E402


class TempTreeTestCase(unittest.TestCase):
    """一時ディレクトリを home・作業ディレクトリとして使う共通の土台。"""

    def setUp(self) -> None:
        # 設定ディレクトリ名をテスト専用の名前へ差し替える。Windows では一時ディレクトリが
        # ホームディレクトリの配下にあるため、上位ディレクトリ探索が実在の
        # ~/.job-change/config.json に当たってしまう。
        patcher = mock.patch.object(jc, "CONFIG_DIRNAME", ".job-change-test")
        patcher.start()
        self.addCleanup(patcher.stop)

        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.data_root = self.root / "data"
        self.data_root.mkdir()
        self.cwd = self.root / "work" / "nested"
        self.cwd.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write_config(self, directory: Path, **overrides: object) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": "1.0", "data_root": str(self.data_root)}
        payload.update(overrides)
        path = directory / "config.json"
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return path


class FindConfigPathTest(TempTreeTestCase):
    def test_env_var_wins(self) -> None:
        env_config = self.write_config(self.root / "explicit")
        self.write_config(self.cwd / jc.CONFIG_DIRNAME)
        self.write_config(self.home / jc.CONFIG_DIRNAME)
        found, source = jc.find_config_path(
            env={jc.ENV_VAR: str(env_config)}, start_dir=self.cwd, home=self.home
        )
        self.assertEqual(found, env_config)
        self.assertEqual(source, "env")

    def test_env_var_pointing_at_missing_file_is_ignored(self) -> None:
        home_config = self.write_config(self.home / jc.CONFIG_DIRNAME)
        found, source = jc.find_config_path(
            env={jc.ENV_VAR: str(self.root / "nope.json")}, start_dir=self.cwd, home=self.home
        )
        self.assertEqual(found, home_config)
        self.assertEqual(source, "home")

    def test_project_config_found_in_ancestor_directory(self) -> None:
        project_config = self.write_config(self.root / "work" / jc.CONFIG_DIRNAME)
        self.write_config(self.home / jc.CONFIG_DIRNAME)
        found, source = jc.find_config_path(env={}, start_dir=self.cwd, home=self.home)
        self.assertEqual(found, project_config)
        self.assertEqual(source, "project")

    def test_nearest_project_config_wins_over_outer_one(self) -> None:
        self.write_config(self.root / "work" / jc.CONFIG_DIRNAME)
        nearest = self.write_config(self.cwd / jc.CONFIG_DIRNAME)
        found, _ = jc.find_config_path(env={}, start_dir=self.cwd, home=self.home)
        self.assertEqual(found, nearest)

    def test_home_config_is_last_resort(self) -> None:
        home_config = self.write_config(self.home / jc.CONFIG_DIRNAME)
        found, source = jc.find_config_path(env={}, start_dir=self.cwd, home=self.home)
        self.assertEqual(found, home_config)
        self.assertEqual(source, "home")

    def test_returns_none_when_nothing_is_configured(self) -> None:
        found, source = jc.find_config_path(env={}, start_dir=self.cwd, home=self.home)
        self.assertIsNone(found)
        self.assertEqual(source, "")


class LoadConfigTest(TempTreeTestCase):
    def test_defaults_are_applied(self) -> None:
        path = self.write_config(self.home / jc.CONFIG_DIRNAME)
        config = jc.load_config(path)
        self.assertEqual(config["private_dir"], "career-private")
        self.assertEqual(config["companies_dir"], "companies")
        self.assertEqual(config["job_search_dir"], "job-search")
        self.assertEqual(config["python"], "python")

    def test_overrides_are_kept(self) -> None:
        path = self.write_config(self.home / jc.CONFIG_DIRNAME, python="python3", companies_dir="corp")
        config = jc.load_config(path)
        self.assertEqual(config["python"], "python3")
        self.assertEqual(config["companies_dir"], "corp")

    def test_missing_data_root_is_an_error(self) -> None:
        path = self.home / jc.CONFIG_DIRNAME / "config.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
        with self.assertRaises(jc.ConfigError):
            jc.load_config(path)

    def test_relative_data_root_is_an_error(self) -> None:
        path = self.write_config(self.home / jc.CONFIG_DIRNAME, data_root="relative-dir")
        with self.assertRaises(jc.ConfigError):
            jc.load_config(path)

    def test_broken_json_is_an_error(self) -> None:
        path = self.home / jc.CONFIG_DIRNAME / "config.json"
        path.parent.mkdir(parents=True)
        path.write_text("{ not json", encoding="utf-8")
        with self.assertRaises(jc.ConfigError):
            jc.load_config(path)

    def test_directory_name_containing_separator_is_an_error(self) -> None:
        path = self.write_config(self.home / jc.CONFIG_DIRNAME, private_dir="../outside")
        with self.assertRaises(jc.ConfigError):
            jc.load_config(path)

    def test_tilde_in_data_root_is_expanded(self) -> None:
        path = self.write_config(self.home / jc.CONFIG_DIRNAME, data_root="~/job-change-data")
        config = jc.load_config(path, home=self.home)
        self.assertEqual(config["data_root"], str(self.home / "job-change-data"))


class ResolveTest(TempTreeTestCase):
    def test_all_known_paths_are_absolute_and_under_data_root(self) -> None:
        config = jc.load_config(self.write_config(self.home / jc.CONFIG_DIRNAME))
        paths = jc.resolve_paths(config)
        for key, value in paths.items():
            with self.subTest(key=key):
                self.assertTrue(Path(value).is_absolute())
                self.assertTrue(str(value).startswith(str(self.data_root)))

    def test_private_artifacts_live_under_the_private_directory(self) -> None:
        config = jc.load_config(self.write_config(self.home / jc.CONFIG_DIRNAME))
        paths = jc.resolve_paths(config)
        private = Path(paths["private"])
        self.assertEqual(Path(paths["profile"]), private / "profile.json")
        self.assertEqual(Path(paths["company_index"]), private / "company_index.json")
        self.assertEqual(Path(paths["self_analysis"]), private / "self_analysis.json")
        self.assertEqual(Path(paths["commute"]), private / "commute.json")

    def test_custom_directory_names_are_honoured(self) -> None:
        config = jc.load_config(
            self.write_config(self.home / jc.CONFIG_DIRNAME, private_dir="secret", companies_dir="corp")
        )
        paths = jc.resolve_paths(config)
        self.assertEqual(Path(paths["private"]), self.data_root / "secret")
        self.assertEqual(Path(paths["companies"]), self.data_root / "corp")

    def test_resolve_does_not_create_directories(self) -> None:
        config = jc.load_config(self.write_config(self.home / jc.CONFIG_DIRNAME))
        jc.resolve_paths(config)
        self.assertFalse((self.data_root / "career-private").exists())


class InitConfigTest(TempTreeTestCase):
    def test_creates_config_under_home(self) -> None:
        path = jc.init_config(str(self.data_root), home=self.home)
        self.assertEqual(path, self.home / jc.CONFIG_DIRNAME / "config.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["data_root"], str(self.data_root))
        self.assertEqual(payload["schema_version"], jc.CONFIG_SCHEMA_VERSION)

    def test_does_not_overwrite_an_existing_config(self) -> None:
        existing = self.write_config(self.home / jc.CONFIG_DIRNAME, data_root=str(self.root / "old"))
        with self.assertRaises(jc.ConfigError):
            jc.init_config(str(self.data_root), home=self.home)
        payload = json.loads(existing.read_text(encoding="utf-8"))
        self.assertEqual(payload["data_root"], str(self.root / "old"))

    def test_relative_data_root_is_rejected(self) -> None:
        with self.assertRaises(jc.ConfigError):
            jc.init_config("relative-dir", home=self.home)

    def test_created_config_is_loadable(self) -> None:
        path = jc.init_config(str(self.data_root), home=self.home)
        config = jc.load_config(path)
        self.assertEqual(config["data_root"], str(self.data_root))


class MainTest(TempTreeTestCase):
    def _run(self, argv: list[str], env: dict | None = None) -> tuple[int, str]:
        from io import StringIO

        buffer = StringIO()
        code = jc.main(argv, env=env or {}, start_dir=self.cwd, home=self.home, stream=buffer)
        return code, buffer.getvalue()

    def test_show_returns_2_when_unconfigured(self) -> None:
        code, output = self._run(["--show"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output)["status"], "unconfigured")

    def test_show_returns_0_and_reports_paths(self) -> None:
        self.write_config(self.home / jc.CONFIG_DIRNAME)
        code, output = self._run(["--show"])
        self.assertEqual(code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["source"], "home")
        self.assertEqual(payload["data_root"], str(self.data_root))
        self.assertIn("profile", payload["paths"])

    def test_show_returns_1_on_invalid_config(self) -> None:
        self.write_config(self.home / jc.CONFIG_DIRNAME, data_root="relative")
        code, output = self._run(["--show"])
        self.assertEqual(code, 1)
        payload = json.loads(output)
        self.assertEqual(payload["status"], "invalid")
        self.assertTrue(payload["errors"])

    def test_init_creates_the_config(self) -> None:
        code, output = self._run(["--init", "--data-root", str(self.data_root)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["status"], "created")
        self.assertTrue((self.home / jc.CONFIG_DIRNAME / "config.json").exists())

    def test_init_returns_1_when_config_exists(self) -> None:
        self.write_config(self.home / jc.CONFIG_DIRNAME)
        code, output = self._run(["--init", "--data-root", str(self.data_root)])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output)["status"], "exists")

    def test_path_prints_a_single_absolute_path(self) -> None:
        self.write_config(self.home / jc.CONFIG_DIRNAME)
        code, output = self._run(["--path", "profile"])
        self.assertEqual(code, 0)
        self.assertEqual(output.strip(), str(self.data_root / "career-private" / "profile.json"))

    def test_path_returns_2_when_unconfigured(self) -> None:
        code, _ = self._run(["--path", "profile"])
        self.assertEqual(code, 2)

    def test_env_var_is_honoured_by_main(self) -> None:
        env_config = self.write_config(self.root / "explicit")
        code, output = self._run(["--show"], env={jc.ENV_VAR: str(env_config)})
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["source"], "env")


if __name__ == "__main__":
    unittest.main()

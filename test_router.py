import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class RouterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="router-test-", dir="/tmp/opencode")
        self.home = Path(self.tmp.name)
        self.router = Path(__file__).with_name("opencode-router")
        self.env = {"HOME": str(self.home), "PATH": f"{self.home}/bin:{os.environ['PATH']}"}
        (self.home / "bin").mkdir()
        binary = self.home / "bin/opencode"
        binary.write_text('''#!/usr/bin/env python3
import json, os, sys
if sys.argv[1:] == ["--version"]:
    print(os.environ.get("TEST_VERSION", "opencode v2.0.27"))
else:
    print(json.dumps({"args": sys.argv[1:], "env": {key: value for key, value in os.environ.items() if key.startswith(("XDG_", "OPENCODE_"))}}))
''')
        binary.chmod(0o755)
        self.call("new", "work", str(self.home))

    def tearDown(self):
        self.tmp.cleanup()

    def call(self, *args):
        return subprocess.check_output([str(self.router), *args], env=self.env, cwd=self.home, text=True).strip()

    def test_v2_launches(self):
        for args in [(), ("run", "hello"), ("mini",), ("api", "get", "/api/info")]:
            with self.subTest(args=args):
                result = json.loads(self.call("profile", "work", *args))
                expected = [args[0], "--standalone", *args[1:]] if args else ["--standalone"]
                self.assertEqual(result["args"], expected)
                self.assertEqual(result["env"]["XDG_STATE_HOME"], str(self.home / ".local/opencode-profiles/work/state"))

    def test_auth_and_service_config(self):
        result = json.loads(self.call("profile", "work", "auth", "list"))
        config = Path(result["env"]["OPENCODE_CONFIG_DIR"])
        self.assertEqual(result["args"], ["auth", "list"])
        self.assertEqual(json.loads((config / "service.json").read_text()), {"disabled": True})
        (config / "service.json").write_text('{"disabled":true,"port":54321}')
        self.call("profile", "work", "auth", "list")
        self.assertEqual(json.loads((config / "service.json").read_text())["port"], 54321)

    def test_default_drops_profile_environment(self):
        self.env.update(json.loads(self.call("profile", "work", "auth", "list"))["env"])
        result = json.loads(self.call("profile", "default", "auth", "list"))
        self.assertEqual(result["args"], ["auth", "list"])
        self.assertEqual(result["env"], {})

    def test_explicit_server_is_not_combined_with_standalone(self):
        args = ("api", "--server", "http://localhost:5555", "get", "/api/info")
        self.assertEqual(json.loads(self.call("profile", "work", *args))["args"], list(args))

    def test_no_config_and_full_isolation(self):
        for flags in [("--no-config",), ("--full-config-isolation",)]:
            with self.subTest(flags=flags):
                self.call("new", "isolated", "--force", *flags)
                result = json.loads(self.call("profile", "isolated", "auth", "list"))
                self.assertTrue(Path(result["env"]["OPENCODE_CONFIG_DIR"], "service.json").is_file())

    def test_v1_keeps_optional_state_and_argv(self):
        self.env["TEST_VERSION"] = "1.18.7"
        result = json.loads(self.call("profile", "work", "run", "hello"))
        self.assertEqual(result["args"], ["run", "hello"])
        self.assertNotIn("XDG_STATE_HOME", result["env"])

    def test_shared_config_and_definitions_are_linked_without_overwriting(self):
        shared = self.home / ".config/opencode"
        (shared / "commands").mkdir(parents=True)
        (shared / "opencode.jsonc").write_text('{"agents":{"plan":{"color":"#8AADF4"}}}')
        (shared / "commands/shared.md").write_text("shared command")
        (shared / "commands/own.md").write_text("global command")
        profile = self.home / ".config/opencode-router/profiles/work/config/opencode"
        (profile / "commands").mkdir()
        (profile / "commands/own.md").write_text("profile command")
        self.call("profile", "work", "auth", "list")
        self.assertTrue((profile / "opencode.json").is_symlink())
        self.assertTrue((profile / "commands/shared.md").is_symlink())
        self.assertEqual((profile / "commands/own.md").read_text(), "profile command")
        self.call("new", "private", "--full-config-isolation")
        self.call("profile", "private", "auth", "list")
        self.assertFalse((self.home / ".config/opencode-router/profiles/private/config/opencode/opencode.json").exists())

    def test_v2_commands_are_not_directory_arguments(self):
        for command in ["api", "mini", "pair", "reload", "service", "update"]:
            (self.home / command).mkdir()
            self.call("new", command, str(self.home / command))
            self.assertEqual(self.call("which", command), "work")

    def test_concurrent_profile_launches(self):
        shared = self.home / ".config/opencode"
        (shared / "plugins").mkdir(parents=True)
        (shared / "plugins/state.js").write_text("export default {}")
        (shared / "opencode.jsonc").write_text("{}")
        (shared / "AGENTS.md").write_text("shared instructions")
        processes = [subprocess.Popen([str(self.router), "profile", "work", "auth", "list"], env=self.env,
                                      cwd=self.home, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for _ in range(8)]
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertEqual(json.loads(stdout)["args"], ["auth", "list"])


if __name__ == "__main__":
    unittest.main()

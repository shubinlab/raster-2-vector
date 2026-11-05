"""OS-neutral skill distribution tests. No imaging dependencies."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("r2v_installer",ROOT/"scripts"/"install.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class DistributionTests(unittest.TestCase):
    def test_metadata(self):
        s=(ROOT/"SKILL.md").read_text("utf-8")
        self.assertTrue(s.startswith("---\n"))
        self.assertIn("name: raster-2-vector",s.split("---",2)[1])
    def test_project_install_agents(self):
        with tempfile.TemporaryDirectory() as d:
            for agent in ("codex","claude-code","cursor","opencode","gemini-cli",
                          "github-copilot","hermes-agent","openclaw"):
                paths=mod.install(agent,scope="project",project_dir=Path(d)/agent)
                self.assertEqual(len(paths),1)
                self.assertTrue((paths[0]/"SKILL.md").is_file())
                self.assertTrue((paths[0]/"scripts"/"r2v.py").is_file())
    def test_all_agents_deduplicated(self):
        with tempfile.TemporaryDirectory() as d:
            paths=mod.install("all",scope="project",project_dir=Path(d))
            self.assertEqual(len(paths),len(set(paths)))
            self.assertGreaterEqual(len(paths),2)
    def test_install_into_source_repo_no_recursion(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"SKILL.md").write_text("---\\nname: raster-2-vector\\n---\\n")
            (root/"scripts").mkdir()
            (root/"scripts"/"r2v.py").write_text("# dummy")
            old_root=mod.ROOT
            mod.ROOT=root
            try:
                paths=mod.install("codex",scope="project",project_dir=root)
                self.assertTrue((paths[0]/"SKILL.md").is_file())
                self.assertFalse((paths[0]/".agents").exists())
            finally:
                mod.ROOT=old_root

    def test_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            mod.install("codex",scope="user",home=Path(d))
            with self.assertRaises(FileExistsError):
                mod.install("codex",scope="user",home=Path(d))

if __name__=="__main__":unittest.main()

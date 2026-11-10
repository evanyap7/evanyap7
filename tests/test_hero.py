"""Smoke-test the hero banner renderer. Stdlib only: python3 -m unittest."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG = "{http://www.w3.org/2000/svg}"


def render(**env):
    tmp = Path(tempfile.mkdtemp())
    (tmp / "scripts").mkdir()
    shutil.copy(ROOT / "scripts" / "render_hero_svg.py", tmp / "scripts")
    subprocess.run(
        [sys.executable, str(tmp / "scripts" / "render_hero_svg.py")], check=True, capture_output=True, env=env
    )
    return tmp, (tmp / "hero.svg").read_text()


class RenderHero(unittest.TestCase):
    def test_animated_is_well_formed_with_one_timeline_per_phrase(self):
        tmp, text = render()
        self.addCleanup(shutil.rmtree, tmp)
        ET.fromstring(text)  # raises if not well-formed XML
        for kind in "wcv":
            self.assertEqual(len(re.findall(rf"@keyframes {kind}\d+", text)), 3)

    def test_visibility_keyframes_never_ramp(self):
        tmp, text = render()
        self.addCleanup(shutil.rmtree, tmp)
        # A repeated offset with a different value makes the browser ramp opacity (a later phrase showed through
        # while it should have been hidden), so every offset in a phrase's visibility timeline must be unique.
        blocks = re.findall(r"@keyframes v\d+\{(.*?)\}\.w\d+", text)
        self.assertEqual(len(blocks), 3)
        for block in blocks:
            values = {}
            for offsets, value in re.findall(r"([\d.%,]+)\{opacity:([01])\}", block):
                for offset in offsets.split(","):
                    self.assertEqual(values.setdefault(offset, value), value, f"{offset} has conflicting opacities")

    def test_static_mode_has_no_animation(self):
        tmp, text = render(STATIC="1")
        self.addCleanup(shutil.rmtree, tmp)
        root = ET.fromstring(text)
        self.assertNotIn("@keyframes", text)
        self.assertEqual(len(list(root.iter(f"{SVG}clipPath"))), 0)


if __name__ == "__main__":
    unittest.main()

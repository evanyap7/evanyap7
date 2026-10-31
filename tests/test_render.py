"""Smoke-test the heatmap renderer against the committed data. Stdlib only: python3 -m unittest."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG = "{http://www.w3.org/2000/svg}"


class RenderHeatmap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The script writes next to its own parent dir, so render inside a throwaway copy.
        cls.tmp = Path(tempfile.mkdtemp())
        (cls.tmp / "scripts").mkdir()
        (cls.tmp / "data").mkdir()
        shutil.copy(ROOT / "scripts" / "render_heatmap_svg.py", cls.tmp / "scripts")
        shutil.copy(ROOT / "data" / "contributions.json", cls.tmp / "data")
        cls.data = json.loads((ROOT / "data" / "contributions.json").read_text())
        subprocess.run([sys.executable, str(cls.tmp / "scripts" / "render_heatmap_svg.py")], check=True, capture_output=True)
        cls.svg = ET.parse(cls.tmp / "contrib-heatmap.svg").getroot()  # raises if not well-formed XML

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_one_cell_per_day(self):
        cells = [r for r in self.svg.iter(f"{SVG}rect") if r.find(f"{SVG}title") is not None]
        self.assertEqual(len(cells), len(self.data["days"]))

    def test_days_are_sorted_and_unique(self):
        dates = [d["date"] for d in self.data["days"]]
        self.assertEqual(dates, sorted(set(dates)))

    def test_total_matches_sum_of_days(self):
        self.assertEqual(self.data["total"], sum(d["count"] for d in self.data["days"]))

    def test_streaks_are_consistent(self):
        self.assertLessEqual(self.data["current_streak"], self.data["longest_streak"])

    def test_summary_line_uses_the_data(self):
        text = " ".join("".join(t.itertext()) for t in self.svg.iter(f"{SVG}text"))
        self.assertIn(f"{self.data['total']} contributions", text)


if __name__ == "__main__":
    unittest.main()

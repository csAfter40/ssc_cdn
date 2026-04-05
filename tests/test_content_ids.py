"""
Validate that top-level category, subcategory, and script objects have unique `id`
values within each locale JSON file (en / tr).
"""

from __future__ import annotations

import json
import unittest
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "assets" / "content"
LOCALES = ("en", "tr")
CONTENT_BASENAMES = ("categories.json", "subcategories.json", "scripts.json")


def content_json_paths() -> list[Path]:
    paths: list[Path] = []
    for locale in LOCALES:
        for name in CONTENT_BASENAMES:
            paths.append(CONTENT_DIR / locale / name)
    return paths


def assert_unique_top_level_ids(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise AssertionError(f"{path}: invalid JSON ({e})") from e

    if not isinstance(data, list):
        raise AssertionError(f"{path}: expected a JSON array at the top level, got {type(data).__name__}")

    id_to_indices: dict[object, list[int]] = defaultdict(list)

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise AssertionError(f"{path}: item at index {i} must be an object, got {type(item).__name__}")
        if "id" not in item:
            raise AssertionError(f"{path}: item at index {i} is missing required field 'id'")
        oid = item["id"]
        id_to_indices[oid].append(i)

    duplicates = {k: v for k, v in id_to_indices.items() if len(v) > 1}
    if duplicates:
        lines = [f"{path}: duplicate id values (id -> indices):"]
        for oid in sorted(duplicates, key=lambda x: (str(type(x).__name__), str(x))):
            lines.append(f"  {oid!r} at indices {duplicates[oid]}")
        raise AssertionError("\n".join(lines))


class TestContentUniqueIds(unittest.TestCase):
    def test_expected_content_files_exist(self) -> None:
        missing = [p for p in content_json_paths() if not p.is_file()]
        self.assertEqual(
            missing,
            [],
            "Missing expected content JSON files:\n"
            + "\n".join(str(p.relative_to(REPO_ROOT)) for p in missing),
        )

    def test_unique_ids_per_file(self) -> None:
        for path in content_json_paths():
            rel = path.relative_to(REPO_ROOT)
            with self.subTest(file=str(rel)):
                self.assertTrue(path.is_file(), f"missing file: {rel}")
                assert_unique_top_level_ids(path)


if __name__ == "__main__":
    unittest.main()

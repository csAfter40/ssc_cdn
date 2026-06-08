"""
Validate situations.json: unique ids and script reference integrity per locale.
"""

from __future__ import annotations

import json
import unittest
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "assets" / "content"
LOCALES = ("en", "tr")

SCRIPT_REF_FIELDS = ("correctScriptId", "distractorPrimary", "distractorSecondary")


def situations_path(locale: str) -> Path:
    return CONTENT_DIR / locale / "situations.json"


def scripts_path(locale: str) -> Path:
    return CONTENT_DIR / locale / "scripts.json"


def load_json_array(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise AssertionError(f"{path}: invalid JSON ({e})") from e
    if not isinstance(data, list):
        raise AssertionError(
            f"{path}: expected a JSON array at the top level, got {type(data).__name__}"
        )
    return data


def script_ids_for_locale(locale: str) -> set[str]:
    path = scripts_path(locale)
    data = load_json_array(path)
    ids: set[str] = set()
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise AssertionError(
                f"{path}: item at index {i} must be an object, got {type(item).__name__}"
            )
        if "id" not in item:
            raise AssertionError(f"{path}: item at index {i} is missing required field 'id'")
        ids.add(item["id"])
    return ids


def assert_unique_situation_ids(path: Path) -> None:
    data = load_json_array(path)
    id_to_indices: dict[object, list[int]] = defaultdict(list)

    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise AssertionError(f"{path}: item at index {i} must be an object, got {type(item).__name__}")
        if "id" not in item:
            raise AssertionError(f"{path}: item at index {i} is missing required field 'id'")
        id_to_indices[item["id"]].append(i)

    duplicates = {k: v for k, v in id_to_indices.items() if len(v) > 1}
    if duplicates:
        lines = [f"{path}: duplicate situation id values (id -> indices):"]
        for oid in sorted(duplicates, key=lambda x: (str(type(x).__name__), str(x))):
            lines.append(f"  {oid!r} at indices {duplicates[oid]}")
        raise AssertionError("\n".join(lines))


class TestSituations(unittest.TestCase):
    def test_expected_situations_files_exist(self) -> None:
        missing = [situations_path(locale) for locale in LOCALES if not situations_path(locale).is_file()]
        self.assertEqual(
            missing,
            [],
            "Missing expected situations.json files:\n"
            + "\n".join(str(p.relative_to(REPO_ROOT)) for p in missing),
        )

    def test_unique_situation_ids_per_file(self) -> None:
        for locale in LOCALES:
            path = situations_path(locale)
            rel = path.relative_to(REPO_ROOT)
            with self.subTest(file=str(rel)):
                self.assertTrue(path.is_file(), f"missing file: {rel}")
                assert_unique_situation_ids(path)

    def test_situation_script_references_exist_in_locale_scripts(self) -> None:
        for locale in LOCALES:
            sit_path = situations_path(locale)
            rel = sit_path.relative_to(REPO_ROOT)
            with self.subTest(locale=locale):
                self.assertTrue(sit_path.is_file(), f"missing file: {rel}")
                script_ids = script_ids_for_locale(locale)
                situations = load_json_array(sit_path)

                for i, item in enumerate(situations):
                    situation_id = item.get("id", f"<missing id at index {i}>")
                    with self.subTest(file=str(rel), situation_id=situation_id, index=i):
                        self.assertIsInstance(
                            item,
                            dict,
                            f"{rel}: item at index {i} must be an object, got {type(item).__name__}",
                        )
                        for field in SCRIPT_REF_FIELDS:
                            self.assertIn(
                                field,
                                item,
                                f"{rel}: situation {situation_id!r} (index {i}) is missing required field {field!r}",
                            )
                            ref = item[field]
                            self.assertIsInstance(
                                ref,
                                str,
                                f"{rel}: situation {situation_id!r} field {field!r} must be a string",
                            )
                            self.assertIn(
                                ref,
                                script_ids,
                                f"{rel}: situation {situation_id!r} field {field!r} references unknown script id {ref!r}",
                            )


if __name__ == "__main__":
    unittest.main()

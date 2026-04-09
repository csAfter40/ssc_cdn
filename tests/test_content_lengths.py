"""
Validate maximum string lengths and step counts for scripts and categories
content JSON (en / tr).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "assets" / "content"
LOCALES = ("en", "tr")

SCRIPT_MAX_TITLE_LEN = 70
SCRIPT_MAX_STEP_TEXT_LEN = 150
SCRIPT_MAX_STEPS_COUNT = 12

CATEGORY_MAX_TITLE_LEN = 40


def scripts_paths() -> list[Path]:
    return [CONTENT_DIR / locale / "scripts.json" for locale in LOCALES]


def categories_paths() -> list[Path]:
    return [CONTENT_DIR / locale / "categories.json" for locale in LOCALES]


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


class TestContentLengths(unittest.TestCase):
    def test_expected_scripts_and_categories_files_exist(self) -> None:
        missing = [p for p in (*scripts_paths(), *categories_paths()) if not p.is_file()]
        self.assertEqual(
            missing,
            [],
            "Missing expected content JSON files:\n"
            + "\n".join(str(p.relative_to(REPO_ROOT)) for p in missing),
        )

    def test_scripts_title_step_lengths_and_step_count(self) -> None:
        for path in scripts_paths():
            rel = path.relative_to(REPO_ROOT)
            with self.subTest(file=str(rel)):
                self.assertTrue(path.is_file(), f"missing file: {rel}")
                data = load_json_array(path)
                for i, item in enumerate(data):
                    with self.subTest(file=str(rel), index=i):
                        self.assertIsInstance(
                            item,
                            dict,
                            f"{rel}: item at index {i} must be an object, got {type(item).__name__}",
                        )
                        script_id = item.get("id", f"<missing id at index {i}>")

                        self.assertIn(
                            "title",
                            item,
                            f"{rel}: script {script_id!r} (index {i}) is missing required field 'title'",
                        )
                        title = item["title"]
                        self.assertIsInstance(
                            title,
                            str,
                            f"{rel}: script {script_id!r} title must be a string",
                        )
                        self.assertLessEqual(
                            len(title),
                            SCRIPT_MAX_TITLE_LEN,
                            f"{rel}: script {script_id!r} title length {len(title)} exceeds "
                            f"max {SCRIPT_MAX_TITLE_LEN}: {title!r}",
                        )

                        self.assertIn(
                            "steps",
                            item,
                            f"{rel}: script {script_id!r} (index {i}) is missing required field 'steps'",
                        )
                        steps = item["steps"]
                        self.assertIsInstance(
                            steps,
                            list,
                            f"{rel}: script {script_id!r} 'steps' must be a list",
                        )
                        self.assertLessEqual(
                            len(steps),
                            SCRIPT_MAX_STEPS_COUNT,
                            f"{rel}: script {script_id!r} has {len(steps)} steps, "
                            f"max allowed is {SCRIPT_MAX_STEPS_COUNT}",
                        )

                        for si, step in enumerate(steps):
                            with self.subTest(file=str(rel), script_id=script_id, step_index=si):
                                self.assertIsInstance(
                                    step,
                                    dict,
                                    f"{rel}: script {script_id!r} step at index {si} must be an object",
                                )
                                self.assertIn(
                                    "text",
                                    step,
                                    f"{rel}: script {script_id!r} step at index {si} is missing 'text'",
                                )
                                text = step["text"]
                                self.assertIsInstance(
                                    text,
                                    str,
                                    f"{rel}: script {script_id!r} step {si} 'text' must be a string",
                                )
                                self.assertLessEqual(
                                    len(text),
                                    SCRIPT_MAX_STEP_TEXT_LEN,
                                    f"{rel}: script {script_id!r} step {si} text length {len(text)} "
                                    f"exceeds max {SCRIPT_MAX_STEP_TEXT_LEN}: {text!r}",
                                )

    def test_categories_title_length(self) -> None:
        for path in categories_paths():
            rel = path.relative_to(REPO_ROOT)
            with self.subTest(file=str(rel)):
                self.assertTrue(path.is_file(), f"missing file: {rel}")
                data = load_json_array(path)
                for i, item in enumerate(data):
                    with self.subTest(file=str(rel), index=i):
                        self.assertIsInstance(
                            item,
                            dict,
                            f"{rel}: item at index {i} must be an object, got {type(item).__name__}",
                        )
                        cat_id = item.get("id", f"<missing id at index {i}>")

                        self.assertIn(
                            "title",
                            item,
                            f"{rel}: category {cat_id!r} (index {i}) is missing required field 'title'",
                        )
                        title = item["title"]
                        self.assertIsInstance(
                            title,
                            str,
                            f"{rel}: category {cat_id!r} title must be a string",
                        )
                        self.assertLessEqual(
                            len(title),
                            CATEGORY_MAX_TITLE_LEN,
                            f"{rel}: category {cat_id!r} title length {len(title)} exceeds "
                            f"max {CATEGORY_MAX_TITLE_LEN}: {title!r}",
                        )


if __name__ == "__main__":
    unittest.main()

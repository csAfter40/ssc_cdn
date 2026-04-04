import os
import json
import hashlib
from datetime import datetime

BASE_DIR = "assets"
MANIFEST_PATH = "manifest.json"


# ------------------------
# Helpers
# ------------------------

def sha256_file(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def file_size(filepath):
    return os.path.getsize(filepath)


def load_old_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_old_entry(old_manifest, path_keys):
    ref = old_manifest
    try:
        for key in path_keys:
            ref = ref[key]
        return ref
    except:
        return None


def build_file_entry(filepath, relative_path, old_entry):
    new_hash = sha256_file(filepath)
    size = file_size(filepath)

    if old_entry and old_entry.get("hash") == new_hash:
        version = old_entry.get("version", 1)
    else:
        version = (old_entry.get("version", 0) + 1) if old_entry else 1

    return {
        "path": relative_path.replace("\\", "/"),
        "version": version,
        "hash": new_hash,
        "size": size
    }


# ------------------------
# Main Builder
# ------------------------

def build_manifest():
    old_manifest = load_old_manifest()

    manifest = {
        "manifestVersion": 1,
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "content": {
            "config": {},
            "locales": {}
        },
        "images": {}
    }

    # ------------------------
    # CONFIG
    # ------------------------
    config_path = os.path.join(BASE_DIR, "content", "config", "premium_config.json")

    if os.path.exists(config_path):
        rel_path = config_path
        old_entry = get_old_entry(old_manifest, ["content", "config", "premium"])

        manifest["content"]["config"]["premium"] = build_file_entry(
            config_path,
            rel_path,
            old_entry
        )

    # ------------------------
    # LOCALES (en, tr)
    # ------------------------
    locales_dir = os.path.join(BASE_DIR, "content")

    for locale in os.listdir(locales_dir):
        locale_path = os.path.join(locales_dir, locale)

        if not os.path.isdir(locale_path) or locale == "config":
            continue

        manifest["content"]["locales"][locale] = {}

        for filename in ["categories.json", "subcategories.json", "scripts.json"]:
            filepath = os.path.join(locale_path, filename)

            if not os.path.exists(filepath):
                continue

            key = filename.replace(".json", "")
            rel_path = filepath

            old_entry = get_old_entry(
                old_manifest,
                ["content", "locales", locale, key]
            )

            manifest["content"]["locales"][locale][key] = build_file_entry(
                filepath,
                rel_path,
                old_entry
            )

    # ------------------------
    # IMAGES
    # ------------------------
    images_base = os.path.join(BASE_DIR, "images")

    for group in os.listdir(images_base):
        group_path = os.path.join(images_base, group)

        if not os.path.isdir(group_path):
            continue

        group_key = group.replace("_", "")  # category_images → categoryimages (optional)

        old_group = old_manifest.get("images", {}).get(group_key, {})

        files_dict = {}
        version_changed = False

        for filename in os.listdir(group_path):
            filepath = os.path.join(group_path, filename)

            if not os.path.isfile(filepath):
                continue

            rel_path = filepath.replace("\\", "/")

            new_hash = sha256_file(filepath)
            size = file_size(filepath)

            old_file = old_group.get("files", {}).get(filename)

            if old_file and old_file.get("hash") == new_hash:
                version = old_file.get("version", 1)
            else:
                version = (old_file.get("version", 0) + 1) if old_file else 1
                version_changed = True

            files_dict[filename] = {
                "hash": new_hash,
                "size": size,
                "version": version
            }

        # group version
        old_version = old_group.get("version", 0)
        group_version = old_version + 1 if version_changed else old_version or 1

        manifest["images"][group_key] = {
            "basePath": f"{images_base}/{group}/".replace("\\", "/"),
            "version": group_version,
            "files": files_dict
        }

    return manifest


# ------------------------
# Run
# ------------------------

if __name__ == "__main__":
    manifest = build_manifest()

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("✅ manifest.json generated successfully")
#!/usr/bin/env python3
"""Add a firmware build to the site and point the product's manifest.json at it.

Used by the release workflow, and by hand for a one-off publish:

  python3 scripts/publish.py --product zones --title "LAB. Zones" --version 0.6.1 \
      --factory firmware.factory.bin --ota firmware.ota.bin

Builds are kept in <product>/<version>/, so rolling back is: point manifest.json at an older
folder (or rerun this with that folder's files) and commit. Sensors only install a version that
differs from theirs, and only when someone presses Install.
"""
import argparse
import hashlib
import json
import pathlib
import shutil

SITE = pathlib.Path(__file__).resolve().parent.parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--product", required=True, help="folder name, e.g. presence")
    p.add_argument("--title", required=True, help='e.g. "LAB. Presence"')
    p.add_argument("--version", required=True)
    p.add_argument("--factory", required=True, type=pathlib.Path, help="firmware.factory.bin (USB install)")
    p.add_argument("--ota", required=True, type=pathlib.Path, help="firmware.ota.bin (updates)")
    p.add_argument("--chip", default="ESP32-C3")
    p.add_argument("--summary", default="")
    p.add_argument("--release-url", default="")
    a = p.parse_args()

    slug = f"lab-{a.product}"
    folder = SITE / a.product / a.version
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(a.factory, folder / f"{slug}.factory.bin")
    shutil.copyfile(a.ota, folder / f"{slug}.ota.bin")

    ota = {
        # Relative paths: the installer and ESPHome both resolve them against manifest.json.
        "path": f"{a.version}/{slug}.ota.bin",
        "md5": hashlib.md5((folder / f"{slug}.ota.bin").read_bytes()).hexdigest(),
        "summary": a.summary or f"{a.title} {a.version}",
    }
    if a.release_url:
        ota["release_url"] = a.release_url

    manifest = {
        "name": a.title,
        "version": a.version,
        "home_assistant_domain": "esphome",
        "new_install_prompt_erase": True,
        "builds": [{
            "chipFamily": a.chip,
            "parts": [{"path": f"{a.version}/{slug}.factory.bin", "offset": 0}],
            "ota": ota,
        }],
    }
    (SITE / a.product / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{a.product}/manifest.json -> {a.version}")


if __name__ == "__main__":
    main()

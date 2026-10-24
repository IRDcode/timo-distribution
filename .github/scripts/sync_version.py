#!/usr/bin/env python3
"""Fill __APP_VERSION__ / __SETUP_ASSET__ / __SETUP_SIZE_FA__ tokens from a release.

Usage: TAG=v0.5.0 [GH_TOKEN=...] python3 sync_version.py
Run from the repo root. Used by .github/workflows/sync-readme-version.yml
and locally to stamp the current release.
"""
import json
import os
import urllib.request

REPO = "IRDcode/timo-distribution"
TAG = os.environ.get("TAG", "").strip()
if not TAG:
    raise SystemExit("TAG env var is required (e.g. TAG=v0.5.0)")

version = TAG[1:] if TAG.startswith("v") else TAG

headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "readme-version-sync",
}
token = os.environ.get("GH_TOKEN", "")
if token:
    headers["Authorization"] = f"Bearer {token}"

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}", headers=headers
)
release = json.load(urllib.request.urlopen(req, timeout=30))

asset = next(
    (a for a in release.get("assets", []) if a["name"].endswith("-setup.exe")),
    None,
)
if asset is None:
    raise SystemExit(f"no -setup.exe asset found in release {TAG}")

exe_name = asset["name"]
size_fa = str(round(asset["size"] / 1_000_000)).translate(
    str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
)

targets = ["README.md", "assets/hero.svg", "assets/features.svg"]
changed = []
for path in targets:
    if not os.path.exists(path):
        continue
    text = open(path, encoding="utf-8").read()
    new = (
        text.replace("__APP_VERSION__", version)
        .replace("__SETUP_ASSET__", exe_name)
        .replace("__SETUP_SIZE_FA__", size_fa)
    )
    if new != text:
        open(path, "w", encoding="utf-8").write(new)
        changed.append(path)

print(f"synced -> version={version} asset={exe_name} size_fa={size_fa} files={changed}")

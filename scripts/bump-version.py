#!/usr/bin/env python3
"""Bump an image manifest version and its matching Helm chart version."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def next_version(current: str, bump: str) -> str:
    major, minor, patch = (int(part) for part in current.split(".")[:3])
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return bump


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: bump-version.py IMAGE (major|minor|patch|VERSION)", file=sys.stderr)
        return 2

    image_name, requested = sys.argv[1:]
    manifest_path = ROOT / "images" / image_name / "image.json"
    if not manifest_path.is_file():
        print(f"unknown image: {image_name}", file=sys.stderr)
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest["version"]
    version = next_version(current, requested) if requested in {"major", "minor", "patch"} else requested
    if not SEMVER_PATTERN.fullmatch(version):
        print(f"invalid semantic version: {version}", file=sys.stderr)
        return 2

    manifest["version"] = version
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    chart = manifest.get("chart")
    if chart:
        chart_path = ROOT / chart / "Chart.yaml"
        chart_text = chart_path.read_text(encoding="utf-8")
        updated, count = re.subn(
            r"^version:\s*[\"']?[^\"'\s#]+[\"']?\s*$",
            f"version: {version}",
            chart_text,
            count=1,
            flags=re.MULTILINE,
        )
        if count != 1:
            raise ValueError(f"could not update chart version in {chart_path}")
        chart_path.write_text(updated, encoding="utf-8")

    print(f"{image_name}: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

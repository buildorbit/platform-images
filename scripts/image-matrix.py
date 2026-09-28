#!/usr/bin/env python3
"""Validate image manifests and emit a GitHub Actions matrix."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
REQUIRED_FIELDS = {
    "name",
    "version",
    "repository",
    "context",
    "dockerfile",
    "platforms",
    "validation_platform",
}
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def repo_path(value: str, field: str, manifest: Path) -> Path:
    candidate = (ROOT / value).resolve()
    try:
        candidate.relative_to(ROOT)
    except ValueError as error:
        raise ValueError(f"{manifest}: {field} must stay inside the repository") from error
    return candidate


def load_manifest(manifest: Path) -> dict[str, object]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{manifest}: root value must be an object")
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        raise ValueError(f"{manifest}: missing fields: {', '.join(sorted(missing))}")

    name = data["name"]
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        raise ValueError(f"{manifest}: name must contain lowercase letters, numbers, and hyphens")
    if name != manifest.parent.name:
        raise ValueError(f"{manifest}: name must match its image directory")

    version = data["version"]
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        raise ValueError(f"{manifest}: version must be a semantic version")

    platforms = data["platforms"]
    if not isinstance(platforms, list) or not platforms or not all(
        isinstance(platform, str) and platform for platform in platforms
    ):
        raise ValueError(f"{manifest}: platforms must be a non-empty list of strings")
    validation_platform = data["validation_platform"]
    if not isinstance(validation_platform, str) or validation_platform not in platforms:
        raise ValueError(f"{manifest}: validation_platform must be listed in platforms")

    for field in ("context", "dockerfile"):
        value = data[field]
        if not isinstance(value, str) or not value:
            raise ValueError(f"{manifest}: {field} must be a non-empty string")
        path = repo_path(value, field, manifest)
        if not path.exists() or (field == "dockerfile" and not path.is_file()):
            raise ValueError(f"{manifest}: {field} does not exist: {value}")

    for optional_path in ("chart", "smoke_test"):
        value = data.get(optional_path, "")
        if value:
            if not isinstance(value, str):
                raise ValueError(f"{manifest}: {optional_path} must be a string")
            path = repo_path(value, optional_path, manifest)
            if optional_path == "chart":
                valid_path = path.is_dir() and (path / "Chart.yaml").is_file()
                if valid_path:
                    chart_text = (path / "Chart.yaml").read_text(encoding="utf-8")
                    chart_match = re.search(
                        r"^version:\s*[\"']?([^\"'\s#]+)", chart_text, re.MULTILINE
                    )
                    if not chart_match or chart_match.group(1) != version:
                        raise ValueError(
                            f"{manifest}: chart version must match image version {version}"
                        )
            else:
                valid_path = path.is_file()
            if not valid_path:
                raise ValueError(f"{manifest}: {optional_path} does not exist: {value}")

    repository = data["repository"]
    if not isinstance(repository, str) or "://" in repository or not repository:
        raise ValueError(f"{manifest}: repository must be a container image reference")

    return {
        "name": name,
        "version": version,
        "repository": repository,
        "context": data["context"],
        "dockerfile": data["dockerfile"],
        "platforms": ",".join(platforms),
        "validation_platform": validation_platform,
        "chart": data.get("chart", ""),
        "smoke_test": data.get("smoke_test", ""),
    }


def release_image_names(entries: list[dict[str, object]]) -> set[str] | None:
    """Select the image named by an artifact-specific release tag."""

    release_tag = os.environ.get("RELEASE_TAG")
    if not release_tag:
        return None

    all_names = {str(entry["name"]) for entry in entries}
    for entry in entries:
        prefix = f"{entry['name']}-v"
        if release_tag.startswith(prefix):
            version = release_tag[len(prefix) :]
            if not SEMVER_PATTERN.fullmatch(version):
                raise ValueError(f"{release_tag}: release tag must contain a semantic version")
            if version != entry["version"]:
                raise ValueError(
                    f"{release_tag}: release version does not match {entry['name']} version {entry['version']}"
                )
            return {str(entry["name"])}

    names = ", ".join(sorted(all_names))
    raise ValueError(f"{release_tag}: release tag must be <image>-v<version>; known images: {names}")


def changed_image_names(all_names: set[str]) -> set[str] | None:
    """Return images touched by a diff, or None when the full matrix is required."""

    base_sha = os.environ.get("CHANGE_BASE_SHA")
    head_sha = os.environ.get("CHANGE_HEAD_SHA")
    if not base_sha or not head_sha:
        return None

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_sha}...{head_sha}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    changed_paths = result.stdout.splitlines()
    if any(
        path == ".github/workflows/build-images.yml" or path.startswith("scripts/")
        for path in changed_paths
    ):
        return None

    selected = {
        parts[1]
        for path in changed_paths
        if (parts := Path(path).parts)
        and len(parts) >= 2
        and parts[0] in {"images", "charts"}
        and parts[1] in all_names
    }
    return selected


def main() -> None:
    manifests = sorted((ROOT / "images").glob("*/image.json"))
    if not manifests:
        raise ValueError("no image manifests found under images/*/image.json")

    entries = [load_manifest(manifest) for manifest in manifests]
    all_names = {entry["name"] for entry in entries}
    selected_names = release_image_names(entries) or changed_image_names(all_names)
    if selected_names is not None:
        entries = [entry for entry in entries if entry["name"] in selected_names]
    matrix = json.dumps({"include": entries}, separators=(",", ":"))
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with Path(github_output).open("a", encoding="utf-8") as output:
            output.write(f"matrix={matrix}\n")
    else:
        print(matrix)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"image manifest validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error

#!/usr/bin/env python3
"""Build OpenBB Workspace metadata into an image-owned JSON file."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from openbb_core.api.rest_api import app
from openbb_platform_api.utils.widgets import build_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    metadata = build_json(app.openapi(), [])

    # Write atomically so a partially written metadata file can never become part
    # of a layer if this helper is reused outside of Docker.
    fd, temporary_name = tempfile.mkstemp(
        prefix="widgets.", suffix=".json", dir=args.output.parent
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, ensure_ascii=False, indent=2, sort_keys=True)
            metadata_file.write("\n")
        os.replace(temporary_name, args.output)
    except Exception:
        os.unlink(temporary_name)
        raise


if __name__ == "__main__":
    main()


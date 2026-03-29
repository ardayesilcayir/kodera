#!/usr/bin/env python3
"""Write JSON Schema files derived from Pydantic models (run from optimization_location/)."""

from __future__ import annotations

import json
from pathlib import Path

from validation_service import (
    request_json_schema,
    validation_accepted_json_schema,
    validation_rejected_json_schema,
)


def main() -> None:
    root = Path(__file__).resolve().parent / "schemas"
    root.mkdir(parents=True, exist_ok=True)
    mapping = {
        "orbit_design_request.schema.json": request_json_schema(),
        "validation_accepted_response.schema.json": validation_accepted_json_schema(),
        "validation_rejected_response.schema.json": validation_rejected_json_schema(),
    }
    for name, schema in mapping.items():
        path = root / name
        path.write_text(json.dumps(schema, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()

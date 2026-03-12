"""
Generate openapi.yaml from the Flask app.

Usage:
    python gen_spec.py

This script treats the app source code (schemas.py + route decorators) as the
single source of truth, then serialises the auto-generated OpenAPI 3.0 spec to
openapi.yaml. Commit openapi.yaml as a generated artefact — never edit it by
hand. Re-run this script whenever routes or schemas change.
"""

import json
import yaml
from pathlib import Path
from app import create_app

app = create_app()

with app.test_client() as client:
    resp = client.get("/openapi.json")
    spec = resp.get_json()

out_json = Path("openapi.json")
out_yaml = Path("openapi.yaml")

out_json.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
out_yaml.write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True))

print(f"Generated {out_json}  ({out_json.stat().st_size} bytes)")
print(f"Generated {out_yaml}  ({out_yaml.stat().st_size} bytes)")

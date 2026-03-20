"""
Generate OpenAPI JSON/YAML from Flask app.

Usage:
    python gen.py
"""

import json
from pathlib import Path

import yaml

from main import create_app

app = create_app()

with app.test_client() as client:
    response = client.get("/swagger.json")
    spec = response.get_json()

out_json = Path("openapi.json")
out_yaml = Path("openapi.yaml")

out_json.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
out_yaml.write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True))

print(f"Generated {out_json} ({out_json.stat().st_size} bytes)")
print(f"Generated {out_yaml} ({out_yaml.stat().st_size} bytes)")

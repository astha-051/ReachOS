import sys
import os
import json

sys.path.insert(0, os.path.abspath("backend"))

from app.main import app

openapi = app.openapi()
print("=== OPENAPI REGISTERED PATHS ===")
for path, methods in openapi.get("paths", {}).items():
    for method in methods.keys():
        print(f"{method.upper():<10} {path}")

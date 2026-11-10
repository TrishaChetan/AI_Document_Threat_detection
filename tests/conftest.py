"""Make the backend importable from pytest (`pytest tests` from the repo root).

The modules under backend/ import each other as top-level packages
(`from parsers.xml_parser import ...`), and the legacy test scripts use paths
relative to backend/, so put backend on sys.path and run from there.
"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))
os.chdir(BACKEND)

# Legacy scripts that run at import time and need outside resources:
# the NVIDIA API (key in .env) or files saved by a previous upload.
collect_ignore = []
if not os.getenv("NVIDIA_API_KEY"):
    collect_ignore += ["test_llm.py", "test_recommendation.py"]
if not (BACKEND / "temp_uploads").is_dir():
    collect_ignore += ["test_batch_executor.py", "test_batch_planner.py"]

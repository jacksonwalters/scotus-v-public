"""Compatibility entry point. Run from repository root with PYTHONPATH=. .

The maintained app uses SCVPO_ARTIFACT; see README.md for build/deployment.
"""
from scvpublic.web import create_app

app = create_app()

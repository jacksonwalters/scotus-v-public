"""Legacy WSGI filename; prefer 'scvpublic.web:create_app()' in Gunicorn."""
from scvpublic.web import create_app

app = create_app()

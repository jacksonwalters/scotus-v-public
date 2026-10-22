PYTHON ?= python3.12
VENV ?= .venv
PY = $(VENV)/bin/python
ARTIFACT ?= artifacts/casesumm.sqlite

.PHONY: setup test demo build serve inspect
setup:
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install -r requirements-casesumm.txt
test:
	$(PY) -m unittest discover -s tests -v
demo:
	$(PY) -m scvpublic.build --demo --output artifacts/demo.sqlite
build:
	$(PY) -m scvpublic.build --output artifacts/legacy.sqlite
serve:
	SCVPO_ARTIFACT=$(ARTIFACT) $(VENV)/bin/gunicorn --bind 127.0.0.1:8000 --workers 1 --threads 2 --timeout 60 'scvpublic.web:create_app()'
inspect:
	$(PY) -m scvpublic.inspect $(ARTIFACT)

.PHONY: anes
anes:
	$(PY) -m scvpublic.anes

.PHONY: public public-sample
public:
	$(PY) -m scvpublic.public
public-sample: public
	$(PY) -m scvpublic.sample --public-artifact data/processed/anes-20260205/public.json --output artifacts/sample-public.sqlite

.PHONY: casesumm
casesumm:
	$(PY) -m scvpublic.casesumm

.PHONY: check-serving release refresh-public
check-serving:
	PYTHONPATH=. $(PY) scripts/check_serving.py $(ARTIFACT)
release: check-serving
	PYTHONPATH=. $(PY) scripts/package_release.py $(ARTIFACT)
refresh-public: public
	$(PY) -m scvpublic.refresh_public --artifact $(ARTIFACT)

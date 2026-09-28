PY ?= python

.PHONY: run eval regrade install

install:
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) run.py

eval:
	$(PY) run.py --eval-only

regrade:
	$(PY) run.py --regrade

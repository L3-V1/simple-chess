ifeq ($(OS),Windows_NT)
PYTHON := py -3
VENV_PYTHON := .env/Scripts/python.exe
else
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
PYTHON := python3
VENV_PYTHON := .env/bin/python
else
$(error Unsupported operating system: $(UNAME_S))
endif
endif

VENV_DIR := .env
DEPS_STAMP := $(VENV_DIR)/.deps-installed

.PHONY: venv setup install run test

venv: $(VENV_PYTHON)

$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV_DIR)

setup: $(DEPS_STAMP)

install: setup

$(DEPS_STAMP): requirements.txt | $(VENV_PYTHON)
	$(VENV_PYTHON) -m pip install --upgrade pip
	$(VENV_PYTHON) -m pip install -r requirements.txt
	$(VENV_PYTHON) -c "from pathlib import Path; Path(r'$(DEPS_STAMP)').write_text('ok\n', encoding='utf-8')"

run:
	$(VENV_PYTHON) main.py

test:
	$(VENV_PYTHON) -m pytest

# CPP AI Hackathon 2026 — Common Dev Commands
# Usage: make <target> [CAT=1]
#   CAT defaults to the ACTIVE_CATEGORY from CLAUDE.md (set manually)

CAT ?= 4
CATEGORY_DIR := $(shell ls -d "Category $(CAT) - "* 2>/dev/null | head -1)

.PHONY: help setup install run test lint clean

help:
	@echo "Available targets:"
	@echo "  make setup CAT=N    — Create venv + install deps for category N"
	@echo "  make install CAT=N  — pip install -r requirements.txt for category N"
	@echo "  make run CAT=N      — Run Streamlit app for category N"
	@echo "  make test CAT=N     — Run tests for category N"
	@echo "  make lint           — Run ruff linter across all Python files"
	@echo "  make clean          — Remove __pycache__ and .pytest_cache"

setup:
	@echo "Setting up Category $(CAT): $(CATEGORY_DIR)"
	cd "$(CATEGORY_DIR)" && python -m venv .venv
	cd "$(CATEGORY_DIR)" && .venv/bin/pip install --upgrade pip
	cd "$(CATEGORY_DIR)" && .venv/bin/pip install -r requirements.txt
	@echo "Done. Activate with: source \"$(CATEGORY_DIR)/.venv/bin/activate\""

install:
	@echo "Installing deps for Category $(CAT): $(CATEGORY_DIR)"
	cd "$(CATEGORY_DIR)" && pip install -r requirements.txt

run:
	@echo "Running Category $(CAT): $(CATEGORY_DIR)"
	cd "$(CATEGORY_DIR)" && streamlit run src/app.py

test:
	@echo "Testing Category $(CAT): $(CATEGORY_DIR)"
	cd "$(CATEGORY_DIR)" && python -m pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	@command -v ruff >/dev/null 2>&1 || pip install ruff -q
	ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete."

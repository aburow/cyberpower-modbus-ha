# Repository Guidelines

## Overview
This repository is currently empty (no tracked files yet). Use this guide as a baseline when adding initial code, and update it once real structure, tooling, and conventions exist.

## Project Structure & Module Organization
- Planned layout (adjust to match actual code once added):
  - `src/` for application code (e.g., Modbus/HA integration logic).
  - `tests/` for automated tests.
  - `docs/` for architecture notes and operational instructions.
  - `scripts/` for local tooling (setup, lint, release).
- If you introduce a different structure, document it here with concrete paths.

## Build, Test, and Development Commands
No build or test commands are defined yet. When you add tooling, list the exact commands here. Examples to document if added later:
- `make build` for producing release artifacts.
- `make test` for running the full test suite.
- `npm run dev` or `python -m ...` for local development.

## Coding Style & Naming Conventions
No formatter or linter is configured yet. Until one is chosen:
- Match the style of nearby files once they exist.
- Prefer clear, descriptive names (e.g., `modbus_client.py`, `ha_bridge.rs`).
- Document indentation and lint rules here when you add tooling.

## Testing Guidelines
No test framework is configured. When adding tests:
- Place unit tests under `tests/` with names like `test_*.py` or `*_test.rs`.
- Describe how to run tests and any coverage expectations.

## Commit & Pull Request Guidelines
There is no commit history yet. Suggested baseline until a convention emerges:
- Use concise, imperative commit subjects (e.g., "Add Modbus client").
- PRs should include: purpose, summary of changes, and any test notes.

## Configuration & Secrets
If the project requires credentials or device configuration, document:
- Expected env vars (e.g., `MODBUS_HOST`, `MODBUS_PORT`).
- Example config files with safe placeholders.

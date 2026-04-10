#!/usr/bin/env bash
set -euo pipefail

uvx --from ruff ruff check "$@"

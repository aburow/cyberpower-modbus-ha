#!/usr/bin/env bash
set -euo pipefail

uvx --from semgrep semgrep scan --config auto "$@"

#!/usr/bin/env bash
set -euo pipefail

uvx --from grain-lint grain check "$@"

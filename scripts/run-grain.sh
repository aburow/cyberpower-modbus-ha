#!/usr/bin/env bash
set -euo pipefail

if [[ $# -eq 0 ]]; then
  exit 0
fi

paths=()
for path in "$@"; do
  case "$path" in
    .tools/*|.venv/*|node_modules/*)
      continue
      ;;
  esac
  paths+=("$path")
done

if [[ ${#paths[@]} -eq 0 ]]; then
  exit 0
fi

uvx --from grain-lint grain check "${paths[@]}"

#!/usr/bin/env bash
set -euo pipefail
# Run git pull --ff-only yourself first; this script does not reset your checkout.
exec python3 "$(dirname -- "$(readlink -f -- "$0")")/manage.py" install "$@"

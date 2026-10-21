#!/usr/bin/env python3
"""Load the actual Plasma packages under Xvfb; reject QML load/runtime errors."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    env = dict(os.environ, XDG_DATA_HOME=temp, QT_QUICK_BACKEND='software', QT_QPA_PLATFORM='xcb')
    destination = Path(temp)/'plasma/plasmoids'
    shutil.copytree(ROOT/'assets/plasma/plasmoids', destination)
    failed = []
    for widget in sorted(destination.iterdir()):
        result = subprocess.run(['xvfb-run', '-a', 'dbus-run-session', '--', 'timeout', '12s',
                                 'plasmawindowed', widget.name], env=env, capture_output=True, text=True)
        logs = result.stdout + result.stderr
        print(widget.name, result.returncode, logs, flush=True)
        if result.returncode != 124 or any(term in logs for term in (
                'Error loading QML', 'is not installed', 'is not a type', 'Cannot assign',
                'ReferenceError:', 'TypeError:', 'Cannot load library', 'does not exist')):
            failed.append(widget.name)
    if failed:
        raise SystemExit('Widget smoke check failed: ' + ', '.join(failed))

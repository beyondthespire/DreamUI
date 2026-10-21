#!/usr/bin/env python3
"""Install dependencies and apply the complete DreamUI desktop on Plasma 6."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import manage

PACKAGES = ['plasma-desktop', 'plasma-workspace', 'kde-cli-tools', 'kwin-common',
            'breeze', 'breeze-icon-theme', 'dolphin', 'konsole', 'kate', 'gwenview', 'elisa',
            'qml6-module-qtquick', 'qml6-module-qtquick-controls', 'qml6-module-qtquick-layouts',
            'qml6-module-qtqml-workerscript', 'qml6-module-qtquick-window', 'qml6-module-qtcore',
            'libqt6svg6', 'qt6-svg-plugins']

def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def dbus_tool():
    return next((shutil.which(c) for c in ('qdbus6', 'qdbus-qt6', 'qdbus') if shutil.which(c)),
                next((p for p in ('/usr/lib/qt6/bin/qdbus', '/usr/lib64/qt6/bin/qdbus') if Path(p).exists()), None))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=['blue', 'violet'], default='blue')
    parser.add_argument('--skip-dependencies', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.dry_run:
        print('Would install Debian/Ubuntu dependencies: ' + ', '.join(PACKAGES))
        print('Would install DreamUI assets, back up settings, apply theme/wallpaper, replace screen 0 panel, and add widgets.')
        return
    if os.geteuid() == 0:
        raise RuntimeError('Run ./install.sh as your desktop user, without sudo. Only package installation uses sudo.')
    manage.require_plasma()
    if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        raise RuntimeError('Run this inside your Plasma 6 desktop session.')
    if not args.skip_dependencies:
        if not shutil.which('apt-get'):
            raise RuntimeError('Automatic dependencies currently support Debian/Ubuntu only. See docs/INSTALL.md.')
        run('sudo', 'apt-get', 'update')
        packages = PACKAGES.copy()
        if not dbus_tool():
            for candidate in ('qdbus-qt6', 'qdbus6', 'qt6-tools-dev-tools'):
                result = run('apt-cache', 'policy', candidate, capture_output=True, text=True)
                if 'Candidate:' in result.stdout and 'Candidate: (none)' not in result.stdout:
                    packages.append(candidate)
                    break
            else:
                raise RuntimeError('No Qt 6 qdbus package available from your configured repositories.')
        run('apt-get', '--simulate', '--no-remove', 'install', '--no-install-recommends', *packages)
        run('sudo', 'apt-get', '--no-remove', 'install', '--no-install-recommends', '-y', *packages)
    qdbus = dbus_tool()
    if not qdbus:
        raise RuntimeError('Missing Qt 6 qdbus tool.')
    run(sys.executable, str(manage.ROOT/'scripts/manage.py'), 'install')
    # Existing deployment manager owns the lock and original settings snapshot.
    run(sys.executable, str(manage.ROOT/'scripts/manage.py'), 'apply', args.variant, '--wallpaper')
    for key, value in [('ButtonsOnLeft', 'M'), ('ButtonsOnRight', 'IAX'),
                       ('library', 'org.kde.kwin.aurorae'), ('theme', '__aurorae__svg__DreamGlass')]:
        run('kwriteconfig6', '--file', 'kwinrc', '--group', 'org.kde.kdecoration2', '--key', key, value)
    run(qdbus, 'org.kde.KWin', '/KWin', 'reconfigure')
    run('kbuildsycoca6', '--noincremental')
    # Restart only the session-managed shell to refresh newly installed packages.
    if subprocess.run(['systemctl', '--user', 'is-active', '--quiet', 'plasma-plasmashell.service']).returncode == 0:
        run('systemctl', '--user', 'restart', 'plasma-plasmashell.service')
    script = (manage.ROOT/'layouts/full-desktop.js').read_text()
    for attempt in range(20):
        result = subprocess.run([qdbus, 'org.kde.plasmashell', '/PlasmaShell',
                                 'org.kde.PlasmaShell.evaluateScript', script], capture_output=True, text=True)
        if 'DREAMUI_DESKTOP_OK' in result.stdout:
            print('DreamUI desktop installed. Log out and back in to clear cached artwork.')
            return
        if 'DREAMUI_WAIT' not in result.stdout + result.stderr and result.returncode == 0:
            break
        time.sleep(1)
    raise RuntimeError('Desktop layout was not confirmed. Log out/in, then rerun ./install.sh --skip-dependencies.\n' + result.stdout + result.stderr)

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print('DreamUI: ' + str(exc), file=sys.stderr)
        sys.exit(1)

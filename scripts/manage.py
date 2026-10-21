#!/usr/bin/env python3
"""Per-user DreamUI deployment. Standard library only; never runs sudo or git."""
import argparse
import base64
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILES = ('kdeglobals', 'plasmarc', 'kwinrc', 'plasma-org.kde.plasma.desktop-appletsrc',
                'kdedefaults/kdeglobals', 'kdedefaults/plasmarc', 'kdedefaults/kwinrc',
                'kdedefaults/package')

def digest(content):
    return hashlib.sha256(content).hexdigest()

def safe_path(root, relative):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise RuntimeError(f'Invalid managed path: {relative}')
    target = root / rel
    for path in (target, *target.parents):
        if path.is_symlink():
            raise RuntimeError(f'Refusing symlink: {path}')
    if target.exists() and not target.is_file():
        raise RuntimeError(f'Expected a regular file: {target}')
    return target

def snapshot(path):
    if not path.exists():
        return None
    return {'content': base64.b64encode(path.read_bytes()).decode(),
            'mode': path.stat().st_mode & 0o777}

def atomic_write(path, content, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.dreamui-tmp')
    if temp.exists() or temp.is_symlink():
        raise RuntimeError(f'Remove stale temporary file first: {temp}')
    try:
        with temp.open('xb') as stream:
            stream.write(content)
        temp.chmod(mode)
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()

def restore(path, value):
    if value is None:
        path.unlink(missing_ok=True)
    else:
        atomic_write(path, base64.b64decode(value['content']), value['mode'])

class Manager:
    def __init__(self, data, config, state):
        self.data, self.config, self.state = map(Path, (data, config, state))
        self.ledger_path = safe_path(self.state, 'installation.json')
        if self.ledger_path.exists():
            self.ledger = json.loads(self.ledger_path.read_text())
            if self.ledger['data'] != str(self.data) or self.ledger['config'] != str(self.config):
                raise RuntimeError('XDG paths changed since installation. Use the original XDG paths.')
        else:
            self.ledger = {'data':str(self.data), 'config':str(self.config), 'files':{}, 'settings':None}

    def save(self):
        atomic_write(self.ledger_path, (json.dumps(self.ledger, indent=2)+'\n').encode(), 0o600)

    def sources(self, source):
        files = {}
        for path in sorted(Path(source).rglob('*')):
            if path.is_symlink():
                raise RuntimeError(f'Source symlinks are unsupported: {path}')
            if path.is_file():
                files[path.relative_to(source).as_posix()] = path.read_bytes()
        if not files:
            raise RuntimeError('No assets found.')
        return files

    def check_managed(self):
        conflicts=[]
        for rel, entry in self.ledger['files'].items():
            path=safe_path(self.data, rel)
            if not path.exists() or digest(path.read_bytes()) != entry['installed']:
                conflicts.append(str(path))
        if conflicts:
            raise RuntimeError('Managed files were changed or removed; back up your edits and restore the installed versions first:\n'+'\n'.join(conflicts))

    def install(self, source, dry=False):
        files=self.sources(source)
        self.check_managed()
        for rel in files:
            safe_path(self.data, rel)
        print(f'{"Would install" if dry else "Installing"} {len(files)} files into {self.data}')
        if dry:
            return
        previous=copy.deepcopy(self.ledger)
        undo={rel:snapshot(safe_path(self.data,rel)) for rel in set(files)|set(self.ledger['files'])}
        # Write a recovery journal before the first asset mutation.
        journal=safe_path(self.state,'pending.json')
        atomic_write(journal,json.dumps({'data':str(self.data),'undo':undo,
                                        'ledger':snapshot(self.ledger_path)}).encode(),0o600)
        try:
            for rel in set(self.ledger['files'])-set(files):
                restore(safe_path(self.data,rel),self.ledger['files'].pop(rel)['original'])
            for rel,content in files.items():
                path=safe_path(self.data,rel)
                entry=self.ledger['files'].setdefault(rel,{'original':snapshot(path)})
                atomic_write(path,content)
                entry['installed']=digest(content)
            self.save()
        except Exception:
            for rel,value in undo.items():
                restore(safe_path(self.data,rel),value)
            self.ledger=previous
            restore(self.ledger_path,json.loads(journal.read_text())['ledger'])
            journal.unlink()
            raise
        journal.unlink()
        print('Assets installed. Apply with ./scripts/apply.sh blue (or violet).')

    def backup_settings(self):
        if self.ledger['settings'] is None:
            self.ledger['settings']={rel:snapshot(safe_path(self.config,rel)) for rel in CONFIG_FILES}
            self.save()

    def uninstall(self, restore_settings=False, dry=False):
        self.check_managed()
        if self.ledger['settings'] is not None and not restore_settings:
            raise RuntimeError('Appearance was applied. Log out of Plasma, use a text console, and run ./scripts/uninstall.sh --restore-settings. This restores the original appearance and panel settings.')
        if restore_settings:
            if subprocess.run(['pgrep','-u',str(os.getuid()),'-x','plasmashell'],stdout=subprocess.DEVNULL).returncode == 0:
                raise RuntimeError('Log out of Plasma before restoring settings; the running desktop could overwrite them.')
            for rel in self.ledger['settings'] or {}:
                safe_path(self.config,rel)
        if dry:
            print(f'Would restore/remove {len(self.ledger["files"])} managed files.'); return
        # Save each completed removal so a partial uninstall can be resumed.
        for rel in list(self.ledger['files']):
            restore(safe_path(self.data,rel),self.ledger['files'][rel]['original'])
            del self.ledger['files'][rel]
            self.save()
        if restore_settings:
            for rel,value in (self.ledger['settings'] or {}).items():
                restore(safe_path(self.config,rel),value)
        self.ledger_path.unlink(missing_ok=True)
        print('DreamUI removed; original files restored. Empty asset directories may remain.')

def require_plasma():
    if not shutil.which('plasmashell'):
        raise RuntimeError('KDE Plasma 6 must be installed first.')
    result=subprocess.run(['plasmashell','--version'],capture_output=True,text=True,check=True)
    if not re.search(r'plasmashell\s+6\.',result.stdout):
        raise RuntimeError('This starter targets Plasma 6 only. Detected: '+result.stdout.strip())

def apply(manager, variant, wallpaper=False, layout=False):
    require_plasma()
    if not os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        raise RuntimeError('Run apply from a terminal inside your KDE Plasma session.')
    required=['plasma-apply-lookandfeel']
    if wallpaper: required.append('plasma-apply-wallpaperimage')
    qdbus=None
    if layout:
        qdbus=next((shutil.which(c) for c in ('qdbus6','qdbus-qt6','qdbus') if shutil.which(c)),None)
        if not qdbus: raise RuntimeError('Layout requires qdbus6 (Qt 6 D-Bus tools).')
    for command in required:
        if not shutil.which(command): raise RuntimeError('Missing KDE tool: '+command)
    manager.check_managed()
    theme=f'org.beyondthespire.dreamui.{variant}'
    if f'plasma/look-and-feel/{theme}/metadata.json' not in manager.ledger['files']:
        raise RuntimeError('Install DreamUI first: ./scripts/install.sh')
    manager.backup_settings()
    subprocess.run(['plasma-apply-lookandfeel','-a',theme],check=True)
    if wallpaper:
        path=manager.data/'wallpapers/DreamMoon/contents/images/2560x1440.png'
        subprocess.run(['plasma-apply-wallpaperimage',str(path)],check=True)
    if layout:
        script=(ROOT/'layouts/classic-panel.js').read_text()
        result=subprocess.run([qdbus,'org.kde.plasmashell','/PlasmaShell','org.kde.PlasmaShell.evaluateScript',script],capture_output=True,text=True,check=True)
        if 'DREAMUI_PANEL_OK' not in result.stdout:
            raise RuntimeError('Panel script did not confirm success: '+result.stdout+result.stderr)
    print('Appearance applied. Log out/in if Plasma retains cached artwork.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['install','apply','uninstall','recover'])
    parser.add_argument('variant',nargs='?',default='blue',choices=['blue','violet'])
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--wallpaper',action='store_true',help='Apply Dream Moon wallpaper')
    parser.add_argument('--layout',action='store_true',help='Add a classic panel; refuses to replace existing panels')
    parser.add_argument('--restore-settings',action='store_true',help='Restore the pre-DreamUI config snapshot; Plasma must be logged out')
    args=parser.parse_args()
    if args.action != 'apply' and (args.wallpaper or args.layout): parser.error('--wallpaper and --layout are apply-only')
    if args.action != 'uninstall' and args.restore_settings: parser.error('--restore-settings is uninstall-only')
    if os.geteuid()==0 and not args.dry_run:
        raise RuntimeError('Run as your normal desktop user, without sudo.')
    home=Path.home()
    def xdg(key,default):
        path=Path(os.environ.get(key) or default).expanduser()
        if not path.is_absolute(): raise RuntimeError(key+' must be absolute')
        return path
    data=xdg('XDG_DATA_HOME',home/'.local/share')
    config=xdg('XDG_CONFIG_HOME',home/'.config')
    state=xdg('XDG_STATE_HOME',home/'.local/state')/'dreamui'
    if args.dry_run:
        manager=Manager(data,config,state)
        if args.action=='install': manager.install(ROOT/'assets',True)
        elif args.action=='uninstall': manager.uninstall(args.restore_settings,True)
        else: print('Would '+args.action+' DreamUI; no changes made.')
        return
    safe_path(state,'lock')
    state.mkdir(parents=True,exist_ok=True)
    state.chmod(0o700)
    with (state/'lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        manager=Manager(data,config,state)
        pending=safe_path(state,'pending.json')
        if args.action=='recover':
            if not pending.exists(): print('No interrupted installation.'); return
            journal=json.loads(pending.read_text())
            if journal['data'] != str(data): raise RuntimeError('Recovery data path does not match')
            for rel,value in journal['undo'].items(): restore(safe_path(data,rel),value)
            restore(manager.ledger_path,journal['ledger'])
            pending.unlink()
            print('Interrupted asset installation rolled back.'); return
        if pending.exists(): raise RuntimeError('Interrupted install detected. Run python3 scripts/manage.py recover first.')
        if args.action=='install':
            require_plasma()
            manager.install(ROOT/'assets')
        elif args.action=='apply': apply(manager,args.variant,args.wallpaper,args.layout)
        else: manager.uninstall(args.restore_settings)

if __name__=='__main__':
    try:
        main()
    except (RuntimeError,OSError,subprocess.CalledProcessError) as exc:
        print(f'DreamUI: {exc}',file=sys.stderr)
        sys.exit(1)

# DreamUI

**A familiar place to come home to.**

DreamUI is a nostalgic appearance layer for **KDE Plasma 6**, developed for the
SoñoOS desktop project. Blue glass, pearl application interiors, glossy icons,
and a quiet moonlit landscape. KDE continues to handle the desktop and applications.

**0.2.0 — experimental desktop installer.** No ISO is required.

[Desktop design reference](docs/design/desktop-concept.png) — a visual target,
not a screenshot. DreamUI now includes its own launcher, clock/media sidebar,
and desktop shortcuts. Application interiors still use Breeze controls.

## Install the complete desktop

Use an existing **KDE Plasma 6** session on Debian/Ubuntu. Run as your normal
user, without sudo (the installer asks for sudo only for distribution packages):

```bash
git clone --branch feat/dreamui-foundation https://github.com/beyondthespire/DreamUI.git
cd DreamUI
./install.sh
```

Already cloned this development branch?

```bash
cd DreamUI
git pull --ff-only
./install.sh
```

Log out and back in afterward to clear cached artwork. The installer:

- Installs required Qt/Plasma runtime packages and Dolphin, Konsole, Kate, Gwenview and Elisa.
- Installs DreamUI Blue/Violet, original icons, Dream Moon wallpaper and Dream Glass window frames.
- Backs up the original appearance and panel configuration before applying changes.
- Replaces the screen 0 panel with Dream Launcher, labeled tasks, tray, clock and show-desktop.
- Adds clock/media and Computer/Home/Trash widgets; preserves unrelated desktop widgets.

Use `./install.sh --variant violet` for violet application colors, `--dry-run`
to describe changes, or `--skip-dependencies` when packages are already installed.
Package installation uses your configured repositories and refuses package removals.
Plasma 5 and automatic installation of a new desktop environment are unsupported.

## Theme-only installation and updates

The older scripts remain available for users who want to preserve their layout:

```bash
./scripts/install.sh
./scripts/apply.sh blue --wallpaper
```

For subsequent asset updates without resetting the panel:

```bash
git pull --ff-only
./scripts/update.sh
```

Assets live under `${XDG_DATA_HOME:-~/.local/share}`. All three custom widgets ship
in the repository; no KDE Store downloads are needed. Media controls use MPRIS
and become active when a supported player is running. The violet option changes
application colors; window frames and widgets remain blue. The full installer
rebuilds the main panel when rerun; use `scripts/update.sh` to retain customizations.

Proxmox guests use the same installer as physical desktops. Actual transparency
and animation depend on the guest's working graphics/compositor; the script does
not change Proxmox hardware settings. The design preview is not a promise of
identical application layouts or glass effects on every graphics driver.

## Restore and uninstall

If you only installed assets and never applied the theme:

```bash
./scripts/uninstall.sh
```

If you used `apply.sh`, **log out of KDE**, switch to a text console (usually
Ctrl+Alt+F3), log in as the same user, and run:

```bash
cd /path/to/DreamUI
./scripts/uninstall.sh --restore-settings
```

This restores the saved pre-DreamUI appearance and panel configuration. Any later
edits to those backed-up configuration files are also reverted. Return to the
graphical login screen and log in again. The backup is kept in
`${XDG_STATE_HOME:-~/.local/state}/dreamui/installation.json` until uninstall succeeds.
Keep the same XDG paths used for installation.

## Develop

```bash
python3 tools/build_assets.py
python3 tools/build_preview.py
python3 tools/validate.py
python3 -m unittest discover -s tests -v
```

SVGs and metadata are generated from editable Python sources. With Inkscape installed,
regenerate the raster wallpaper and concept preview after artwork changes:

```bash
inkscape assets/wallpapers/DreamMoon/contents/images/2560x1440.svg --export-type=png --export-filename=assets/wallpapers/DreamMoon/contents/images/2560x1440.png
inkscape docs/design/desktop-concept.svg --export-type=png --export-filename=docs/design/desktop-concept.png
```

See [desktop test checklist](docs/TESTING.md), [installation details](docs/INSTALL.md),
and [asset provenance](docs/CREDITS.md).

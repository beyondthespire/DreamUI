# Installation behavior and recovery

## File ownership

`assets/` mirrors the per-user XDG data directory. Files are copied, not symlinked,
so the checkout can be moved without breaking installed themes. The installer
records each installed file's SHA-256 and the previous contents/mode, if any.
Updates preserve the first backup; removed upstream files are restored or removed
according to that backup. Unrelated files are not deleted. Empty directories may remain.

The state file is private (mode 0600). Concurrent operations use a file lock.
Symlinked source assets and destination path components are rejected, including
symlinked home/XDG paths. This conservative v0.1 restriction is intentional.

## Changed installed files

If an installed asset was modified or removed, deployment stops before writes.
Copy your changes somewhere safe, then restore that file from the **previously
installed Git revision**, not an arbitrary newer version, and rerun the command.
For personal customization, use a separate theme ID instead of editing managed assets.

## Interrupted installation

Regular write failures roll back asset changes. A recovery journal remains after
an interrupted process or failed rollback. Before retrying installation:

```bash
python3 scripts/manage.py recover
```

This restores the pre-operation asset files and installation ledger. Do not edit
managed files while a recovery journal is pending. Appearance application is a
separate KDE operation: if it fails after making partial changes, the original
settings snapshot remains available for the documented logged-out restoration.

## Appearance backup scope

The first script-based apply snapshots `kdeglobals`, `plasmarc`, `kwinrc`,
`plasma-org.kde.plasma.desktop-appletsrc`, and the corresponding theme defaults in
`kdedefaults/`. Files that did not exist are recorded as absent. Repeated applies
do not replace this baseline. Uninstall with restoration rewinds these entire
files, including later unrelated edits to them; it is not a key-by-key merge.

The optional panel uses KDE's scripting API and requires a running Plasma session.
Apply normally once before manually removing panels, so the baseline includes them.

## Appearance differences

- If a frame is unavailable, verify the Aurorae engine is installed through your
  distribution and choose Dream Glass under Window Decorations.
- Breeze supplies application controls and all unspecified shell SVGs/icons.
- Client-decorated applications can draw their own titlebars and may not use Aurorae.
- GTK applications and sandboxed apps may not inherit all KDE styling.
- Blur depends on KWin/compositing. Opaque shell alternatives are included.
- Global theme changes may need a logout/login to clear caches.
- The scripts do not restart Plasma, install system packages, or change login managers.

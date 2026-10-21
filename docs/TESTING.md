# Validation and desktop acceptance

## Automated checks completed for the foundation

- JSON metadata identities and global theme cross-references.
- SVG XML, unique IDs, nine-slice shell backgrounds and decoration button IDs.
- PNG signature and shell/JavaScript syntax.
- Isolated install, update, previous-file restoration, stale file handling.
- Conflict protection, symlink rejection, path traversal rejection, dry-run behavior.
- Failure rollback, settings snapshot retention, running-session restore guard.
- Generated vector source reproducibility in GitHub Actions.

These tests do not replace a running KDE desktop test. No Plasma session is
available in the authoring environment. This version is experimental.

## Required before tagging a stable release

Record distribution release, `plasmashell --version`, Qt version, GPU, session
type (Wayland/X11), display arrangement and scale for each test run.

- [ ] Clean install under a non-root user on a Debian/Ubuntu Plasma 6 desktop.
- [ ] Both themes appear in System Settings and apply successfully.
- [ ] Aurorae buttons render and close/minimize/maximize/restore correctly.
- [ ] Active/inactive/maximized frames, corners and title text are readable.
- [ ] Panels, menus, tooltips, tray popups and notifications have readable text.
- [ ] Wallpaper selection and icons work after logout/login.
- [ ] Stock panel remains intact after normal apply and update.
- [ ] Optional panel adds once and refuses to replace existing panels.
- [ ] 100%, 150% and 200% scale; one and two screens; light/dark wallpaper.
- [ ] Keyboard navigation and focus indications are visible.
- [ ] Opaque backgrounds work without blur/compositing where supported.
- [ ] Install → apply → update → logged-out restore returns to original settings.
- [ ] Modified assets are preserved by a refused update/uninstall.
- [ ] Inspect Dolphin, Konsole, System Settings, a browser, GTK and Flatpak apps.

Capture actual installed-desktop screenshots separately from `docs/design/`.

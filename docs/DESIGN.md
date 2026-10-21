# DreamUI design direction

## Moonlight Glass

The reference images combine Longhorn blue, Vista glass, metallic media controls,
dimensional icons, nature imagery and a dreamy lunar palette. DreamUI translates
that vocabulary into an original KDE appearance layer.

| Token | Value | Use |
| --- | --- | --- |
| Midnight | `#111b43` | Wallpaper sky |
| Deep glass | `#233b66` | Panel/dialog base |
| Glass highlight | `#627eaa` | Reflective surfaces |
| Pearl | `#ecf2fb` | Application backgrounds |
| Ink | `#1b2741` | Application text |
| Blue accent | `#3670bf` | Selections and focus |
| Violet accent | `#6d58ad` | Alternate application scheme |
| Moonlight | `#f3fbff` | Glass text and highlights |

Use compact controls, modest corner rounding, one bright edge, and readable solid
application interiors. Transparency belongs to window frames and the shell rather
than every content surface. Preserve the user's font and cursor choices in v0.1.
Pixel text belongs in optional decorative artwork, not everyday application text.

## What the concept represents

`design/desktop-concept.svg` is an editable composition built with the actual icon
and wallpaper assets. It is not a screenshot or an exact promise of current KDE
rendering. Its illustrated launcher, sidebar, and polished Dolphin controls guide
later implementation. The installed starter uses Kickoff, Breeze controls and a
minimal original Aurorae frame. Dolphin's menus and toolbar layout are not rewritten.

## Implementation milestones

1. **Foundation (this change):** Blue/Violet color schemes, global-theme packages,
   Plasma backgrounds, Aurorae frames, starter icons, moon wallpaper, installer,
   restoration, concept, and automated validation.
2. **Desktop verification:** run the checklist on a named Debian/Ubuntu release,
   record Plasma/Qt versions, fix rendering and test multiple displays/scaling.
3. **Application styling:** evaluate a maintainable Qt/Kvantum style for raised
   controls and toolbars; document GTK/Flatpak limitations separately.
4. **Shell polish:** complete task-button states, coordinate violet glass, expand
   icons, and tune launcher layout. Keep components optional.
5. **Widgets:** clock/calendar and media sidebar, using KDE data sources. Do not
   install decorative sample data as a working weather or music integration.

ISO development is intentionally outside this repository milestone. No shell
replacement, system service, greeter change, or KDE fork is introduced.

## KDE references

- https://develop.kde.org/docs/plasma/theme/theme-details/
- https://develop.kde.org/docs/plasma/theme/background-svg/
- https://develop.kde.org/docs/plasma/aurorae/
- https://develop.kde.org/docs/plasma/scripting/
- https://develop.kde.org/docs/plasma/theme/theme-porting-to-plasma6/

#!/usr/bin/env python3
"""Rebuild original vector assets; no third-party artwork or Python packages."""
from pathlib import Path
import json
import random
import html

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'assets'
VERSION = '0.1.0'

def write(path, content):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + '\n')

def svg(body, width=128, height=128):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{body}</svg>'

def meta(name, ident, structure=None):
    value = {'KPlugin': {'Name': name, 'Id': ident, 'Version': VERSION,
             'Description': 'DreamUI — comfort, ease, and nostalgia',
             'Authors': [{'Name': 'DreamUI contributors'}],
             'Website': 'https://github.com/beyondthespire/DreamUI'}}
    if structure:
        value['KPackageStructure'] = structure
    return json.dumps(value, indent=2)

def gradient(ident, top, bottom):
    return f'<linearGradient id="{ident}" x2="0" y2="1"><stop stop-color="{top}"/><stop offset=".48" stop-color="{bottom}"/><stop offset=".5" stop-color="{bottom}"/><stop offset="1" stop-color="{top}" stop-opacity=".35"/></linearGradient>'

def frame(prefix='', color='#263c6a', opacity=0.94, offset=0):
    """Nine independent tiles: no clip paths (Qt SVG element bounds stay exact)."""
    p = prefix + '-' if prefix else ''
    out = []
    for name, x, y, w, h in [('topleft',0,0,6,6),('top',6,0,32,6),('topright',38,0,6,6),
                            ('left',0,6,6,32),('center',6,6,32,32),('right',38,6,6,32),
                            ('bottomleft',0,38,6,6),('bottom',6,38,32,6),('bottomright',38,38,6,6)]:
        fill = color if name != 'center' else 'url(#glass)'
        if color == '#000000':
            fill = color
        corners={'topleft':'M6 0Q0 0 0 6H6Z','topright':'M38 0Q44 0 44 6H38Z',
                 'bottomleft':'M0 38Q0 44 6 44V38Z','bottomright':'M38 44Q44 44 44 38H38Z'}
        out.append(f'<g id="{p}{name}" transform="translate({offset},0)">')
        if name in corners:
            out.append(f'<path d="{corners[name]}" fill="{fill}" fill-opacity="{opacity}"/>')
        else:
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" fill-opacity="{opacity}"/>')
        if color != '#000000':
            if name == 'top':
                out.append(f'<path d="M{x} .5h{w}" stroke="#c7e5ff" stroke-opacity=".65"/>')
            if name == 'bottom':
                out.append(f'<path d="M{x} 43.5h{w}" stroke="#101f40" stroke-opacity=".7"/>')
        out.append('</g>')
    for direction in ['top','bottom','left','right']:
        out.append(f'<rect id="{p}hint-{direction}-margin" x="{offset}" y="50" width="6" height="6" fill="#ff00ff"/>')
    return ''.join(out)

def palette(name, accent, dark=False):
    bg = '30,44,76' if dark else '236,242,251'
    fg = '245,248,255' if dark else '27,39,65'
    view = '24,36,65' if dark else '251,253,255'
    out = f'[General]\nName={name}\nColorScheme={name.replace(" ", "")}\n\n'
    for group in ['Window','View','Button','Selection','Tooltip','Complementary','Header']:
        back = accent if group == 'Selection' else (view if group == 'View' else bg)
        fore = '255,255,255' if group == 'Selection' else fg
        out += f'''[Colors:{group}]
BackgroundNormal={back}
BackgroundAlternate={bg}
ForegroundNormal={fore}
ForegroundInactive={'176,190,214' if dark else '88,105,132'}
ForegroundActive={accent}
ForegroundLink={'143,201,255' if dark else accent}
ForegroundVisited=145,104,188
ForegroundNegative=215,66,82
ForegroundNeutral=185,125,38
ForegroundPositive=39,137,107
DecorationFocus={accent}
DecorationHover={accent}

'''
    out += f'''[WM]
activeBackground={accent}
activeForeground=255,255,255
inactiveBackground=107,121,151
inactiveForeground=235,241,251

[ColorEffects:Disabled]
Enable=true
Color=112,123,145
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
Enable=false
ChangeSelectionColor=true
'''
    return out

def themes():
    for variant, accent in [('Blue','54,112,191'), ('Violet','109,88,173')]:
        write(f'assets/color-schemes/Dream{variant}.colors', palette(f'Dream {variant}',accent))
        ident=f'org.beyondthespire.dreamui.{variant.lower()}'
        base=f'assets/plasma/look-and-feel/{ident}'
        write(f'{base}/metadata.json',meta(f'DreamUI {variant}',ident,'Plasma/LookAndFeel'))
        write(f'{base}/contents/defaults',f'''[kdeglobals][General]
ColorScheme=Dream{variant}

[kdeglobals][KDE]
widgetStyle=Breeze

[kdeglobals][Icons]
Theme=DreamUI

[plasmarc][Theme]
name=dreamui

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae
theme=__aurorae__svg__DreamGlass
''')
    base='assets/plasma/desktoptheme/dreamui'
    metadata=json.loads(meta('DreamUI Glass','dreamui'))
    metadata['X-Plasma-API']='5.0'
    write(f'{base}/metadata.json',json.dumps(metadata,indent=2))
    write(f'{base}/plasmarc','''[Settings]
FallbackTheme=default

[BlurBehindEffect]
enabled=true

[ContrastEffect]
enabled=false

[Wallpaper]
defaultWallpaperTheme=DreamMoon
defaultFileSuffix=.png
defaultWidth=2560
defaultHeight=1440
''')
    write(f'{base}/colors',palette('Dream Glass','112,166,235',True).split('[WM]')[0])
    for file in ['widgets/panel-background.svg','dialogs/background.svg','widgets/background.svg','widgets/tooltip.svg']:
        for opaque in [False,True]:
            defs=f'<defs>{gradient("glass", "#627eaa", "#233b66")}</defs>'
            body=defs+frame(opacity=1 if opaque else .93)+frame('mask','#000000',1,60)
            if 'panel-' in file:
                for i, direction in enumerate(['north','south','east','west']):
                    body+=frame(direction,opacity=1 if opaque else .93,offset=120+i*60)
            body+='<rect id="hint-stretch-borders" x="0" y="64" width="1" height="1"/>'
            write(f'{base}/{"opaque/" if opaque else ""}{file}',svg(body,420,70))

def decoration():
    base='assets/aurorae/themes/DreamGlass'
    write(f'{base}/metadata.desktop','''[Desktop Entry]
Name=Dream Glass
Comment=Original blue glass window frames for DreamUI
X-KDE-PluginInfo-Name=DreamGlass
X-KDE-PluginInfo-Author=DreamUI contributors
X-KDE-PluginInfo-Version=0.1.0
X-KDE-PluginInfo-Website=https://github.com/beyondthespire/DreamUI
''')
    write(f'{base}/DreamGlassrc','''[General]
TitleAlignment=Left
TitleVerticalAlignment=Center
ActiveTextColor=248,251,255
InactiveTextColor=220,228,244
UseTextShadow=true
ActiveTextShadowColor=13,26,55
InactiveTextShadowColor=30,40,61
TextShadowOffsetY=1
Animation=120
LeftButtons=M
RightButtons=IAX
Shadow=false

[Layout]
BorderLeft=6
BorderRight=6
BorderBottom=6
TitleEdgeTop=4
TitleEdgeBottom=4
TitleEdgeLeft=7
TitleEdgeRight=7
TitleHeight=24
ButtonWidth=28
ButtonWidthClose=36
ButtonHeight=22
ButtonSpacing=2
ButtonMarginTop=0
''')
    body=f'<defs>{gradient("glass","#6f93c2","#294e82")}</defs>'
    for i,p in enumerate(['decoration','decoration-inactive','decoration-opaque','decoration-opaque-inactive']):
        body+=frame(p,opacity=1 if 'opaque' in p else .94,offset=i*60)
    body+=frame('mask','#000000',1,240)
    write(f'{base}/decoration.svg',svg(body,300,70))
    glyphs={'close':'M11 7l8 8m0-8l-8 8','minimize':'M10 15h10',
            'maximize':'M10 7h10v9H10z M10 9h10','restore':'M9 10h9v7H9z M12 10V6h9v8h-3',
            'alldesktops':'M15 5v12 M9 11h12','keepabove':'M9 14l6-6 6 6',
            'keepbelow':'M9 8l6 6 6-6','shade':'M9 7h12 M9 15l6-5 6 5',
            'help':'M11 8q4-6 8 0q0 3-4 4v1 M15 16v1'}
    for kind,glyph in glyphs.items():
        out=f'<defs>{gradient("button", "#a5c4e5", "#376294")}{gradient("red","#f3aaa9","#9c3e55")}</defs>'
        for i,state in enumerate(['active','inactive','hover','hover-inactive','pressed','pressed-inactive','deactivated','deactivated-inactive']):
            fill='url(#red)' if kind=='close' else 'url(#button)'
            if 'pressed' in state: fill='#244a75'
            out+=f'<g id="{state}-center" transform="translate({i*34},0)" opacity="{.5 if "deactivated" in state else 1}"><rect x=".5" y=".5" width="29" height="21" rx="3" fill="{fill}" stroke="#b3cce6" stroke-opacity=".8"/>'
            if 'hover' in state: out+='<rect x="1" y="1" width="28" height="20" rx="3" fill="#d5f3ff" opacity=".25"/>'
            out+=f'<path d="{glyph}" fill="none" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></g>'
        write(f'{base}/{kind}.svg',svg(out,272,22))

def icons():
    folder='<path d="M7 17q0-4 4-4h17l6 6h19q4 0 4 4v28H7z" fill="#426ca6" stroke="#244b7e"/><path d="M7 25h50l-4 28H11z" fill="url(#i)" stroke="#3973ae"/><path d="M9 27h46" stroke="#e8f8ff"/>'
    orb='<circle cx="32" cy="32" r="27" fill="url(#i)" stroke="#c4e8ff" stroke-width="2"/><ellipse cx="31" cy="21" rx="21" ry="12" fill="#fff" opacity=".28"/><path d="M39 15a17 17 0 1 0 9 28A18 18 0 0 1 39 15" fill="#e5f8ff"/><path d="M46 15l2 5 5 2-5 2-2 5-2-5-5-2 5-2z" fill="#fff"/>'
    shapes={'places/folder':folder,'places/folder-documents':folder+'<path d="M25 32h14v17H25z" fill="#eef8ff"/><path d="M28 36h8m-8 4h8m-8 4h6" stroke="#628bb8"/>',
      'places/folder-pictures':folder+'<rect x="23" y="32" width="20" height="15" fill="#d1edff"/><path d="M24 46l6-9 5 6 4-4 4 7" fill="#608c96"/>',
      'places/folder-music':folder+'<path d="M31 45V32l12-2v12" fill="none" stroke="#fff" stroke-width="3"/><ellipse cx="28" cy="46" rx="5" ry="3" fill="#fff"/><ellipse cx="40" cy="43" rx="5" ry="3" fill="#fff"/>',
      'places/user-home':'<path d="M8 30L32 9l24 21" fill="url(#i)" stroke="#d1ecff" stroke-width="2"/><path d="M15 28v26h34V28L32 14z" fill="url(#i)" stroke="#4382b8"/><path d="M27 54V36h11v18" fill="#e3f3ff"/>',
      'devices/computer':'<rect x="5" y="9" width="54" height="37" rx="4" fill="#d5e0f0" stroke="#839bb9"/><rect x="9" y="13" width="46" height="28" fill="url(#i)"/><path d="M28 46v8H18v4h28v-4H36v-8" fill="#b6c8de"/>',
      'places/user-trash':'<path d="M17 19h30l-3 38H20z" fill="url(#i)" stroke="#c4e5fc"/><ellipse cx="32" cy="19" rx="16" ry="5" fill="#d7edff" stroke="#7598be"/><path d="M26 29v19m12-19v19" stroke="#eef9ff" stroke-width="3"/>',
      'apps/start-here':orb,'apps/dreamui':orb}
    for name,shape in shapes.items():
        write(f'assets/icons/DreamUI/scalable/{name}.svg',svg(f'<defs>{gradient("i","#b4ecff","#4386ce")}</defs>'+shape,64,64))
    write('assets/icons/DreamUI/index.theme','''[Icon Theme]
Name=DreamUI
Comment=Original glossy starter icons; Breeze supplies remaining icons
Inherits=breeze,hicolor
Directories=scalable/places,scalable/devices,scalable/apps

[scalable/places]
Size=64
Type=Scalable
MinSize=16
MaxSize=256
Context=Places

[scalable/devices]
Size=64
Type=Scalable
MinSize=16
MaxSize=256
Context=Devices

[scalable/apps]
Size=64
Type=Scalable
MinSize=16
MaxSize=256
Context=Applications
''')

def wallpaper():
    r=random.Random(21)
    body='''<defs>
<linearGradient id="sky" x2=".2" y2="1"><stop stop-color="#111b43"/><stop offset=".52" stop-color="#3c528c"/><stop offset=".76" stop-color="#a4add5"/><stop offset="1" stop-color="#597499"/></linearGradient>
<linearGradient id="water" x2="0" y2="1"><stop stop-color="#7893be"/><stop offset=".3" stop-color="#294b78"/><stop offset="1" stop-color="#0b2041"/></linearGradient>
<radialGradient id="halo"><stop stop-color="#d7eaff" stop-opacity=".45"/><stop offset="1" stop-color="#c1cfff" stop-opacity="0"/></radialGradient>
<linearGradient id="moon" x2=".8" y2="1"><stop stop-color="#f3fbff"/><stop offset="1" stop-color="#b0c5ed"/></linearGradient>
</defs><rect width="2560" height="1440" fill="url(#sky)"/>
<ellipse cx="1870" cy="340" rx="480" ry="420" fill="url(#halo)"/>
'''
    for _ in range(125):
        x,y=r.randrange(2560),r.randrange(700)
        body+=f'<circle cx="{x}" cy="{y}" r="{r.choice([.8,1,1.5,2])}" fill="#d8eaff" opacity="{r.uniform(.2,.75):.2f}"/>'
    body+='''<path d="M1900 177a140 140 0 1 0 101 221A143 143 0 0 1 1900 177" fill="url(#moon)"/>
<path d="M0 700Q250 660 530 710T1100 680T1700 710T2560 655V850H0z" fill="#a9b9dc" opacity=".13"/>
<path d="M0 765l170-45 150 44 220-95 210 111 260-42 140 64H0z" fill="#243d64"/>
<path d="M2560 670l-240 80-190-45-290 108h720z" fill="#263f68"/>
<rect y="810" width="2560" height="630" fill="url(#water)"/>
<ellipse cx="1850" cy="870" rx="580" ry="135" fill="url(#halo)"/>
'''
    for i in range(115):
        y=820+i*5.3; w=r.uniform(30,240)*(1+i/55); x=1870+r.uniform(-170,170)-w/2
        body+=f'<path d="M{x:.1f} {y:.1f}h{w:.1f}" stroke="#c4dfff" opacity="{r.uniform(.025,.22):.3f}" stroke-width="{r.uniform(1,3):.1f}"/>'
    for i in range(45):
        y=860+i*13
        body+=f'<path d="M0 {y}q300 -12 650 0t700 0t700 0t650 0" fill="none" stroke="#94b8da" stroke-opacity=".045" stroke-width="2"/>'
    body+='<path d="M0 1300q200-80 410-25t390 165H0z" fill="#0b1c38"/><path d="M2560 1190q-170 10-310 100t-250 150h560z" fill="#0a1b34"/>'
    write('assets/wallpapers/DreamMoon/contents/images/2560x1440.svg',svg(body,2560,1440))
    write('assets/wallpapers/DreamMoon/metadata.json',meta('Dream Moon','DreamMoon','Wallpaper/Images'))

if __name__=='__main__':
    themes(); decoration(); icons(); wallpaper()
    print('Built original DreamUI assets.')

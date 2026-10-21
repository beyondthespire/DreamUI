#!/usr/bin/env python3
"""Editable SVG concept board using the actual DreamUI icon and wallpaper assets."""
from pathlib import Path
import base64
from html import escape
ROOT=Path(__file__).resolve().parents[1]

def image(path,x,y,w,h):
    data=base64.b64encode((ROOT/path).read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/svg+xml;base64,{data}"/>'

def text(x,y,value,size=14,color='#243958',weight=400):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(value)}</text>'

def rect(x,y,w,h,fill,rx=0,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'

def icon(name,x,y,size=40):
    return image(f'assets/icons/DreamUI/scalable/{name}.svg',x,y,size,size)

def build():
    s=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600" height="1060" viewBox="0 0 1600 1060">',
    '''<defs>
<linearGradient id="glass" x2="0" y2="1"><stop stop-color="#a2b4d2" stop-opacity=".92"/><stop offset=".4" stop-color="#536f9b" stop-opacity=".94"/><stop offset=".43" stop-color="#294570" stop-opacity=".96"/><stop offset="1" stop-color="#42638d" stop-opacity=".96"/></linearGradient>
<linearGradient id="toolbar" x2="0" y2="1"><stop stop-color="#fcfdff"/><stop offset="1" stop-color="#dce5f3"/></linearGradient>
<linearGradient id="select" x2="0" y2="1"><stop stop-color="#e6f4ff"/><stop offset="1" stop-color="#bad5f3"/></linearGradient>
<linearGradient id="sidebar" x2="0" y2="1"><stop stop-color="#e2eafa"/><stop offset="1" stop-color="#f3f5fc"/></linearGradient>
</defs>''',rect(0,0,1600,1060,'#0d1428'),text(64,52,'DreamUI',30,'#edf4ff',600),
    text(250,51,'A familiar place to come home to.',15,'#9daeca'),text(1270,49,'DESIGN STUDY  /  01',12,'#a3b5d3'),
    '<g transform="translate(64,94)">',image('assets/wallpapers/DreamMoon/contents/images/2560x1440.svg',0,0,1472,828)]
    for name,label,y in [('devices/computer','Computer',24),('places/user-home','Home',124),('places/user-trash','Trash',224)]:
        s += [icon(name,29,y,52),text(21 if label=='Computer' else 37,y+73,label,13,'#eff5ff')]
    # Main window: concept for mature application styling; initial version uses Breeze.
    s += [rect(295,144,880,531,'#061126',9),rect(288,134,880,531,'url(#glass)',8,'#9ebfe8'),
          text(303,158,'Home — Dolphin',14,'#f5faff',500)]
    for x,glyph,fill,w in [(1053,'−','url(#glass)',28),(1082,'□','url(#glass)',28),(1111,'×','#a75b70',44)]:
        s += [rect(x,139,w,23,fill,3,'#a6bbd8'),text(x+9,155,glyph,16,'#fff')]
    s += [rect(295,170,866,488,'#fbfdff'),rect(295,170,866,29,'#f5f8ff'),
          text(310,190,'File     Edit     View     Go     Tools     Settings     Help',13),
          rect(295,199,866,48,'url(#toolbar)'),rect(308,208,29,29,'url(#select)',14,'#95b7da'),text(316,229,'‹',23),
          rect(344,208,29,29,'url(#toolbar)',14,'#adbed3'),text(353,229,'›',23),
          rect(390,210,480,27,'#fff',3,'#b0bfd3'),text(402,229,'Home   ›   Randy',13),
          rect(884,210,261,27,'#fff',14,'#b0bfd3'),text(900,229,'Search in Home…',12,'#7888a1'),
          rect(295,247,180,380,'url(#sidebar)'),text(311,276,'Places',13,'#50698c',600)]
    for i,(name,label) in enumerate([('places/user-home','Home'),('places/folder','Desktop'),('places/folder-documents','Documents'),('places/folder-pictures','Pictures'),('places/folder-music','Music'),('places/user-trash','Trash')]):
        y=288+i*39
        if i==0:s += [rect(302,y,165,35,'url(#select)',4,'#a7c3e5')]
        s += [icon(name,311,y+5,25),text(346,y+23,label,13)]
    s += [text(312,570,'Devices',12,'#50698c',600),text(320,600,'▸   System drive',12)]
    folders=[('folder-documents','Documents','12 items'),('folder-pictures','Pictures','48 items'),('folder-music','Music','8 albums'),('folder','Downloads','6 items'),('folder','Projects','4 items'),('folder','Videos','3 items')]
    for i,(name,label,sub) in enumerate(folders):
        x=520+(i%3)*209; y=278+(i//3)*153
        if i==1:s += [rect(x-17,y-9,151,135,'url(#select)',5,'#b6d0ed')]
        s += [icon('places/'+name,x+20,y,76),text(x+5,y+98,label,14),text(x+10,y+119,sub,11,'#7a8da6')]
    s += [rect(295,627,866,31,'url(#toolbar)'),text(312,648,'6 folders',12,'#59718e'),text(970,648,'A little space for everything.',11,'#657d9c')]
    # Sidebar concept widgets.
    s += [rect(1240,39,207,176,'url(#glass)',9,'#8ba7cc'),text(1272,95,'10:30',41,'#fff',300),
          text(1282,126,'Wednesday',15,'#e5edff'),text(1286,152,'October 21',13,'#d6e4ff'),
          '<path d="M1262 170h162" stroke="#a7bfdf" opacity=".5"/>',text(1276,193,'Make room to dream.',11,'#e6efff'),
          rect(1240,233,207,207,'url(#glass)',9,'#8ba7cc'),text(1256,259,'NOW PLAYING',10,'#d2e5ff',600)]
    s += [image('assets/wallpapers/DreamMoon/contents/images/2560x1440.svg',1256,274,175,98),text(1256,393,'Moonlight on the water',12,'#fff'),text(1292,423,'‹‹       Ⅱ       ››',19,'#fff')]
    # Launcher visual target, deliberately labeled as concept in caption.
    s += [rect(14,432,257,340,'url(#glass)',8,'#9cb9df'),icon('apps/dreamui',29,446,42),text(82,471,'Welcome home',16,'#f7fbff',500),
          rect(24,499,237,223,'#eaf1fc',5)]
    for i,(name,label) in enumerate([('places/folder','File manager'),('devices/computer','System settings'),('places/folder-pictures','Photos'),('places/folder-music','Music'),('places/folder-documents','Text editor')]):
        y=508+i*41
        s += [icon(name,36,y,29),text(79,y+21,label,13)]
    s += [rect(26,733,185,27,'#f5faff',4,'#aec2dc'),text(38,751,'Search applications…',11,'#697e9c'),text(226,752,'⏻',19,'#fff')]
    # Taskbar.
    s += [rect(0,780,1472,48,'url(#glass)',0,'#9bb6d7'),icon('apps/dreamui',12,775,52),text(74,811,'Dream',15,'#f7fbff',600)]
    for x,name,label,width in [(158,'places/folder','Home — Dolphin',205),(372,'places/folder-music','Music',160)]:
        s += [rect(x,786,width,35,'url(#glass)',4,'#9ebadc'),icon(name,x+8,790,27),text(x+44,808,label,12,'#fff')]
    s += [text(1292,808,'⌁   ♪',18,'#f3f7ff'),text(1361,801,'10:30 AM',12,'#fff'),text(1363,817,'10/21/2026',10,'#d8e6f9'),'</g>',
          text(64,969,'MOONLIGHT GLASS',12,'#d1e0f7',600),text(64,999,'Blue glass  ·  Pearl interiors  ·  Glossy icons  ·  A quieter kind of nostalgia',14,'#93a9cc'),
          text(1005,969,'Visual target — not a running desktop screenshot.',12,'#b8c9e2'),text(1005,994,'Launcher, app controls and sidebar need further styling.',11,'#8fa3c2'),'</svg>']
    # SVG 1.1 image compatibility for Inkscape and GitHub renderers.
    result=''.join(s).replace(' href=',' xlink:href=')
    out=ROOT/'docs/design/desktop-concept.svg'
    out.write_text(result+'\n')
    print(out)

if __name__=='__main__': build()

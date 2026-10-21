#!/usr/bin/env python3
"""Validate asset syntax, identities and cross-references without a KDE session."""
import configparser
import json
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets'

def main():
    count=0
    for path in ASSETS.rglob('*'):
        if path.suffix=='.json':
            value=json.loads(path.read_text())
            assert value['KPlugin']['Id']==path.parent.name,path
        if path.suffix=='.svg':
            tree=ET.parse(path)
            ids=[e.attrib['id'] for e in tree.iter() if 'id' in e.attrib]
            assert len(ids)==len(set(ids)),f'Duplicate SVG ID: {path}'
        if path.is_file(): count+=1
    for path in (ASSETS/'plasma/look-and-feel').iterdir():
        assert json.loads((path/'metadata.json').read_text())['KPackageStructure']=='Plasma/LookAndFeel'
        config=configparser.ConfigParser(); config.read(path/'contents/defaults')
        color=config['kdeglobals][General']['ColorScheme']
        assert (ASSETS/f'color-schemes/{color}.colors').exists()
        assert (ASSETS/'aurorae/themes/DreamGlass/DreamGlassrc').exists()
    positions=['top','topleft','topright','left','center','right','bottom','bottomleft','bottomright']
    for path in (ASSETS/'plasma/desktoptheme/dreamui').rglob('*.svg'):
        ids={e.get('id') for e in ET.parse(path).iter()}
        for name in positions:
            assert name in ids,(path,name)
            assert 'mask-'+name in ids,(path,name)
    for name in ['close','minimize','maximize','restore','help','shade','keepabove','keepbelow','alldesktops']:
        path=ASSETS/f'aurorae/themes/DreamGlass/{name}.svg'
        assert 'active-center' in {e.get('id') for e in ET.parse(path).iter()}
    png=ASSETS/'wallpapers/DreamMoon/contents/images/2560x1440.png'
    assert png.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
    print(f'Validated {count} asset files. Live Plasma rendering still requires desktop testing.')

if __name__=='__main__': main()

#!/usr/bin/env python3
"""Build PROMPTURE Command Library v2.8 from v2.7 / v2.7.1 index.html.

Appends 1,000 new STUDIO commands (#1961-#2960 across 5 new categories)
from STUDIO_ADDON_1000_v2_8.md right after STUDIO #1960 (index 2179).
- Old prompture (0..219) and studio (#1-#1960 -> 220..2179) stay in place.
- Collections after studio (outfit..blueprint, old 2180..3625) shift +1000.
- Favorites migrate one-time v4 -> v5 seamlessly (also supports v3/v2 chains).
- Total commands: 3626 -> 4626 (STUDIO: 1960 -> 2960).
"""
import json
import re
import shutil

SRC = 'index.html'
BACKUP = 'index.html.v2_7_bak'
ADDON = 'STUDIO_ADDON_1000_v2_8.md'

MM_3626 = 'Command ' + ''.join(chr(c) for c in [0x1043, 0x1046, 0x1042, 0x1046])
MM_4626 = 'Command ' + ''.join(chr(c) for c in [0x1044, 0x1046, 0x1042, 0x1046])

EXPECTED_NEW_CATS = [
    '🔧 Fix, Repair & Inpaint',
    '🧵 Fabric Realism & Material Physics',
    '📸 Flash, Film & Modern Camera Aesthetics',
    '🪴 Prop & Environment Interaction',
    '🖼️ Output Format, Layout & Commercial Shots',
]


def parse_addon(path):
    raw = open(path, encoding='utf-8').read()
    lines = raw.split('\n')
    cats = []
    entries = []
    cur = None
    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            continue
        m = re.match(r'^## (.+?) \(\d+[–-]\d+\)\s*$', line)
        if m:
            cur = m.group(1).strip()
            if cur not in cats:
                cats.append(cur)
            continue
        m = re.match(r'^(\d+)\. (.+)$', line)
        if m:
            assert cur is not None, f'Entry before category heading at line {i + 1}'
            num = int(m.group(1))
            en = m.group(2).strip()
            assert i + 1 < len(lines), f'{path}:{num} missing MM line'
            mm = re.match(r'^   (.+)$', lines[i + 1])
            assert mm, f'{path}:{num} missing 3-space indented MM line'
            mm_txt = mm.group(1).strip()
            assert '</script' not in en.lower() and '</script' not in mm_txt.lower()
            entries.append({
                'collection': 'studio',
                'category': cur,
                'num': num,
                'text': en,
                'mm': mm_txt,
            })
    nums = [e['num'] for e in entries]
    assert nums == list(range(1961, 2961)), f'Expected sequential 1961-2960, got {len(nums)} items ({nums[:3]}..{nums[-3:]})'
    assert cats == EXPECTED_NEW_CATS, f'Categories mismatch: {cats}'
    counts = {c: sum(1 for e in entries if e['category'] == c) for c in cats}
    assert all(v == 200 for v in counts.values()), f'Expected 200 per category: {counts}'
    return cats, entries


def main():
    shutil.copy2(SRC, BACKUP)
    html = open(SRC, encoding='utf-8').read()
    m = re.search(r'<script>\n(.*?)\n</script>', html, re.S)
    assert m, 'script block not found'
    js = m.group(1)

    assert 'PROMPTURE Command Library v2.7' in html, 'Expected v2.7 / v2.7.1 index.html'
    old_cmds = json.loads(re.search(r'COMMANDS = (\[.*?\]);\nconst CAT_ORDER', js, re.S).group(1))
    assert len(old_cmds) == 3626, f'Expected baseline 3626, got {len(old_cmds)}'
    assert all(c['collection'] == 'prompture' for c in old_cmds[:220])
    assert all(c['collection'] == 'studio' for c in old_cmds[220:2180])
    assert old_cmds[2179]['num'] == 1960
    assert old_cmds[2180]['collection'] == 'outfit'

    new_cats, addon_entries = parse_addon(ADDON)

    # Check uniqueness across all studio commands
    old_studio_texts = {c['text'] for c in old_cmds[220:2180]}
    addon_texts = [e['text'] for e in addon_entries]
    assert len(set(addon_texts)) == 1000, 'Duplicate text inside addon!'
    dups = old_studio_texts.intersection(addon_texts)
    assert not dups, f'Overlap with existing studio commands: {list(dups)[:5]}'
    print(f'[OK] Parsed {len(addon_entries)} unique addon commands (#1961-#2960)')

    # Build new COMMANDS (4626 total)
    new_cmds = old_cmds[:2180] + addon_entries + old_cmds[2180:]
    assert len(new_cmds) == 4626, len(new_cmds)

    # 1. Replace COMMANDS
    start = js.find('COMMANDS = [')
    end_marker = '];\nconst CAT_ORDER'
    end = js.find(end_marker, start)
    assert start >= 0 and end > start
    new_json = 'COMMANDS = [' + ', '.join(json.dumps(e, ensure_ascii=False) for e in new_cmds)
    js = js[:start] + new_json + js[end:]

    # 2. Update CAT_ORDER['studio']
    co_start = js.find('const CAT_ORDER = ')
    co_end_marker = ';\nconst COLL_NAME'
    co_end = js.find(co_end_marker, co_start)
    assert co_start >= 0 and co_end > co_start
    co = json.loads(js[co_start + len('const CAT_ORDER = '):co_end])
    assert len(co['studio']) == 14
    co['studio'] = co['studio'] + new_cats
    js = js[:co_start] + 'const CAT_ORDER = ' + json.dumps(co, ensure_ascii=False) + js[co_end:]
    print('[OK] Updated CAT_ORDER[studio] -> 19 categories')

    # 3. Add migrateFavsV5 & upgrade localStorage v4 -> v5
    mig_v5 = (
        'function migrateFavsV5(old){ const out=[]; old.forEach(i=>{ '
        'const ni=i<2180?i:i+1000; if(ni>=0&&ni<4626&&out.indexOf(ni)<0) out.push(ni); }); return out; }\n'
    )
    anchor = 'function migrateFavsV4(old)'
    assert anchor in js, 'migrateFavsV4 not found'
    js = js.replace(anchor, mig_v5 + anchor, 1)

    old_load = (
        "let favs=[]; try{ const v4=localStorage.getItem('prompture_cmd_favs_v4');\n"
        "  if(v4!==null){ favs=JSON.parse(v4); }\n"
        "  else { const v3=localStorage.getItem('prompture_cmd_favs_v3');\n"
        "    if(v3!==null){ favs=migrateFavsV4(JSON.parse(v3)); }\n"
        "    else { favs=migrateFavsV4(migrateFavs(JSON.parse(localStorage.getItem('prompture_cmd_favs_v2')||'[]'))); }\n"
        "    try{ localStorage.setItem('prompture_cmd_favs_v4', JSON.stringify(favs)); }catch(e){} }\n"
        "}catch(e){ favs=[]; }"
    )
    new_load = (
        "let favs=[]; try{ const v5=localStorage.getItem('prompture_cmd_favs_v5');\n"
        "  if(v5!==null){ favs=JSON.parse(v5); }\n"
        "  else { const v4=localStorage.getItem('prompture_cmd_favs_v4');\n"
        "    if(v4!==null){ favs=migrateFavsV5(JSON.parse(v4)); }\n"
        "    else { const v3=localStorage.getItem('prompture_cmd_favs_v3');\n"
        "      if(v3!==null){ favs=migrateFavsV5(migrateFavsV4(JSON.parse(v3))); }\n"
        "      else { favs=migrateFavsV5(migrateFavsV4(migrateFavs(JSON.parse(localStorage.getItem('prompture_cmd_favs_v2')||'[]')))); } }\n"
        "    try{ localStorage.setItem('prompture_cmd_favs_v5', JSON.stringify(favs)); }catch(e){} }\n"
        "}catch(e){ favs=[]; }"
    )
    assert old_load in js, 'load block not found'
    js = js.replace(old_load, new_load, 1)

    old_save = "function saveFavs(){ localStorage.setItem('prompture_cmd_favs_v4'"
    assert old_save in js, 'saveFavs not found'
    js = js.replace(old_save, "function saveFavs(){ localStorage.setItem('prompture_cmd_favs_v5'", 1)
    print('[OK] Added Favorites v4 -> v5 migration')

    # 4. Update JS counts & subtitles
    assert "t.all+' (3626)</button>'" in js
    js = js.replace("t.all+' (3626)</button>'", "t.all+' (4626)</button>'", 1)
    assert "🎨 STUDIO (1960)</button>'" in js
    js = js.replace("🎨 STUDIO (1960)</button>'", "🎨 STUDIO (2960)</button>'", 1)
    assert "subtitle:'3626 commands" in js
    js = js.replace("subtitle:'3626 commands", "subtitle:'4626 commands", 1)
    assert MM_3626 in js
    js = js.replace(MM_3626, MM_4626, 1)

    html = html[:m.start(1)] + js + html[m.end(1):]

    # 5. Update static HTML
    assert '🌟 အားလုံး (3626)' in html
    html = html.replace('🌟 အားလုံး (3626)', '🌟 အားလုံး (4626)', 1)
    assert '🎨 STUDIO (1960)' in html
    html = html.replace('🎨 STUDIO (1960)', '🎨 STUDIO (2960)', 1)
    assert MM_3626 in html
    html = html.replace(MM_3626, MM_4626, 1)
    assert 'PROMPTURE Command Library v2.7 · 3626 commands' in html
    html = html.replace(
        'PROMPTURE Command Library v2.7 · 3626 commands',
        'PROMPTURE Command Library v2.8 · 4626 commands',
        1,
    )

    open(SRC, 'w', encoding='utf-8').write(html)
    print(f'[OK] Built v2.8 successfully! ({SRC} updated, backup at {BACKUP})')


if __name__ == '__main__':
    main()
from pathlib import Path
p = Path('index.html')
s = p.read_text(encoding='utf-8')
marker = '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">'
if 'http-equiv="Cache-Control"' not in s:
    block = marker + '\n<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0">\n<meta http-equiv="Pragma" content="no-cache">\n<meta http-equiv="Expires" content="0">'
    if marker not in s:
        raise SystemExit('viewport marker not found')
    s = s.replace(marker, block, 1)
    p.write_text(s, encoding='utf-8')
print('cache headers added')

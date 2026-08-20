from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
old = "const rates = [100, 98, 80, 75, 65, 50, 45, 30, 25, 15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2];"
new = "const rates = [100, 98, 80, 75, 65, 50, 45, 30, 25, 15, 15, 15, 15, 15, 10, 10, 10, 10, 5, 5];"
if old not in s:
    raise SystemExit('target rate table not found or already changed')
s = s.replace(old, new, 1)
p.write_text(s, encoding='utf-8')
print('enhancement rates updated')

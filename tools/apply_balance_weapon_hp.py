from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

replacements = [
    ('{ name: "목검", atk: 7, desc: "" }', '{ name: "목검", atk: 10, desc: "" }'),
    ('{ name: "철검", atk: 10, awakenChance: 0.04', '{ name: "철검", atk: 20, awakenChance: 0.04'),
    ('{ name: "화검", atk: 10, fire: true', '{ name: "화검", atk: 25, fire: true'),
    ('{ name: "백사의 침", atk: 15, extra: 20', '{ name: "백사의 침", atk: 35, extra: 20'),
    ('{ name: "공허의 대검", atk: 10, corrupt: true', '{ name: "공허의 대검", atk: 15, corrupt: true'),
    ('{ name: "몰락한 신의 검", atk: 30, absorb: 0.05', '{ name: "몰락한 신의 검", atk: 45, absorb: 0.05'),
    ('{ name: "신의 유산", atk: 35, revive: true', '{ name: "신의 유산", atk: 65, revive: true'),
    ('{ name: "나무 지팡이", atk: 5, seal: 0.02', '{ name: "나무 지팡이", atk: 10, seal: 0.02'),
]

for old, new in replacements:
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'expected exactly 1 match for {old!r}, got {count}')
    s = s.replace(old, new, 1)

player_hp_count = s.count('level * 50')
if player_hp_count < 1:
    raise SystemExit('no player enhancement HP formulas found')
s = s.replace('level * 50', 'level * 100')

enemy_hp_count = s.count('enemyLevel * 50')
if enemy_hp_count < 1:
    raise SystemExit('no AI enhancement HP formula found')
s = s.replace('enemyLevel * 50', 'enemyLevel * 100')

required = [
    '{ name: "목검", atk: 10, desc: "" }',
    '{ name: "나무 지팡이", atk: 10, seal: 0.02',
    '{ name: "철검", atk: 20, awakenChance: 0.04',
    '{ name: "화검", atk: 25, fire: true',
    '{ name: "백사의 침", atk: 35, extra: 20',
    '{ name: "공허의 대검", atk: 15, corrupt: true',
    '{ name: "몰락한 신의 검", atk: 45, absorb: 0.05',
    '{ name: "신의 유산", atk: 65, revive: true',
    'base + level * 100',
    'enemyBase + (enemyLevel * 100)',
]
for token in required:
    if token not in s:
        raise SystemExit(f'missing required result: {token}')

if 'base + level * 50' in s or 'enemyLevel * 50' in s:
    raise SystemExit('old +50 HP scaling remains')

p.write_text(s, encoding='utf-8')
print(f'Applied balance patch; player HP formulas changed: {player_hp_count}, AI formulas changed: {enemy_hp_count}')

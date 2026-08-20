from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove WELCOM alias; keep only WELCOME.
welcom_line = "  '9c708286ba5458be8adda01ac28b33331ed6aeaac4e5c10897a0e7b7e17956dd': { codeId: 'welcome_reward', lp: 0, lr: 500, label: '500 LR' }\n"
if welcom_line not in s:
    raise SystemExit('WELCOM hash entry not found')
s = s.replace(welcom_line, '', 1)

# Add explicit +11~+20 weapon names.
marker = "function getWeapon(cls, lv, awakened, awakenType) {"
if marker not in s:
    raise SystemExit('getWeapon marker not found')

name_table = r'''const TRANSCEND_WEAPON_NAMES = Object.freeze({
  sword: Object.freeze({
    11: '신의 운명',
    12: '참살쇄도류',
    13: '안슐루스',
    14: '신살흑도',
    15: '적월도',
    16: '명월도',
    17: '마검 데스티니',
    18: '엑스칼리버',
    19: '불멸 무라마사',
    20: '살신명도'
  }),
  mage: Object.freeze({
    11: '고대의 전설',
    12: '신 전설의 시작',
    13: '파멸의 징조',
    14: '파멸의 노래',
    15: '공허의 균열 지팡이',
    16: '만물의 혼돈',
    17: '만물의 파멸',
    18: '만물의 샘물 지팡이',
    19: '무한의 지팡이',
    20: '천지창조'
  })
});

'''
if 'const TRANSCEND_WEAPON_NAMES = Object.freeze({' not in s:
    s = s.replace(marker, name_table + marker, 1)

old_name = "    weapon.name = `${weapon.name} · 초월 +${lv}`;"
new_name = "    weapon.name = (TRANSCEND_WEAPON_NAMES[cls] && TRANSCEND_WEAPON_NAMES[cls][lv]) || `${weapon.name} · 초월 +${lv}`;"
if old_name not in s:
    raise SystemExit('old transcend weapon naming line not found')
s = s.replace(old_name, new_name, 1)

# Safety checks.
if '9c708286ba5458be8adda01ac28b33331ed6aeaac4e5c10897a0e7b7e17956dd' in s:
    raise SystemExit('WELCOM hash still present')
if '280d44ab1e9f79b5cce2dd4f58f5fe91f0fbacdac9f7447dffc318ceb79f2d02' not in s:
    raise SystemExit('WELCOME hash missing')
for name in [
    '신의 운명','참살쇄도류','안슐루스','신살흑도','적월도','명월도','마검 데스티니','엑스칼리버','불멸 무라마사','살신명도',
    '고대의 전설','신 전설의 시작','파멸의 징조','파멸의 노래','공허의 균열 지팡이','만물의 혼돈','만물의 파멸','만물의 샘물 지팡이','무한의 지팡이','천지창조'
]:
    if name not in s:
        raise SystemExit(f'missing weapon name: {name}')

p.write_text(s, encoding='utf-8')
print('weapon names and WELCOME-only coupon applied')

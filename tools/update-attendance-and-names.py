from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

replacements = {
    "7일 연속마다 추가 +100 LP": "7일 연속마다 추가 +200 LR",
    "    11: '신의 운명',": "    11: '천명의 신검',",
    "    12: '참살쇄도류',": "    12: '참살쇄도',",
    "    18: '엑스칼리버',": "    18: '진·엑스칼리버',",
    "    19: '불멸 무라마사',": "    19: '불멸의 무라마사',",
    "    20: '살신명도'": "    20: '살신명도·종언'",
    "    15: '공허의 균열 지팡이',": "    15: '공허균열의 지팡이',",
    "    17: '만물의 파멸',": "    17: '만물의 근절',",
    "    18: '만물의 샘물 지팡이',": "    18: '만물의 근원',",
    "    19: '무한의 지팡이',": "    19: '무한회귀의 지팡이',",
}
for old, new in replacements.items():
    if old not in s:
        raise SystemExit(f'missing target: {old}')
    s = s.replace(old, new, 1)

old_logic = """      const lrReward = 100;\n      const lpReward = streak % 7 === 0 ? 100 : 0;\n\n      base.lr = Math.max(0, Number(base.lr) || 0) + lrReward;\n      base.lp = Math.max(0, Number(base.lp) || 0) + lpReward;"""
new_logic = """      const streakLrBonus = streak % 7 === 0 ? 200 : 0;\n      const lrReward = 100 + streakLrBonus;\n      const lpReward = 0;\n\n      base.lr = Math.max(0, Number(base.lr) || 0) + lrReward;\n      base.lp = Math.max(0, Number(base.lp) || 0) + lpReward;"""
if old_logic not in s:
    raise SystemExit('attendance reward logic target not found')
s = s.replace(old_logic, new_logic, 1)

old_text = """      rewardText = lpReward > 0\n        ? `출석 완료! +${lrReward} LR · 7일 연속 보너스 +${lpReward} LP`\n        : `출석 완료! +${lrReward} LR`;"""
new_text = """      rewardText = streakLrBonus > 0\n        ? `출석 완료! +100 LR · 7일 연속 보너스 +${streakLrBonus} LR`\n        : `출석 완료! +${lrReward} LR`;"""
if old_text not in s:
    raise SystemExit('attendance reward text target not found')
s = s.replace(old_text, new_text, 1)

for check in [
    "7일 연속마다 추가 +200 LR",
    "11: '천명의 신검'",
    "12: '참살쇄도'",
    "18: '진·엑스칼리버'",
    "19: '불멸의 무라마사'",
    "20: '살신명도·종언'",
    "15: '공허균열의 지팡이'",
    "17: '만물의 근절'",
    "18: '만물의 근원'",
    "19: '무한회귀의 지팡이'",
    "const streakLrBonus = streak % 7 === 0 ? 200 : 0;"
]:
    if check not in s:
        raise SystemExit(f'validation failed: {check}')

p.write_text(s, encoding='utf-8')
print('attendance and weapon names updated')

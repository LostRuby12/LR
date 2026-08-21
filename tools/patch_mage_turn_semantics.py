from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="12: Object.freeze({ name: '신 전설의 시작', atk: 75, mythicStart: true, desc: '스킬 「신화의 시작」 · 자신의 2번째 턴부터 사용 · 사용 시 공격력 +15% 누적 · 사용 후 2턴 충전' })"
new="12: Object.freeze({ name: '신 전설의 시작', atk: 75, mythicStart: true, desc: '스킬 「신화의 시작」 · 자신의 2턴 경과 후 사용 · 사용 시 공격력 +15% 누적 · 사용 후 2턴 충전' })"
if s.count(old)!=1: raise SystemExit('desc target mismatch')
s=s.replace(old,new,1)
old2="if (level === 12) mageSkillNextReadyTurn = 2;"
new2="if (level === 12) mageSkillNextReadyTurn = 3;"
if s.count(old2)!=1: raise SystemExit('turn target mismatch')
s=s.replace(old2,new2,1)
p.write_text(s,encoding='utf-8')
print('mage +12 first skill set to turn 3')

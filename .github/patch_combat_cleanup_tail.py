from pathlib import Path
import re, subprocess, sys
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit('target not found: '+label)
    s=s.replace(old,new,1)

# 적 정화 대기도 실제 효과를 막을 때만 소모
rep("""  if (enemyPurifyNext) enemyPurifyNext = false;\n\n  if (enemyAwakened && enemyAwakenType === 'excalibur') {""",
    """  // 적 정화 대기도 실제 상태이상/부패를 막았을 때만 소모된다.\n\n  if (enemyAwakened && enemyAwakenType === 'excalibur') {""",
    'enemy purify expiry')

# 일반 적 월광봉멸 반사는 해당 공격 1회 처리 직후 종료
rep("""    if (canAbility && w.corrupt) {\n      const hasC = (typeof w.corrupt === 'boolean' && w.corrupt) || (typeof w.corrupt === 'number' && rand() < w.corrupt);\n      if (hasC) {\n        const cDmg = Math.floor(Math.max(1, enemy.hp) * 0.10);\n        dmgEnemy(cDmg);\n        await showAbility('☠️ 타락 부패!', `적에게 부패 ${cDmg}!`);\n      }\n    }\n  } else if (!dodged) {""",
    """    if (canAbility && w.corrupt) {\n      const hasC = (typeof w.corrupt === 'boolean' && w.corrupt) || (typeof w.corrupt === 'number' && rand() < w.corrupt);\n      if (hasC) {\n        const cDmg = Math.floor(Math.max(1, enemy.hp) * 0.10);\n        dmgEnemy(cDmg);\n        await showAbility('☠️ 타락 부패!', `적에게 부패 ${cDmg}!`);\n      }\n    }\n    if (sword16ReflectActive) sword16ReflectActive = false;\n  } else if (!dodged) {""",
    'normal reflect clear')

# 이벤트 보스도 실제 공격(이중 포함)이 끝난 뒤 반사 종료
rep("""      if (enemy.lifestealOnHit && actual > 0) {\n        const heal = Math.floor(actual * enemy.lifestealOnHit);\n        enemy.hp = Math.min(enemy.maxHp, enemy.hp + heal);\n        await showAbility('🩸 흡혈!', `보스 체력 +${heal}`);\n      }\n    } else {""",
    """      if (enemy.lifestealOnHit && actual > 0) {\n        const heal = Math.floor(actual * enemy.lifestealOnHit);\n        enemy.hp = Math.min(enemy.maxHp, enemy.hp + heal);\n        await showAbility('🩸 흡혈!', `보스 체력 +${heal}`);\n      }\n      if (sword16ReflectActive) sword16ReflectActive = false;\n    } else {""",
    'boss reflect clear')

p.write_text(s,encoding='utf-8')
scripts=re.findall(r'<script(?:\\s[^>]*)?>(.*?)</script>',s,flags=re.S|re.I)
js='\n'.join(x for x in scripts if x.strip())
t=Path('/tmp/lr_tail_check.js');t.write_text(js,encoding='utf-8')
r=subprocess.run(['node','--check',str(t)],capture_output=True,text=True)
if r.returncode:
    print(r.stderr,file=sys.stderr);raise SystemExit(r.returncode)
print('tail cleanup PASS')

from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def rep(old,new,count=1):
    global s
    if old not in s:
        raise SystemExit('ANCHOR NOT FOUND:\n'+old[:300])
    s=s.replace(old,new,count)

# +16 reflection uses pending -> active semantics so skipped enemy turns do not consume it.
rep("let sword16ReflectEnemyTurn = -1;\nlet sword16DoubleNext = false;",
    "let sword16ReflectPending = false;\nlet sword16ReflectActive = false;\nlet sword16DoubleNext = false;")
rep("  sword16ReflectEnemyTurn = -1;\n  sword16DoubleNext = false;",
    "  sword16ReflectPending = false;\n  sword16ReflectActive = false;\n  sword16DoubleNext = false;")

# At the beginning of each player action, an already-consumed reflection is definitely over.
rep("async function beginSwordTranscendTurn() {\n  if (playerClass !== 'sword' || level < 11 || level > 20 || !enemy) return false;",
    "async function beginSwordTranscendTurn() {\n  if (playerClass !== 'sword' || level < 11 || level > 20 || !enemy) return false;\n  if (level === 16) sword16ReflectActive = false;")

# Numeric damage reflection only while an enemy attack is actually active.
rep("if (playerClass === 'sword' && level === 16 && sword16ReflectEnemyTurn === enemyTurnCount && Number(amount) > 0) {",
    "if (playerClass === 'sword' && level === 16 && sword16ReflectActive && Number(amount) > 0) {")

# Normal enemy flow: consume pending only after seal/paralyze early returns and once real attack logic begins.
rep("""  let enemyFallSelf = false;
  if (playerClass === 'sword' && level === 16 && sword16ReflectEnemyTurn === enemyTurnCount) {
    enemyFall = false;
    enemyFallSelf = true;
    await showAbility('🌙 월광봉멸 반사!', '상대의 공격과 능력을 그대로 반사!');
    addLog('ability', '월광봉멸: 상대 공격 반사');
  } else if (enemyFall) {""",
"""  let enemyFallSelf = false;
  if (playerClass === 'sword' && level === 16 && sword16ReflectPending) {
    sword16ReflectPending = false;
    sword16ReflectActive = true;
    enemyFall = false;
    enemyFallSelf = true;
    await showAbility('🌙 월광봉멸 반사!', '상대의 다음 실제 공격과 능력을 그대로 반사!');
    addLog('ability', '월광봉멸: 상대 실제 공격 1회 반사');
  } else if (enemyFall) {""")

# Boss flow occurs before the generic flow. Activate pending immediately before a real boss attack.
boss_anchor="""  if (gameMode === 'boss' && enemy && enemy.isBoss) {
    bossAttackCount++;"""
rep(boss_anchor,
"""  if (gameMode === 'boss' && enemy && enemy.isBoss) {
    if (playerClass === 'sword' && level === 16 && sword16ReflectPending) {
      sword16ReflectPending = false;
      sword16ReflectActive = true;
      await showAbility('🌙 월광봉멸 반사!', '보스의 다음 실제 공격을 그대로 반사!');
      addLog('ability', '월광봉멸: 보스 실제 공격 1회 반사');
    }
    bossAttackCount++;""")

# Skill arms the next real attack rather than a numbered enemy turn.
rep("sword16ReflectEnemyTurn = enemyTurnCount + 1;\n        sword16DoubleNext = true;",
    "sword16ReflectPending = true;\n        sword16ReflectActive = false;\n        sword16DoubleNext = true;")

# +14: checking boss immortality must be side-effect free. Do not call applyBossUndying here,
# because that helper already chips 40% max HP before the intended 65% fallback.
old="""        let instantSucceeded = false;
        if (rand() < 0.35) {
          if (await applyBossUndying('흑악신멸')) {
            instantSucceeded = false;
          } else {
            instantSucceeded = true;
            enemy.hp = 0;
            await playFx('kill');
            await showAbility('⚫ 흑악신멸!', '35% 신살 발동! 대상을 즉사시켰다!');
            addLog('ability', '흑악신멸: 즉사 성공');
          }
        }
        if (!instantSucceeded) {"""
new="""        let instantSucceeded = false;
        if (rand() < 0.35 && !bossIsUndying()) {
          instantSucceeded = true;
          enemy.hp = 0;
          await playFx('kill');
          await showAbility('⚫ 흑악신멸!', '35% 신살 발동! 대상을 즉사시켰다!');
          addLog('ability', '흑악신멸: 즉사 성공');
        }
        if (!instantSucceeded) {"""
rep(old,new)

# Sanity checks.
for bad in ['sword16ReflectEnemyTurn']:
    if bad in s:
        raise SystemExit('OLD REFLECTION STATE REMAINS: '+bad)
for good in [
    'let sword16ReflectPending = false;',
    'let sword16ReflectActive = false;',
    "rand() < 0.35 && !bossIsUndying()",
    'sword16ReflectPending = true;'
]:
    if good not in s:
        raise SystemExit('MISSING: '+good)

p.write_text(s,encoding='utf-8')
print('follow-up patched',len(s))

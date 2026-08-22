from pathlib import Path
import re, subprocess, sys

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def rep(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'patch target not found: {label}')
    s = s.replace(old, new, 1)

# 결과 화면 지연 재표시 방지
rep("""  const paint = () => {\n    try {\n      clearBattleOverlays();""",
    """  const paint = () => {\n    if (!battleEnded) return;\n    try {\n      clearBattleOverlays();""", 'result paint guard')

# 플레이어 -> 적 : 정화 대기 1회가 화염/마비/타락/저주도 동일하게 막도록 통일
rep("""  if (canAbility && !fallSelf && abilityW.fire && rand() < (abilityW.fireRate || 0.05)) {\n    if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '화염이 막혔다!');\n    } else {\n      fireTurns = 2;\n      await showAbility('🔥 화염 부여!', '2턴 화염! (현재HP 2% + 회복 반감)');\n    }\n  }""",
    """  if (canAbility && !fallSelf && abilityW.fire && rand() < (abilityW.fireRate || 0.05)) {\n    if (enemyPurifyNext) {\n      enemyPurifyNext = false;\n      await showAbility('✨ 적의 정화!', '화염이 무효화되었다!');\n      addLog('ability', '적 정화로 화염 무효');\n    } else if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '화염이 막혔다!');\n    } else {\n      fireTurns = 2;\n      await showAbility('🔥 화염 부여!', '2턴 화염! (현재HP 2% + 회복 반감)');\n    }\n  }""", 'enemy purify fire')

rep("""  if (canAbility && !fallSelf && abilityW.paralyze && rand() < abilityW.paralyze) {\n    if (enemyShield > 0) {\n      await showAbility('🛡️ 보호막!', '상태이상이 막혔다!');\n    } else if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '마비가 막혔다!');\n    } else {\n      enemyParalyzed = true;\n      await showAbility('💫 마비!', '상대 턴 스킵!');\n    }\n  }""",
    """  if (canAbility && !fallSelf && abilityW.paralyze && rand() < abilityW.paralyze) {\n    if (enemyShield > 0) {\n      await showAbility('🛡️ 보호막!', '상태이상이 막혔다!');\n    } else if (enemyPurifyNext) {\n      enemyPurifyNext = false;\n      await showAbility('✨ 적의 정화!', '마비가 무효화되었다!');\n      addLog('ability', '적 정화로 마비 무효');\n    } else if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '마비가 막혔다!');\n    } else {\n      enemyParalyzed = true;\n      await showAbility('💫 마비!', '상대 턴 스킵!');\n    }\n  }""", 'enemy purify paralyze')

rep("""  if (canAbility && !fallSelf && abilityW.fall && rand() < abilityW.fall) {\n    if (enemyShield > 0) {\n      await showAbility('🛡️ 보호막!', '상태이상이 막혔다!');\n    } else if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '타락이 막혔다!');\n    } else {\n      enemyFall = true;\n      await showAbility('😈 타락!', '다음 상대 공격이 반사!');\n    }\n  }""",
    """  if (canAbility && !fallSelf && abilityW.fall && rand() < abilityW.fall) {\n    if (enemyShield > 0) {\n      await showAbility('🛡️ 보호막!', '상태이상이 막혔다!');\n    } else if (enemyPurifyNext) {\n      enemyPurifyNext = false;\n      await showAbility('✨ 적의 정화!', '타락이 무효화되었다!');\n      addLog('ability', '적 정화로 타락 무효');\n    } else if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '타락이 막혔다!');\n    } else {\n      enemyFall = true;\n      await showAbility('😈 타락!', '다음 상대 공격이 반사!');\n    }\n  }""", 'enemy purify fall')

rep("""  if (canAbility && !fallSelf && abilityW.curse && rand() < abilityW.curse) {\n    if (enemyShield > 0) {\n      await showAbility('🛡️ 보호막!', '상태이상이 막혔다!');\n    } else if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '저주가 막혔다!');\n    } else if (enemyCursed >= 2) {""",
    """  if (canAbility && !fallSelf && abilityW.curse && rand() < abilityW.curse) {\n    if (enemyShield > 0) {\n      await showAbility('🛡️ 보호막!', '상태이상이 막혔다!');\n    } else if (enemyPurifyNext) {\n      enemyPurifyNext = false;\n      await showAbility('✨ 적의 정화!', '저주가 무효화되었다!');\n      addLog('ability', '적 정화로 저주 무효');\n    } else if (hasNullify(false)) {\n      await showAbility('💧 적의 능력 무효!', '저주가 막혔다!');\n    } else if (enemyCursed >= 2) {""", 'enemy purify curse')

# 적 자신의 정화도 플레이어와 같은 범위를 제거
rep("""  if (canAbility && abilityW.purify && rand() < abilityW.purify) {\n    if (enemyFall || enemyCursed) {\n      enemyFall = false; enemyCursed = 0;\n      await showAbility('✨ 적의 정화!', '상태이상 제거');\n    } else {\n      enemyPurifyNext = true;\n      await showAbility('✨ 적의 정화!', '다음 내 능력 무시');\n    }\n  }""",
    """  if (canAbility && abilityW.purify && rand() < abilityW.purify) {\n    const enemyHasStatus = enemyParalyzed || enemyFall || enemyCursed > 0 || enemySealed || fireTurns > 0;\n    if (enemyHasStatus) {\n      enemyParalyzed = false; enemyFall = false; enemyCursed = 0; enemySealed = false; fireTurns = 0;\n      await showAbility('✨ 적의 정화!', '걸려 있던 상태이상을 모두 제거했다!');\n      addLog('ability', '적 정화: 상태이상 제거');\n    } else {\n      enemyPurifyNext = true;\n      await showAbility('✨ 적의 정화!', '다음 상태이상·부패 1회를 무효화');\n    }\n  }""", 'enemy self purify')

# 적 -> 플레이어 : 정화를 실제로 사용했을 때 바로 소모
for label, old, new in [
('player purify fall', """    } else if (playerPurifyNext) {\n      await showAbility('✨ 정화 발동!', '적의 타락을 무효화했다!');\n      addLog('ability', '정화로 타락 무효');""", """    } else if (playerPurifyNext) {\n      playerPurifyNext = false;\n      await showAbility('✨ 정화 발동!', '적의 타락을 무효화했다!');\n      addLog('ability', '정화로 타락 무효');"""),
('player purify paralyze', """    } else if (playerPurifyNext) {\n      await showAbility('✨ 정화 발동!', '적의 마비를 무효화했다!');\n      addLog('ability', '정화로 마비 무효');""", """    } else if (playerPurifyNext) {\n      playerPurifyNext = false;\n      await showAbility('✨ 정화 발동!', '적의 마비를 무효화했다!');\n      addLog('ability', '정화로 마비 무효');"""),
('player purify curse', """    } else if (playerPurifyNext) {\n      await showAbility('✨ 정화 발동!', '적의 저주를 무효화했다!');\n      addLog('ability', '정화로 저주 무효');""", """    } else if (playerPurifyNext) {\n      playerPurifyNext = false;\n      await showAbility('✨ 정화 발동!', '적의 저주를 무효화했다!');\n      addLog('ability', '정화로 저주 무효');"""),
('player purify corrupt', """      if (playerPurifyNext) {\n        await showAbility('✨ 정화 발동!', '적의 부패를 무효화했다!');\n        addLog('ability', '정화로 부패 무효');""", """      if (playerPurifyNext) {\n        playerPurifyNext = false;\n        await showAbility('✨ 정화 발동!', '적의 부패를 무효화했다!');\n        addLog('ability', '정화로 부패 무효');""")]:
    rep(old, new, label)

rep("""  if (canAbility && abilityW.fire && rand() < (abilityW.fireRate || 0.05)) {\n    if (hasNullify(true)) {\n      await showAbility('💧 능력 무효!', '신의 눈물이 화염을 무효화!');\n    } else {\n      enemy.fireTurns = 2;\n      await showAbility('🔥 적의 화염 부여!', '2턴 화염! (현재HP 2% + 회복 반감)');\n    }\n  }""",
    """  if (canAbility && !enemyFallSelf && abilityW.fire && rand() < (abilityW.fireRate || 0.05)) {\n    if (playerPurifyNext) {\n      playerPurifyNext = false;\n      await showAbility('✨ 정화 발동!', '적의 화염을 무효화했다!');\n      addLog('ability', '정화로 화염 무효');\n    } else if (hasNullify(true)) {\n      await showAbility('💧 능력 무효!', '신의 눈물이 화염을 무효화!');\n    } else {\n      enemy.fireTurns = 2;\n      await showAbility('🔥 적의 화염 부여!', '2턴 화염! (현재HP 2% + 회복 반감)');\n    }\n  }""", 'player purify fire')

rep("""  if (playerPurifyNext) {\n    playerPurifyNext = false;\n    addLog('ability', '정화 효과가 소모되었다');\n  }\n\n  // 적 화염 도트 (플레이어에게 걸린 화염)""",
    """  // 정화 대기는 실제 상태이상/부패를 막았을 때만 소모된다.\n\n  // 적 화염 도트 (플레이어에게 걸린 화염)""", 'purify expiry')

# 월광봉멸/타락 반사 : 즉사, 봉인, 초신성도 공격자에게 되돌림
rep("""      await playFx(isCham ? 'chamgyeok' : 'kill');\n      if (playerHasImmortality()) {""",
    """      await playFx(isCham ? 'chamgyeok' : 'kill');\n      if (enemyFallSelf) {\n        enemy.hp = 0;\n        await showAbility('🌙 반사된 즉사!', '상대의 즉사 효과가 자신에게 되돌아갔다!');\n        addLog('ability', '월광봉멸/타락: 즉사 효과 반사');\n        updateHPBars();\n        if (await resolveEnemyDeathFromMageSkill('반사된 즉사')) return;\n        sword16ReflectActive = false;\n        $('atk-btn').disabled = false;\n        if (autoMode) scheduleAutoAttack(400);\n        return;\n      } else if (playerHasImmortality()) {""", 'reflect instant')

rep("""  if (canAbility && abilityW.seal && rand() < abilityW.seal) {\n    await playFx('seal');\n    await showAbility('🔒 적의 봉인!', '봉인 당했다!');\n    hp = 0;""",
    """  if (canAbility && abilityW.seal && rand() < abilityW.seal) {\n    await playFx('seal');\n    if (enemyFallSelf) {\n      enemy.hp = 0;\n      await showAbility('🌙 반사된 봉인!', '상대의 봉인이 자신에게 되돌아갔다!');\n      addLog('ability', '월광봉멸/타락: 봉인 반사 · 즉사');\n      updateHPBars();\n      endBattle(true, '반사된 봉인');\n      return;\n    }\n    await showAbility('🔒 적의 봉인!', '봉인 당했다!');\n    hp = 0;""", 'reflect seal')

rep("""  if (canAbility && abilityW.instantCond && enemy.hp < enemy.maxHp * 0.6 && rand() < abilityW.instantCond) {\n    await playFx('supernova');\n    if (playerHasImmortality()) {""",
    """  if (canAbility && abilityW.instantCond && enemy.hp < enemy.maxHp * 0.6 && rand() < abilityW.instantCond) {\n    await playFx('supernova');\n    if (enemyFallSelf) {\n      enemy.hp = 0;\n      await showAbility('🌙 반사된 초신성!', '초신성 즉사가 공격자에게 되돌아갔다!');\n      addLog('ability', '월광봉멸/타락: 초신성 반사');\n      updateHPBars();\n      if (await resolveEnemyDeathFromMageSkill('반사된 초신성')) return;\n      sword16ReflectActive = false;\n      $('atk-btn').disabled = false;\n      if (autoMode) scheduleAutoAttack(400);\n      return;\n    }\n    if (playerHasImmortality()) {""", 'reflect supernova')

# 반사 중에는 흡수/몰락/상태이상이 플레이어에게 새지 않게 함
rep("if (canAbility && abilityW.absorb) {", "if (canAbility && !enemyFallSelf && abilityW.absorb) {", 'reflect absorb')
rep("if (canAbility && abilityW.halfkill && rand() < abilityW.halfkill) {", "if (canAbility && !enemyFallSelf && abilityW.halfkill && rand() < abilityW.halfkill) {", 'reflect halfkill')
rep("if (canAbility && abilityW.curse && rand() < abilityW.curse) {", "if (canAbility && !enemyFallSelf && abilityW.curse && rand() < abilityW.curse) {", 'reflect curse')

needle = """  if (canAbility && !enemyMirroringThisTurn && abilityW.mirror && rand() < abilityW.mirror) {\n    enemyMirror = true;\n    await showAbility('🪞 적의 미러링 준비!', '다음 적 공격에 내 능력!');\n  }\n  if (canAbility && abilityW.lifesteal) {"""
insert = """  if (canAbility && enemyFallSelf) {\n    if (abilityW.paralyze && rand() < abilityW.paralyze) { enemyParalyzed = true; addLog('ability', '반사: 적에게 마비'); }\n    if (abilityW.fall && rand() < abilityW.fall) { enemyFall = true; addLog('ability', '반사: 적에게 타락'); }\n    if (abilityW.fire && rand() < (abilityW.fireRate || 0.05)) { fireTurns = 2; addLog('ability', '반사: 적에게 화염'); }\n    if (abilityW.curse && rand() < abilityW.curse && enemyCursed < 2) { enemyCursed++; addLog('ability', `반사: 적에게 저주 ${enemyCursed}중첩`); }\n  }\n  if (canAbility && !enemyMirroringThisTurn && abilityW.mirror && rand() < abilityW.mirror) {\n    enemyMirror = true;\n    await showAbility('🪞 적의 미러링 준비!', '다음 적 공격에 내 능력!');\n  }\n  if (canAbility && abilityW.lifesteal) {"""
rep(needle, insert, 'reflected statuses')

rep("""  if (enemyFallSelf) {\n    dmgEnemy(dmg);\n    addLog('enemy', `타락 반사! 적에게 ${dmg}`);""",
    """  if (enemyFallSelf) {\n    const reflected1 = dmgEnemy(dmg);\n    addLog('enemy', `반사! 적에게 ${reflected1}`);\n    if (enemyDoubleHit && enemy.hp > 0) {\n      const reflected2 = dmgEnemy(dmg);\n      addLog('enemy', `반사 이중 2타! 적에게 ${reflected2}`);\n    }""", 'reflect double')

# 이벤트 보스의 마비도 월광봉멸 반사 시 보스에게 되돌림
rep("""    if (enemy.paralyze && rand() < enemy.paralyze) {\n      if (playerShield > 0) {""",
    """    if (enemy.paralyze && rand() < enemy.paralyze) {\n      if (sword16ReflectActive) {\n        enemyParalyzed = true;\n        await showAbility('🌙 월광봉멸 반사!', '보스의 마비 효과까지 되돌려 보냈다!');\n        addLog('ability', '월광봉멸: 보스 마비 반사');\n      } else if (playerShield > 0) {""", 'boss paralyze reflect')

p.write_text(s, encoding='utf-8')

# JS 문법 검사
scripts = re.findall(r'<script(?:\\s[^>]*)?>(.*?)</script>', s, flags=re.S|re.I)
js = '\n'.join(x for x in scripts if x.strip())
tmp = Path('/tmp/lr_check.js')
tmp.write_text(js, encoding='utf-8')
proc = subprocess.run(['node','--check',str(tmp)], capture_output=True, text=True)
if proc.returncode != 0:
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)
    raise SystemExit(proc.returncode)
print('combat cleanup patch PASS')

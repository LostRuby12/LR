from pathlib import Path
p = Path('index.html')
s = p.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 got {n}')
    s=s.replace(old,new,1)

# 스킬은 자동전투 중 수동으로 끼어들지 못하게 해 턴 중복 방지
rep(
"  if (!info || battleEnded || playerAttackLock || rtActive) return false;",
"  if (!info || battleEnded || playerAttackLock || rtActive || autoMode) return false;",
'auto skill guard')
rep(
"  } else if (playerCursed > 0) {\n    status = '저주로 스킬 사용 불가';\n  } else if (upcomingTurn >= mageSkillNextReadyTurn) {",
"  } else if (playerCursed > 0) {\n    status = '저주로 스킬 사용 불가';\n  } else if (autoMode) {\n    status = '자동전투 중에는 스킬 사용 불가';\n  } else if (upcomingTurn >= mageSkillNextReadyTurn) {",
'auto skill status')

# 균열은 보호막/정화는 무시하지만 능력무효 자체까지 관통하지는 않음
rep(
"""  if (canAbility && !fallSelf && abilityW.rift && rand() < abilityW.rift) {
    riftThisTurn = true;
    dmg *= 2;
    await showAbility('🕳️ 균열!', `공격 데미지 2배 (${dmg}) · 보호막/정화 무시!`);
    addLog('ability', `균열 발동: ${dmg} 데미지`);
  }""",
"""  if (canAbility && !fallSelf && abilityW.rift && rand() < abilityW.rift) {
    if (hasNullify(false)) {
      await showAbility('💧 적의 능력 무효!', '균열이 능력 무효에 막혔다!');
      addLog('ability', '균열 발동 실패: 능력 무효');
    } else {
      riftThisTurn = true;
      dmg *= 2;
      await showAbility('🕳️ 균열!', `공격 데미지 2배 (${dmg}) · 보호막/정화 무시!`);
      addLog('ability', `균열 발동: ${dmg} 데미지`);
    }
  }""",
'rift nullify semantics')

# 천지창조로 재구성한 무기는 기존 강화 무기의 자동 각성/보호막을 다시 참조하지 않음
rep(
"""      const base = getWeapon(enemy.class, enemy.level, false, null);
      return !!(base && base.shield);""",
"""      const base = enemy.creationLocked
        ? (enemy.weapon || {})
        : getWeapon(enemy.class, enemy.level, false, null);
      return !!(base && base.shield);""",
'creation shield source')
rep(
"  let baseEW = getWeapon(enemy.class, enemy.level, false, null);",
"  let baseEW = enemy && enemy.creationLocked ? (enemy.weapon || {}) : getWeapon(enemy.class, enemy.level, false, null);",
'creation awakening source')

# 천지창조의 강화레벨 변경은 게임의 +100 HP/강 규칙까지 반영. 현재 HP는 새 최대HP까지만 보존.
rep(
"""    enemy.level = newLv;
    enemy.atk = newAtk;
    enemy.weapon = newWeapon;
    enemyAwakened = false;
    enemyAwakenType = null;
    enemy.double = 0;
    enemy.paralyze = 0;
    enemy.lifestealOnHit = 0;
    if ($('e-weapon')) $('e-weapon').textContent = `${newWeapon.name} +${newLv}`;
    if ($('e-desc')) $('e-desc').textContent = newWeapon.desc;
    await showAbility('🌌 천지창조!', `상대를 +${newLv} · 공격력 ${newAtk} · ${newWeapon.desc} 로 재구성!`);
    addLog('ability', `천지창조: 상대 +${newLv}, ATK ${newAtk}, ${newWeapon.desc}`);""",
"""    enemy.level = newLv;
    enemy.atk = newAtk;
    enemy.weapon = newWeapon;
    enemy.creationLocked = true;
    const rebuiltMaxHp = getBaseHp(enemy.class) + newLv * 100;
    enemy.maxHp = Math.max(1, rebuiltMaxHp);
    enemy.hp = clamp(Number(enemy.hp) || 0, 0, enemy.maxHp);
    enemyAwakened = false;
    enemyAwakenType = null;
    enemyExcalTurns = 0;
    enemyLastStandUsed = false;
    enemyShield = 0;
    enemyShieldUsed = false;
    enemyPurifyNext = false;
    enemy.double = 0;
    enemy.paralyze = 0;
    enemy.lifestealOnHit = 0;
    if ($('e-weapon')) $('e-weapon').textContent = `${newWeapon.name} +${newLv}`;
    if ($('e-desc')) $('e-desc').textContent = newWeapon.desc;
    await showAbility('🌌 천지창조!', `상대를 +${newLv} · 최대HP ${enemy.maxHp} · 공격력 ${newAtk} · ${newWeapon.desc} 로 재구성!`);
    addLog('ability', `천지창조: 상대 +${newLv}, MaxHP ${enemy.maxHp}, ATK ${newAtk}, ${newWeapon.desc}`);
    updateHPBars();
    updateStatusIcons();""",
'creation rebuild')

p.write_text(s,encoding='utf-8')
print('follow-up applied')

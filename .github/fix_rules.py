from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'NOT FOUND: {label}')
    s = s.replace(old, new, 1)
    print('patched:', label)


def sub_once(pattern, repl, label, flags=0):
    global s
    s2, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'REGEX {label}: expected 1, got {n}')
    s = s2
    print('patched:', label)

# --- descriptions / rules ---
replace_once(
"11: Object.freeze({ name: '천명의 신검', atk: 85, heavenlyMandate: true, desc: '패시브 「천명」 · 3턴 신의 명령(공격 데미지 +30%) · 6턴 신의 하사(보호막 200) · 9턴 천명(즉사)' }),",
"11: Object.freeze({ name: '천명의 신검', atk: 85, heavenlyMandate: true, desc: '패시브 「천명」 · 8턴 신의 명령(공격 데미지 +30%) · 16턴 신의 하사(보호막 200) · 24턴 천명(즉사)' }),",
'천명 설명 8/16/24')
replace_once(
"12: Object.freeze({ name: '참살쇄도', atk: 105, slashRush: true, desc: '5번째 턴 「참살쇄도」 1회(공격력 70%×3) · 10번째 턴 「휘몰아치는 칼날」 1회(공격력 250%)' }),",
"12: Object.freeze({ name: '참살쇄도', atk: 105, slashRush: true, desc: '5번째 턴부터 「참살쇄도」 1회(공격력 70%×3) · 10번째 턴부터 「휘몰아치는 칼날」 1회(공격력 250%)' }),",
'참살쇄도 설명')
replace_once(
"19: Object.freeze({ name: '불멸의 무라마사', atk: 420, muramasaBurn: 0.02, immortalRevives: 3, desc: '공격 후 상대 현재 체력 2% 화상 · 패시브 「불멸」 최대 체력 75%로 3회 부활' }),",
"19: Object.freeze({ name: '불멸의 무라마사', atk: 420, muramasaBurn: 0.02, immortalRevives: 3, desc: '공격 후 상대 현재 체력 2% 화상 · 패시브 「불멸」 일반 즉사계열은 1 피해로 무효(종언·소멸·봉인 제외) · 최대 체력 75%로 3회 부활' }),",
'무라마사 불멸 설명')
replace_once(
"desc: '불사(즉사→최대HP40%피해, 봉인관통) · 흡혈20% · 3턴마다 살상돌격'",
"desc: '불사(일반 즉사계열→1피해, 종언·소멸·봉인 관통) · 흡혈20% · 3턴마다 살상돌격'",
'라아스트 불사 설명')

# --- immortality helpers ---
sub_once(
r"function bossIsUndying\(\) \{\n  return !!\(gameMode === 'boss' && enemy && \(enemy\.undying === true \|\| enemy\.name === '다르킨의 낫'\)\);\n\}\n\n/\*\* 즉사류를 불사로 흡수\. true면 즉사 무효 처리됨 \*/\nasync function applyBossUndying\(sourceLabel\) \{.*?\n\}\n\nasync function tryBossTransform",
"""function bossIsUndying() {
  return !!(gameMode === 'boss' && enemy && (enemy.undying === true || enemy.name === '다르킨의 낫'));
}

/** 불사: 일반 즉사계열을 1 피해로 바꾼다. 종언·소멸·봉인은 이 함수를 호출하지 않고 관통한다. */
async function applyBossUndying(sourceLabel) {
  if (!bossIsUndying()) return false;
  const before = Math.max(1, Number(enemy.hp) || Number(enemy.maxHp) || 1);
  enemy.hp = Math.max(1, before - 1);
  enemy.undying = true;
  await showAbility('♾️ 불사!', (sourceLabel || '즉사') + ' 무효! 즉사 피해가 1로 변환 (' + before + '→' + enemy.hp + ')');
  addLog('ability', '불사: ' + (sourceLabel || '즉사') + ' 무효, 1 피해 (' + before + '→' + enemy.hp + ')');
  updateHPBars();
  updateStatusIcons();
  return true;
}

function playerHasImmortality() {
  return playerClass === 'sword' && level === 19;
}

/** 무라마사의 불멸: 일반 즉사계열을 1 피해로 바꾼다. */
async function applyPlayerImmortality(sourceLabel) {
  if (!playerHasImmortality()) return false;
  const before = Math.max(1, Number(hp) || Number(maxHp) || 1);
  hp = Math.max(1, before - 1);
  await showAbility('♾️ 불멸!', (sourceLabel || '즉사') + ' 무효! 즉사 피해가 1로 변환 (' + before + '→' + hp + ')');
  addLog('ability', '불멸: ' + (sourceLabel || '즉사') + ' 무효, 1 피해 (' + before + '→' + hp + ')');
  updateHPBars();
  updateStatusIcons();
  return true;
}

async function tryBossTransform""",
'immortality helpers', flags=re.S)

# --- heavenly mandate turns ---
replace_once("playerTurnCount === 3 && !sword11DamageBuff", "playerTurnCount === 8 && !sword11DamageBuff", '천명 1단계 턴')
replace_once("playerTurnCount === 6 && !sword11ShieldGranted", "playerTurnCount === 16 && !sword11ShieldGranted", '천명 2단계 턴')
replace_once("playerTurnCount === 9 && !sword11DestinyUsed", "playerTurnCount === 24 && !sword11DestinyUsed", '천명 3단계 턴')

old_mandate = """    if (playerTurnCount === 24 && !sword11DestinyUsed && enemy.hp > 0) {
      sword11DestinyUsed = true;
      enemy.hp = 0;
      await playFx('kill');
      await showAbility('👑 천명', '신의 뜻으로 대상을 즉사시켰다!');
      addLog('ability', '천명 3단계: 대상 즉사');
      updateHPBars();
      if (await resolveEnemyDeathFromMageSkill('천명')) return true;
    }"""
new_mandate = """    if (playerTurnCount === 24 && !sword11DestinyUsed && enemy.hp > 0) {
      sword11DestinyUsed = true;
      if (await applyBossUndying('천명')) {
        addLog('ability', '천명 3단계: 불사로 즉사가 1 피해로 변환');
      } else {
        enemy.hp = 0;
        await playFx('kill');
        await showAbility('👑 천명', '신의 뜻으로 대상을 즉사시켰다!');
        addLog('ability', '천명 3단계: 대상 즉사');
        updateHPBars();
        if (await resolveEnemyDeathFromMageSkill('천명')) return true;
      }
    }"""
replace_once(old_mandate, new_mandate, '천명 vs 불사')

# --- +12: unlock on/after turn instead of exact-turn disappearance ---
old_slash_info = """    if (level === 12) {
      if (!sword12SlashUsed && upcomingTurn <= 5) return { name: '참살쇄도', cooldown: 0, icon: '⚔️', exactTurn: 5 };
      if (!sword12TornadoUsed && upcomingTurn <= 10) return { name: '휘몰아치는 칼날', cooldown: 0, icon: '🌪️', exactTurn: 10 };
      return null;
    }"""
new_slash_info = """    if (level === 12) {
      if (!sword12SlashUsed) return { name: '참살쇄도', cooldown: 0, icon: '⚔️', unlockTurn: 5 };
      if (!sword12TornadoUsed) return { name: '휘몰아치는 칼날', cooldown: 0, icon: '🌪️', unlockTurn: 10 };
      return null;
    }"""
replace_once(old_slash_info, new_slash_info, '참살쇄도 해금 방식')
replace_once("if (info.exactTurn != null) return upcomingTurn === info.exactTurn;", "if (info.unlockTurn != null) return upcomingTurn >= info.unlockTurn;", '스킬 사용 가능 판정')
old_skill_status = """  } else if (info.exactTurn != null && upcomingTurn < info.exactTurn) {
    status = `자신의 ${info.exactTurn}번째 턴에 1회 사용 가능`;
  } else if (info.exactTurn != null && upcomingTurn > info.exactTurn) {
    status = '해당 스킬 사용 가능 턴이 지났습니다';
  } else if (playerParalyzed || playerSealed) {"""
new_skill_status = """  } else if (info.unlockTurn != null && upcomingTurn < info.unlockTurn) {
    status = `자신의 ${info.unlockTurn}번째 턴부터 1회 사용 가능`;
  } else if (playerParalyzed || playerSealed) {"""
replace_once(old_skill_status, new_skill_status, '참살쇄도 상태 문구')

# --- +17 봉인은 즉사 ---
replace_once(
"if (rand() < 0.04) { playerSealed = true; triggered.push('봉인'); }",
"if (rand() < 0.04) { hp = 0; triggered.push('봉인(즉사)'); }",
'마검의 저항 봉인 즉사')

# +19 icon remains visible after revive charges are exhausted because instant immunity remains.
replace_once(
"if (playerClass === 'sword' && level === 19 && sword19RevivesLeft > 0) pIcons.push(`♾️불멸x${sword19RevivesLeft}`);",
"if (playerClass === 'sword' && level === 19) pIcons.push(`♾️불멸 · 부활x${sword19RevivesLeft}`);",
'불멸 상태 아이콘')

# +19 revival must not protect the explicit immortality-piercing instant types.
old_revive = """  if (level === 19 && sword19RevivesLeft > 0) {
    sword19RevivesLeft--;"""
new_revive = """  if (level === 19 && sword19RevivesLeft > 0) {
    if (/봉인|종언/.test(String(reason || ''))) return false;
    sword19RevivesLeft--;"""
replace_once(old_revive, new_revive, '불멸 관통 예외')

# --- +14 black god slayer: successful instant vs immortal = 1 damage, not 65% fallback ---
old_black = """      } else if (level === 14) {
        let instantSucceeded = false;
        if (rand() < 0.35 && !bossIsUndying()) {
          instantSucceeded = true;
          enemy.hp = 0;
          await playFx('kill');
          await showAbility('⚫ 흑악신멸!', '35% 신살 발동! 대상을 즉사시켰다!');
          addLog('ability', '흑악신멸: 즉사 성공');
        }
        if (!instantSucceeded) {
          const raw = Math.max(1, Math.floor(enemy.maxHp * 0.65));
          const actual = dmgEnemy(raw);
          await showAbility('⚫ 흑악신멸!', `즉사 불발 → 상대 최대 체력 65% · ${actual} 피해!`);
          addLog('ability', `흑악신멸 대체 피해: ${actual}`);
        }
"""
new_black = """      } else if (level === 14) {
        const instantRolled = rand() < 0.35;
        if (instantRolled) {
          if (await applyBossUndying('흑악신멸')) {
            addLog('ability', '흑악신멸: 즉사 성공 판정 → 불사로 1 피해');
          } else {
            enemy.hp = 0;
            await playFx('kill');
            await showAbility('⚫ 흑악신멸!', '35% 신살 발동! 대상을 즉사시켰다!');
            addLog('ability', '흑악신멸: 즉사 성공');
          }
        } else {
          const raw = Math.max(1, Math.floor(enemy.maxHp * 0.65));
          const actual = dmgEnemy(raw);
          await showAbility('⚫ 흑악신멸!', `즉사 불발 → 상대 최대 체력 65% · ${actual} 피해!`);
          addLog('ability', `흑악신멸 대체 피해: ${actual}`);
        }
"""
replace_once(old_black, new_black, '흑악신멸 불사 처리')

# --- incoming ordinary instant vs +19 immortality ---
old_instant_shield = """      if (playerShield > 0) {
        await showAbility('🛡️ 보호막 방어!', `즉사를 막았다! (보호막 ${playerShield} 소모)`);
        playerShield = 0;
        updateStatusIcons();
      } else {
      await showAbility(isCham ? '⚔️ 적의 세계를 가르는 참격!' : '⚔️ 적의 즉사!', '즉사 당했다...');"""
new_instant_shield = """      if (playerHasImmortality()) {
        await applyPlayerImmortality(isCham ? '참격' : '즉사');
        $('atk-btn').disabled = false;
        if (autoMode) scheduleAutoAttack(400);
        return;
      } else if (playerShield > 0) {
        await showAbility('🛡️ 보호막 방어!', `즉사를 막았다! (보호막 ${playerShield} 소모)`);
        playerShield = 0;
        updateStatusIcons();
      } else {
      await showAbility(isCham ? '⚔️ 적의 세계를 가르는 참격!' : '⚔️ 적의 즉사!', '즉사 당했다...');"""
replace_once(old_instant_shield, new_instant_shield, '무라마사 일반 즉사 면역')

old_supernova = """  if (canAbility && abilityW.instantCond && enemy.hp < enemy.maxHp * 0.6 && rand() < abilityW.instantCond) {
    await playFx('supernova');
    await showAbility('💥 적의 초신성 폭발!', '체력 60% 미만 즉사!');
    hp = 0;"""
new_supernova = """  if (canAbility && abilityW.instantCond && enemy.hp < enemy.maxHp * 0.6 && rand() < abilityW.instantCond) {
    await playFx('supernova');
    if (playerHasImmortality()) {
      await applyPlayerImmortality('초신성');
      $('atk-btn').disabled = false;
      if (autoMode) scheduleAutoAttack(400);
      return;
    }
    await showAbility('💥 적의 초신성 폭발!', '체력 60% 미만 즉사!');
    hp = 0;"""
replace_once(old_supernova, new_supernova, '무라마사 초신성 면역')

# Sanity checks
assert "playerTurnCount === 8 && !sword11DamageBuff" in s
assert "playerTurnCount === 16 && !sword11ShieldGranted" in s
assert "playerTurnCount === 24 && !sword11DestinyUsed" in s
assert "unlockTurn: 5" in s and "unlockTurn: 10" in s
assert "봉인(즉사)" in s
assert "즉사 피해가 1로 변환" in s
assert "일반 즉사계열은 1 피해로 무효" in s
assert "즉사→최대HP40%피해" not in s

p.write_text(s, encoding='utf-8')
print('all combat rule patches applied')

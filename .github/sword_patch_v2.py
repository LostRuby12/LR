from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def rep(old, new, count=1):
    global s
    if old not in s:
        raise SystemExit('ANCHOR NOT FOUND:\n' + old[:260])
    s = s.replace(old, new, count)


def rx(pattern, repl, count=1, flags=re.S):
    global s
    s2, n = re.subn(pattern, repl, s, count=count, flags=flags)
    if n != count:
        raise SystemExit(f'REGEX FAILED ({n}/{count}): {pattern[:220]}')
    s = s2


# ------------------------------------------------------------------
# 1. Sword +11~+20 dedicated weapon data
# ------------------------------------------------------------------
if 'const SWORD_TRANSCEND_WEAPONS = Object.freeze({' not in s:
    sword_data = """const SWORD_TRANSCEND_WEAPONS = Object.freeze({
  11: Object.freeze({ name: '천명의 신검', atk: 85, heavenlyMandate: true, desc: '패시브 「천명」 · 3턴 신의 명령(공격 데미지 +30%) · 6턴 신의 하사(보호막 200) · 9턴 천명(즉사)' }),
  12: Object.freeze({ name: '참살쇄도', atk: 105, slashRush: true, desc: '5번째 턴 「참살쇄도」 1회(공격력 70%×3) · 10번째 턴 「휘몰아치는 칼날」 1회(공격력 250%)' }),
  13: Object.freeze({ name: '안슐루스', atk: 130, annexation: 0.05, desc: '패시브 「합병」 · 자신의 턴마다 상대 현재 체력 5% 흡수 → 같은 양 보호막' }),
  14: Object.freeze({ name: '신살흑도', atk: 145, blackGodSlayer: true, desc: '스킬 「흑악신멸」 · 4턴마다 · 35% 즉사 · 즉사 불발 시 상대 최대 체력 65% 피해' }),
  15: Object.freeze({ name: '적월도', atk: 180, redMoonMadness: true, desc: '패시브 「적월의 광기」 · 잃은 체력 1%당 공격 데미지 +1% (최대 +100%)' }),
  16: Object.freeze({ name: '명월도', atk: 200, moonSeal: true, desc: '스킬 「월광봉멸」 · 3턴마다 · 다음 상대 공격 반사 · 다음 내 공격 2연타 · 15% 봉인' }),
  17: Object.freeze({ name: '마검 데스티니', atk: 225, demonResistance: true, demonEye: true, desc: '패시브 「마검의 저항」 · 매 자신의 턴 부패/타락/저주/봉인/즉사 각각 4% 자기 발동 · 「마검의 눈」 사망 후 공격 3회까지 불사' }),
  18: Object.freeze({ name: '진·엑스칼리버', atk: 300, instant: 0.65, transcendLastStand: 2, desc: '일반 공격마다 즉사 65% · 최후의 저항 2회' }),
  19: Object.freeze({ name: '불멸의 무라마사', atk: 420, muramasaBurn: 0.02, immortalRevives: 3, desc: '공격 후 상대 현재 체력 2% 화상 · 패시브 「불멸」 최대 체력 75%로 3회 부활' }),
  20: Object.freeze({ name: '살신명도·종언', atk: 500, endingSkill: true, desc: '자신의 2번째 턴부터 전투당 1회 스킬 「종언」 · 50% 반드시 즉사 · 불발 시 10,000 피해' })
});

"""
    rep('const MAGE_TRANSCEND_WEAPONS = Object.freeze({', sword_data + 'const MAGE_TRANSCEND_WEAPONS = Object.freeze({')

# getWeapon: remove inherited +10 sword and automatic +10% scaling
rx(
    r"  const weapon = Object\.assign\(\{\}, list\[Math\.min\(lv - 1, 9\)\]\);\n"
    r"  if \(lv > 10 && cls === 'sword'\) \{.*?\n  \}\n  return weapon;",
    """  if (lv > 10 && cls === 'sword') {
    const t = SWORD_TRANSCEND_WEAPONS[Math.min(20, Math.max(11, lv))];
    return Object.assign({}, t);
  }
  const weapon = Object.assign({}, list[Math.min(lv - 1, 9)]);
  return weapon;"""
)

# ------------------------------------------------------------------
# 2. Battle state
# ------------------------------------------------------------------
if 'let sword11DamageBuff = false;' not in s:
    rep(
        "let mage20SkillUsed = false;\n\n// 이벤트(구 보스전)",
        """let mage20SkillUsed = false;

// 검사 +11~+20 초월 전투 상태
let sword11DamageBuff = false;
let sword11ShieldGranted = false;
let sword11DestinyUsed = false;
let sword12SlashUsed = false;
let sword12TornadoUsed = false;
let sword16ReflectEnemyTurn = -1;
let sword16DoubleNext = false;
let sword17DeathEyeActive = false;
let sword17DeathEyeUsed = false;
let sword17DeathEyeAttacksLeft = 0;
let sword18LastStandLeft = 0;
let sword19RevivesLeft = 0;
let sword20SkillUsed = false;

// 이벤트(구 보스전)"""
    )

# status icons
if "pIcons.push('👑신의명령+30%')" not in s:
    rep(
        "  if (playerClass === 'mage' && level === 19 && mage19RewindCharges > 0) pIcons.push(`⏪회귀x${mage19RewindCharges}`);\n",
        """  if (playerClass === 'mage' && level === 19 && mage19RewindCharges > 0) pIcons.push(`⏪회귀x${mage19RewindCharges}`);
  if (playerClass === 'sword' && level === 11 && sword11DamageBuff) pIcons.push('👑신의명령+30%');
  if (playerClass === 'sword' && level === 15) {
    const madnessPct = maxHp > 0 ? Math.round(Math.max(0, Math.min(1, (maxHp - Math.max(0, hp)) / maxHp)) * 100) : 0;
    if (madnessPct > 0) pIcons.push(`🌙광기+${madnessPct}%`);
  }
  if (playerClass === 'sword' && level === 17 && sword17DeathEyeActive) pIcons.push(`👁️마검의눈${sword17DeathEyeAttacksLeft}`);
  if (playerClass === 'sword' && level === 18 && sword18LastStandLeft > 0) pIcons.push(`⚔️저항x${sword18LastStandLeft}`);
  if (playerClass === 'sword' && level === 19 && sword19RevivesLeft > 0) pIcons.push(`♾️불멸x${sword19RevivesLeft}`);
"""
    )

# reset function block
m = re.search(r"function resetMageTranscendBattleState\(\) \{.*?\n\}\n\nfunction mageActiveSkillInfo", s, re.S)
if not m:
    raise SystemExit('resetMageTranscendBattleState block not found')
block = m.group(0)
if 'sword11DamageBuff = false;' not in block:
    block = block.replace(
        '  mage20SkillUsed = false;\n',
        """  mage20SkillUsed = false;
  sword11DamageBuff = false;
  sword11ShieldGranted = false;
  sword11DestinyUsed = false;
  sword12SlashUsed = false;
  sword12TornadoUsed = false;
  sword16ReflectEnemyTurn = -1;
  sword16DoubleNext = false;
  sword17DeathEyeActive = false;
  sword17DeathEyeUsed = false;
  sword17DeathEyeAttacksLeft = 0;
  sword18LastStandLeft = (playerClass === 'sword' && level === 18) ? 2 : 0;
  sword19RevivesLeft = (playerClass === 'sword' && level === 19) ? 3 : 0;
  sword20SkillUsed = false;
""",
        1
    )
    old_ready = """  if (playerClass === 'mage') {
    if (level === 12) mageSkillNextReadyTurn = 3;
    else if (level === 14) mageSkillNextReadyTurn = 4;
    else if (level === 17) mageSkillNextReadyTurn = 3;
    else if (level === 18) mageSkillNextReadyTurn = 7;
    else if (level === 20) mageSkillNextReadyTurn = 2;
    else mageSkillNextReadyTurn = 0;
  } else {
    mageSkillNextReadyTurn = 0;
  }"""
    new_ready = """  if (playerClass === 'mage') {
    if (level === 12) mageSkillNextReadyTurn = 3;
    else if (level === 14) mageSkillNextReadyTurn = 4;
    else if (level === 17) mageSkillNextReadyTurn = 3;
    else if (level === 18) mageSkillNextReadyTurn = 7;
    else if (level === 20) mageSkillNextReadyTurn = 2;
    else mageSkillNextReadyTurn = 0;
  } else if (playerClass === 'sword') {
    if (level === 14) mageSkillNextReadyTurn = 4;
    else if (level === 16) mageSkillNextReadyTurn = 3;
    else if (level === 20) mageSkillNextReadyTurn = 2;
    else mageSkillNextReadyTurn = 0;
  } else {
    mageSkillNextReadyTurn = 0;
  }"""
    if old_ready not in block:
        raise SystemExit('skill-ready reset block not found')
    block = block.replace(old_ready, new_ready, 1)
    s = s[:m.start()] + block + s[m.end():]

# ------------------------------------------------------------------
# 3. Shared active skill button supports Sword
# ------------------------------------------------------------------
rx(
    r"function mageActiveSkillInfo\(\) \{.*?\n\}\n\nfunction canUseMageSkillNow",
    """function mageActiveSkillInfo() {
  const upcomingTurn = playerTurnCount + 1;
  if (playerClass === 'mage') {
    if (level === 12) return { name: '신화의 시작', cooldown: 2, icon: '📖' };
    if (level === 14) return { name: '레퀴엠', cooldown: 4, icon: '🎼' };
    if (level === 17) return { name: '몰락의 밤', cooldown: 3, icon: '🌑' };
    if (level === 18) return { name: '생명의 샘', cooldown: 7, icon: '💧' };
    if (level === 20) return { name: '천지의 선택', cooldown: 0, icon: '🌌' };
    return null;
  }
  if (playerClass === 'sword') {
    if (level === 12) {
      if (!sword12SlashUsed && upcomingTurn <= 5) return { name: '참살쇄도', cooldown: 0, icon: '⚔️', exactTurn: 5 };
      if (!sword12TornadoUsed && upcomingTurn <= 10) return { name: '휘몰아치는 칼날', cooldown: 0, icon: '🌪️', exactTurn: 10 };
      return null;
    }
    if (level === 14) return { name: '흑악신멸', cooldown: 4, icon: '⚫' };
    if (level === 16) return { name: '월광봉멸', cooldown: 3, icon: '🌙' };
    if (level === 20) return { name: '종언', cooldown: 0, icon: '☄️' };
  }
  return null;
}

function canUseMageSkillNow"""
)

rep(
    "  if (level === 20 && mage20SkillUsed) return false;\n  const upcomingTurn = playerTurnCount + 1;\n  return upcomingTurn >= mageSkillNextReadyTurn;",
    """  if (playerClass === 'mage' && level === 20 && mage20SkillUsed) return false;
  if (playerClass === 'sword' && level === 20 && sword20SkillUsed) return false;
  const upcomingTurn = playerTurnCount + 1;
  if (info.exactTurn != null) return upcomingTurn === info.exactTurn;
  return upcomingTurn >= mageSkillNextReadyTurn;"""
)

rep(
    """  if (level === 20 && mage20SkillUsed) {
    status = '전투당 1회 사용 완료';
  } else if (playerParalyzed || playerSealed) {""",
    """  if ((playerClass === 'mage' && level === 20 && mage20SkillUsed) || (playerClass === 'sword' && level === 20 && sword20SkillUsed)) {
    status = '전투당 1회 사용 완료';
  } else if (info.exactTurn != null && upcomingTurn < info.exactTurn) {
    status = `자신의 ${info.exactTurn}번째 턴에 1회 사용 가능`;
  } else if (info.exactTurn != null && upcomingTurn > info.exactTurn) {
    status = '해당 스킬 사용 가능 턴이 지났습니다';
  } else if (playerParalyzed || playerSealed) {"""
)

# ------------------------------------------------------------------
# 4. Sword passive/survival helpers
# ------------------------------------------------------------------
if 'async function beginSwordTranscendTurn()' not in s:
    helpers = r'''
async function playSwordTornadoFx() {
  const overlay = $('fx-overlay');
  if (!overlay) return;
  overlay.classList.add('active');
  const t = document.createElement('div');
  t.textContent = '🌪️';
  t.style.cssText = 'position:absolute;left:50%;top:50%;font-size:7rem;transform:translate(-50%,-50%) scale(.2) rotate(0deg);filter:drop-shadow(0 0 25px #8fe8ff);z-index:3;';
  overlay.appendChild(t);
  try {
    t.animate([
      { transform:'translate(-50%,-50%) scale(.2) rotate(0deg)', opacity:0.2 },
      { transform:'translate(-50%,-50%) scale(1.35) rotate(540deg)', opacity:1 },
      { transform:'translate(-50%,-50%) scale(.8) rotate(900deg)', opacity:0 }
    ], { duration:700, easing:'ease-out' });
  } catch (e) {}
  await sleep(700);
  overlay.classList.remove('active');
  overlay.innerHTML = '';
}

function restorePlayerControlAfterSwordSurvival() {
  battleEnded = false;
  autoMode = false;
  playerAttackLock = false;
  try {
    const atk = $('atk-btn');
    if (atk) { atk.style.display = 'block'; atk.disabled = false; }
  } catch (e) {}
  updateHPBars();
  updateStatusIcons();
  updateMageSkillButton();
}

function trySwordTranscendSurvival(reason) {
  if (playerClass !== 'sword' || hp > 0) return false;
  if (/강제 종료|항복|연결|소멸/.test(String(reason || ''))) return false;

  if (level === 17) {
    if (!sword17DeathEyeActive && !sword17DeathEyeUsed) {
      sword17DeathEyeUsed = true;
      sword17DeathEyeActive = true;
      sword17DeathEyeAttacksLeft = 3;
      hp = 1;
      addLog('ability', '👁️ 마검의 눈! 사망 후 공격 3회까지 죽지 않는다.');
      showAbility('👁️ 마검의 눈', '죽음 이후에도 공격 3회 가능! 마검의 저항은 비활성화됩니다.');
    } else if (sword17DeathEyeActive && sword17DeathEyeAttacksLeft > 0) {
      hp = 1;
    } else {
      return false;
    }
    restorePlayerControlAfterSwordSurvival();
    return true;
  }

  if (level === 18 && sword18LastStandLeft > 0) {
    sword18LastStandLeft--;
    hp = 1;
    addLog('ability', `⚔️ 진·엑스칼리버 최후의 저항! 남은 ${sword18LastStandLeft}회`);
    showAbility('⚔️ 최후의 저항!', `체력 1로 버텼다! 남은 ${sword18LastStandLeft}회`);
    restorePlayerControlAfterSwordSurvival();
    return true;
  }

  if (level === 19 && sword19RevivesLeft > 0) {
    sword19RevivesLeft--;
    hp = Math.max(1, Math.floor(maxHp * 0.75));
    addLog('ability', `♾️ 불멸! 최대 체력 75%로 부활 · 남은 ${sword19RevivesLeft}회`);
    showAbility('♾️ 불멸의 무라마사!', `체력 75%로 부활! 남은 ${sword19RevivesLeft}회`);
    restorePlayerControlAfterSwordSurvival();
    return true;
  }
  return false;
}

async function beginSwordTranscendTurn() {
  if (playerClass !== 'sword' || level < 11 || level > 20 || !enemy) return false;

  if (level === 11) {
    if (playerTurnCount === 3 && !sword11DamageBuff) {
      sword11DamageBuff = true;
      await showAbility('👑 신의 명령', '공격 데미지 +30%를 획득했다!');
      addLog('ability', '천명 1단계: 신의 명령 · 공격 데미지 +30%');
    }
    if (playerTurnCount === 6 && !sword11ShieldGranted) {
      sword11ShieldGranted = true;
      playerShield += 200;
      await showAbility('🛡️ 신의 하사', `보호막 200 획득! 현재 보호막 ${playerShield}`);
      addLog('ability', '천명 2단계: 신의 하사 · 보호막 +200');
    }
    if (playerTurnCount === 9 && !sword11DestinyUsed && enemy.hp > 0) {
      sword11DestinyUsed = true;
      enemy.hp = 0;
      await playFx('kill');
      await showAbility('👑 천명', '신의 뜻으로 대상을 즉사시켰다!');
      addLog('ability', '천명 3단계: 대상 즉사');
      updateHPBars();
      if (await resolveEnemyDeathFromMageSkill('천명')) return true;
    }
  }

  if (level === 13 && enemy.hp > 0) {
    const raw = Math.max(1, Math.floor(enemy.hp * 0.05));
    const actual = dmgEnemy(raw, { bypassShield: true });
    if (actual > 0) {
      playerShield += actual;
      await showAbility('🛡️ 합병', `상대 현재 체력 5% 흡수: ${actual} 피해 → 보호막 +${actual}`);
      addLog('ability', `합병: ${actual} 흡수 · 보호막 ${playerShield}`);
      updateHPBars();
      updateStatusIcons();
      if (await resolveEnemyDeathFromMageSkill('합병')) return true;
    }
  }

  if (level === 17 && !sword17DeathEyeActive) {
    const triggered = [];
    if (rand() < 0.04) {
      const raw = Math.max(1, Math.floor(Math.max(1, hp) * 0.10));
      const actual = dmgPlayer(raw);
      triggered.push(`부패 ${actual}`);
    }
    if (rand() < 0.04) { playerFall = true; triggered.push('타락'); }
    if (rand() < 0.04) { playerCursed = Math.min(2, playerCursed + 1); triggered.push(`저주${playerCursed}`); }
    if (rand() < 0.04) { playerSealed = true; triggered.push('봉인'); }
    if (rand() < 0.04) { hp = 0; triggered.push('즉사'); }
    if (triggered.length) {
      await showAbility('🩸 마검의 저항', `자신에게 ${triggered.join(' · ')} 발동!`);
      addLog('ability', `마검의 저항: ${triggered.join(', ')}`);
      updateHPBars();
      updateStatusIcons();
    }
    if (hp <= 0) {
      endBattle(false, '마검의 저항 즉사');
      return true;
    }
  }
  return false;
}

async function finishSword17DeathEyeAttack() {
  if (playerClass !== 'sword' || level !== 17 || !sword17DeathEyeActive) return false;
  sword17DeathEyeAttacksLeft = Math.max(0, sword17DeathEyeAttacksLeft - 1);
  hp = 1;
  updateHPBars();
  updateStatusIcons();
  if (sword17DeathEyeAttacksLeft <= 0) {
    sword17DeathEyeActive = false;
    hp = 0;
    await showAbility('👁️ 마검의 눈 종료', '죽음 이후의 마지막 공격을 마쳤다.');
    endBattle(false, '마검의 눈 종료');
    return true;
  }
  addLog('ability', `마검의 눈: 남은 공격 ${sword17DeathEyeAttacksLeft}회`);
  return false;
}

'''
    rep('async function beginPlayerActionTurn() {', helpers + 'async function beginPlayerActionTurn() {')

rep(
    "async function beginPlayerActionTurn() {\n  playerTurnCount++;\n",
    "async function beginPlayerActionTurn() {\n  playerTurnCount++;\n\n  if (await beginSwordTranscendTurn()) return true;\n",
)

# Reflect all numerical damage during the enemy turn targeted by Moonlight Seal.
rep(
    "function dmgPlayer(amount) {\n",
    """function dmgPlayer(amount) {
  if (playerClass === 'sword' && level === 16 && sword16ReflectEnemyTurn === enemyTurnCount && Number(amount) > 0) {
    const reflected = dmgEnemy(Number(amount) || 0);
    addLog('ability', `🌙 월광봉멸 반사: 적에게 ${reflected} 피해`);
    return 0;
  }
  if (playerClass === 'sword' && level === 17 && sword17DeathEyeActive) {
    amount = Math.min(Math.max(0, Number(amount) || 0), Math.max(0, hp - 1));
  }
""",
)

# ------------------------------------------------------------------
# 5. Player attack hooks
# ------------------------------------------------------------------
pa_start = s.index('async function playerAttack() {')
pa_end = s.index('async function enemyAttack() {', pa_start)
pa = s[pa_start:pa_end]

old = """  if (playerClass === 'mage' && level === 12 && mage12BuffStacks > 0) {
    dmg = Math.round(dmg * (1 + mage12BuffStacks * 0.15));
  }
  if (playerCursed > 0) dmg = Math.floor(dmg * Math.pow(0.7, playerCursed));"""
new = """  if (playerClass === 'mage' && level === 12 && mage12BuffStacks > 0) {
    dmg = Math.round(dmg * (1 + mage12BuffStacks * 0.15));
  }
  if (playerClass === 'sword' && level === 11 && sword11DamageBuff) {
    dmg = Math.round(dmg * 1.30);
  }
  if (playerClass === 'sword' && level === 15) {
    const lostRatio = maxHp > 0 ? clamp((maxHp - Math.max(0, hp)) / maxHp, 0, 1) : 0;
    dmg = Math.round(dmg * (1 + lostRatio));
  }
  if (playerCursed > 0) dmg = Math.floor(dmg * Math.pow(0.7, playerCursed));"""
if old not in pa:
    raise SystemExit('player damage anchor missing')
pa = pa.replace(old, new, 1)

old = """  let doubleHit = false;
  if (canAbility && abilityW.double && rand() < abilityW.double) {
    doubleHit = true;
    await showAbility('⚡ 이중 공격!', '한 턴에 공격 두 번!');
    logMsg = `이중 공격! ${dmg} x2`;
  }"""
new = """  let doubleHit = false;
  if (playerClass === 'sword' && level === 16 && sword16DoubleNext) {
    sword16DoubleNext = false;
    doubleHit = true;
    await showAbility('🌙 월광 2연격!', '월광봉멸의 힘으로 이번 공격은 2연타!');
    logMsg = `월광 2연격! ${dmg} x2`;
  } else if (canAbility && abilityW.double && rand() < abilityW.double) {
    doubleHit = true;
    await showAbility('⚡ 이중 공격!', '한 턴에 공격 두 번!');
    logMsg = `이중 공격! ${dmg} x2`;
  }"""
if old not in pa:
    raise SystemExit('double-hit anchor missing')
pa = pa.replace(old, new, 1)

# Muramasa current-HP 2% burn after the normal attack block.
burn_anchor = '  if (fireTurns > 0) {'
if burn_anchor not in pa:
    raise SystemExit('fire turn anchor missing')
burn_code = """  if (playerClass === 'sword' && level === 19 && !fallSelf && enemy && enemy.hp > 0 && dealtToEnemy > 0) {
    const burnRaw = Math.max(1, Math.floor(enemy.hp * 0.02));
    const burnActual = dmgEnemy(burnRaw);
    if (burnActual > 0) {
      dealtToEnemy += burnActual;
      await showAbility('🔥 무라마사 화상', `상대 현재 체력 2% · ${burnActual} 추가 피해!`);
      addLog('ability', `무라마사 화상 ${burnActual}`);
    }
  }
"""
pa = pa.replace(burn_anchor, burn_code + burn_anchor, 1)

# Death Eye consumes one charge only after a real attack action, and only if enemy survived.
death_eye_anchor = '  // 마비로 적 턴 스킵. 실시간에서는 상태를 상대에게 넘겨 상대 클라이언트가 자기 턴을 스킵한다.\n'
if death_eye_anchor not in pa:
    raise SystemExit('death-eye finish anchor missing')
pa = pa.replace(death_eye_anchor, '  if (await finishSword17DeathEyeAttack()) return;\n\n' + death_eye_anchor, 1)

s = s[:pa_start] + pa + s[pa_end:]

# ------------------------------------------------------------------
# 6. Enemy attack ability reflection for +16
# ------------------------------------------------------------------
ea_start = s.index('async function enemyAttack() {')
ea_end = s.index('function endBattle(', ea_start)
ea = s[ea_start:ea_end]
old = """  let enemyFallSelf = false;
  if (enemyFall) {
    enemyFall = false;
    enemyFallSelf = true;
    await showAbility('😈 타락 발동!', '적 공격과 능력이 적에게로!');
  }"""
new = """  let enemyFallSelf = false;
  if (playerClass === 'sword' && level === 16 && sword16ReflectEnemyTurn === enemyTurnCount) {
    enemyFall = false;
    enemyFallSelf = true;
    await showAbility('🌙 월광봉멸 반사!', '상대의 공격과 능력을 그대로 반사!');
    addLog('ability', '월광봉멸: 상대 공격 반사');
  } else if (enemyFall) {
    enemyFall = false;
    enemyFallSelf = true;
    await showAbility('😈 타락 발동!', '적 공격과 능력이 적에게로!');
  }"""
if old not in ea:
    raise SystemExit('enemyFallSelf anchor missing')
ea = ea.replace(old, new, 1)
s = s[:ea_start] + ea + s[ea_end:]

# ------------------------------------------------------------------
# 7. Sword active skills
# ------------------------------------------------------------------
rep(
    """  if (level === 20) {
    if (canUseMageSkillNow()) openMage20Choice();
    return;
  }
  if (!canUseMageSkillNow()) return;""",
    """  if (playerClass === 'mage' && level === 20) {
    if (canUseMageSkillNow()) openMage20Choice();
    return;
  }
  if (!canUseMageSkillNow()) return;""",
)

skill_anchor = """    const turnUsed = playerTurnCount;
    mageSkillNextReadyTurn = turnUsed + info.cooldown;

    if (level === 12) {"""
skill_code = """    const turnUsed = playerTurnCount;
    mageSkillNextReadyTurn = turnUsed + info.cooldown;

    if (playerClass === 'sword') {
      if (level === 12 && info.name === '참살쇄도') {
        sword12SlashUsed = true;
        const hit = Math.max(1, Math.round(105 * 0.70));
        await showAbility('⚔️ 참살쇄도!', `${hit} 피해 × 3연타!`);
        for (let i = 1; i <= 3; i++) {
          const actual = dmgEnemy(hit);
          addLog('ability', `참살쇄도 ${i}타: ${actual} 피해`);
          updateHPBars();
          if (await resolveEnemyDeathFromMageSkill('참살쇄도')) return;
        }
      } else if (level === 12 && info.name === '휘몰아치는 칼날') {
        sword12TornadoUsed = true;
        await playSwordTornadoFx();
        const raw = Math.max(1, Math.round(105 * 2.50));
        const actual = dmgEnemy(raw);
        await showAbility('🌪️ 휘몰아치는 칼날!', `토네이도 참격! 공격력 250% · ${actual} 피해`);
        addLog('ability', `휘몰아치는 칼날: ${actual} 피해`);
      } else if (level === 14) {
        let instantSucceeded = false;
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
        if (!instantSucceeded) {
          const raw = Math.max(1, Math.floor(enemy.maxHp * 0.65));
          const actual = dmgEnemy(raw);
          await showAbility('⚫ 흑악신멸!', `즉사 불발 → 상대 최대 체력 65% · ${actual} 피해!`);
          addLog('ability', `흑악신멸 대체 피해: ${actual}`);
        }
      } else if (level === 16) {
        sword16ReflectEnemyTurn = enemyTurnCount + 1;
        sword16DoubleNext = true;
        await showAbility('🌙 월광봉멸!', '다음 상대 공격 반사 · 다음 내 공격 2연타!');
        addLog('ability', '월광봉멸: 반사 대기 + 다음 공격 2연타');
        if (rand() < 0.15) {
          enemy.hp = 0;
          await playFx('seal');
          await showAbility('🔒 월광 봉인!', '15% 봉인 발동! 상대 즉사');
          addLog('ability', '월광봉멸: 봉인 성공');
        }
      } else if (level === 20) {
        sword20SkillUsed = true;
        mageSkillNextReadyTurn = 999999;
        if (rand() < 0.50) {
          enemy.hp = 0;
          enemy.undying = false;
          enemy.revived = true;
          enemyLastStandUsed = true;
          await playFx('kill');
          await showAbility('☄️ 종언', '50% 종언 발동! 회피·보호막·불사·부활을 무시하고 반드시 즉사!');
          addLog('ability', '종언: 반드시 즉사 성공');
          updateHPBars();
          endBattle(true, '종언 즉사');
          return;
        } else {
          const actual = dmgEnemy(10000);
          await playFx('chamgyeok');
          await showAbility('☄️ 종언', `즉사 불발 → 10,000 피해! 실제 ${actual} 피해`);
          addLog('ability', `종언: 10,000 피해 (실피해 ${actual})`);
        }
      }

      updateHPBars();
      updateStatusIcons();
      updateMageSkillButton();
      if (await resolveEnemyDeathFromMageSkill(info.name)) return;
      await enemyAttack();
      return;
    }

    if (level === 12) {"""
rep(skill_anchor, skill_code)

# ------------------------------------------------------------------
# 8. Survival hooks and attack-lock safety
# ------------------------------------------------------------------
rep(
    """function endBattle(win, reason) {
  if (!win && tryMage19CheckpointRevive(reason)) return;
  if (!win && offerMage14DeathRequiem(reason)) return;""",
    """function endBattle(win, reason) {
  if (!win && trySwordTranscendSurvival(reason)) return;
  if (!win && tryMage19CheckpointRevive(reason)) return;
  if (!win && offerMage14DeathRequiem(reason)) return;""",
)

# Restore the attack button if an unexpected exception/early path leaves combat alive.
player_tail = """  } finally {
    playerAttackLock = false;
    updateMageSkillButton();
  }
}

async function enemyAttack() {"""
player_tail_new = """  } finally {
    playerAttackLock = false;
    if (!battleEnded && !rtActive) {
      try { if ($('atk-btn')) $('atk-btn').disabled = false; } catch (e) {}
    }
    updateMageSkillButton();
  }
}

async function enemyAttack() {"""
rep(player_tail, player_tail_new)

# ------------------------------------------------------------------
# 9. Sanity markers
# ------------------------------------------------------------------
required = [
    "name: '천명의 신검', atk: 85",
    "name: '참살쇄도', atk: 105",
    "name: '안슐루스', atk: 130",
    "name: '신살흑도', atk: 145",
    "name: '적월도', atk: 180",
    "name: '명월도', atk: 200",
    "name: '마검 데스티니', atk: 225",
    "name: '진·엑스칼리버', atk: 300",
    "name: '불멸의 무라마사', atk: 420",
    "name: '살신명도·종언', atk: 500",
    'async function beginSwordTranscendTurn()',
    'function trySwordTranscendSurvival(reason)',
    'async function playSwordTornadoFx()',
]
for marker in required:
    if marker not in s:
        raise SystemExit('MISSING MARKER: ' + marker)

p.write_text(s, encoding='utf-8')
print('patched index.html:', len(s), 'chars')

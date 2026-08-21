from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    s = s.replace(old, new, 1)


def sub_once(pattern, repl, label, flags=re.S):
    global s
    s2, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected exactly 1 regex match, got {n}')
    s = s2

# 1) Realtime session safety flags.
replace_once(
"""let rtEnhanceStarted = false; // 결투 강화 세션 시작 여부
let rtBuildLocked = false;    // 준비 완료 후 재강화 금지
""",
"""let rtEnhanceStarted = false; // 결투 강화 세션 시작 여부
let rtBuildLocked = false;    // 준비 완료 후 재강화 금지
let rtClosingLocally = false; // 내가 직접 연결을 닫을 때 상대 이탈 팝업 방지
let rtBattleStarted = false;  // ready/start 중복 신호로 전투가 두 번 시작되는 것 방지
""",
'realtime state flags')

# 2) Daily missions: cloud accounts never trust device date.
replace_once(
"""function missionToday() {
  const d = new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}
""",
"""function missionToday() {
  // 클라우드 계정은 기기 날짜를 사용하지 않는다. 서버 날짜 동기화 전에는
  // 기존 미션 날짜를 유지해 날짜 조작으로 일일 보상이 초기화되지 않게 한다.
  if (useCloud && fbUserId) {
    return trustedAttendanceToday || (saveData.missions && saveData.missions.day) || '';
  }
  const d = new Date();
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
}
""",
'mission server date')

# Sync trusted server day during session restore.
replace_once(
"""    } else {
      saveData = defaultSaveData('');
      await cloudSaveProfile();
    }
    normalizeMissions();
    updateRecordSummary();
""",
"""    } else {
      saveData = defaultSaveData('');
      await cloudSaveProfile();
    }
    try { await getTrustedAttendanceToday(); } catch (e) { console.warn('daily server date sync failed', e); }
    normalizeMissions();
    updateRecordSummary();
""",
'restore daily sync')

# Sync trusted server day on explicit login too.
replace_once(
"""    } else {
      saveData = defaultSaveData(nick);
      await cloudSaveProfile();
    }
    normalizeMissions();
    try { localStorage.setItem('sword_mage_last_nick', nick); } catch (e) {}
""",
"""    } else {
      saveData = defaultSaveData(nick);
      await cloudSaveProfile();
    }
    try { await getTrustedAttendanceToday(); } catch (e) { console.warn('daily server date sync failed', e); }
    normalizeMissions();
    try { localStorage.setItem('sword_mage_last_nick', nick); } catch (e) {}
""",
'login daily sync')

# Missions screen also requires a fresh trusted date before reset/reward display.
replace_once(
"""function openMissions() {
  if (!requireLogin()) return;
  normalizeMissions();
  persistSave();
""",
"""async function openMissions() {
  if (!requireLogin()) return;
  if (useCloud && fbDb && fbUserId) {
    try {
      await getTrustedAttendanceToday();
    } catch (e) {
      console.warn('mission server clock failed', e);
      alert('서버 날짜를 확인할 수 없습니다. 인터넷 연결 후 다시 시도하세요.');
      return;
    }
  }
  normalizeMissions();
  persistSave();
""",
'open missions trusted date')

# Clear trusted date on logout to avoid leaking session state across accounts.
replace_once(
"""  fbUserId = null;
  currentUserKey = null;
  saveData = defaultSaveData('');
  setAutoLoginFlag(false);
""",
"""  fbUserId = null;
  currentUserKey = null;
  saveData = defaultSaveData('');
  trustedAttendanceToday = '';
  setAutoLoginFlag(false);
""",
'logout clear trusted date')

# 3) Only show realtime controls in duel flow; boss/story/quick builds cannot jump into PvP.
replace_once(
"""function updateEnhanceRtBox() {
  const readyBtn = $('btn-rt-ready');
  const openBtn = $('btn-rt-open');
  const status = $('enhance-rt-status');
  const gb = $('btn-go-battle');
  const connected = !!(rtConnected && rtActive !== true && (rtPeer || rtConn));
  // rtConnected is the right flag during lobby/enhance before battle
  const inRoom = !!rtConnected;
""",
"""function updateEnhanceRtBox() {
  const readyBtn = $('btn-rt-ready');
  const openBtn = $('btn-rt-open');
  const status = $('enhance-rt-status');
  const gb = $('btn-go-battle');
  const box = $('enhance-rt-box');
  const duelFlow = pendingPlayMode === 'duel-normal' || pendingPlayMode === 'duel-ranked';
  const connected = !!(rtConnected && rtActive !== true && (rtPeer || rtConn));
  const inRoom = !!rtConnected;
  if (box) box.style.display = (duelFlow || inRoom) ? 'block' : 'none';
  if (!duelFlow && !inRoom) {
    if (gb) gb.style.display = 'block';
    return;
  }
  // rtConnected is the right flag during lobby/enhance before battle
""",
'hide realtime box outside duel')

# Opening duel room always clears raid/event state and pins the PvP mode.
replace_once(
"""function openChallengeMenu(mode) {
  if (!requireNick()) return;
  if (mode === 'ranked' || mode === 'normal') duelTypeMode = mode;
  challengeCreating = false;
""",
"""function openChallengeMenu(mode) {
  if (!requireNick()) return;
  if (mode === 'ranked' || mode === 'normal') duelTypeMode = mode;
  pendingPlayMode = duelTypeMode === 'ranked' ? 'duel-ranked' : 'duel-normal';
  pendingRaidBoss = false;
  selectedRaidBossId = null;
  gameMode = 'normal';
  challengeMode = false;
  challengeEnemyData = null;
  challengeCreating = false;
""",
'clear non-pvp mode state')

# 4) Enhancement UI must show +11~+20 rates when transcend is actually available.
replace_once(
"""  $('chance').textContent = chances;
  $('rate').textContent = level >= 10 ? '-' : getSuccessRate(level);
  if ($('enemy-level-preview')) {
    const lo = Math.max(1, level - 2);
    const hi = Math.min(10, Math.max(level, 1) + 2);
    $('enemy-level-preview').textContent = level === 0 ? '+1~3 예상' : `+${lo}~${hi} (나 ±1~2)`;
  }
""",
"""  $('chance').textContent = chances;
  const maxEnhanceLevel = getEnhanceMaxLevel();
  $('rate').textContent = level >= maxEnhanceLevel ? '-' : getSuccessRate(level);
  if ($('enemy-level-preview')) {
    if (pendingRaidBoss) {
      $('enemy-level-preview').textContent = '보스 고정';
    } else {
      const lo = Math.max(1, level - 2);
      const hi = Math.min(10, Math.max(level, 1) + 2);
      $('enemy-level-preview').textContent = level === 0 ? '+1~3 예상' : `+${lo}~${hi} (나 ±1~2)`;
    }
  }
""",
'enhance rate display')

# 5) Weapon badge bug: assassin/priest/archer must not unlock staff badges.
replace_once(
"""  if (level >= 1 && level <= 10) {
    const prefix = playerClass === 'sword' ? 'sw' : 'st';
    unlockBadge(prefix + level);
  }
""",
"""  if (level >= 1 && level <= 10) {
    const prefix = playerClass === 'sword' ? 'sw' : (playerClass === 'mage' ? 'st' : '');
    if (prefix) unlockBadge(prefix + level);
  }
""",
'weapon badge class mapping')

# 6) Auto battle must never force-release a live attack lock.
replace_once(
"""  if (autoMode && !battleEnded && !rtActive) {
    // 멈춘 락 강제 해제 후 시작
    playerAttackLock = false;
    try { $('atk-btn').disabled = false; } catch (e) {}
    playerAttack();
  }
""",
"""  if (autoMode && !battleEnded && !rtActive) {
    if (playerAttackLock) {
      scheduleAutoAttack(220);
    } else {
      try { $('atk-btn').disabled = false; } catch (e) {}
      playerAttack();
    }
  }
""",
'auto battle lock')

# 7) Lifesteal uses actual damage dealt, not nominal attack damage.
replace_once(
"""    if (abilityW.lifesteal) {
      let ls = Math.max(1, Math.floor(dmg * abilityW.lifesteal));
      ls = healAmount(ls, true);
      hp = Math.min(maxHp, hp + ls);
      await showAbility('🩸 흡혈!', `${ls} 회복!`);
      addLog('ability', `흡혈 ${ls}`);
    }
""",
"""    if (abilityW.lifesteal && dealt > 0) {
      let ls = Math.floor(dealt * abilityW.lifesteal);
      ls = healAmount(ls, true);
      if (ls > 0) {
        hp = Math.min(maxHp, hp + ls);
        await showAbility('🩸 흡혈!', `${ls} 회복!`);
        addLog('ability', `흡혈 ${ls}`);
      }
    }
""",
'player lifesteal first hit')

replace_once(
"""        if (abilityW.lifesteal) {
          let ls2 = Math.max(1, Math.floor(dmg * abilityW.lifesteal));
          ls2 = healAmount(ls2, true);
          hp = Math.min(maxHp, hp + ls2);
        }
""",
"""        if (abilityW.lifesteal && dealt2 > 0) {
          let ls2 = Math.floor(dealt2 * abilityW.lifesteal);
          ls2 = healAmount(ls2, true);
          if (ls2 > 0) hp = Math.min(maxHp, hp + ls2);
        }
""",
'player lifesteal second hit')

replace_once(
"""    if (abilityW.lifesteal) {
      let ls = Math.floor(dmg * abilityW.lifesteal);
      ls = healAmount(ls, false);
      enemy.hp = Math.min(enemy.maxHp, enemy.hp + ls);
    }
""",
"""    if (abilityW.lifesteal && actual > 0) {
      let ls = Math.floor(actual * abilityW.lifesteal);
      ls = healAmount(ls, false);
      if (ls > 0) enemy.hp = Math.min(enemy.maxHp, enemy.hp + ls);
    }
""",
'enemy lifesteal first hit')

replace_once(
"""      if (abilityW.lifesteal) {
        let ls2 = Math.floor(dmg * abilityW.lifesteal);
        ls2 = healAmount(ls2, false);
        enemy.hp = Math.min(enemy.maxHp, enemy.hp + ls2);
      }
""",
"""      if (abilityW.lifesteal && actual2 > 0) {
        let ls2 = Math.floor(actual2 * abilityW.lifesteal);
        ls2 = healAmount(ls2, false);
        if (ls2 > 0) enemy.hp = Math.min(enemy.maxHp, enemy.hp + ls2);
      }
""",
'enemy lifesteal second hit')

# Enemy absorb also heals only the HP actually removed after shields/resists.
replace_once(
"""  if (canAbility && abilityW.absorb) {
    let absorbAmt = Math.floor(Math.max(0, hp) * abilityW.absorb);
    const actual = dmgPlayer(absorbAmt);
    lastDamageTaken += actual;
    absorbAmt = healAmount(absorbAmt, false);
    enemy.hp = Math.min(enemy.maxHp, enemy.hp + absorbAmt);
  }
""",
"""  if (canAbility && abilityW.absorb) {
    const absorbAmt = Math.floor(Math.max(0, hp) * abilityW.absorb);
    const actual = dmgPlayer(absorbAmt);
    lastDamageTaken += actual;
    let heal = healAmount(actual, false);
    if (heal > 0) enemy.hp = Math.min(enemy.maxHp, enemy.hp + heal);
  }
""",
'enemy absorb actual damage')

# 8) Realtime full state snapshots and safe build validation.
rt_helpers = r'''
const RT_ALLOWED_CLASSES = new Set(['sword', 'mage', 'assassin', 'priest', 'archer']);

function rtNormalizeBuild(data) {
  const cls = RT_ALLOWED_CLASSES.has(data && data.cls) ? data.cls : 'sword';
  const lvRaw = Number(data && data.lv);
  const lv = clamp(Number.isFinite(lvRaw) ? Math.floor(lvRaw) : 0, 0, 10);
  const maxHpSafe = getBaseHp(cls) + lv * 100;
  return {
    nick: String((data && data.nick) || '상대').slice(0, 12),
    cls,
    lv,
    hp: maxHpSafe,
    lr: Math.max(0, Number(data && data.lr) || 0)
  };
}

function rtSnapshotPlayerState() {
  return {
    hp: Math.max(0, Number(hp) || 0),
    paralyzed: !!playerParalyzed,
    fall: !!playerFall,
    cursed: Math.max(0, Number(playerCursed) || 0),
    mirror: !!playerMirror,
    sealed: !!playerSealed,
    purifyNext: !!playerPurifyNext,
    shield: Math.max(0, Number(playerShield) || 0),
    shieldUsed: !!playerShieldUsed,
    awakened: !!playerAwakened,
    awakenType: playerAwakenType || null,
    excalTurns: Math.max(0, Number(playerExcalTurns) || 0),
    lastStandUsed: !!playerLastStandUsed,
    revived: !!playerRevived,
    fireTurns: Math.max(0, Number(enemy && enemy.fireTurns) || 0)
  };
}

function rtSnapshotEnemyState() {
  return {
    hp: Math.max(0, Number(enemy && enemy.hp) || 0),
    paralyzed: !!enemyParalyzed,
    fall: !!enemyFall,
    cursed: Math.max(0, Number(enemyCursed) || 0),
    mirror: !!enemyMirror,
    sealed: !!enemySealed,
    purifyNext: !!enemyPurifyNext,
    shield: Math.max(0, Number(enemyShield) || 0),
    shieldUsed: !!enemyShieldUsed,
    awakened: !!enemyAwakened,
    awakenType: enemyAwakenType || null,
    excalTurns: Math.max(0, Number(enemyExcalTurns) || 0),
    lastStandUsed: !!enemyLastStandUsed,
    revived: !!(enemy && enemy.revived),
    fireTurns: Math.max(0, Number(fireTurns) || 0)
  };
}

function rtApplyPlayerState(st) {
  if (!st || typeof st !== 'object') return;
  if (Number.isFinite(Number(st.hp))) hp = clamp(Number(st.hp), 0, maxHp);
  playerParalyzed = !!st.paralyzed;
  playerFall = !!st.fall;
  playerCursed = clamp(Number(st.cursed) || 0, 0, 2);
  playerMirror = !!st.mirror;
  playerSealed = !!st.sealed;
  playerPurifyNext = !!st.purifyNext;
  playerShield = Math.max(0, Number(st.shield) || 0);
  playerShieldUsed = !!st.shieldUsed;
  playerAwakened = !!st.awakened;
  playerAwakenType = st.awakenType === 'guardian' ? 'guardian' : (st.awakenType === 'excalibur' ? 'excalibur' : null);
  playerExcalTurns = Math.max(0, Number(st.excalTurns) || 0);
  playerLastStandUsed = !!st.lastStandUsed;
  playerRevived = !!st.revived;
  if (enemy) enemy.fireTurns = Math.max(0, Number(st.fireTurns) || 0);
}

function rtApplyEnemyState(st) {
  if (!enemy || !st || typeof st !== 'object') return;
  if (Number.isFinite(Number(st.hp))) enemy.hp = clamp(Number(st.hp), 0, enemy.maxHp);
  enemyParalyzed = !!st.paralyzed;
  enemyFall = !!st.fall;
  enemyCursed = clamp(Number(st.cursed) || 0, 0, 2);
  enemyMirror = !!st.mirror;
  enemySealed = !!st.sealed;
  enemyPurifyNext = !!st.purifyNext;
  enemyShield = Math.max(0, Number(st.shield) || 0);
  enemyShieldUsed = !!st.shieldUsed;
  enemyAwakened = !!st.awakened;
  enemyAwakenType = st.awakenType === 'guardian' ? 'guardian' : (st.awakenType === 'excalibur' ? 'excalibur' : null);
  enemyExcalTurns = Math.max(0, Number(st.excalTurns) || 0);
  enemyLastStandUsed = !!st.lastStandUsed;
  enemy.revived = !!st.revived;
  fireTurns = Math.max(0, Number(st.fireTurns) || 0);
  enemy.weapon = enemyAwakened
    ? (enemyAwakenType === 'guardian' ? Object.assign({}, GUARDIAN) : Object.assign({}, EXCALIBUR))
    : getWeapon(enemy.class, enemy.level, false, null);
}

function rtRefreshBattleActors() {
  try {
    const pw = getWeapon(playerClass, level, playerAwakened, playerAwakenType);
    if ($('p-weapon')) $('p-weapon').textContent = `${pw.name} +${level}`;
    if ($('p-desc')) $('p-desc').textContent = pw.desc || '';
    if (enemy) {
      enemy.weapon = enemyAwakened
        ? (enemyAwakenType === 'guardian' ? Object.assign({}, GUARDIAN) : Object.assign({}, EXCALIBUR))
        : getWeapon(enemy.class, enemy.level, false, null);
      if ($('e-weapon')) $('e-weapon').textContent = `${enemy.weapon.name} +${enemy.level}`;
      if ($('e-desc')) $('e-desc').textContent = enemy.weapon.desc || '';
    }
  } catch (e) { console.warn('rtRefreshBattleActors', e); }
}

'''
replace_once("function rtSetupConn(conn) {", rt_helpers + "function rtSetupConn(conn) {", 'realtime helper insertion')

# Disconnect outcome + local-close guard.
replace_once(
"""  conn.on('close', () => {
    rtConnected = false;
    if (rtActive) {
      alert('상대와의 연결이 끊겼습니다.');
      rtActive = false;
      if (!battleEnded) endBattle(false, '상대 연결 끊김');
    } else {
      alert('상대가 나갔습니다.');
      rtLeave();
    }
  });
""",
"""  conn.on('close', () => {
    if (rtClosingLocally) {
      rtConnected = false;
      return;
    }
    rtConnected = false;
    if (rtActive && !battleEnded) {
      const ranked = duelTypeMode === 'ranked';
      alert(ranked ? '상대 연결이 종료되어 랭크전 승리 처리됩니다.' : '상대 연결이 종료되어 일반전은 무효 처리됩니다.');
      if (ranked) endBattle(true, '상대 연결 종료');
      else endBattle(false, '상대 연결 종료 · 일반전 무효');
    } else if (!battleEnded) {
      alert('상대가 나갔습니다.');
      rtLeave();
    }
  });
""",
'realtime disconnect result')

# Reset duplicate-start guard in lobby.
replace_once(
"""function rtEnterLobby() {
  rtMyReady = false;
  rtOppReady = false;
  rtOppBuild = null;
""",
"""function rtEnterLobby() {
  rtMyReady = false;
  rtOppReady = false;
  rtOppBuild = null;
  rtBattleStarted = false;
""",
'lobby start guard reset')

# PvP is capped at +10 regardless of any prior boss state.
replace_once(
"""  if (rtMyReady || rtBuildLocked) {
    alert('이미 준비 완료된 빌드입니다.');
    showScreen('rt-lobby-screen');
    return;
  }
  if (level === 0 && !confirm('강화 0으로 준비할까요?')) return;
""",
"""  if (rtMyReady || rtBuildLocked) {
    alert('이미 준비 완료된 빌드입니다.');
    showScreen('rt-lobby-screen');
    return;
  }
  if (level > 10) {
    alert('결투방에서는 최대 +10 강화까지만 사용할 수 있습니다. 다시 강화해 주세요.');
    rtEnhanceStarted = false;
    startEnhance();
    return;
  }
  if (level === 0 && !confirm('강화 0으로 준비할까요?')) return;
""",
'pvp max level validation')

# Randomize first player and block duplicate start.
replace_once(
"""function rtTryStart() {
  if (!(rtMyReady && rtOppReady && rtOppBuild)) return;
  // Both ready — host starts, host goes first
  if (rtIsHost) {
    rtSend({ type: 'start', hostFirst: true });
    rtBeginBattle(true);
  }
}
""",
"""function rtTryStart() {
  if (!(rtMyReady && rtOppReady && rtOppBuild)) return;
  if (!rtIsHost || rtBattleStarted) return;
  rtBattleStarted = true;
  const hostFirst = rand() < 0.5;
  rtSend({ type: 'start', hostFirst });
  rtBeginBattle(hostFirst);
}
""",
'random pvp first turn')

# Validate incoming ready build and start signal.
replace_once(
"""  } else if (data.type === 'ready') {
    rtOppReady = true;
    rtOppBuild = {
      nick: data.nick,
      cls: data.cls,
      lv: data.lv,
      hp: data.hp,
      lr: data.lr || 0
    };
    upsertRankBoard(data.nick, data.lr || 0);
    $('rt-lobby-status').textContent = `상대 준비됨: ${data.nick} +${data.lv}`;
    rtTryStart();
  } else if (data.type === 'start') {
    // guest receives start
    if (!rtIsHost) rtBeginBattle(false);
""",
"""  } else if (data.type === 'ready') {
    rtOppReady = true;
    rtOppBuild = rtNormalizeBuild(data);
    upsertRankBoard(rtOppBuild.nick, rtOppBuild.lr || 0);
    $('rt-lobby-status').textContent = `상대 준비됨: ${rtOppBuild.nick} +${rtOppBuild.lv}`;
    rtTryStart();
  } else if (data.type === 'start') {
    // guest receives start; host chooses first player once.
    if (!rtIsHost && !rtBattleStarted) {
      rtBattleStarted = true;
      rtBeginBattle(!data.hostFirst);
    }
""",
'validate ready and start')

# Full state apply, while retaining old HP fields as fallback for mixed cached clients.
sub_once(
r"function rtApplyOppTurn\(data\) \{.*?\n\}\n\nfunction rtAfterMyTurn\(ended, win, reason, logs\) \{",
r'''function rtApplyOppTurn(data) {
  // Sender view: myState=sender, oppState=receiver. Apply mirrored to this client.
  if (data && data.oppState && data.myState) {
    rtApplyPlayerState(data.oppState);
    rtApplyEnemyState(data.myState);
  } else {
    if (typeof data.oppHp === 'number') hp = clamp(data.oppHp, 0, maxHp);
    if (typeof data.myHp === 'number' && enemy) enemy.hp = clamp(data.myHp, 0, enemy.maxHp);
  }
  if (Array.isArray(data.logs)) {
    data.logs.forEach(l => addLog(l.type || 'system', l.msg));
  } else if (data.log) {
    addLog('enemy', data.log);
  }
  rtRefreshBattleActors();
  updateHPBars();
  updateStatusIcons();
  if (data.ended || hp <= 0 || (enemy && enemy.hp <= 0)) {
    clearBattleOverlays();
    playerAttackLock = false;
    let iWin;
    if (data.ended) iWin = !data.win;
    else if (hp <= 0) iWin = false;
    else iWin = true;
    endBattle(iWin, data.reason || (iWin ? '결투 승리' : '결투 패배'));
    return;
  }
  rtMyTurn = true;
  playerAttackLock = false;
  const atk = $('atk-btn');
  if (atk) { atk.style.display = 'block'; atk.disabled = false; }
  addLog('system', '당신 턴!');
}

function rtAfterMyTurn(ended, win, reason, logs) {''',
'realtime state apply')

# Add snapshots to each turn payload.
replace_once(
"""      oppHp: enemy ? Math.max(0, enemy.hp) : 0,
      oppMaxHp: enemy ? enemy.maxHp : 0,
      ended: !!ended,
""",
"""      oppHp: enemy ? Math.max(0, enemy.hp) : 0,
      oppMaxHp: enemy ? enemy.maxHp : 0,
      myState: rtSnapshotPlayerState(),
      oppState: rtSnapshotEnemyState(),
      ended: !!ended,
""",
'realtime snapshot payload')

# Local close should not feed back as a remote disconnect; reset guards.
replace_once(
"""function rtLeave(silent) {
  rtActive = false;
  rtConnected = false;
  rtMyReady = false;
""",
"""function rtLeave(silent) {
  rtClosingLocally = true;
  rtActive = false;
  rtConnected = false;
  rtMyReady = false;
""",
'local close guard start')

replace_once(
"""  rtEnhanceStarted = false;
  rtBuildLocked = false;
  try {
""",
"""  rtEnhanceStarted = false;
  rtBuildLocked = false;
  rtBattleStarted = false;
  try {
""",
'leave reset battle started')

replace_once(
"""  rtRoomId = null;
  try { updateEnhanceRtBox(); } catch (e) {}
  if (!silent) showScreen('challenge-menu-screen');
}
""",
"""  rtRoomId = null;
  setTimeout(() => { rtClosingLocally = false; }, 0);
  try { updateEnhanceRtBox(); } catch (e) {}
  if (!silent) showScreen('challenge-menu-screen');
}
""",
'local close guard end')

# Realtime paralyze belongs to the remote player; don't consume it on attacker's client.
replace_once(
"""  // 마비로 적 턴 스킵
  if (enemyParalyzed) {
    enemyParalyzed = false;
    addLog('ability', '적 마비로 턴 스킵');
    updateStatusIcons();
    if (rtActive) {
      const ended = enemy.hp <= 0 || hp <= 0;
      const win = enemy.hp <= 0 && hp > 0;
      if (ended) {
        if (rtActive) rtAfterMyTurn(true, win, win ? '결투 승리' : '결투 패배');
        endBattle(win, win ? '결투 승리' : '결투 패배');
      } else {
        rtAfterMyTurn(false, false, '', []);
      }
      return;
    }
    $('atk-btn').disabled = false;
    if (autoMode) scheduleAutoAttack(400);
    return;
  }
""",
"""  // 마비로 적 턴 스킵. 실시간에서는 상태를 상대에게 넘겨 상대 클라이언트가 자기 턴을 스킵한다.
  if (enemyParalyzed) {
    if (rtActive) {
      rtAfterMyTurn(false, false, '', [{ type: 'ability', msg: '마비 상태 전달' }]);
      return;
    }
    enemyParalyzed = false;
    addLog('ability', '적 마비로 턴 스킵');
    updateStatusIcons();
    $('atk-btn').disabled = false;
    if (autoMode) scheduleAutoAttack(400);
    return;
  }
""",
'realtime paralyze transfer')

# 9) Neutral normal-match disconnect result title/description.
replace_once(
"""  const title = win ? (isDuel ? '결투 승리!' : '승리!') : (isDuel ? '결투 패배...' : '패배...');
  let desc = '';
""",
"""  const duelVoid = !!(isDuel && !win && /무효/.test(defeatReason || reason || ''));
  const title = duelVoid ? '결투 무효' : (win ? (isDuel ? '결투 승리!' : '승리!') : (isDuel ? '결투 패배...' : '패배...'));
  let desc = '';
""",
'neutral disconnect title')

replace_once(
"""  } else {
    if (isDuel) {
      desc = (rivalNick ? rivalNick + ' 님에게 패배' : '결투 패배') + (defeatReason ? ('\\n' + defeatReason) : '');
    } else if (defeatReason) {
""",
"""  } else {
    if (duelVoid) {
      desc = '상대 연결이 종료되어 일반전 기록과 보상에 반영되지 않습니다.';
    } else if (isDuel) {
      desc = (rivalNick ? rivalNick + ' 님에게 패배' : '결투 패배') + (defeatReason ? ('\\n' + defeatReason) : '');
    } else if (defeatReason) {
""",
'neutral disconnect description')

# UI result class for neutral should not be red defeat styling.
replace_once(
"""        rt.className = 'result-title ' + (win ? 'win' : 'lose');
""",
"""        rt.className = 'result-title ' + (duelVoid ? '' : (win ? 'win' : 'lose'));
""",
'neutral result style')

# Sanity checks for all requested fixes.
required = [
    "myState: rtSnapshotPlayerState()",
    "oppState: rtSnapshotEnemyState()",
    "rtOppBuild = rtNormalizeBuild(data)",
    "const hostFirst = rand() < 0.5",
    "상대 연결 종료 · 일반전 무효",
    "return trustedAttendanceToday || (saveData.missions && saveData.missions.day) || ''",
    "const prefix = playerClass === 'sword' ? 'sw' : (playerClass === 'mage' ? 'st' : '')",
    "const maxEnhanceLevel = getEnhanceMaxLevel()",
    "if (abilityW.lifesteal && dealt > 0)",
    "if (abilityW.lifesteal && actual > 0)",
    "if (box) box.style.display = (duelFlow || inRoom) ? 'block' : 'none'",
]
for needle in required:
    if needle not in s:
        raise SystemExit(f'missing postcondition: {needle}')

p.write_text(s, encoding='utf-8')
print('core bug fixes applied successfully')

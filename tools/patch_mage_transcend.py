from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s = s.replace(old, new, 1)


def replace_after(marker, old, new, label):
    global s
    i = s.find(marker)
    if i < 0:
        raise SystemExit(f'{label}: marker not found')
    j = s.find(old, i)
    if j < 0:
        raise SystemExit(f'{label}: target not found after marker')
    s = s[:j] + new + s[j+len(old):]

# 1) 전투 UI: 스킬 버튼 + +20 선택/편집 팝업
replace_once(
'''    <button class="btn" id="atk-btn" onclick="playerAttack()">공격!</button>
    <button class="btn btn-danger" id="auto-btn" onclick="toggleAuto()" style="display:none;">자동 전투</button>''',
'''    <button class="btn" id="atk-btn" onclick="playerAttack()">공격!</button>
    <button class="btn btn-gold" id="mage-skill-btn" onclick="useMageSkill()" style="display:none;" disabled>✨ 스킬</button>
    <div id="mage-skill-status" style="display:none;text-align:center;font-size:0.8rem;color:#cbb8ff;margin:-2px 0 6px;"></div>
    <button class="btn btn-danger" id="auto-btn" onclick="toggleAuto()" style="display:none;">자동 전투</button>''',
'battle skill button')

replace_once(
'''  <!-- 특수 이펙트 -->
  <div id="fx-overlay"></div>''',
'''  <!-- +20 마법사 스킬 선택 -->
  <div id="mage20-choice-popup" style="display:none;position:absolute;inset:0;background:rgba(0,0,0,0.88);z-index:360;align-items:center;justify-content:center;padding:18px;">
    <div style="width:100%;max-width:420px;background:linear-gradient(145deg,#15152a,#302b63);border:2px solid #ffd700;border-radius:18px;padding:18px;">
      <h2 style="margin:0 0 8px;">🌌 천지의 선택</h2>
      <p style="font-size:0.85rem;opacity:0.85;text-align:center;margin-bottom:12px;">+20 천지창조 · 전투당 1회</p>
      <button class="btn btn-gold" onclick="chooseMage20Skill('creation')">🌌 천지창조</button>
      <p style="font-size:0.78rem;opacity:0.75;margin:-2px 4px 8px;">상대 강화레벨·공격력·능력을 원하는 값으로 재구성</p>
      <button class="btn btn-danger" onclick="chooseMage20Skill('annihilation')">☄️ 만물의 소멸</button>
      <p style="font-size:0.78rem;opacity:0.75;margin:-2px 4px 8px;">회피·보호막·무효·부활을 무시하고 반드시 소멸</p>
      <button class="btn" onclick="closeMage20Choice()">취소</button>
    </div>
  </div>

  <div id="mage20-create-popup" style="display:none;position:absolute;inset:0;background:rgba(0,0,0,0.9);z-index:370;align-items:center;justify-content:center;padding:18px;">
    <div style="width:100%;max-width:420px;background:linear-gradient(145deg,#15152a,#302b63);border:2px solid #8e7dff;border-radius:18px;padding:18px;">
      <h2 style="margin:0 0 10px;">🌌 천지창조</h2>
      <label style="display:block;font-size:0.82rem;margin-top:8px;">상대 강화 레벨 (0~20)</label>
      <input id="creation-level" type="number" min="0" max="20" value="10" style="width:100%;padding:10px;border-radius:9px;border:1px solid #6655aa;background:#111126;color:#fff;">
      <label style="display:block;font-size:0.82rem;margin-top:8px;">상대 공격력 (0~9999)</label>
      <input id="creation-atk" type="number" min="0" max="9999" value="0" style="width:100%;padding:10px;border-radius:9px;border:1px solid #6655aa;background:#111126;color:#fff;">
      <label style="display:block;font-size:0.82rem;margin-top:8px;">상대 능력</label>
      <select id="creation-ability" style="width:100%;padding:10px;border-radius:9px;border:1px solid #6655aa;background:#111126;color:#fff;">
        <option value="none">능력 없음</option>
        <option value="seal">봉인</option>
        <option value="curse">저주</option>
        <option value="corrupt">부패</option>
        <option value="fall">타락</option>
        <option value="paralyze">마비</option>
        <option value="fire">화염</option>
        <option value="instant">즉사</option>
        <option value="double">이중 공격</option>
        <option value="mirror">미러링</option>
        <option value="purify">정화</option>
        <option value="halfkill">몰락의 밤</option>
        <option value="dodge">공격 무시</option>
        <option value="nullify">능력 무효</option>
        <option value="absorb">생명 흡수</option>
        <option value="lifesteal">흡혈</option>
      </select>
      <label style="display:block;font-size:0.82rem;margin-top:8px;">능력 수치 (%)</label>
      <input id="creation-rate" type="number" min="0" max="100" value="50" style="width:100%;padding:10px;border-radius:9px;border:1px solid #6655aa;background:#111126;color:#fff;">
      <p style="font-size:0.72rem;opacity:0.65;margin-top:5px;">확률형 능력은 발동 확률, 흡수/흡혈은 흡수 비율로 적용됩니다.</p>
      <button class="btn btn-gold" style="margin-top:12px;" onclick="applyMage20Creation()">천지창조 적용</button>
      <button class="btn" onclick="cancelMage20Creation()">취소</button>
    </div>
  </div>

  <!-- 특수 이펙트 -->
  <div id="fx-overlay"></div>''',
'mage20 popups')

# 2) +11~+20 마법사 무기: +10 복사 금지, 각 단계 고유 능력
marker = 'function getWeapon(cls, lv, awakened, awakenType) {'
idx = s.find(marker)
if idx < 0:
    raise SystemExit('getWeapon marker missing')
const_block = r'''const MAGE_TRANSCEND_WEAPONS = Object.freeze({
  11: Object.freeze({ name: '고대의 전설', atk: 65, seal: 0.05, curse: 0.15, desc: '봉인 5% · 저주 15%' }),
  12: Object.freeze({ name: '신 전설의 시작', atk: 75, mythicStart: true, desc: '스킬 「신화의 시작」 · 자신의 2번째 턴부터 사용 · 사용 시 공격력 +15% 누적 · 사용 후 2턴 충전' }),
  13: Object.freeze({ name: '파멸의 징조', atk: 110, omenChance: 0.30, desc: '패시브: 자신의 턴마다 30% 징조 부여 · 다음 자신의 턴에 공격력 150% 추가 공격' }),
  14: Object.freeze({ name: '파멸의 노래', atk: 35, requiem: true, desc: '스킬 「레퀴엠」 · 4턴마다 사용 · 상대 최대 체력 30% 피해' }),
  15: Object.freeze({ name: '공허균열의 지팡이', atk: 140, rift: 0.40, desc: '균열 40% · 공격 데미지 2배 · 보호막/정화 무시' }),
  16: Object.freeze({ name: '만물의 혼돈', atk: 175, fall: 0.05, corrupt: 0.05, rift: 0.05, paralyze: 0.05, fire: true, fireRate: 0.05, instant: 0.05, desc: '타락·부패·균열·마비·화염·즉사 각각 5%' }),
  17: Object.freeze({ name: '만물의 근절', atk: 195, nightfallSkill: true, desc: '스킬 「몰락의 밤」 · 3턴마다 사용 · 상대 현재 체력 절반 삭제' }),
  18: Object.freeze({ name: '만물의 근원', atk: 220, lifeSpring: true, desc: '스킬 「생명의 샘」 · 7턴마다 사용 · 풀피 회복 + 상대 2턴 일반 공격 데미지 무시(능력/스킬 제외)' }),
  19: Object.freeze({ name: '무한회귀의 지팡이', atk: 250, checkpoint: true, desc: '1·3번째 자신의 턴 체크포인트 · 이후 3턴마다 회귀 기회 +1 · 사망 시 기회 1개로 체크포인트 체력 부활' }),
  20: Object.freeze({ name: '천지창조', atk: 500, creationChoice: true, desc: '자신의 2번째 턴부터 전투당 1회 · 「천지창조」 또는 「만물의 소멸」 선택' })
});

'''
s = s[:idx] + const_block + s[idx:]

old_overcap = '''  const weapon = Object.assign({}, list[Math.min(lv - 1, 9)]);
  if (lv > 10 && (cls === 'sword' || cls === 'mage')) {
    const extra = Math.max(0, lv - 10);
    weapon.atk = Math.max(0, Math.round((Number(weapon.atk) || 0) * (1 + extra * 0.10)));
    weapon.name = (TRANSCEND_WEAPON_NAMES[cls] && TRANSCEND_WEAPON_NAMES[cls][lv]) || `${weapon.name} · 초월 +${lv}`;
    weapon.desc = `초월 강화: +10 이후 단계당 공격력 +10% · ${weapon.desc || '기본 능력 유지'}`;
  }
  return weapon;'''
new_overcap = '''  if (lv > 10 && cls === 'mage') {
    const t = MAGE_TRANSCEND_WEAPONS[Math.min(20, Math.max(11, lv))];
    return Object.assign({}, t);
  }
  const weapon = Object.assign({}, list[Math.min(lv - 1, 9)]);
  if (lv > 10 && cls === 'sword') {
    const extra = Math.max(0, lv - 10);
    weapon.atk = Math.max(0, Math.round((Number(weapon.atk) || 0) * (1 + extra * 0.10)));
    weapon.name = (TRANSCEND_WEAPON_NAMES[cls] && TRANSCEND_WEAPON_NAMES[cls][lv]) || `${weapon.name} · 초월 +${lv}`;
    weapon.desc = `초월 강화: +10 이후 단계당 공격력 +10% · ${weapon.desc || '기본 능력 유지'}`;
  }
  return weapon;'''
replace_once(old_overcap, new_overcap, 'getWeapon overcap')

# 3) 전투 상태
replace_once(
'''let enemyShieldUsed = false;

// 이벤트(구 보스전)''',
'''let enemyShieldUsed = false;

// 마법사 +11~+20 초월 전투 상태
let playerTurnCount = 0;
let mageSkillNextReadyTurn = 0;
let mage12BuffStacks = 0;
let mage13OmenPending = false;
let mage18NormalImmuneEnemyTurns = 0;
let mage18EnemyTurnNormalImmune = false;
let mage19CheckpointHp = 0;
let mage19RewindCharges = 0;
let mage20SkillUsed = false;

// 이벤트(구 보스전)''',
'mage transcend state')

# 4) 균열의 보호막 관통 지원
replace_once(
'''function dmgEnemy(amount) {
  // 보스 그림자: 3공격 이후 확정 회피''',
'''function dmgEnemy(amount, options) {
  options = options || {};
  // 보스 그림자: 3공격 이후 확정 회피''',
'dmgEnemy signature')
replace_once(
'''  amount = Math.max(0, amount);
  if (amount > 0) tryEmergencyShield(false, amount);
  if (enemyShield > 0) {''',
'''  amount = Math.max(0, amount);
  if (amount > 0 && !options.bypassShield) tryEmergencyShield(false, amount);
  if (!options.bypassShield && enemyShield > 0) {''',
'dmgEnemy shield bypass')

# 5) 상태 아이콘에 초월 상태 표시
replace_once(
'''  if (playerShield > 0) pIcons.push('🛡️보호막' + playerShield);
  if ($('p-status')) $('p-status').textContent = pIcons.join(' ');''',
'''  if (playerShield > 0) pIcons.push('🛡️보호막' + playerShield);
  if (playerClass === 'mage' && level === 12 && mage12BuffStacks > 0) pIcons.push(`📖신화+${mage12BuffStacks * 15}%`);
  if (playerClass === 'mage' && level === 18 && mage18NormalImmuneEnemyTurns > 0) pIcons.push(`💧일반무효${mage18NormalImmuneEnemyTurns}`);
  if (playerClass === 'mage' && level === 19 && mage19RewindCharges > 0) pIcons.push(`⏪회귀x${mage19RewindCharges}`);
  if ($('p-status')) $('p-status').textContent = pIcons.join(' ');''',
'player transcend icons')
replace_once(
'''  if (enemyShield > 0) eIcons.push('🛡️보호막' + enemyShield);
  if ($('e-status')) $('e-status').textContent = eIcons.join(' ');''',
'''  if (enemyShield > 0) eIcons.push('🛡️보호막' + enemyShield);
  if (playerClass === 'mage' && level === 13 && mage13OmenPending) eIcons.push('☄️징조');
  if ($('e-status')) $('e-status').textContent = eIcons.join(' ');''',
'enemy omen icon')

# 6) 초월 스킬/패시브 헬퍼를 playerAttack 앞에 삽입
helpers = r'''
function resetMageTranscendBattleState() {
  playerTurnCount = 0;
  mage12BuffStacks = 0;
  mage13OmenPending = false;
  mage18NormalImmuneEnemyTurns = 0;
  mage18EnemyTurnNormalImmune = false;
  mage19CheckpointHp = 0;
  mage19RewindCharges = 0;
  mage20SkillUsed = false;
  if (playerClass === 'mage') {
    if (level === 12) mageSkillNextReadyTurn = 2;
    else if (level === 14) mageSkillNextReadyTurn = 4;
    else if (level === 17) mageSkillNextReadyTurn = 3;
    else if (level === 18) mageSkillNextReadyTurn = 7;
    else if (level === 20) mageSkillNextReadyTurn = 2;
    else mageSkillNextReadyTurn = 0;
  } else {
    mageSkillNextReadyTurn = 0;
  }
  closeMage20Choice();
  cancelMage20Creation();
}

function mageActiveSkillInfo() {
  if (playerClass !== 'mage') return null;
  if (level === 12) return { name: '신화의 시작', cooldown: 2, icon: '📖' };
  if (level === 14) return { name: '레퀴엠', cooldown: 4, icon: '🎼' };
  if (level === 17) return { name: '몰락의 밤', cooldown: 3, icon: '🌑' };
  if (level === 18) return { name: '생명의 샘', cooldown: 7, icon: '💧' };
  if (level === 20) return { name: '천지의 선택', cooldown: 0, icon: '🌌' };
  return null;
}

function canUseMageSkillNow() {
  const info = mageActiveSkillInfo();
  if (!info || battleEnded || playerAttackLock || rtActive) return false;
  if (playerParalyzed || playerSealed || playerCursed > 0) return false;
  if (level === 20 && mage20SkillUsed) return false;
  const upcomingTurn = playerTurnCount + 1;
  return upcomingTurn >= mageSkillNextReadyTurn;
}

function updateMageSkillButton() {
  const btn = $('mage-skill-btn');
  const st = $('mage-skill-status');
  if (!btn || !st) return;
  const info = mageActiveSkillInfo();
  if (!info || battleEnded || rtActive) {
    btn.style.display = 'none';
    st.style.display = 'none';
    return;
  }
  btn.style.display = 'block';
  st.style.display = 'block';
  btn.textContent = `${info.icon} 스킬: ${info.name}`;
  const upcomingTurn = playerTurnCount + 1;
  let status = '';
  if (level === 20 && mage20SkillUsed) {
    status = '전투당 1회 사용 완료';
  } else if (playerParalyzed || playerSealed) {
    status = '상태이상으로 이번 턴 스킬 사용 불가';
  } else if (playerCursed > 0) {
    status = '저주로 스킬 사용 불가';
  } else if (upcomingTurn >= mageSkillNextReadyTurn) {
    status = `사용 가능 · 자신의 ${upcomingTurn}번째 턴`;
  } else {
    status = `다음 사용 가능: 자신의 ${mageSkillNextReadyTurn}번째 턴`;
  }
  btn.disabled = !canUseMageSkillNow();
  st.textContent = status;
}

async function resolveEnemyDeathFromMageSkill(reason) {
  if (!enemy || enemy.hp > 0) return false;
  if (enemyAwakened && !enemyLastStandUsed) {
    enemyLastStandUsed = true;
    if (enemyAwakenType === 'guardian') enemy.hp = Math.max(1, Math.floor(enemy.maxHp * 0.25));
    else enemy.hp = 1;
    await showAbility('🛡️ 적의 최후의 저항!', '처치를 버텼다!');
  }
  if (enemy.hp <= 0 && !enemy.revived) {
    const ew = enemyAwakened
      ? (enemyAwakenType === 'guardian' ? GUARDIAN : EXCALIBUR)
      : enemy.weapon;
    if (ew && ew.revive) {
      enemy.revived = true;
      enemy.hp = Math.max(1, Math.floor(enemy.maxHp * 0.5));
      await showAbility('👑 적 부활!', '적이 체력 50%로 부활했다!');
    }
  }
  if (enemy.hp <= 0 && await tryBossTransform()) {
    updateHPBars();
    return false;
  }
  if (enemy.hp <= 0) {
    endBattle(true, reason || '스킬 처치');
    return true;
  }
  updateHPBars();
  return false;
}

async function beginPlayerActionTurn() {
  playerTurnCount++;

  if (playerClass === 'mage' && level === 13) {
    if (mage13OmenPending && enemy && enemy.hp > 0) {
      mage13OmenPending = false;
      const omenDamage = Math.max(1, Math.round((getWeapon('mage', 13, false, null).atk || 0) * 1.5));
      const actual = dmgEnemy(omenDamage);
      await showAbility('☄️ 파멸의 징조!', `징조 폭발! ${actual} 피해`);
      addLog('ability', `파멸의 징조: ${actual} 피해`);
      updateHPBars();
      updateStatusIcons();
      if (await resolveEnemyDeathFromMageSkill('파멸의 징조')) return true;
    }
    if (enemy && enemy.hp > 0 && rand() < 0.30) {
      mage13OmenPending = true;
      await showAbility('☄️ 징조 부여!', '다음 자신의 턴에 공격력 150%의 징조 공격!');
      addLog('ability', '상대에게 파멸의 징조 부여');
      updateStatusIcons();
    }
  }

  if (playerClass === 'mage' && level === 19) {
    if (playerTurnCount === 1 || playerTurnCount === 3) {
      mage19CheckpointHp = Math.max(1, Math.floor(hp));
      await showAbility('⏪ 체크포인트', `${playerTurnCount}번째 턴 체력 ${mage19CheckpointHp} 저장`);
      addLog('ability', `체크포인트 저장: HP ${mage19CheckpointHp}`);
    }
    if (playerTurnCount >= 6 && (playerTurnCount - 3) % 3 === 0) {
      mage19RewindCharges++;
      await showAbility('♾️ 무한회귀', `회귀 기회 +1 (현재 ${mage19RewindCharges})`);
      addLog('ability', `회귀 기회 +1 (현재 ${mage19RewindCharges})`);
      updateStatusIcons();
    }
  }
  return false;
}

function tryMage19CheckpointRevive(reason) {
  if (playerClass !== 'mage' || level !== 19 || hp > 0) return false;
  if (mage19RewindCharges <= 0 || mage19CheckpointHp <= 0) return false;
  if (/강제 종료|항복|연결|소멸/.test(String(reason || ''))) return false;
  mage19RewindCharges--;
  hp = clamp(mage19CheckpointHp, 1, maxHp);
  battleEnded = false;
  playerAttackLock = false;
  autoMode = false;
  addLog('ability', `⏪ 무한회귀! 체크포인트 HP ${hp}로 부활 (남은 기회 ${mage19RewindCharges})`);
  updateHPBars();
  updateStatusIcons();
  showAbility('⏪ 무한회귀!', `체크포인트 HP ${hp}로 부활! 남은 기회 ${mage19RewindCharges}`);
  try {
    const atk = $('atk-btn');
    if (atk) { atk.style.display = 'block'; atk.disabled = false; }
  } catch (e) {}
  updateMageSkillButton();
  return true;
}

function closeMage20Choice() {
  const p = $('mage20-choice-popup');
  if (p) p.style.display = 'none';
}
function cancelMage20Creation() {
  const p = $('mage20-create-popup');
  if (p) p.style.display = 'none';
}
function openMage20Choice() {
  if (!canUseMageSkillNow() || level !== 20) return;
  const p = $('mage20-choice-popup');
  if (p) p.style.display = 'flex';
}
function chooseMage20Skill(kind) {
  closeMage20Choice();
  if (kind === 'annihilation') {
    executeMage20Annihilation();
    return;
  }
  if (kind === 'creation') {
    const lv = $('creation-level');
    const atk = $('creation-atk');
    if (lv) lv.value = String(clamp(Number(enemy && enemy.level) || 0, 0, 20));
    if (atk) atk.value = String(Math.max(0, Number(enemy && enemy.weapon && enemy.weapon.atk) || Number(enemy && enemy.atk) || 0));
    const p = $('mage20-create-popup');
    if (p) p.style.display = 'flex';
  }
}

function buildCreationAbilityWeapon(atk, abilityKey, percent) {
  const rate = clamp(Number(percent) || 0, 0, 100) / 100;
  const w = { name: '천지창조로 재구성된 무기', atk: Math.max(0, Math.floor(atk)), desc: '능력 없음' };
  const labels = {
    seal: '봉인', curse: '저주', corrupt: '부패', fall: '타락', paralyze: '마비', fire: '화염',
    instant: '즉사', double: '이중 공격', mirror: '미러링', purify: '정화', halfkill: '몰락의 밤',
    dodge: '공격 무시', nullify: '능력 무효', absorb: '생명 흡수', lifesteal: '흡혈'
  };
  if (!abilityKey || abilityKey === 'none') return w;
  if (abilityKey === 'fire') { w.fire = true; w.fireRate = rate; }
  else if (abilityKey === 'absorb') w.absorb = rate;
  else if (abilityKey === 'lifesteal') w.lifesteal = rate;
  else w[abilityKey] = rate;
  w.desc = `천지창조: ${labels[abilityKey] || abilityKey} ${Math.round(rate * 100)}%`;
  return w;
}

async function applyMage20Creation() {
  if (!canUseMageSkillNow() || level !== 20 || !enemy) return;
  cancelMage20Creation();
  playerAttackLock = true;
  try {
    const endedByPassive = await beginPlayerActionTurn();
    if (endedByPassive) return;
    mage20SkillUsed = true;
    mageSkillNextReadyTurn = 999999;
    const newLv = clamp(Math.floor(Number($('creation-level') && $('creation-level').value) || 0), 0, 20);
    const newAtk = clamp(Math.floor(Number($('creation-atk') && $('creation-atk').value) || 0), 0, 9999);
    const abilityKey = String(($('creation-ability') && $('creation-ability').value) || 'none');
    const rate = clamp(Number($('creation-rate') && $('creation-rate').value) || 0, 0, 100);
    const newWeapon = buildCreationAbilityWeapon(newAtk, abilityKey, rate);
    enemy.level = newLv;
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
    addLog('ability', `천지창조: 상대 +${newLv}, ATK ${newAtk}, ${newWeapon.desc}`);
    updateMageSkillButton();
    await enemyAttack();
  } finally {
    playerAttackLock = false;
    updateMageSkillButton();
  }
}

async function executeMage20Annihilation() {
  if (!canUseMageSkillNow() || level !== 20 || !enemy) return;
  playerAttackLock = true;
  try {
    const endedByPassive = await beginPlayerActionTurn();
    if (endedByPassive) return;
    mage20SkillUsed = true;
    mageSkillNextReadyTurn = 999999;
    enemy.hp = 0;
    enemy.revived = true;
    enemyLastStandUsed = true;
    enemy.undying = false;
    await playFx('kill');
    await showAbility('☄️ 만물의 소멸', '대상을 존재째 소멸시켰다. 회피·무효·보호막·부활 불가.');
    addLog('ability', '만물의 소멸 — 대상 완전 소멸');
    updateHPBars();
    endBattle(true, '만물의 소멸');
  } finally {
    playerAttackLock = false;
    updateMageSkillButton();
  }
}

async function useMageSkill() {
  if (level === 20) {
    if (canUseMageSkillNow()) openMage20Choice();
    return;
  }
  if (!canUseMageSkillNow()) return;
  const info = mageActiveSkillInfo();
  if (!info || !enemy) return;
  playerAttackLock = true;
  try {
    const endedByPassive = await beginPlayerActionTurn();
    if (endedByPassive) return;
    const turnUsed = playerTurnCount;
    mageSkillNextReadyTurn = turnUsed + info.cooldown;

    if (level === 12) {
      mage12BuffStacks++;
      await showAbility('📖 신화의 시작', `공격력 +15% 누적! 현재 +${mage12BuffStacks * 15}%`);
      addLog('ability', `신화의 시작: 공격력 +${mage12BuffStacks * 15}%`);
    } else if (level === 14) {
      const raw = Math.max(1, Math.floor(enemy.maxHp * 0.30));
      const actual = dmgEnemy(raw);
      await showAbility('🎼 레퀴엠', `상대 최대 체력의 30% · ${actual} 피해!`);
      addLog('ability', `레퀴엠: ${actual} 피해`);
    } else if (level === 17) {
      const raw = Math.max(1, Math.floor(enemy.hp * 0.50));
      const actual = dmgEnemy(raw);
      await showAbility('🌑 몰락의 밤', `상대 현재 체력 절반 · ${actual} 피해!`);
      addLog('ability', `몰락의 밤: ${actual} 피해`);
    } else if (level === 18) {
      hp = maxHp;
      mage18NormalImmuneEnemyTurns = 2;
      await showAbility('💧 생명의 샘', '체력 완전 회복! 상대의 다음 2턴 일반 공격 데미지를 무시합니다. (능력/스킬 제외)');
      addLog('ability', '생명의 샘: 풀피 + 일반 공격 무효 2턴');
    }

    updateHPBars();
    updateStatusIcons();
    updateMageSkillButton();
    if (await resolveEnemyDeathFromMageSkill(info.name)) return;
    await enemyAttack();
  } finally {
    playerAttackLock = false;
    updateMageSkillButton();
  }
}

'''
insert_marker = 'let playerAttackLock = false;\nasync function playerAttack() {'
replace_once(insert_marker, helpers + insert_marker, 'mage helper insertion')

# 7) playerAttack: 자신의 턴 카운트/패시브 -> 공격
replace_once(
'''  playerAttackLock = true;
  $('atk-btn').disabled = true;
  updateStatusIcons();
  try {
''',
'''  playerAttackLock = true;
  $('atk-btn').disabled = true;
  updateMageSkillButton();
  updateStatusIcons();
  try {
    const endedByMagePassive = await beginPlayerActionTurn();
    if (endedByMagePassive) return;
''',
'player turn begin')

# +12 누적 공격력
replace_after(
'async function playerAttack() {',
'''  let dmg = w.atk || 0;
  if (playerCursed > 0) dmg = Math.floor(dmg * Math.pow(0.7, playerCursed));''',
'''  let dmg = w.atk || 0;
  if (playerClass === 'mage' && level === 12 && mage12BuffStacks > 0) {
    dmg = Math.round(dmg * (1 + mage12BuffStacks * 0.15));
  }
  if (playerCursed > 0) dmg = Math.floor(dmg * Math.pow(0.7, playerCursed));''',
'mage12 attack buff')

# 균열은 데미지 2배 + 보호막 관통
replace_after(
'async function playerAttack() {',
'''  // 데미지 적용
  let dealtToEnemy = 0;''',
'''  // 균열: +15 40%, +16 5% — 데미지 2배 + 보호막/정화 무시
  let riftThisTurn = false;
  if (canAbility && !fallSelf && abilityW.rift && rand() < abilityW.rift) {
    riftThisTurn = true;
    dmg *= 2;
    await showAbility('🕳️ 균열!', `공격 데미지 2배 (${dmg}) · 보호막/정화 무시!`);
    addLog('ability', `균열 발동: ${dmg} 데미지`);
  }

  // 데미지 적용
  let dealtToEnemy = 0;''',
'rift proc')
replace_after('async function playerAttack() {', '    const dealt = dmgEnemy(dmg);', '    const dealt = dmgEnemy(dmg, { bypassShield: riftThisTurn });', 'rift first hit')
replace_after('async function playerAttack() {', '      const dealt2 = dmgEnemy(dmg);', '      const dealt2 = dmgEnemy(dmg, { bypassShield: riftThisTurn });', 'rift double hit')

# finally에서 스킬 버튼 갱신
replace_after(
'async function playerAttack() {',
'''  } finally {
    playerAttackLock = false;
  }
}

async function enemyAttack() {''',
'''  } finally {
    playerAttackLock = false;
    updateMageSkillButton();
  }
}

async function enemyAttack() {''',
'player attack finally')

# 8) 생명의 샘: 적의 다음 2턴 일반 공격 데미지만 무시
replace_once(
'''async function enemyAttack() {
  if (battleEnded) return;
  enemyTurnCount++;
  lastDamageTaken = 0;''',
'''async function enemyAttack() {
  if (battleEnded) return;
  enemyTurnCount++;
  mage18EnemyTurnNormalImmune = playerClass === 'mage' && level === 18 && mage18NormalImmuneEnemyTurns > 0;
  if (mage18EnemyTurnNormalImmune) mage18NormalImmuneEnemyTurns--;
  lastDamageTaken = 0;''',
'enemy turn life spring')

boss_damage_old = '''    let actual = 0;
    if (!bossDodged) {
      actual = dmgPlayer(dmg);
      lastDamageTaken += actual;
      addLog('enemy', `${enemy.name}의 공격! ${dmg} 데미지`);
      if (bossDoubleHit) {
        const actual2 = dmgPlayer(dmg);
        lastDamageTaken += actual2;
        actual += actual2;
        addLog('enemy', `이중 2타! ${dmg}`);
      }
      if (enemy.lifestealOnHit && actual > 0) {'''
boss_damage_new = '''    let actual = 0;
    if (!bossDodged) {
      if (mage18EnemyTurnNormalImmune && !usedSkill) {
        await showAbility('💧 생명의 샘!', '상대의 일반 공격 데미지를 무시했다!');
        addLog('ability', `${enemy.name}의 일반 공격 무효`);
      } else {
        actual = dmgPlayer(dmg);
        lastDamageTaken += actual;
        addLog('enemy', `${enemy.name}의 공격! ${dmg} 데미지`);
        if (bossDoubleHit) {
          const actual2 = dmgPlayer(dmg);
          lastDamageTaken += actual2;
          actual += actual2;
          addLog('enemy', `이중 2타! ${dmg}`);
        }
      }
      if (enemy.lifestealOnHit && actual > 0) {'''
replace_once(boss_damage_old, boss_damage_new, 'boss normal immunity')

# 일반 적 기본 공격만 무시 (부패/즉사/마비/화염 등 능력은 위에서 그대로 처리)
replace_after(
'  } else if (!dodged) {',
'''    const actual = dmgPlayer(dmg);
    lastDamageTaken += actual;
    addLog('enemy', logMsg);''',
'''    let actual = 0;
    if (mage18EnemyTurnNormalImmune) {
      await showAbility('💧 생명의 샘!', '상대의 일반 공격 데미지를 무시했다!');
      addLog('ability', '생명의 샘: 일반 공격 무효');
    } else {
      actual = dmgPlayer(dmg);
      lastDamageTaken += actual;
      addLog('enemy', logMsg);
    }''',
'generic normal immunity')
replace_after(
'    if (typeof enemyDoubleHit !== \'undefined\' && enemyDoubleHit) {',
'''      const actual2 = dmgPlayer(dmg);
      lastDamageTaken += actual2;
      addLog('enemy', `이중 2타! ${dmg}`);''',
'''      let actual2 = 0;
      if (mage18EnemyTurnNormalImmune) {
        addLog('ability', '생명의 샘: 이중 공격 2타 무효');
      } else {
        actual2 = dmgPlayer(dmg);
        lastDamageTaken += actual2;
        addLog('enemy', `이중 2타! ${dmg}`);
      }''',
'generic double immunity')

# 9) 모든 전투 시작 시 초월 상태 초기화
s = s.replace(
"  battleFlags = { tookDamage: false, minHpRatio: 1, awakened: false, shieldUsed: false };\n",
"  battleFlags = { tookDamage: false, minHpRatio: 1, awakened: false, shieldUsed: false };\n  resetMageTranscendBattleState();\n")

# 전투 화면 진입 시 스킬 버튼 표시 갱신 (일반/실시간 모두)
s = s.replace(
"  $('atk-btn').style.display = 'block';\n",
"  $('atk-btn').style.display = 'block';\n  updateMageSkillButton();\n")

# 10) 패배 직전 +19 회귀 처리, 종료 시 스킬 UI 숨김
replace_once(
'''function endBattle(win, reason) {
  // 이미 끝났어도 결과 화면만 다시 보장''',
'''function endBattle(win, reason) {
  if (!win && tryMage19CheckpointRevive(reason)) return;
  // 이미 끝났어도 결과 화면만 다시 보장''',
'endBattle checkpoint revive')
replace_once(
'''  battleEnded = true;
  playerAttackLock = false;
  autoMode = false;
  if (reason) defeatReason = reason;''',
'''  battleEnded = true;
  playerAttackLock = false;
  autoMode = false;
  try {
    const ms = $('mage-skill-btn'); if (ms) { ms.style.display = 'none'; ms.disabled = true; }
    const mst = $('mage-skill-status'); if (mst) mst.style.display = 'none';
    closeMage20Choice(); cancelMage20Creation();
  } catch (e) {}
  if (reason) defeatReason = reason;''',
'endBattle skill cleanup')

replace_once(
'''    const bp = $('badge-popup');
    if (bp) bp.style.display = 'none';
  } catch (e) {}''',
'''    const bp = $('badge-popup');
    if (bp) bp.style.display = 'none';
    const m20 = $('mage20-choice-popup'); if (m20) m20.style.display = 'none';
    const m20c = $('mage20-create-popup'); if (m20c) m20c.style.display = 'none';
  } catch (e) {}''',
'clear overlays mage20')

p.write_text(s, encoding='utf-8')
print('mage transcend patch applied')

from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

replacements = [
    (
        "14: Object.freeze({ name: '파멸의 노래', atk: 35, requiem: true, desc: '스킬 「레퀴엠」 · 4턴마다 사용 · 상대 최대 체력 30% 피해' }),",
        "14: Object.freeze({ name: '파멸의 노래', atk: 35, requiem: true, desc: '스킬 「레퀴엠」 · 4턴마다 사용 · 상대 최대 체력 20% 피해 · 사망 후 최후의 레퀴엠 1회' }),"
    ),
    (
        "let mage13OmenPending = false;\nlet mage18NormalImmuneEnemyTurns = 0;",
        "let mage13OmenPending = false;\nlet mage14DeathRequiemPending = false;\nlet mage14DeathRequiemUsed = false;\nlet mage18NormalImmuneEnemyTurns = 0;"
    ),
    (
        "function resetMageTranscendBattleState() {\n  playerTurnCount = 0;\n  mage12BuffStacks = 0;\n  mage13OmenPending = false;",
        "function resetMageTranscendBattleState() {\n  playerTurnCount = 0;\n  mage12BuffStacks = 0;\n  mage13OmenPending = false;\n  mage14DeathRequiemPending = false;\n  mage14DeathRequiemUsed = false;"
    ),
    (
        "function canUseMageSkillNow() {\n  const info = mageActiveSkillInfo();\n  if (!info || battleEnded || playerAttackLock || rtActive || autoMode) return false;",
        "function canUseMageSkillNow() {\n  if (mage14DeathRequiemPending && !mage14DeathRequiemUsed && playerClass === 'mage' && level === 14) return true;\n  const info = mageActiveSkillInfo();\n  if (!info || battleEnded || playerAttackLock || rtActive || autoMode) return false;"
    ),
    (
        "function updateMageSkillButton() {\n  const btn = $('mage-skill-btn');\n  const st = $('mage-skill-status');\n  if (!btn || !st) return;\n  const info = mageActiveSkillInfo();",
        "function updateMageSkillButton() {\n  const btn = $('mage-skill-btn');\n  const st = $('mage-skill-status');\n  if (!btn || !st) return;\n  if (mage14DeathRequiemPending && !mage14DeathRequiemUsed && playerClass === 'mage' && level === 14) {\n    btn.style.display = 'block';\n    st.style.display = 'block';\n    btn.textContent = '🎼 스킬: 최후의 레퀴엠';\n    btn.disabled = false;\n    st.textContent = '사망 후 1회 사용 가능 · 상대 최대 체력 20% 피해';\n    return;\n  }\n  const info = mageActiveSkillInfo();"
    ),
    (
        "      const raw = Math.max(1, Math.floor(enemy.maxHp * 0.30));\n      const actual = dmgEnemy(raw);\n      await showAbility('🎼 레퀴엠', `상대 최대 체력의 30% · ${actual} 피해!`);",
        "      const raw = Math.max(1, Math.floor(enemy.maxHp * 0.20));\n      const actual = dmgEnemy(raw);\n      await showAbility('🎼 레퀴엠', `상대 최대 체력의 20% · ${actual} 피해!`);"
    ),
    (
        "async function useMageSkill() {\n  if (level === 20) {",
        "async function useMageSkill() {\n  if (mage14DeathRequiemPending && playerClass === 'mage' && level === 14) {\n    await useMage14DeathRequiem();\n    return;\n  }\n  if (level === 20) {"
    ),
    (
        "function endBattle(win, reason) {\n  if (!win && tryMage19CheckpointRevive(reason)) return;",
        "function endBattle(win, reason) {\n  if (!win && tryMage19CheckpointRevive(reason)) return;\n  if (!win && offerMage14DeathRequiem(reason)) return;"
    ),
]

for old, new in replacements:
    if old not in s:
        raise SystemExit('PATCH_TARGET_NOT_FOUND:\n' + old[:220])
    s = s.replace(old, new, 1)

anchor = "async function useMageSkill() {\n"
helper = r'''function offerMage14DeathRequiem(reason) {
  if (playerClass !== 'mage' || level !== 14) return false;
  if (mage14DeathRequiemPending || mage14DeathRequiemUsed) return false;
  if (!enemy || enemy.hp <= 0) return false;
  if (/강제 종료|항복|연결|소멸/.test(String(reason || ''))) return false;

  mage14DeathRequiemPending = true;
  battleEnded = false;
  autoMode = false;
  playerAttackLock = false;
  try {
    const atk = $('atk-btn');
    if (atk) { atk.style.display = 'block'; atk.disabled = true; }
    const auto = $('auto-btn');
    if (auto) auto.style.display = 'none';
    addLog('ability', '🎼 파멸의 노래: 사망 후 「최후의 레퀴엠」 1회 사용 가능');
    updateHPBars();
    updateStatusIcons();
    updateMageSkillButton();
  } catch (e) { console.warn('offerMage14DeathRequiem', e); }
  return true;
}

async function useMage14DeathRequiem() {
  if (!mage14DeathRequiemPending || mage14DeathRequiemUsed || !enemy) return;
  mage14DeathRequiemPending = false;
  mage14DeathRequiemUsed = true;
  playerAttackLock = true;
  try {
    const raw = Math.max(1, Math.floor(enemy.maxHp * 0.20));
    const actual = dmgEnemy(raw);
    await showAbility('🎼 최후의 레퀴엠', `죽음 뒤 마지막 연주! 상대 최대 체력의 20% · ${actual} 피해!`);
    addLog('ability', `최후의 레퀴엠: ${actual} 피해`);
    updateHPBars();
    updateStatusIcons();
    if (await resolveEnemyDeathFromMageSkill('최후의 레퀴엠')) return;
    endBattle(false, '최후의 레퀴엠 후 패배');
  } finally {
    playerAttackLock = false;
    updateMageSkillButton();
  }
}

'''
if anchor not in s:
    raise SystemExit('HELPER_ANCHOR_NOT_FOUND')
s = s.replace(anchor, helper + anchor, 1)

p.write_text(s, encoding='utf-8')

checks = [
    "상대 최대 체력 20% 피해 · 사망 후 최후의 레퀴엠 1회",
    "mage14DeathRequiemPending",
    "offerMage14DeathRequiem(reason)",
    "useMage14DeathRequiem",
    "enemy.maxHp * 0.20",
    "최후의 레퀴엠 후 패배",
]
for c in checks:
    if c not in s:
        raise SystemExit('VERIFY_MISSING: ' + c)
if "상대 최대 체력의 30% · ${actual} 피해!" in s:
    raise SystemExit('OLD_REQUIEM_DAMAGE_STILL_PRESENT')
print('mage14 patch verified')

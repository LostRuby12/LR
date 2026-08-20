from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Weapon overcap scaling for sword/mage +11~+20.
old = '  return list[Math.min(lv - 1, 9)];'
new = '''  const weapon = Object.assign({}, list[Math.min(lv - 1, 9)]);
  if (lv > 10 && (cls === 'sword' || cls === 'mage')) {
    const extra = Math.max(0, lv - 10);
    weapon.atk = Math.max(0, Math.round((Number(weapon.atk) || 0) * (1 + extra * 0.10)));
    weapon.name = `${weapon.name} · 초월 +${lv}`;
    weapon.desc = `초월 강화: +10 이후 단계당 공격력 +10% · ${weapon.desc || '기본 능력 유지'}`;
  }
  return weapon;'''
if old not in s:
    raise SystemExit('weapon return not found')
s = s.replace(old, new, 1)

# Success rates to +20.
old = "  // 0→1:100 ... 6→7:45, 7→8:30, 8→9:25, 9→10:12\n  const rates = [100, 98, 80, 75, 65, 50, 45, 30, 25, 15];\n  return rates[Math.min(lv, 9)];"
new = "  // +1~+10 기존 확률, +11~+20은 보스전 전용 초월 강화 확률\n  const rates = [100, 98, 80, 75, 65, 50, 45, 30, 25, 15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2];\n  return rates[Math.min(Math.max(0, lv), rates.length - 1)];"
if old not in s:
    raise SystemExit('rate table not found')
s = s.replace(old, new, 1)

# Boss/class-specific max level.
marker = '// ========== 강화 ==========\n'
helper = '''function getEnhanceMaxLevel() {
  if (pendingRaidBoss && selectedRaidBossId === 'fallen_god' && playerClass === 'sword') return 20;
  if (pendingRaidBoss && selectedRaidBossId === 'ancient_mage' && playerClass === 'mage') return 20;
  return 10;
}

'''
if 'function getEnhanceMaxLevel()' not in s:
    s = s.replace(marker, helper + marker, 1)

s = s.replace("  if (level >= 10) {\n    alert('이미 최고 강화(+10)입니다!');", "  const maxEnhanceLevel = getEnhanceMaxLevel();\n  if (level >= maxEnhanceLevel) {\n    alert(`이미 최고 강화(+${maxEnhanceLevel})입니다!`);", 1)
s = s.replace('    if (level >= 10) break;', '    if (level >= maxEnhanceLevel) break;', 1)
s = s.replace('      level = Math.min(10, level + 1);', '      level = Math.min(maxEnhanceLevel, level + 1);', 1)
s = s.replace('let level = 0;          // 0~10', 'let level = 0;          // 일반 0~10 · 특정 보스전 0~20', 1)

# First boss clear permanently raises base chances from 25 to 50.
s = s.replace('  chances = 25 + (shopBuff.extraChances || 0);', '  chances = (saveData.raidChance50Unlocked ? 50 : 25) + (shopBuff.extraChances || 0);', 1)

old_raid = '''  // 보스전 (고대 마법사 / 몰락한 신)
  if (gameMode === 'raid') {
    const mg = grantMission('raid');
    if (mg) pendingNewBadges.push({ icon: '📋', name: '미션', desc: `보스전 클리어 +${mg} LR` });
    persistSave();
    return;
  }'''
new_raid = '''  // 보스전 (고대 마법사 / 몰락한 신)
  if (gameMode === 'raid') {
    if (win) {
      const mg = grantMission('raid');
      if (mg) pendingNewBadges.push({ icon: '📋', name: '미션', desc: `보스전 클리어 +${mg} LR` });
      if (!saveData.raidChance50Unlocked) {
        saveData.raidChance50Unlocked = true;
        pendingNewBadges.push({ icon: '🔓', name: '보스 정복 보상', desc: '강화 기회 최대 50회 영구 해금' });
      }
      persistSave();
    }
    return;
  }'''
if old_raid not in s:
    raise SystemExit('raid reward block not found')
s = s.replace(old_raid, new_raid, 1)

# Boss picker descriptions.
s = s.replace('(상세 설정은 추후 업데이트)', '(첫 보스 클리어 시 강화 기회 50회 영구 해금)', 1)
s = s.replace('오래전 세계를 주름잡던<br>대마법사. 설정 미정', '마법사로 도전 시<br>최대 강화 +20', 1)
s = re.sub(r'(<div class="class-name">몰락한 신</div>\s*<div class="class-desc">)(.*?)(</div>)', r'\1검사로 도전 시<br>최대 강화 +20\3', s, count=1, flags=re.S)

for needed in ['function getEnhanceMaxLevel()', 'Math.min(maxEnhanceLevel, level + 1)', 'raidChance50Unlocked']:
    if needed not in s:
        raise SystemExit('missing: ' + needed)

p.write_text(s, encoding='utf-8')
print('boss progression patched')

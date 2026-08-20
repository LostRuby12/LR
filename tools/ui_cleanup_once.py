from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) 계정 시작 화면 문구 정리 + 제작자 표시
old_auth = '''  <div id="auth-screen" class="screen active">
    <h1>⚔️ 검 vs 지팡이</h1>
    <p style="text-align:center; opacity:0.82; margin:6px 0 22px;">Firebase 서버 계정</p>
    <button class="btn btn-gold" style="margin-top:10px; font-size:1.15rem;" onclick="openLoginScreen()">🔐 로그인</button>
    <button class="btn" style="margin-top:12px; font-size:1.15rem;" onclick="openRegisterScreen()">📝 회원가입</button>
    <p style="text-align:center; opacity:0.55; font-size:0.78rem; margin-top:20px;">이메일 입력 없이 닉네임 + 비밀번호로 이용합니다.</p>
  </div>'''
new_auth = '''  <div id="auth-screen" class="screen active">
    <h1>⚔️ 검 vs 지팡이</h1>
    <div style="height:12px;"></div>
    <button class="btn btn-gold" style="margin-top:10px; font-size:1.15rem;" onclick="openLoginScreen()">🔐 로그인</button>
    <button class="btn" style="margin-top:12px; font-size:1.15rem;" onclick="openRegisterScreen()">📝 회원가입</button>
    <p id="auth-creator-credit" style="text-align:center; margin-top:24px; opacity:0.58; font-size:0.82rem;">제작자: Lost Ruby</p>
  </div>'''
if old_auth not in s:
    raise SystemExit('auth landing block not found')
s = s.replace(old_auth, new_auth, 1)

# 2) 메인 화면의 기타 버튼을 상점과 조금 띄우기
old_etc_btn = '''    <button class="btn" style="margin-top:12px; background:linear-gradient(135deg,#434343,#000000);" onclick="openEtcMenu()">⚙️ 기타</button>'''
new_etc_btn = '''    <button class="btn" style="margin-top:36px; background:linear-gradient(135deg,#434343,#000000);" onclick="openEtcMenu()">⚙️ 기타</button>'''
if old_etc_btn not in s:
    raise SystemExit('main etc button not found')
s = s.replace(old_etc_btn, new_etc_btn, 1)

# 3) 기타 화면을 2 x 2 반칸 카드형 버튼으로 변경
new_etc_block = '''  <!-- 기타 -->
  <div id="etc-screen" class="screen">
    <h2 style="text-align:center;">⚙️ 기타</h2>
    <div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin-top:18px;">
      <button class="btn" style="margin:0; min-height:74px; padding:12px 8px; font-size:0.98rem; background:linear-gradient(135deg,#2b5876,#4e4376);" onclick="openMissions()">📋<br>미션</button>
      <button class="btn" style="margin:0; min-height:74px; padding:12px 8px; font-size:0.98rem; background:linear-gradient(135deg,#4a5568,#2d3748);" onclick="openCodex()">🏅<br>도감</button>
      <button class="btn" style="margin:0; min-height:74px; padding:12px 8px; font-size:0.92rem; background:linear-gradient(135deg,#11998e,#38ef7d);" onclick="openHelp()">📖<br>효과 · 능력 설명</button>
      <button class="btn" style="margin:0; min-height:74px; padding:12px 8px; font-size:0.98rem; background:linear-gradient(135deg,#667eea,#764ba2);" onclick="openStory()">📜<br>스토리</button>
    </div>
    <div style="flex:1; min-height:70px;"></div>
    <button class="btn btn-danger" style="margin-top:28px;" onclick="logoutAccount()">로그아웃</button>
    <button class="btn" style="margin-top:12px; margin-bottom:8px;" onclick="showScreen('select-screen')">← 메인으로</button>
  </div>
'''
s, n = re.subn(r'  <!-- 기타 -->\n  <div id="etc-screen" class="screen">.*?(?=\n  <!-- 효과·능력 설명 -->)', lambda m: new_etc_block, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('etc screen block not found')

# 4) 효과/능력 설명 문구를 간결하게 정리
s = s.replace('<h2 style="text-align:center;">📖 효과·능력 설명</h2>', '<h2 style="text-align:center;">📖 효과 · 능력 설명</h2>', 1)
new_help = '''function renderHelp() {
  const el = $('help-list');
  if (!el) return;
  let h = '';
  h += `<p style="text-align:center;opacity:0.7;font-size:0.82rem;line-height:1.5;margin:0 4px 14px;">아래 내용은 핵심 규칙 요약입니다. 세부 확률과 수치는 각 무기의 강화 화면 설명이 우선합니다.</p>`;

  h += helpSection('상태 효과');
  h += helpCard('💫', '마비', '다음 공격 턴을 1회 건너뜁니다.');
  h += helpCard('😈', '타락', '다음 공격 턴의 공격과 능력이 자신에게 되돌아옵니다.');
  h += helpCard('☠️', '저주', '능력을 사용할 수 없고 공격력이 감소합니다. 최대 2중첩됩니다.');
  h += helpCard('🔥', '화염', '2턴 동안 지속 피해를 받고, 체력 회복 효과가 절반으로 줄어듭니다.');
  h += helpCard('🌑', '부패', '턴이 지날 때마다 체력이 감소합니다. 감소 기준과 발동 확률은 무기별 규칙을 따릅니다.');
  h += helpCard('🔒', '봉인', '발동되면 즉시 패배 판정이 발생합니다. 부활·불사 같은 생존 효과는 각 규칙을 따릅니다.');
  h += helpCard('🪞', '미러링', '다음 공격의 피해는 내 무기로 주고, 능력은 상대 무기의 능력을 빌려 발동합니다.');

  h += helpSection('공격 · 회복');
  h += helpCard('⚡', '이중 공격', '한 턴에 공격을 두 번 합니다.');
  h += helpCard('💀', '즉사 · 참격 · 초신성', '확률 또는 조건을 만족하면 상대를 즉시 쓰러뜨립니다. 보호막이 즉사류를 1회 막는 경우가 있습니다.');
  h += helpCard('🩸', '흡혈', '가한 피해의 일부만큼 자신의 체력을 회복합니다.');
  h += helpCard('📤', '흡수', '상대 체력을 깎으면서 일정량을 자신의 체력으로 회복합니다.');
  h += helpCard('🌑', '몰락의 밤', '상대의 현재 체력을 절반가량 깎는 강력한 효과입니다.');
  h += helpCard('🍽️', '최후의 만찬', '받은 피해의 일부를 체력으로 되돌려 받습니다. 체력이 너무 낮으면 발동하지 않습니다.');

  h += helpSection('방어 · 생존');
  h += helpCard('🛡️', '보호막', '피해를 체력보다 먼저 흡수합니다. 일부 상태 효과와 즉사 판정을 막아주는 경우도 있습니다.');
  h += helpCard('✨', '정화', '상태 효과가 있으면 제거하고, 상태 효과가 없을 때는 다음 상대 능력을 막는 효과로 이어질 수 있습니다.');
  h += helpCard('👑', '부활', '체력이 0이 되었을 때 1회 일정 체력으로 다시 살아납니다. 회복 비율은 무기마다 다릅니다.');
  h += helpCard('🛡️', '최후의 저항', '치명적인 피해를 받아도 1회 체력 1로 버팁니다.');
  h += helpCard('💧', '능력 무효', '피격 시 확률로 상대 무기의 능력 효과를 막습니다.');
  h += helpCard('🛡️', '공격 무시', '피격 시 확률로 일반 공격을 완전히 무시합니다. 즉사류에는 적용되지 않습니다.');
  h += helpCard('✝️', '마법 저항', '마법 계열 직업에게 받는 피해를 감소시킵니다.');

  h += helpSection('각성');
  h += helpCard('⚔️', '엑스칼리버', '일부 검이 각성하면 강력한 즉사 능력과 최후의 저항을 얻습니다. 일정 턴 뒤 무기가 파괴됩니다.');
  h += helpCard('👼', '수호천사', '일부 지팡이가 각성하면 매 턴 보호막을 얻고, 1회 부활 효과를 사용할 수 있습니다.');

  h += helpSection('전투 처리 순서');
  h += helpCard('1️⃣', '턴 시작', '마비 여부를 확인하고 화염·부패 같은 지속 효과를 먼저 처리합니다.');
  h += helpCard('2️⃣', '예약 효과', '타락·미러링처럼 이전 턴에 걸린 효과를 처리합니다.');
  h += helpCard('3️⃣', '능력 판정', '저주·정화·능력 무효·보호막 등 능력 사용 가능 여부를 확인합니다.');
  h += helpCard('4️⃣', '피해와 생존', '보호막 → 체력 감소 → 부활·최후의 저항·무기 교체 순으로 생존 여부를 확인합니다.');

  h += helpSection('직업 기본');
  h += helpCard('🗡️', '검사', '시작 체력 250 · 물리 공격, 흡혈, 참격, 각성 계열에 강점이 있습니다.');
  h += helpCard('🪄', '마법사', '시작 체력 150 · 봉인, 저주, 미러링, 부패 등 특수 효과에 강점이 있습니다.');
  h += helpCard('🗡️', '암살자', '상점 해금 직업 · 낮은 체력 대신 강력한 암살 능력을 노립니다.');
  h += helpCard('✝️', '성직자', '상점 해금 직업 · 회복, 보호막, 정화 등 생존 능력에 강점이 있습니다.');
  h += helpCard('🏹', '궁수', '상점 해금 직업 · 연속 공격과 원거리 견제에 강점이 있습니다.');

  el.innerHTML = h;
}
'''
s, n = re.subn(r'function renderHelp\(\) \{.*?(?=\nfunction ensureShopSave\(\))', lambda m: new_help, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('renderHelp block not found')

# 5) 결투방에서 오프라인 코드 결투 메뉴 제거
old_offline_menu = '''    <p style="text-align:center; opacity:0.55; font-size:0.75rem; margin-top:14px;">오프라인 연습용 코드 결투</p>
    <button class="btn" style="margin-top:6px;" onclick="startChallengeCreate()">📤 코드 결투 만들기</button>
    <button class="btn" style="margin-top:6px;" onclick="showScreen('challenge-accept-screen')">📥 코드 결투 수락</button>
'''
if old_offline_menu not in s:
    raise SystemExit('offline challenge menu not found')
s = s.replace(old_offline_menu, '', 1)

# 6) 오프라인 결투 수락/코드 생성 전용 화면 제거
s, n = re.subn(r'\n\s*<div id="challenge-accept-screen" class="screen">.*?(?=\n\s*<div id="ranking-screen" class="screen">)', '\n\n', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('offline challenge screens not found')

# 7) 강화 화면의 결투 코드 만들기 버튼 제거
challenge_button = '''    <button class="btn btn-super" style="margin-top:8px;" id="btn-make-challenge" onclick="finishChallengeCreate()">📤 결투 코드 만들기</button>\n'''
if challenge_button not in s:
    raise SystemExit('enhance challenge button not found')
s = s.replace(challenge_button, '', 1)

# 8) 오프라인 코드 결투 전용 함수 묶음 제거. 실시간 결투 함수/변수는 유지.
s, n = re.subn(r'\nfunction startChallengeCreate\(\) \{.*?(?=\nfunction buildEnemyFromChallenge\(\))', '\n', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('offline challenge functions not found')

# 9) 삭제된 강화 버튼을 제어하던 코드도 정리
s = s.replace("  const mc = $('btn-make-challenge');\n", '', 1)
s = s.replace("    if (mc) mc.style.display = 'none';\n", '', 1)
s = s.replace("    if (mc) mc.style.display = challengeCreating ? 'block' : 'block';\n", '', 1)

p.write_text(s, encoding='utf-8')
print('UI cleanup applied')

from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Functions SDK + client handle
sdk = '<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore-compat.js"></script>'
if 'firebase-functions-compat.js' not in s:
    s = s.replace(sdk, sdk + '\n<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-functions-compat.js"></script>', 1)
s = s.replace('let fbDb = null;\nlet fbUserId = null;', 'let fbDb = null;\nlet fbFunctions = null;\nlet fbUserId = null;', 1)
s = s.replace('    fbAuth = firebase.auth();\n    fbDb = firebase.firestore();\n    useCloud = true;', "    fbAuth = firebase.auth();\n    fbDb = firebase.firestore();\n    fbFunctions = firebase.app().functions('asia-northeast3');\n    useCloud = true;", 1)

# Save defaults
s = s.replace('    redeemedCodes: {},\n    shop:', "    redeemedCodes: {},\n    attendance: { lastDate: '', streak: 0, total: 0 },\n    raidChance50Unlocked: false,\n    shop:", 1)

# Etc grid bottom row
old = '<button class="btn btn-gold" style="grid-column:1 / -1; margin:0; min-height:64px; padding:12px 8px; font-size:1rem;" onclick="openCodeTab()">🎁 코드</button>'
new = '''<button class="btn" style="margin:0; min-height:64px; padding:12px 8px; font-size:0.98rem; background:linear-gradient(135deg,#f7971e,#ffd200); color:#222;" onclick="openAttendanceTab()">📅<br>출석</button>
      <button class="btn btn-gold" style="margin:0; min-height:64px; padding:12px 8px; font-size:0.98rem;" onclick="openCodeTab()">🎁<br>코드</button>'''
if old not in s:
    raise SystemExit('etc button not found')
s = s.replace(old, new, 1)

# Attendance screen
screen = '''  <!-- 출석 보상 -->
  <div id="attendance-screen" class="screen">
    <h2 style="text-align:center;">📅 출석 보상</h2>
    <div style="background:rgba(0,0,0,0.3);border:1px solid #5a4a8a;border-radius:14px;padding:18px;margin-top:10px;text-align:center;">
      <div style="font-size:1.35rem;font-weight:900;color:#ffd700;">매일 +100 LR</div>
      <div style="font-size:0.88rem;opacity:0.82;margin-top:6px;">7일 연속마다 추가 +100 LP</div>
    </div>
    <p id="attendance-info" style="text-align:center;line-height:1.7;margin-top:18px;opacity:0.88;"></p>
    <p id="attendance-msg" style="text-align:center;min-height:1.4em;margin-top:10px;font-size:0.9rem;"></p>
    <button class="btn btn-gold" id="attendance-claim-btn" style="margin-top:10px;" onclick="claimAttendanceReward()">오늘 출석 보상 받기</button>
    <div style="flex:1;min-height:40px;"></div>
    <button class="btn" onclick="showScreen('etc-screen')">← 기타로</button>
  </div>

'''
marker = '  <!-- 코드 입력 -->\n'
if 'id="attendance-screen"' not in s:
    s = s.replace(marker, screen + marker, 1)

# Replace old coupon implementation up to openHelp.
a = s.find('const REDEEM_CODES = Object.freeze({')
b = s.find('\nfunction openHelp()', a)
if a < 0 or b < 0:
    raise SystemExit('coupon block not found')
replacement = '''function setCodeMessage(text, ok = false) {
  const el = $('redeem-code-msg');
  if (!el) return;
  el.textContent = text || '';
  el.style.color = ok ? '#75ffad' : '#ff9a9a';
}

async function reloadRewardData() {
  if (!useCloud || !fbDb || !fbUserId) return;
  const profile = await cloudLoadProfile(fbUserId);
  if (!profile) return;
  saveData = Object.assign(defaultSaveData(profile.nick || ''), profile.data || {});
  saveData.lr = Number(profile.lr !== undefined ? profile.lr : saveData.lr) || 0;
  saveData.lp = Number(profile.lp !== undefined ? profile.lp : saveData.lp) || 0;
  ensureShopSave();
  normalizeMissions();
  updateRecordSummary();
}

function rewardError(e, fallback) {
  const code = String((e && e.code) || '');
  const msg = String((e && e.message) || '');
  if (code.includes('already-exists')) return msg || '이미 사용했습니다.';
  if (code.includes('not-found')) return msg || '존재하지 않는 코드입니다.';
  if (code.includes('unauthenticated')) return '로그인이 필요합니다.';
  return msg || fallback;
}

function openCodeTab() {
  if (!requireLogin()) return;
  const input = $('redeem-code-input');
  if (input) input.value = '';
  setCodeMessage('');
  showScreen('code-screen');
}

async function redeemCode() {
  if (!requireLogin()) return;
  const input = $('redeem-code-input');
  const btn = $('redeem-code-btn');
  const raw = ((input && input.value) || '').trim();
  if (!raw) { setCodeMessage('코드를 입력하세요.'); return; }
  if (!fbFunctions) { setCodeMessage('보상 서버가 아직 준비되지 않았습니다.'); return; }
  if (btn) btn.disabled = true;
  setCodeMessage('코드 확인 중...');
  try {
    const res = await fbFunctions.httpsCallable('redeemCode')({ code: raw });
    await reloadRewardData();
    setCodeMessage(`코드 사용 완료! +${(res.data && res.data.label) || '보상 지급'}`, true);
    if (input) input.value = '';
  } catch (e) {
    console.warn(e);
    setCodeMessage(rewardError(e, '코드 사용 중 오류가 발생했습니다.'));
  } finally {
    if (btn) btn.disabled = false;
  }
}

function kstTodayClient() {
  try {
    const ps = new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
    const m = Object.fromEntries(ps.map(x => [x.type, x.value]));
    return `${m.year}-${m.month}-${m.day}`;
  } catch (e) { return ''; }
}

function renderAttendanceInfo() {
  const info = $('attendance-info');
  const btn = $('attendance-claim-btn');
  if (!info) return;
  const a = saveData.attendance || { lastDate:'', streak:0, total:0 };
  const done = a.lastDate === kstTodayClient();
  info.innerHTML = `연속 출석 <b style="color:#ffd700;">${Number(a.streak)||0}일</b><br>누적 출석 ${Number(a.total)||0}일${done ? '<br><span style="color:#75ffad;">오늘 출석 완료 ✅</span>' : ''}`;
  if (btn) { btn.disabled = done; btn.textContent = done ? '오늘 출석 완료' : '오늘 출석 보상 받기'; }
}

function openAttendanceTab() {
  if (!requireLogin()) return;
  const msg = $('attendance-msg');
  if (msg) msg.textContent = '';
  renderAttendanceInfo();
  showScreen('attendance-screen');
}

async function claimAttendanceReward() {
  if (!requireLogin()) return;
  const btn = $('attendance-claim-btn');
  const msg = $('attendance-msg');
  if (!fbFunctions) { if (msg) { msg.style.color='#ff9a9a'; msg.textContent='보상 서버가 아직 준비되지 않았습니다.'; } return; }
  if (btn) btn.disabled = true;
  if (msg) { msg.style.color='#c9b6ff'; msg.textContent='출석 확인 중...'; }
  try {
    const res = await fbFunctions.httpsCallable('claimAttendance')({});
    await reloadRewardData();
    renderAttendanceInfo();
    const d = res.data || {};
    const bonus = Number(d.lpReward) > 0 ? ` + ${Number(d.lpReward).toLocaleString()} LP` : '';
    if (msg) { msg.style.color='#75ffad'; msg.textContent=`출석 완료! +${Number(d.lrReward||100).toLocaleString()} LR${bonus}`; }
  } catch (e) {
    if (msg) { msg.style.color='#ff9a9a'; msg.textContent=rewardError(e, '출석 처리 중 오류가 발생했습니다.'); }
    renderAttendanceInfo();
  }
}
'''
s = s[:a] + replacement + s[b:]

if 'const REDEEM_CODES' in s:
    raise SystemExit('old coupon map remains')
p.write_text(s, encoding='utf-8')
print('reward UI patched')

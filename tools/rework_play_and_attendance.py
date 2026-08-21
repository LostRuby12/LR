from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Rebuild play flow while preserving the existing class cards.
play_marker = '  <!-- 플레이 메뉴: 이벤트 / 강화 / 결투 -->'
duel_marker = '  <!-- 결투방 메뉴 -->'
if play_marker not in s or duel_marker not in s:
    raise SystemExit('play/challenge markers not found')
play_start = s.index(play_marker)
play_end = s.index(duel_marker, play_start)
old_play = s[play_start:play_end]
card_start_token = '    <div class="class-cards" id="class-cards-wrap">'
card_end_token = '    <button class="btn" id="start-btn"'
if card_start_token not in old_play or card_end_token not in old_play:
    raise SystemExit('class card block not found')
card_start = old_play.index(card_start_token)
card_end = old_play.index(card_end_token, card_start)
class_cards = old_play[card_start:card_end].rstrip()

new_play = f'''  <!-- 플레이 허브 -->
  <div id="play-menu-screen" class="screen">
    <h2 style="text-align:center;">▶️ 플레이</h2>
    <p style="text-align:center; opacity:0.78; font-size:0.9rem; margin-bottom:16px;">플레이 방식을 선택하세요</p>
    <button class="btn btn-gold" style="padding:18px 14px;" onclick="openMainChapterMenu()">📖 메인 편<br><span style="font-size:0.78rem;font-weight:500;opacity:0.8;">메인 스토리 · 보스전 · 이벤트전</span></button>
    <button class="btn btn-success" style="padding:18px 14px;margin-top:12px;" onclick="openModeClassSelect('quick')">⚡ 신속전<br><span style="font-size:0.78rem;font-weight:500;opacity:0.85;">기존 AI와 빠르게 강화 대결</span></button>
    <button class="btn btn-super" style="padding:18px 14px;margin-top:12px;" onclick="openDuelTypeMenu()">⚔️ 결투방<br><span style="font-size:0.78rem;font-weight:500;opacity:0.85;">일반전 · 랭크전</span></button>
    <div style="flex:1;min-height:34px;"></div>
    <button class="btn" onclick="showScreen('select-screen')">← 메인으로</button>
  </div>

  <div id="main-chapter-screen" class="screen">
    <h2 style="text-align:center;">📖 메인 편</h2>
    <p style="text-align:center;opacity:0.78;font-size:0.9rem;margin-bottom:14px;">콘텐츠를 선택한 뒤 직업을 정합니다</p>
    <button class="btn btn-gold" style="padding:17px 14px;" onclick="openModeClassSelect('story')">📜 메인 스토리<br><span style="font-size:0.78rem;font-weight:500;opacity:0.8;">스토리 강화 전투</span></button>
    <button class="btn btn-danger" style="padding:17px 14px;margin-top:10px;" onclick="openModeClassSelect('raid')">👹 보스전<br><span style="font-size:0.78rem;font-weight:500;opacity:0.85;">고대 마법사 · 몰락한 신</span></button>
    <button class="btn" style="padding:17px 14px;margin-top:10px;background:linear-gradient(135deg,#a8e063,#56ab2f);color:#0b1a0b;font-weight:800;" onclick="openModeClassSelect('event')">🎭 이벤트전<br><span style="font-size:0.78rem;font-weight:600;opacity:0.8;">시이다 케인</span></button>
    <div style="flex:1;min-height:34px;"></div>
    <button class="btn" onclick="showScreen('play-menu-screen')">← 플레이로</button>
  </div>

  <div id="duel-type-screen" class="screen">
    <h2 style="text-align:center;">⚔️ 결투방</h2>
    <p style="text-align:center;opacity:0.78;font-size:0.9rem;margin-bottom:14px;">대전 종류를 선택하세요</p>
    <button class="btn btn-success" style="padding:18px 14px;" onclick="openModeClassSelect('duel-normal')">🟢 일반전<br><span style="font-size:0.78rem;font-weight:500;opacity:0.85;">부담 없이 실시간 대결</span></button>
    <button class="btn btn-gold" style="padding:18px 14px;margin-top:12px;" onclick="openModeClassSelect('duel-ranked')">🏆 랭크전<br><span style="font-size:0.78rem;font-weight:500;opacity:0.8;">랭킹을 확인하며 실시간 대결</span></button>
    <div style="flex:1;min-height:34px;"></div>
    <button class="btn" onclick="showScreen('play-menu-screen')">← 플레이로</button>
  </div>

  <div id="mode-class-screen" class="screen">
    <h2 id="mode-class-title" style="text-align:center;">직업 선택</h2>
    <p id="mode-class-desc" style="text-align:center;opacity:0.78;font-size:0.88rem;margin-bottom:2px;"></p>
{class_cards}
    <button class="btn btn-gold" id="mode-class-next" style="margin-top:16px;" disabled onclick="confirmModeClass()">이 직업으로 계속</button>
    <button class="btn" style="margin-top:10px;" onclick="backFromModeClass()">← 이전으로</button>
  </div>

'''
s = s[:play_start] + new_play + s[play_end:]

# 2) Make the duel room screen aware of General vs Ranked mode.
cstart = s.index(duel_marker)
cend_token = '  <div id="rt-host-screen" class="screen">'
if cend_token not in s[cstart:]:
    raise SystemExit('rt host screen marker not found')
cend = s.index(cend_token, cstart)
challenge_block = s[cstart:cend]
challenge_block = challenge_block.replace('<h2 style="text-align:center;">⚔️ 결투방</h2>', '<h2 id="duel-room-title" style="text-align:center;">⚔️ 일반전</h2>', 1)
challenge_block = challenge_block.replace('<p style="text-align:center; opacity:0.8; font-size:0.9rem; margin-bottom:8px;">실시간 대결 · 승리 시 100 LR</p>', '<p id="duel-room-desc" style="text-align:center; opacity:0.8; font-size:0.9rem; margin-bottom:8px;">일반전 · 실시간 대결 · 승리 시 100 LR</p>', 1)
challenge_block = challenge_block.replace('<button class="btn btn-gold" style="margin-top:10px;" onclick="openRanking()">🏆 랭킹</button>', '<button class="btn btn-gold" id="duel-rank-btn" style="margin-top:10px;display:none;" onclick="openRanking()">🏆 랭킹</button>', 1)
challenge_block = challenge_block.replace('<button class="btn" style="margin-top:14px;" onclick="showScreen(\'play-menu-screen\')">← 플레이로</button>', '<button class="btn" style="margin-top:14px;" onclick="showScreen(\'duel-type-screen\')">← 결투방 선택</button>', 1)
s = s[:cstart] + challenge_block + s[cend:]

# 3) Add play-flow state.
state_old = "let playerClass = null; // sword | mage | assassin | priest | archer"
state_new = """let playerClass = null; // sword | mage | assassin | priest | archer
let pendingPlayMode = null; // story | quick | raid | event | duel-normal | duel-ranked
let duelTypeMode = 'normal'; // normal | ranked"""
if state_old not in s:
    raise SystemExit('playerClass state marker missing')
s = s.replace(state_old, state_new, 1)

# 4) Replace play navigation functions.
old_open = """function openPlayMenu() {
  if (!requireLogin()) return;
  updateRecordSummary();
  refreshClassCards();
  showScreen('play-menu-screen');
}
function openEtcMenu() {"""
new_open = """function openPlayMenu() {
  if (!requireLogin()) return;
  updateRecordSummary();
  pendingPlayMode = null;
  showScreen('play-menu-screen');
}

function openMainChapterMenu() {
  if (!requireLogin()) return;
  showScreen('main-chapter-screen');
}

function openDuelTypeMenu() {
  if (!requireLogin()) return;
  showScreen('duel-type-screen');
}

function playModeMeta(mode) {
  const map = {
    story: ['📜 메인 스토리 · 직업 선택', '직업을 선택하고 강화한 뒤 스토리 전투에 도전합니다.'],
    quick: ['⚡ 신속전 · 직업 선택', '직업을 선택하고 기존 AI와 바로 강화 대결을 시작합니다.'],
    raid: ['👹 보스전 · 직업 선택', '직업 선택 후 도전할 보스를 고르고 강화합니다.'],
    event: ['🎭 이벤트전 · 직업 선택', '이벤트전은 검사와 마법사만 참가할 수 있습니다.'],
    'duel-normal': ['🟢 일반전 · 직업 선택', '직업 선택 후 실시간 방을 만들거나 참가하고 강화합니다.'],
    'duel-ranked': ['🏆 랭크전 · 직업 선택', '직업 선택 후 랭크전 방을 만들거나 참가하고 강화합니다.']
  };
  return map[mode] || ['직업 선택', '직업을 선택하세요.'];
}

function openModeClassSelect(mode) {
  if (!requireLogin()) return;
  pendingPlayMode = mode;
  playerClass = null;
  refreshClassCards();
  document.querySelectorAll('#mode-class-screen .class-card').forEach(c => c.classList.remove('selected'));
  const meta = playModeMeta(mode);
  const title = $('mode-class-title');
  const desc = $('mode-class-desc');
  const next = $('mode-class-next');
  if (title) title.textContent = meta[0];
  if (desc) desc.textContent = meta[1];
  if (next) next.disabled = true;

  // 이벤트전은 기존 이벤트 규칙상 검사/마법사 전용.
  if (mode === 'event') {
    ['assassin', 'priest', 'archer'].forEach(cls => {
      const el = $('cls-' + cls);
      if (el) el.style.display = 'none';
    });
  }
  showScreen('mode-class-screen');
}

function backFromModeClass() {
  if (pendingPlayMode === 'story' || pendingPlayMode === 'raid' || pendingPlayMode === 'event') {
    showScreen('main-chapter-screen');
  } else if (pendingPlayMode === 'duel-normal' || pendingPlayMode === 'duel-ranked') {
    showScreen('duel-type-screen');
  } else {
    showScreen('play-menu-screen');
  }
}

function confirmModeClass() {
  if (!playerClass) {
    alert('직업을 선택하세요!');
    return;
  }
  const mode = pendingPlayMode;
  if (mode === 'story' || mode === 'quick') {
    challengeMode = false;
    pendingRaidBoss = false;
    selectedRaidBossId = null;
    gameMode = 'normal';
    startEnhance();
    return;
  }
  if (mode === 'raid') {
    openRaidBossMode();
    return;
  }
  if (mode === 'event') {
    if (playerClass !== 'sword' && playerClass !== 'mage') {
      alert('이벤트전은 검사 또는 마법사만 참가할 수 있습니다.');
      return;
    }
    openBossMode();
    bossSelectClass(playerClass);
    return;
  }
  if (mode === 'duel-normal' || mode === 'duel-ranked') {
    duelTypeMode = mode === 'duel-ranked' ? 'ranked' : 'normal';
    openChallengeMenu(duelTypeMode);
    return;
  }
}

function openEtcMenu() {"""
if old_open not in s:
    raise SystemExit('openPlayMenu block not found')
s = s.replace(old_open, new_open, 1)

# 5) Enable the new Continue button when a class is selected.
select_old = """  const sb = $('start-btn');
  if (sb) sb.disabled = false;"""
select_new = """  const sb = $('start-btn');
  if (sb) sb.disabled = false;
  const mb = $('mode-class-next');
  if (mb) mb.disabled = false;"""
if select_old not in s:
    raise SystemExit('selectClass button marker missing')
s = s.replace(select_old, select_new, 1)

# 6) Give the enhancement screen context-sensitive titles.
enhance_html_old = '<div id="enhance-screen" class="screen">\n    <h2>무기 강화</h2>'
enhance_html_new = '<div id="enhance-screen" class="screen">\n    <h2 id="enhance-title">무기 강화</h2>'
if enhance_html_old not in s:
    raise SystemExit('enhance screen title marker missing')
s = s.replace(enhance_html_old, enhance_html_new, 1)
start_old = """function startEnhance() {
  if (!playerClass) return;
  level = 0;"""
start_new = """function startEnhance() {
  if (!playerClass) return;
  const enhanceTitle = $('enhance-title');
  if (enhanceTitle) {
    const titles = {
      story: '📜 메인 스토리 강화',
      quick: '⚡ 신속전 강화',
      raid: '👹 보스전 강화',
      'duel-normal': '🟢 일반전 강화',
      'duel-ranked': '🏆 랭크전 강화'
    };
    enhanceTitle.textContent = titles[pendingPlayMode] || '무기 강화';
  }
  level = 0;"""
if start_old not in s:
    raise SystemExit('startEnhance marker missing')
s = s.replace(start_old, start_new, 1)

# 7) General/Ranked room presentation.
old_challenge_fn = """function openChallengeMenu() {
  if (!requireNick()) return;
  challengeCreating = false;
  updateRecordSummary();
  showScreen('challenge-menu-screen');
}"""
new_challenge_fn = """function openChallengeMenu(mode) {
  if (!requireNick()) return;
  if (mode === 'ranked' || mode === 'normal') duelTypeMode = mode;
  challengeCreating = false;
  updateRecordSummary();
  const ranked = duelTypeMode === 'ranked';
  const title = $('duel-room-title');
  const desc = $('duel-room-desc');
  const rankBtn = $('duel-rank-btn');
  if (title) title.textContent = ranked ? '🏆 랭크전' : '⚔️ 일반전';
  if (desc) desc.textContent = ranked
    ? '랭크전 · 실시간 대결 · 승리 시 100 LR'
    : '일반전 · 실시간 대결 · 승리 시 100 LR';
  if (rankBtn) rankBtn.style.display = ranked ? '' : 'none';
  showScreen('challenge-menu-screen');
}"""
if old_challenge_fn not in s:
    raise SystemExit('openChallengeMenu marker missing')
s = s.replace(old_challenge_fn, new_challenge_fn, 1)

hello_old = "rtSend({ type: 'hello', nick: saveData.nick || '익명', lr: saveData.lr || 0 });"
hello_new = "rtSend({ type: 'hello', nick: saveData.nick || '익명', lr: saveData.lr || 0, duelMode: duelTypeMode });"
if hello_old not in s:
    raise SystemExit('realtime hello marker missing')
s = s.replace(hello_old, hello_new, 1)

ondata_old = """  if (data.type === 'hello') {
    rtOppNick = data.nick || '상대';"""
ondata_new = """  if (data.type === 'hello') {
    const remoteMode = data.duelMode === 'ranked' ? 'ranked' : 'normal';
    if (remoteMode !== duelTypeMode) {
      alert(`대전 모드가 다릅니다. 상대는 ${remoteMode === 'ranked' ? '랭크전' : '일반전'} 방입니다.`);
      setTimeout(() => rtLeave(), 0);
      return;
    }
    rtOppNick = data.nick || '상대';"""
if ondata_old not in s:
    raise SystemExit('rtOnData hello marker missing')
s = s.replace(ondata_old, ondata_new, 1)

lobby_old = "if (info) info.textContent = `방 ${rtRoomId} · 상대: ${rtOppNick || '연결됨'}`;"
lobby_new = "if (info) info.textContent = `${duelTypeMode === 'ranked' ? '랭크전' : '일반전'} · 방 ${rtRoomId} · 상대: ${rtOppNick || '연결됨'}`;"
if lobby_old not in s:
    raise SystemExit('rt lobby info marker missing')
s = s.replace(lobby_old, lobby_new, 1)

# 8) Attendance: use Firestore server timestamp, not device date.
attendance_start_token = 'function kstTodayClient() {'
attendance_end_token = 'function openHelp() {'
if attendance_start_token not in s or attendance_end_token not in s:
    raise SystemExit('attendance block markers missing')
a_start = s.index(attendance_start_token)
a_end = s.index(attendance_end_token, a_start)
new_attendance = r'''let trustedAttendanceToday = '';

function formatKstDate(dateValue) {
  try {
    const date = dateValue instanceof Date ? dateValue : new Date(dateValue);
    if (!date || Number.isNaN(date.getTime())) return '';
    const ps = new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(date);
    const m = Object.fromEntries(ps.map(x => [x.type, x.value]));
    return `${m.year}-${m.month}-${m.day}`;
  } catch (e) { return ''; }
}

async function getTrustedAttendanceToday() {
  if (!useCloud || !fbDb || !fbUserId) throw new Error('ATTENDANCE_LOGIN_REQUIRED');
  const ref = fbDb.collection('profiles').doc(fbUserId);
  // Firestore 서버가 실제 시간을 기록한다. 기기 날짜/시간은 사용하지 않는다.
  await ref.set({
    attendance_server_clock: firebase.firestore.FieldValue.serverTimestamp()
  }, { merge: true });
  const snap = await ref.get({ source: 'server' });
  if (!snap.exists) throw new Error('PROFILE_MISSING');
  const row = snap.data() || {};
  const ts = row.attendance_server_clock;
  const serverDate = ts && typeof ts.toDate === 'function' ? ts.toDate() : null;
  const today = formatKstDate(serverDate);
  if (!today) throw new Error('SERVER_TIME_UNAVAILABLE');
  trustedAttendanceToday = today;
  return today;
}

function renderAttendanceInfo(serverToday = trustedAttendanceToday) {
  const info = $('attendance-info');
  const btn = $('attendance-claim-btn');
  if (!info) return;
  const a = saveData.attendance || { lastDate:'', streak:0, total:0 };
  const checking = !serverToday;
  const done = !!serverToday && a.lastDate === serverToday;
  info.innerHTML = `연속 출석 <b style="color:#ffd700;">${Number(a.streak)||0}일</b><br>누적 출석 ${Number(a.total)||0}일${done ? '<br><span style="color:#75ffad;">오늘 출석 완료 ✅</span>' : ''}`;
  if (btn) {
    btn.disabled = checking || done;
    btn.textContent = checking ? '서버 날짜 확인 중...' : (done ? '오늘 출석 완료' : '오늘 출석 보상 받기');
  }
}

async function openAttendanceTab() {
  if (!requireLogin()) return;
  const msg = $('attendance-msg');
  if (msg) { msg.style.color = '#c8c8ff'; msg.textContent = '서버 날짜 확인 중...'; }
  trustedAttendanceToday = '';
  renderAttendanceInfo('');
  showScreen('attendance-screen');
  try {
    const today = await getTrustedAttendanceToday();
    renderAttendanceInfo(today);
    if (msg) { msg.style.color = '#aaa'; msg.textContent = `서버 기준 ${today}`; }
  } catch (e) {
    console.warn('attendance server clock failed', e);
    if (msg) { msg.style.color = '#ff9a9a'; msg.textContent = '서버 시간을 확인할 수 없습니다. 인터넷 연결 후 다시 시도하세요.'; }
  }
}

function attendanceDateSerial(ymd) {
  const parts = String(ymd || '').split('-').map(Number);
  if (parts.length !== 3 || !parts[0] || !parts[1] || !parts[2]) return null;
  return Math.floor(Date.UTC(parts[0], parts[1] - 1, parts[2]) / 86400000);
}

async function claimAttendanceReward() {
  if (!requireLogin()) return;
  const btn = $('attendance-claim-btn');
  const msg = $('attendance-msg');
  if (!useCloud || !fbDb || !fbUserId) {
    if (msg) { msg.style.color = '#ff9a9a'; msg.textContent = '로그인 정보를 확인한 뒤 다시 시도하세요.'; }
    return;
  }

  if (btn) btn.disabled = true;
  if (msg) { msg.style.color = '#c8c8ff'; msg.textContent = '서버 시간으로 출석 확인 중...'; }
  try {
    const today = await getTrustedAttendanceToday();
    const ref = fbDb.collection('profiles').doc(fbUserId);
    let updatedData = null;
    let rewardText = '';

    await fbDb.runTransaction(async (tx) => {
      const snap = await tx.get(ref);
      if (!snap.exists) throw new Error('PROFILE_MISSING');
      const profile = snap.data() || {};
      const base = Object.assign(
        defaultSaveData(profile.nick || saveData.nick || ''),
        profile.data || saveData || {}
      );
      const attendance = Object.assign({ lastDate: '', streak: 0, total: 0 }, base.attendance || {});

      // 이전 출석일도 가능한 경우 서버가 찍은 타임스탬프를 우선 사용한다.
      const lastServerTs = profile.attendance_server_claimed_at;
      const lastServerDate = lastServerTs && typeof lastServerTs.toDate === 'function'
        ? formatKstDate(lastServerTs.toDate())
        : '';
      const previousDate = lastServerDate || attendance.lastDate || '';
      if (previousDate === today) throw new Error('ATTENDANCE_ALREADY_CLAIMED');

      const prev = attendanceDateSerial(previousDate);
      const now = attendanceDateSerial(today);
      const streak = (prev !== null && now !== null && now - prev === 1)
        ? Math.max(0, Number(attendance.streak) || 0) + 1
        : 1;
      const streakLrBonus = streak % 7 === 0 ? 200 : 0;
      const lrReward = 100 + streakLrBonus;

      base.lr = Math.max(0, Number(base.lr) || 0) + lrReward;
      base.lp = Math.max(0, Number(base.lp) || 0);
      base.attendance = {
        lastDate: today,
        streak,
        total: Math.max(0, Number(attendance.total) || 0) + 1
      };

      tx.set(ref, {
        nick: base.nick || profile.nick || '',
        lr: base.lr,
        lp: base.lp,
        data: base,
        attendance_server_claimed_at: firebase.firestore.FieldValue.serverTimestamp(),
        updated_at: new Date().toISOString()
      }, { merge: true });

      updatedData = base;
      rewardText = streakLrBonus > 0
        ? `출석 완료! +100 LR · 7일 연속 보너스 +${streakLrBonus} LR`
        : `출석 완료! +${lrReward} LR`;
    });

    saveData = Object.assign(defaultSaveData((updatedData && updatedData.nick) || saveData.nick || ''), updatedData || {});
    try { upsertRankBoard(saveData.nick || '나', saveData.lr || 0); } catch (e) {}
    updateRecordSummary();
    renderAttendanceInfo(today);
    if (msg) { msg.style.color = '#75ffad'; msg.textContent = rewardText; }
  } catch (e) {
    if (e && e.message === 'ATTENDANCE_ALREADY_CLAIMED') {
      if (msg) { msg.style.color = '#ffdb75'; msg.textContent = '서버 기준으로 오늘 출석 보상은 이미 받았습니다.'; }
    } else {
      console.warn('claimAttendanceReward failed', e);
      if (msg) { msg.style.color = '#ff9a9a'; msg.textContent = '출석 처리 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.'; }
    }
  } finally {
    renderAttendanceInfo(trustedAttendanceToday);
  }
}
'''
s = s[:a_start] + new_attendance + '\n\n' + s[a_end:]

attendance_ui_old = '<div style="font-size:0.88rem;opacity:0.82;margin-top:6px;">7일 연속마다 추가 +200 LR</div>'
attendance_ui_new = attendance_ui_old + '\n      <div style="font-size:0.76rem;opacity:0.62;margin-top:8px;">Firebase 서버 시간 기준 · 기기 날짜 변경 영향 없음</div>'
if attendance_ui_old not in s:
    raise SystemExit('attendance UI text marker missing')
s = s.replace(attendance_ui_old, attendance_ui_new, 1)

# Final static safety checks.
required = [
    'id="main-chapter-screen"', 'id="duel-type-screen"', 'id="mode-class-screen"',
    "openModeClassSelect('quick')", "openModeClassSelect('story')", "openModeClassSelect('raid')",
    "openModeClassSelect('event')", "openModeClassSelect('duel-normal')", "openModeClassSelect('duel-ranked')",
    'attendance_server_clock', 'attendance_server_claimed_at', 'firebase.firestore.FieldValue.serverTimestamp()',
    "let duelTypeMode = 'normal'", "duelMode: duelTypeMode"
]
for token in required:
    if token not in s:
        raise SystemExit(f'missing required token: {token}')
if 'function kstTodayClient()' in s:
    raise SystemExit('local attendance date function still present')

p.write_text(s, encoding='utf-8')
print('play hub and server-time attendance applied')

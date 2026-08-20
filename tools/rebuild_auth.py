from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

auth_html = r'''  <!-- 0. 계정 시작 -->
  <div id="auth-screen" class="screen active">
    <h1>⚔️ 검 vs 지팡이</h1>
    <p style="text-align:center; opacity:0.82; margin:6px 0 22px;">Firebase 서버 계정</p>
    <button class="btn btn-gold" style="margin-top:10px; font-size:1.15rem;" onclick="openLoginScreen()">🔐 로그인</button>
    <button class="btn" style="margin-top:12px; font-size:1.15rem;" onclick="openRegisterScreen()">📝 회원가입</button>
    <p style="text-align:center; opacity:0.55; font-size:0.78rem; margin-top:20px;">이메일 입력 없이 닉네임 + 비밀번호로 이용합니다.</p>
  </div>

  <div id="login-screen" class="screen">
    <h2 style="text-align:center;">🔐 로그인</h2>
    <p style="text-align:center; opacity:0.72; font-size:0.85rem; margin-bottom:14px;">가입한 닉네임과 비밀번호를 입력하세요.</p>
    <input id="login-nick" type="text" maxlength="12" autocomplete="username" placeholder="닉네임"
      style="width:100%;box-sizing:border-box;padding:13px;border-radius:10px;border:2px solid #8e2de2;background:#1a1a2e;color:#fff;margin-bottom:10px;" />
    <input id="login-pass" type="password" maxlength="32" autocomplete="current-password" placeholder="비밀번호 (6자 이상)"
      style="width:100%;box-sizing:border-box;padding:13px;border-radius:10px;border:2px solid #8e2de2;background:#1a1a2e;color:#fff;margin-bottom:8px;" />
    <label style="display:flex;align-items:center;gap:8px;margin:8px 0;font-size:0.9rem;opacity:0.9;">
      <input type="checkbox" id="login-auto" checked style="width:18px;height:18px;" /> 자동 로그인
    </label>
    <p id="login-msg" style="text-align:center;color:#ff9a9a;font-size:0.86rem;min-height:1.35em;margin-top:4px;"></p>
    <button class="btn btn-gold" id="login-submit" style="margin-top:8px;" onclick="submitLogin()">로그인</button>
    <button class="btn" style="margin-top:8px;background:linear-gradient(135deg,#555,#333);" onclick="showAuthLanding()">← 돌아가기</button>
  </div>

  <div id="register-screen" class="screen">
    <h2 style="text-align:center;">📝 회원가입</h2>
    <p style="text-align:center;opacity:0.72;font-size:0.85rem;margin-bottom:14px;">닉네임은 서버에서 중복 확인됩니다.</p>
    <input id="reg-nick" type="text" maxlength="12" autocomplete="username" placeholder="닉네임 (최대 12자)" onblur="checkRegisterNickAvailability()"
      style="width:100%;box-sizing:border-box;padding:13px;border-radius:10px;border:2px solid #ffd700;background:#1a1a2e;color:#fff;margin-bottom:10px;" />
    <input id="reg-pass" type="password" maxlength="32" autocomplete="new-password" placeholder="비밀번호 (6자 이상)"
      style="width:100%;box-sizing:border-box;padding:13px;border-radius:10px;border:2px solid #8e2de2;background:#1a1a2e;color:#fff;margin-bottom:10px;" />
    <input id="reg-pass2" type="password" maxlength="32" autocomplete="new-password" placeholder="비밀번호 확인"
      style="width:100%;box-sizing:border-box;padding:13px;border-radius:10px;border:2px solid #8e2de2;background:#1a1a2e;color:#fff;margin-bottom:8px;" />
    <p id="register-msg" style="text-align:center;color:#ff9a9a;font-size:0.86rem;min-height:1.35em;margin-top:6px;"></p>
    <button class="btn btn-gold" id="register-submit" style="margin-top:8px;" onclick="submitRegister()">계정 만들기</button>
    <button class="btn" style="margin-top:8px;background:linear-gradient(135deg,#555,#333);" onclick="showAuthLanding()">← 돌아가기</button>
  </div>

'''

s, n = re.subn(r'  <!-- 0\. 로그인 -->.*?(?=  <!-- 1\. 메인 -->)', auth_html, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('auth HTML block not found')

s, n = re.subn(
    r'async function cloudNickTaken\(nick\) \{.*?\n\}',
    """async function cloudNickTaken(nick) {
  const snap = await fbDb.collection('nicks').doc(nickKey(nick)).get();
  return snap.exists;
}""",
    s, count=1, flags=re.S
)
if n != 1:
    raise SystemExit('cloudNickTaken not found')

auth_js = r'''function cleanNickname(value) {
  return String(value || '').trim().replace(/\s+/g, ' ').slice(0, 12);
}
function validateNickname(nick) {
  if (!nick) return '닉네임을 입력하세요.';
  if (!/^[0-9A-Za-z가-힣 _-]+$/.test(nick)) return '닉네임은 한글, 영문, 숫자, 공백, _ - 만 사용할 수 있습니다.';
  return '';
}
function authErrorText(err, mode) {
  const code = String((err && err.code) || '');
  const msg = String((err && err.message) || '');
  const all = code + ' ' + msg;
  if (/operation-not-allowed/i.test(all)) return 'Firebase에서 이메일/비밀번호 로그인을 활성화해야 합니다.';
  if (/invalid-api-key|api-key-not-valid/i.test(all)) return 'Firebase API 키 설정을 확인하세요.';
  if (/network-request-failed|network|fetch|unavailable/i.test(all)) return '서버 연결에 실패했습니다. 잠시 후 다시 시도하세요.';
  if (/email-already-in-use|already-in-use/i.test(all)) return '이미 사용 중인 닉네임입니다.';
  if (/invalid-credential|user-not-found|wrong-password|invalid-login-credentials/i.test(all)) return '닉네임 또는 비밀번호가 올바르지 않습니다.';
  if (/weak-password/i.test(all)) return '비밀번호는 6자 이상으로 설정하세요.';
  if (/permission-denied|missing-or-insufficient-permissions/i.test(all)) return 'Firestore 보안 규칙 때문에 저장할 수 없습니다.';
  return (mode === 'register' ? '회원가입 실패: ' : '로그인 실패: ') + (msg || code || '알 수 없는 오류');
}
function setAuthMsg(id, text, success) {
  const el = $(id);
  if (!el) return;
  el.textContent = text || '';
  el.style.color = success ? '#7dff9b' : '#ff9a9a';
}
function showAuthLanding() {
  setAuthMsg('login-msg', '');
  setAuthMsg('register-msg', '');
  showScreen('auth-screen');
}
function openLoginScreen() {
  setAuthMsg('login-msg', '');
  const nickEl = $('login-nick');
  try {
    const last = localStorage.getItem('sword_mage_last_nick') || '';
    if (nickEl && !nickEl.value) nickEl.value = last;
  } catch (e) {}
  const auto = $('login-auto');
  if (auto) auto.checked = isAutoLoginEnabled() || auto.checked;
  showScreen('login-screen');
  setTimeout(() => { if (nickEl) nickEl.focus(); }, 0);
}
function openRegisterScreen() {
  setAuthMsg('register-msg', '');
  const n = $('reg-nick'), p = $('reg-pass'), p2 = $('reg-pass2');
  if (n) n.value = '';
  if (p) p.value = '';
  if (p2) p2.value = '';
  showScreen('register-screen');
  setTimeout(() => { if (n) n.focus(); }, 0);
}
function showAuthTab(mode) {
  if (mode === 'register') openRegisterScreen();
  else openLoginScreen();
}
async function checkRegisterNickAvailability() {
  const nick = cleanNickname($('reg-nick') && $('reg-nick').value);
  const validation = validateNickname(nick);
  if (validation) { setAuthMsg('register-msg', validation); return false; }
  if (!useCloud || !fbDb) { setAuthMsg('register-msg', 'Firebase 서버가 연결되지 않았습니다.'); return false; }
  try {
    if (await cloudNickTaken(nick)) { setAuthMsg('register-msg', '이미 사용 중인 닉네임입니다.'); return false; }
    setAuthMsg('register-msg', '사용 가능한 닉네임입니다.', true);
    return true;
  } catch (e) {
    setAuthMsg('register-msg', authErrorText(e, 'register'));
    return false;
  }
}
async function submitRegister() {
  const nick = cleanNickname($('reg-nick') && $('reg-nick').value);
  const pass = String(($('reg-pass') && $('reg-pass').value) || '');
  const pass2 = String(($('reg-pass2') && $('reg-pass2').value) || '');
  const validation = validateNickname(nick);
  if (validation) { setAuthMsg('register-msg', validation); return; }
  if (pass.length < 6) { setAuthMsg('register-msg', '비밀번호는 6자 이상이어야 합니다.'); return; }
  if (pass !== pass2) { setAuthMsg('register-msg', '비밀번호 확인이 일치하지 않습니다.'); return; }
  if (!useCloud || !fbAuth || !fbDb) { setAuthMsg('register-msg', 'Firebase 서버가 연결되지 않았습니다.'); return; }
  const btn = $('register-submit');
  if (btn) btn.disabled = true;
  setAuthMsg('register-msg', '서버에서 닉네임 확인 중...', true);
  let createdUser = null;
  try {
    if (await cloudNickTaken(nick)) { setAuthMsg('register-msg', '이미 사용 중인 닉네임입니다.'); return; }
    const email = nickToEmail(nick);
    const cred = await fbAuth.createUserWithEmailAndPassword(email, pass);
    createdUser = cred && cred.user;
    if (!createdUser) throw new Error('회원 계정 생성 결과가 없습니다.');
    fbUserId = createdUser.uid;
    currentUserKey = 'cloud:' + fbUserId;
    const nickRef = fbDb.collection('nicks').doc(nickKey(nick));
    await fbDb.runTransaction(async (tx) => {
      const snap = await tx.get(nickRef);
      if (snap.exists) {
        const err = new Error('NICK_TAKEN');
        err.code = 'NICK_TAKEN';
        throw err;
      }
      tx.set(nickRef, { uid: fbUserId, nick, nick_key: nickKey(nick), created_at: new Date().toISOString() });
    });
    saveData = defaultSaveData(nick);
    if (window.__legacySave && confirm('이전 로컬 기록을 이 계정으로 가져올까요?')) {
      saveData = Object.assign(saveData, window.__legacySave);
      saveData.nick = nick;
    }
    normalizeMissions();
    await cloudSaveProfile();
    try { localStorage.setItem('sword_mage_last_nick', nick); } catch (e) {}
    await fbAuth.signOut();
    fbUserId = null;
    currentUserKey = null;
    saveData = defaultSaveData('');
    setAutoLoginFlag(false);
    openLoginScreen();
    if ($('login-nick')) $('login-nick').value = nick;
    setAuthMsg('login-msg', '회원가입 완료! 방금 만든 계정으로 로그인하세요.', true);
  } catch (e) {
    if (createdUser) {
      try { await createdUser.delete(); } catch (cleanupErr) { console.warn('auth cleanup failed', cleanupErr); }
    }
    fbUserId = null;
    currentUserKey = null;
    if (String((e && (e.code || e.message)) || '').includes('NICK_TAKEN')) setAuthMsg('register-msg', '이미 사용 중인 닉네임입니다.');
    else setAuthMsg('register-msg', authErrorText(e, 'register'));
  } finally {
    if (btn) btn.disabled = false;
  }
}
async function submitLogin() {
  const nick = cleanNickname($('login-nick') && $('login-nick').value);
  const pass = String(($('login-pass') && $('login-pass').value) || '');
  const validation = validateNickname(nick);
  if (validation) { setAuthMsg('login-msg', validation); return; }
  if (pass.length < 6) { setAuthMsg('login-msg', '비밀번호는 6자 이상이어야 합니다.'); return; }
  if (!useCloud || !fbAuth || !fbDb) { setAuthMsg('login-msg', 'Firebase 서버가 연결되지 않았습니다.'); return; }
  const btn = $('login-submit');
  if (btn) btn.disabled = true;
  setAuthMsg('login-msg', '서버에서 계정 확인 중...', true);
  try {
    const email = nickToEmail(nick);
    const cred = await fbAuth.signInWithEmailAndPassword(email, pass);
    const user = cred && cred.user;
    if (!user) throw new Error('로그인 사용자 정보가 없습니다.');
    const nickSnap = await fbDb.collection('nicks').doc(nickKey(nick)).get();
    if (!nickSnap.exists || !nickSnap.data() || nickSnap.data().uid !== user.uid) {
      await fbAuth.signOut();
      throw new Error('닉네임 서버 정보가 계정과 일치하지 않습니다.');
    }
    fbUserId = user.uid;
    currentUserKey = 'cloud:' + fbUserId;
    const row = await cloudLoadProfile(fbUserId);
    if (row && row.data) {
      saveData = Object.assign(defaultSaveData(row.nick || nick), row.data);
      saveData.nick = row.nick || nick;
    } else {
      saveData = defaultSaveData(nick);
      await cloudSaveProfile();
    }
    normalizeMissions();
    try { localStorage.setItem('sword_mage_last_nick', nick); } catch (e) {}
    const auto = $('login-auto');
    setAutoLoginFlag(!auto || !!auto.checked);
    setAuthMsg('login-msg', '');
    updateRecordSummary();
    showScreen('select-screen');
  } catch (e) {
    try { if (fbAuth.currentUser) await fbAuth.signOut(); } catch (ignore) {}
    fbUserId = null;
    currentUserKey = null;
    setAuthMsg('login-msg', authErrorText(e, 'login'));
  } finally {
    if (btn) btn.disabled = false;
  }
}
async function submitAuth() {
  const reg = $('register-screen');
  if (reg && reg.classList.contains('active')) return submitRegister();
  return submitLogin();
}
async function logoutAccount() {
  if (!confirm('로그아웃 할까요?')) return;
  if (useCloud && fbAuth) { try { await fbAuth.signOut(); } catch (e) {} }
  fbUserId = null;
  currentUserKey = null;
  saveData = defaultSaveData('');
  setAutoLoginFlag(false);
  try { localStorage.removeItem(SESSION_KEY); } catch (e) {}
  showAuthLanding();
}
function bindAuthEnterKeys() {
  [$('login-nick'), $('login-pass')].forEach(el => { if (el) el.addEventListener('keydown', e => { if (e.key === 'Enter') submitLogin(); }); });
  [$('reg-nick'), $('reg-pass'), $('reg-pass2')].forEach(el => { if (el) el.addEventListener('keydown', e => { if (e.key === 'Enter') submitRegister(); }); });
}

'''

s, n = re.subn(r'function showAuthTab\(mode\) \{.*?(?=function exportSaveFile\(\))', auth_js, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit('auth JS block not found')

if "loadSave();\nshowAuthTab('login');" not in s:
    raise SystemExit('boot auth marker not found')
s = s.replace("loadSave();\nshowAuthTab('login');", "loadSave();\nshowAuthLanding();\nbindAuthEnterKeys();", 1)

marker = "function buyShopItem(id) {\n  const it = SHOP_ITEMS.find(x => x.id === id);\n  if (!it) return;\n  ensureShopSave();"
if marker not in s:
    raise SystemExit('buyShopItem marker not found')
s = s.replace(marker, marker + "\n\n  if (it.id === 'nick_change' && useCloud) {\n    alert('서버 계정에서는 닉네임 변경권을 현재 사용할 수 없습니다.');\n    return;\n  }", 1)

p.write_text(s, encoding='utf-8')
print('auth rebuild patch applied')

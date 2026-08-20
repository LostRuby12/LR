from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old_cloud = '''async function cloudSaveProfile() {
  if (!useCloud || !fbDb || !fbUserId) return;
  normalizeMissions();
  const payload = {
    nick: saveData.nick || '',
    lr: saveData.lr || 0,
    lp: saveData.lp || 0,
    data: saveData,
    updated_at: new Date().toISOString()
  };
  try {
    await fbDb.collection('profiles').doc(fbUserId).set(payload, { merge: true });
  } catch (e) {
    console.warn('cloud save', e);
  }
}'''

new_cloud = '''async function cloudSaveProfile() {
  if (!useCloud || !fbDb || !fbUserId) return;
  normalizeMissions();
  const payload = {
    nick: saveData.nick || '',
    lr: saveData.lr || 0,
    lp: saveData.lp || 0,
    data: saveData,
    updated_at: new Date().toISOString()
  };
  await fbDb.collection('profiles').doc(fbUserId).set(payload, { merge: true });
}'''

if old_cloud not in s:
    raise SystemExit('cloudSaveProfile block not found')
s = s.replace(old_cloud, new_cloud, 1)

start = s.index('async function submitRegister() {')
end = s.index('async function submitLogin()', start)
new_register = '''async function submitRegister() {
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
    if (await cloudNickTaken(nick)) {
      setAuthMsg('register-msg', '이미 사용 중인 닉네임입니다.');
      return;
    }

    const email = nickToEmail(nick);
    const cred = await fbAuth.createUserWithEmailAndPassword(email, pass);
    createdUser = cred && cred.user;
    if (!createdUser) throw new Error('회원 계정 생성 결과가 없습니다.');

    fbUserId = createdUser.uid;
    currentUserKey = 'cloud:' + fbUserId;

    let newSave = defaultSaveData(nick);
    if (window.__legacySave && confirm('이전 로컬 기록을 이 계정으로 가져올까요?')) {
      newSave = Object.assign(newSave, window.__legacySave);
      newSave.nick = nick;
    }
    saveData = newSave;
    normalizeMissions();

    const nickRef = fbDb.collection('nicks').doc(nickKey(nick));
    const profileRef = fbDb.collection('profiles').doc(fbUserId);
    const profilePayload = {
      nick: nick,
      lr: saveData.lr || 0,
      lp: saveData.lp || 0,
      data: saveData,
      updated_at: new Date().toISOString()
    };

    // 닉네임 선점과 프로필 생성을 한 트랜잭션에서 처리한다.
    await fbDb.runTransaction(async (tx) => {
      const nickSnap = await tx.get(nickRef);
      if (nickSnap.exists) {
        const err = new Error('NICK_TAKEN');
        err.code = 'NICK_TAKEN';
        throw err;
      }
      tx.set(nickRef, {
        uid: fbUserId,
        nick: nick,
        nick_key: nickKey(nick),
        created_at: new Date().toISOString()
      });
      tx.set(profileRef, profilePayload);
    });

    try { localStorage.setItem('sword_mage_last_nick', nick); } catch (e) {}

    // 회원가입 완료 후 로그인 화면으로 돌아가 직접 로그인한다.
    await fbAuth.signOut();
    fbUserId = null;
    currentUserKey = null;
    saveData = defaultSaveData('');
    setAutoLoginFlag(false);

    openLoginScreen();
    if ($('login-nick')) $('login-nick').value = nick;
    setAuthMsg('login-msg', '회원가입 완료! 방금 만든 계정으로 로그인하세요.', true);
  } catch (e) {
    // 트랜잭션 실패 시 Firestore에는 아무것도 남지 않는다. Auth 계정도 정리한다.
    if (createdUser) {
      try { await createdUser.delete(); } catch (cleanupErr) { console.warn('auth cleanup failed', cleanupErr); }
    }
    fbUserId = null;
    currentUserKey = null;
    saveData = defaultSaveData('');
    const key = String((e && (e.code || e.message)) || '');
    if (key.includes('NICK_TAKEN')) setAuthMsg('register-msg', '이미 사용 중인 닉네임입니다.');
    else setAuthMsg('register-msg', authErrorText(e, 'register'));
  } finally {
    if (btn) btn.disabled = false;
  }
}
'''
s = s[:start] + new_register + s[end:]

old_boot = '''// 시작 시 세이브 로드
loadSave();
showAuthLanding();
bindAuthEnterKeys();
(async function bootAuth() {
  let ok = false;
  // 자동 로그인이 켜져 있을 때만 세션 복구
  if (isAutoLoginEnabled() || true) {
    // 기본: 세션 있으면 바로 입장 (편의를 위해 세션 우선)
    if (useCloud) {
      ok = await restoreCloudSession();
    } else {
      ok = isLoggedIn();
    }
  }
  // 자동 로그인 끄고 로그아웃한 경우 세션 없음 → 로그인 화면
  if (ok) {
    showScreen('select-screen');
  } else {
    showScreen('auth-screen');
    if (window.__legacySave) {
      const am = $('auth-msg');
      if (am) am.textContent = '이전 기록이 있습니다. 회원가입 시 가져올 수 있습니다.';
    }
  }
})();'''

new_boot = '''// 시작 시 세이브 로드
loadSave();
showAuthLanding();
bindAuthEnterKeys();
(async function bootAuth() {
  let ok = false;
  if (useCloud && fbAuth) {
    if (isAutoLoginEnabled()) {
      ok = await restoreCloudSession();
    } else {
      try { await fbAuth.signOut(); } catch (e) {}
    }
  } else {
    ok = isLoggedIn();
  }

  if (ok) showScreen('select-screen');
  else showAuthLanding();
})();'''

if old_boot not in s:
    raise SystemExit('boot block not found')
s = s.replace(old_boot, new_boot, 1)

p.write_text(s, encoding='utf-8')
print('final auth fixes applied')

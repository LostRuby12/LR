from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Remove Cloud Functions client dependency / references.
s = s.replace('\n<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-functions-compat.js"></script>', '')
s = s.replace('let fbFunctions = null;\n', '')
s = s.replace("    fbFunctions = firebase.app().functions('asia-northeast3');\n", '')

# 2) Add client-side SHA-256 reward lookup. Plain coupon strings are not stored in HTML.
reward_helpers = r'''const CODE_REWARD_TABLE = Object.freeze({
  '2f9b71232ffe6929a600c93140179eab6c3cd6f1274f0e26e63fdcf5abbb9edb': { codeId: 'reward_a', lp: 7777, lr: 0, label: '7,777 LP' },
  'c93438a758c9aa9c5aa17a2b8cc3ea1b41a355be4fecf4f400d2a66a654506a2': { codeId: 'reward_b', lp: 0, lr: 777, label: '777 LR' },
  '280d44ab1e9f79b5cce2dd4f58f5fe91f0fbacdac9f7447dffc318ceb79f2d02': { codeId: 'welcome_reward', lp: 0, lr: 500, label: '500 LR' },
  '9c708286ba5458be8adda01ac28b33331ed6aeaac4e5c10897a0e7b7e17956dd': { codeId: 'welcome_reward', lp: 0, lr: 500, label: '500 LR' }
});

async function hashRewardCode(value) {
  const normalized = String(value || '').trim().toLowerCase();
  if (!normalized) return '';
  if (!window.crypto || !window.crypto.subtle || typeof TextEncoder === 'undefined') {
    throw new Error('HASH_UNSUPPORTED');
  }
  const bytes = new TextEncoder().encode(normalized);
  const digest = await window.crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

'''
if 'const CODE_REWARD_TABLE = Object.freeze({' not in s:
    marker = 'function setCodeMessage(text, ok = false) {'
    if marker not in s:
        raise SystemExit('setCodeMessage marker not found')
    s = s.replace(marker, reward_helpers + marker, 1)

# 3) Replace paid callable coupon redemption with Firestore transaction + hash lookup.
new_redeem = r'''async function redeemCode() {
  if (!requireLogin()) return;
  const input = $('redeem-code-input');
  const btn = $('redeem-code-btn');
  const raw = ((input && input.value) || '').trim();
  if (!raw) {
    setCodeMessage('코드를 입력하세요.');
    return;
  }
  if (!useCloud || !fbDb || !fbUserId) {
    setCodeMessage('로그인 정보를 확인한 뒤 다시 시도하세요.');
    return;
  }

  if (btn) btn.disabled = true;
  setCodeMessage('코드 확인 중...');
  try {
    const hash = await hashRewardCode(raw);
    const reward = CODE_REWARD_TABLE[hash];
    if (!reward) {
      setCodeMessage('존재하지 않는 코드입니다.');
      return;
    }

    const ref = fbDb.collection('profiles').doc(fbUserId);
    let updatedData = null;
    await fbDb.runTransaction(async (tx) => {
      const snap = await tx.get(ref);
      if (!snap.exists) throw new Error('PROFILE_MISSING');
      const profile = snap.data() || {};
      const base = Object.assign(
        defaultSaveData(profile.nick || saveData.nick || ''),
        profile.data || saveData || {}
      );
      base.redeemedCodes = Object.assign({}, base.redeemedCodes || {});
      if (base.redeemedCodes[reward.codeId]) throw new Error('CODE_ALREADY_USED');

      base.redeemedCodes[reward.codeId] = new Date().toISOString();
      base.lr = Math.max(0, Number(base.lr) || 0) + (Number(reward.lr) || 0);
      base.lp = Math.max(0, Number(base.lp) || 0) + (Number(reward.lp) || 0);

      tx.set(ref, {
        nick: base.nick || profile.nick || '',
        lr: base.lr,
        lp: base.lp,
        data: base,
        updated_at: new Date().toISOString()
      }, { merge: true });
      updatedData = base;
    });

    saveData = Object.assign(defaultSaveData((updatedData && updatedData.nick) || saveData.nick || ''), updatedData || {});
    try { upsertRankBoard(saveData.nick || '나', saveData.lr || 0); } catch (e) {}
    updateRecordSummary();
    setCodeMessage(`코드 사용 완료! +${reward.label}`, true);
    if (input) input.value = '';
  } catch (e) {
    if (e && e.message === 'CODE_ALREADY_USED') {
      setCodeMessage('이미 사용한 코드입니다.');
    } else if (e && e.message === 'HASH_UNSUPPORTED') {
      setCodeMessage('현재 브라우저에서는 코드 확인을 지원하지 않습니다.');
    } else {
      console.warn('redeemCode failed', e);
      setCodeMessage('코드 지급 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.');
    }
  } finally {
    if (btn) btn.disabled = false;
  }
}

function openHelp()'''
s, n = re.subn(r'async function redeemCode\(\) \{.*?\n\}\n\nfunction openHelp\(\)', new_redeem, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'redeem replacement count={n}')

# 4) Replace paid attendance callable with free Firestore transaction.
new_attendance = r'''function attendanceDateSerial(ymd) {
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

  const today = kstTodayClient();
  if (!today) {
    if (msg) { msg.style.color = '#ff9a9a'; msg.textContent = '날짜 확인에 실패했습니다.'; }
    return;
  }

  if (btn) btn.disabled = true;
  if (msg) { msg.style.color = '#c8c8ff'; msg.textContent = '출석 확인 중...'; }
  try {
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
      if (attendance.lastDate === today) throw new Error('ATTENDANCE_ALREADY_CLAIMED');

      const prev = attendanceDateSerial(attendance.lastDate);
      const now = attendanceDateSerial(today);
      const streak = (prev !== null && now !== null && now - prev === 1)
        ? Math.max(0, Number(attendance.streak) || 0) + 1
        : 1;
      const lrReward = 100;
      const lpReward = streak % 7 === 0 ? 100 : 0;

      base.lr = Math.max(0, Number(base.lr) || 0) + lrReward;
      base.lp = Math.max(0, Number(base.lp) || 0) + lpReward;
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
        updated_at: new Date().toISOString()
      }, { merge: true });

      updatedData = base;
      rewardText = lpReward > 0
        ? `출석 완료! +${lrReward} LR · 7일 연속 보너스 +${lpReward} LP`
        : `출석 완료! +${lrReward} LR`;
    });

    saveData = Object.assign(defaultSaveData((updatedData && updatedData.nick) || saveData.nick || ''), updatedData || {});
    try { upsertRankBoard(saveData.nick || '나', saveData.lr || 0); } catch (e) {}
    updateRecordSummary();
    renderAttendanceInfo();
    if (msg) { msg.style.color = '#75ffad'; msg.textContent = rewardText; }
  } catch (e) {
    if (e && e.message === 'ATTENDANCE_ALREADY_CLAIMED') {
      if (msg) { msg.style.color = '#ffdb75'; msg.textContent = '오늘 출석 보상은 이미 받았습니다.'; }
    } else {
      console.warn('claimAttendanceReward failed', e);
      if (msg) { msg.style.color = '#ff9a9a'; msg.textContent = '출석 처리 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.'; }
    }
  } finally {
    if (btn) btn.disabled = false;
  }
}

function kstTodayClient()'''
s, n = re.subn(r'async function claimAttendanceReward\(\) \{.*?\n\}\n\nfunction kstTodayClient\(\)', new_attendance, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'attendance replacement count={n}')

# 5) Safety checks: no Cloud Functions client remains and no coupon plaintext is embedded.
for forbidden in [
    'firebase-functions-compat.js',
    'fbFunctions',
    "httpsCallable('redeemCode')",
    "httpsCallable('claimAttendance')",
    'godruin',
    'lostruby'
]:
    if forbidden in s.lower() if forbidden in ('godruin', 'lostruby') else forbidden in s:
        raise SystemExit(f'forbidden token remains: {forbidden}')

p.write_text(s, encoding='utf-8')
print('free reward patch applied')

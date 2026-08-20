const crypto = require('crypto');
const { onCall, HttpsError } = require('firebase-functions/v2/https');
const { setGlobalOptions } = require('firebase-functions/v2');
const { initializeApp } = require('firebase-admin/app');
const { getFirestore, FieldValue } = require('firebase-admin/firestore');

initializeApp();
setGlobalOptions({ region: 'asia-northeast3', maxInstances: 10 });

const db = getFirestore();

// Plain-text coupon strings are intentionally NOT stored here.
// These are SHA-256 hashes only. Existing public codes are kept for compatibility.
const LEGACY_CODE_HASHES = Object.freeze({
  '2f9b71232ffe6929a600c93140179eab6c3cd6f1274f0e26e63fdcf5abbb9edb': { codeId: 'legacy_a', lp: 7777, lr: 0, label: '7,777 LP' },
  'c93438a758c9aa9c5aa17a2b8cc3ea1b41a355be4fecf4f400d2a66a654506a2': { codeId: 'legacy_b', lp: 0, lr: 777, label: '777 LR' },
  '280d44ab1e9f79b5cce2dd4f58f5fe91f0fbacdac9f7447dffc318ceb79f2d02': { codeId: 'welcome_1', lp: 0, lr: 500, label: '500 LR' },
  '9c708286ba5458be8adda01ac28b33331ed6aeaac4e5c10897a0e7b7e17956dd': { codeId: 'welcome_1', lp: 0, lr: 500, label: '500 LR' }
});

function normalizeCode(value) {
  return String(value || '').trim().toLowerCase();
}

function sha256(value) {
  return crypto.createHash('sha256').update(value, 'utf8').digest('hex');
}

function num(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function buildSave(profile) {
  const data = profile && profile.data && typeof profile.data === 'object' ? { ...profile.data } : {};
  data.nick = data.nick || (profile && profile.nick) || '';
  data.lr = Math.max(0, num(data.lr !== undefined ? data.lr : profile && profile.lr));
  data.lp = Math.max(0, num(data.lp !== undefined ? data.lp : profile && profile.lp));
  data.redeemedCodes = data.redeemedCodes && typeof data.redeemedCodes === 'object' ? { ...data.redeemedCodes } : {};
  data.attendance = data.attendance && typeof data.attendance === 'object'
    ? { ...data.attendance }
    : { lastDate: '', streak: 0, total: 0 };
  return data;
}

async function lookupCode(hash) {
  const dynamicSnap = await db.collection('couponCodes').doc(hash).get();
  if (dynamicSnap.exists) {
    const d = dynamicSnap.data() || {};
    if (d.active === false) return null;
    const lr = Math.max(0, num(d.lr));
    const lp = Math.max(0, num(d.lp));
    if (lr <= 0 && lp <= 0) return null;
    return {
      codeId: String(d.codeId || hash),
      lr,
      lp,
      label: String(d.label || [lr ? `${lr.toLocaleString()} LR` : '', lp ? `${lp.toLocaleString()} LP` : ''].filter(Boolean).join(' + '))
    };
  }
  return LEGACY_CODE_HASHES[hash] || null;
}

exports.redeemCode = onCall(async (request) => {
  if (!request.auth || !request.auth.uid) {
    throw new HttpsError('unauthenticated', '로그인이 필요합니다.');
  }

  const code = normalizeCode(request.data && request.data.code);
  if (!code || code.length > 64) {
    throw new HttpsError('invalid-argument', '올바른 코드를 입력하세요.');
  }

  const hash = sha256(code);
  const reward = await lookupCode(hash);
  if (!reward) {
    throw new HttpsError('not-found', '존재하지 않거나 종료된 코드입니다.');
  }

  const uid = request.auth.uid;
  const ref = db.collection('profiles').doc(uid);

  const result = await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError('failed-precondition', '프로필이 없습니다. 다시 로그인하세요.');

    const profile = snap.data() || {};
    const data = buildSave(profile);
    if (data.redeemedCodes[reward.codeId]) {
      throw new HttpsError('already-exists', '이미 사용한 코드입니다.');
    }

    data.redeemedCodes[reward.codeId] = new Date().toISOString();
    data.lr += reward.lr || 0;
    data.lp += reward.lp || 0;

    tx.set(ref, {
      nick: data.nick || profile.nick || '',
      lr: data.lr,
      lp: data.lp,
      data,
      updated_at: FieldValue.serverTimestamp()
    }, { merge: true });

    return { lr: data.lr, lp: data.lp };
  });

  return {
    ok: true,
    label: reward.label,
    lr: result.lr,
    lp: result.lp
  };
});

function kstDateString(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).formatToParts(date);
  const map = Object.fromEntries(parts.map(p => [p.type, p.value]));
  return `${map.year}-${map.month}-${map.day}`;
}

function dateSerial(ymd) {
  const [y, m, d] = String(ymd || '').split('-').map(Number);
  if (!y || !m || !d) return null;
  return Math.floor(Date.UTC(y, m - 1, d) / 86400000);
}

exports.claimAttendance = onCall(async (request) => {
  if (!request.auth || !request.auth.uid) {
    throw new HttpsError('unauthenticated', '로그인이 필요합니다.');
  }

  const uid = request.auth.uid;
  const today = kstDateString();
  const ref = db.collection('profiles').doc(uid);

  const result = await db.runTransaction(async (tx) => {
    const snap = await tx.get(ref);
    if (!snap.exists) throw new HttpsError('failed-precondition', '프로필이 없습니다. 다시 로그인하세요.');

    const profile = snap.data() || {};
    const data = buildSave(profile);
    const attendance = data.attendance || { lastDate: '', streak: 0, total: 0 };

    if (attendance.lastDate === today) {
      throw new HttpsError('already-exists', '오늘 출석 보상은 이미 받았습니다.');
    }

    const prevSerial = dateSerial(attendance.lastDate);
    const todaySerial = dateSerial(today);
    const streak = prevSerial !== null && todaySerial - prevSerial === 1
      ? Math.max(0, num(attendance.streak)) + 1
      : 1;

    const lrReward = 100;
    const lpReward = streak % 7 === 0 ? 100 : 0;

    data.lr += lrReward;
    data.lp += lpReward;
    data.attendance = {
      lastDate: today,
      streak,
      total: Math.max(0, num(attendance.total)) + 1
    };

    tx.set(ref, {
      nick: data.nick || profile.nick || '',
      lr: data.lr,
      lp: data.lp,
      data,
      updated_at: FieldValue.serverTimestamp()
    }, { merge: true });

    return {
      streak,
      total: data.attendance.total,
      lrReward,
      lpReward,
      lr: data.lr,
      lp: data.lp
    };
  });

  return { ok: true, today, ...result };
});

from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# 1) Save schema: redeemed code history
old = """    nick: nick || '', tag: '', lr: 0, lp: 0, rankBoard: [],
    shop: { goldNick: false, assassin: false, priest: false, archer: false },"""
new = """    nick: nick || '', tag: '', lr: 0, lp: 0, rankBoard: [],
    redeemedCodes: {},
    shop: { goldNick: false, assassin: false, priest: false, archer: false },"""
if old not in s:
    raise SystemExit('defaultSaveData anchor not found')
s = s.replace(old, new, 1)

# 2) Shop exchanges
old = """const SHOP_ITEMS = [
  { id: 'lr_to_lp', name: 'LR → LP 교환', desc: '100 LR → 10 LP', price: 100, currency: 'lr', type: 'exchange' },"""
new = """const SHOP_ITEMS = [
  { id: 'lr_to_lp_100', name: 'LR → LP 교환', desc: '100 LR → 10 LP', price: 100, lpGain: 10, currency: 'lr', type: 'exchange' },
  { id: 'lr_to_lp_1000', name: 'LR → LP 교환', desc: '1,000 LR → 100 LP', price: 1000, lpGain: 100, currency: 'lr', type: 'exchange' },
  { id: 'lr_to_lp_10000', name: 'LR → LP 교환', desc: '10,000 LR → 1,000 LP', price: 10000, lpGain: 1000, currency: 'lr', type: 'exchange' },"""
if old not in s:
    raise SystemExit('SHOP_ITEMS anchor not found')
s = s.replace(old, new, 1)

old = """  if (it.type === 'exchange') {
    saveData.lr -= 100;
    saveData.lp = (saveData.lp || 0) + 10;
    persistSave();
    try { upsertRankBoard(saveData.nick || '나', saveData.lr); } catch (e) {}
    alert(`교환 완료! +10 LP (보유 LP ${saveData.lp})`);
    renderShop();
    return;
  }"""
new = """  if (it.type === 'exchange') {
    const cost = Number(it.price) || 0;
    const gain = Number(it.lpGain) || 0;
    if ((saveData.lr || 0) < cost) {
      alert(`LR이 부족합니다. 필요 LR: ${cost.toLocaleString()}`);
      return;
    }
    saveData.lr -= cost;
    saveData.lp = (saveData.lp || 0) + gain;
    persistSave();
    try { upsertRankBoard(saveData.nick || '나', saveData.lr); } catch (e) {}
    alert(`교환 완료! +${gain.toLocaleString()} LP (보유 LP ${saveData.lp.toLocaleString()})`);
    renderShop();
    return;
  }"""
if old not in s:
    raise SystemExit('exchange handler anchor not found')
s = s.replace(old, new, 1)

# 3) Code button in Etc grid, full width
old = """      <button class=\"btn\" style=\"margin:0; min-height:74px; padding:12px 8px; font-size:0.98rem; background:linear-gradient(135deg,#667eea,#764ba2);\" onclick=\"openStory()\">📜<br>스토리</button>
    </div>"""
new = """      <button class=\"btn\" style=\"margin:0; min-height:74px; padding:12px 8px; font-size:0.98rem; background:linear-gradient(135deg,#667eea,#764ba2);\" onclick=\"openStory()\">📜<br>스토리</button>
      <button class=\"btn btn-gold\" style=\"grid-column:1 / -1; margin:0; min-height:64px; padding:12px 8px; font-size:1rem;\" onclick=\"openCodeTab()\">🎁 코드</button>
    </div>"""
if old not in s:
    raise SystemExit('etc grid anchor not found')
s = s.replace(old, new, 1)

# 4) Code screen before help screen
anchor = """  <!-- 효과·능력 설명 -->
  <div id=\"help-screen\" class=\"screen\">"""
insert = """  <!-- 코드 입력 -->
  <div id=\"code-screen\" class=\"screen\">
    <h2 style=\"text-align:center;\">🎁 코드</h2>
    <p style=\"text-align:center; opacity:0.72; font-size:0.85rem; margin-bottom:16px;\">이벤트 코드를 입력하세요. 각 코드는 계정당 1회만 사용할 수 있습니다.</p>
    <input id=\"redeem-code-input\" type=\"text\" maxlength=\"32\" autocomplete=\"off\" placeholder=\"코드 입력\"
      style=\"width:100%;box-sizing:border-box;padding:14px;border-radius:12px;border:2px solid #ffd700;background:#111526;color:#fff;font-size:1rem;text-align:center;margin-top:8px;\" />
    <p id=\"redeem-code-msg\" style=\"text-align:center;min-height:1.4em;margin-top:12px;font-size:0.9rem;color:#ff9a9a;\"></p>
    <button class=\"btn btn-gold\" id=\"redeem-code-btn\" style=\"margin-top:8px;\" onclick=\"redeemCode()\">코드 사용</button>
    <div style=\"flex:1; min-height:40px;\"></div>
    <button class=\"btn\" style=\"margin-top:12px;\" onclick=\"showScreen('etc-screen')\">← 기타로</button>
  </div>

  <!-- 효과·능력 설명 -->
  <div id=\"help-screen\" class=\"screen\">"""
if anchor not in s:
    raise SystemExit('help-screen anchor not found')
s = s.replace(anchor, insert, 1)

# 5) Code redemption logic. Codes are case-insensitive; Firestore transaction makes one-use check atomic per account.
anchor = """function openEtcMenu() {
  if (!requireLogin()) return;
  showScreen('etc-screen');
}
function openHelp() {"""
insert = """function openEtcMenu() {
  if (!requireLogin()) return;
  showScreen('etc-screen');
}

const REDEEM_CODES = Object.freeze({
  godruin: { lp: 7777, label: '7,777 LP' },
  lostruby: { lr: 777, label: '777 LR' }
});

function setCodeMessage(text, ok = false) {
  const el = $('redeem-code-msg');
  if (!el) return;
  el.textContent = text || '';
  el.style.color = ok ? '#75ffad' : '#ff9a9a';
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
  const key = raw.toLowerCase();
  if (!key) {
    setCodeMessage('코드를 입력하세요.');
    return;
  }

  const reward = REDEEM_CODES[key];
  if (!reward) {
    setCodeMessage('존재하지 않는 코드입니다.');
    return;
  }

  if (btn) btn.disabled = true;
  setCodeMessage('코드 확인 중...');

  try {
    let updatedData = null;
    const now = new Date().toISOString();

    if (useCloud && fbDb && fbUserId) {
      const ref = fbDb.collection('profiles').doc(fbUserId);
      updatedData = await fbDb.runTransaction(async (tx) => {
        const snap = await tx.get(ref);
        const profile = snap.exists ? (snap.data() || {}) : {};
        const base = Object.assign(defaultSaveData(profile.nick || saveData.nick || ''), profile.data || saveData || {});
        base.redeemedCodes = Object.assign({}, base.redeemedCodes || {});
        if (base.redeemedCodes[key]) throw new Error('CODE_ALREADY_USED');

        base.redeemedCodes[key] = now;
        base.lr = Math.max(0, Number(base.lr) || 0) + (Number(reward.lr) || 0);
        base.lp = Math.max(0, Number(base.lp) || 0) + (Number(reward.lp) || 0);

        tx.set(ref, {
          nick: base.nick || saveData.nick || '',
          lr: base.lr,
          lp: base.lp,
          data: base,
          updated_at: now
        }, { merge: true });
        return base;
      });
      saveData = Object.assign(defaultSaveData(updatedData.nick || ''), updatedData);
    } else {
      saveData.redeemedCodes = Object.assign({}, saveData.redeemedCodes || {});
      if (saveData.redeemedCodes[key]) throw new Error('CODE_ALREADY_USED');
      saveData.redeemedCodes[key] = now;
      saveData.lr = Math.max(0, Number(saveData.lr) || 0) + (Number(reward.lr) || 0);
      saveData.lp = Math.max(0, Number(saveData.lp) || 0) + (Number(reward.lp) || 0);
    }

    persistSave();
    try { upsertRankBoard(saveData.nick || '나', saveData.lr || 0); } catch (e) {}
    updateRecordSummary();
    setCodeMessage(`코드 사용 완료! +${reward.label}`, true);
    if (input) input.value = '';
  } catch (e) {
    if (e && e.message === 'CODE_ALREADY_USED') {
      setCodeMessage('이미 사용한 코드입니다.');
    } else {
      console.warn('redeemCode failed', e);
      setCodeMessage('코드 지급 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.');
    }
  } finally {
    if (btn) btn.disabled = false;
  }
}

function openHelp() {"""
if anchor not in s:
    raise SystemExit('openEtcMenu anchor not found')
s = s.replace(anchor, insert, 1)

p.write_text(s, encoding='utf-8')

# Basic validation
assert 'godruin' in s and 'lostruby' in s
assert 'lr_to_lp_1000' in s and 'lr_to_lp_10000' in s
assert 'id="code-screen"' in s
assert s.count('id="code-screen"') == 1
print('patched index.html')

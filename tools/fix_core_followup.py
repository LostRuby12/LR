from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    s = s.replace(old, new, 1)

# Local PeerJS close events can arrive after rtLeave() has nulled rtConn.
# Treat stale/local connection callbacks as local closes even if the timer flag reset already happened.
replace_once(
"""  conn.on('close', () => {
    if (rtClosingLocally) {
      rtConnected = false;
      return;
    }
""",
"""  conn.on('close', () => {
    if (rtClosingLocally || conn !== rtConn) {
      rtConnected = false;
      return;
    }
""",
'local close race')

# Clamp peer-provided shield snapshots to the legitimate in-game maximum.
replace_once(
"""  playerShield = Math.max(0, Number(st.shield) || 0);
""",
"""  playerShield = clamp(Number(st.shield) || 0, 0, 300);
""",
'player shield clamp')
replace_once(
"""  enemyShield = Math.max(0, Number(st.shield) || 0);
""",
"""  enemyShield = clamp(Number(st.shield) || 0, 0, 300);
""",
'enemy shield clamp')

# Sanitize peer-provided nickname before it can reach local ranking HTML or lobby UI.
replace_once(
"""function rtNormalizeBuild(data) {
  const cls = RT_ALLOWED_CLASSES.has(data && data.cls) ? data.cls : 'sword';
  const lvRaw = Number(data && data.lv);
  const lv = clamp(Number.isFinite(lvRaw) ? Math.floor(lvRaw) : 0, 0, 10);
  const maxHpSafe = getBaseHp(cls) + lv * 100;
  return {
    nick: String((data && data.nick) || '상대').slice(0, 12),
""",
"""function rtNormalizeBuild(data) {
  const cls = RT_ALLOWED_CLASSES.has(data && data.cls) ? data.cls : 'sword';
  const lvRaw = Number(data && data.lv);
  const lv = clamp(Number.isFinite(lvRaw) ? Math.floor(lvRaw) : 0, 0, 10);
  const maxHpSafe = getBaseHp(cls) + lv * 100;
  const candidateNick = cleanNickname(String((data && data.nick) || '상대'));
  const safeNick = validateNickname(candidateNick) ? '상대' : candidateNick;
  return {
    nick: safeNick || '상대',
""",
'ready nick sanitize')

replace_once(
"""    rtOppNick = data.nick || '상대';
    if (typeof data.lr === 'number') upsertRankBoard(rtOppNick, data.lr);
""",
"""    const candidateNick = cleanNickname(String(data.nick || '상대'));
    rtOppNick = validateNickname(candidateNick) ? '상대' : (candidateNick || '상대');
    if (typeof data.lr === 'number') upsertRankBoard(rtOppNick, data.lr);
""",
'hello nick sanitize')

# If the app stays open across midnight, refresh the trusted KST day when entering Play.
replace_once(
"""function openPlayMenu() {
  if (!requireLogin()) return;
  updateRecordSummary();
  pendingPlayMode = null;
  showScreen('play-menu-screen');
}
""",
"""async function openPlayMenu() {
  if (!requireLogin()) return;
  if (useCloud && fbDb && fbUserId) {
    try { await getTrustedAttendanceToday(); } catch (e) { console.warn('play daily server date sync failed', e); }
  }
  normalizeMissions();
  updateRecordSummary();
  pendingPlayMode = null;
  showScreen('play-menu-screen');
}
""",
'play midnight refresh')

checks = [
    "rtClosingLocally || conn !== rtConn",
    "playerShield = clamp(Number(st.shield) || 0, 0, 300)",
    "enemyShield = clamp(Number(st.shield) || 0, 0, 300)",
    "const safeNick = validateNickname(candidateNick) ? '상대' : candidateNick",
    "async function openPlayMenu()",
    "await getTrustedAttendanceToday()",
]
for needle in checks:
    if needle not in s:
        raise SystemExit('missing postcondition: ' + needle)

p.write_text(s, encoding='utf-8')
print('follow-up hardening applied')

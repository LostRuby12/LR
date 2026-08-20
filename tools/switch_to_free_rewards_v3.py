from pathlib import Path
import re

index_path = Path('index.html')
base_script_path = Path('tools/switch_to_free_rewards.py')
s = index_path.read_text(encoding='utf-8')
base_src = base_script_path.read_text(encoding='utf-8')

# Reuse the already-reviewed replacement blocks from v1 without executing v1.
def extract_raw(name):
    m = re.search(rf"{re.escape(name)}\s*=\s*r'''(.*?)'''", base_src, flags=re.S)
    if not m:
        raise SystemExit(f'cannot extract {name}')
    return m.group(1)

reward_helpers = extract_raw('reward_helpers')
new_redeem = extract_raw('new_redeem')
new_attendance = extract_raw('new_attendance')

# Remove marker signatures that v1 used for regex replacement.
redeem_tail = '\n\nfunction openHelp()'
if not new_redeem.endswith(redeem_tail):
    raise SystemExit('unexpected redeem replacement tail')
new_redeem = new_redeem[:-len(redeem_tail)]

attendance_tail = '\n\nfunction kstTodayClient()'
if not new_attendance.endswith(attendance_tail):
    raise SystemExit('unexpected attendance replacement tail')
new_attendance = new_attendance[:-len(attendance_tail)]

# Cloud Functions is not used in the free version.
s = s.replace('\n<script src="https://www.gstatic.com/firebasejs/10.14.1/firebase-functions-compat.js"></script>', '')
s = s.replace('let fbFunctions = null;\n', '')
s = s.replace("    fbFunctions = firebase.app().functions('asia-northeast3');\n", '')

# Insert SHA-256 reward table before the existing message helper.
if 'const CODE_REWARD_TABLE = Object.freeze({' not in s:
    marker = 'function setCodeMessage(text, ok = false) {'
    pos = s.find(marker)
    if pos < 0:
        raise SystemExit('setCodeMessage marker not found')
    s = s[:pos] + reward_helpers + s[pos:]

# Replace exactly one function range while preserving the next function.
def replace_between(text, start_marker, end_marker, replacement):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'start marker not found: {start_marker}')
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise SystemExit(f'end marker not found: {end_marker}')
    return text[:start] + replacement.rstrip() + '\n\n' + text[end:]

s = replace_between(
    s,
    'async function redeemCode() {',
    'function kstTodayClient() {',
    new_redeem
)

s = replace_between(
    s,
    'async function claimAttendanceReward() {',
    'function openHelp() {',
    new_attendance
)

# Final safety checks.
checks_absent = [
    'firebase-functions-compat.js',
    'fbFunctions',
    "httpsCallable('redeemCode')",
    "httpsCallable('claimAttendance')"
]
for token in checks_absent:
    if token in s:
        raise SystemExit(f'forbidden token remains: {token}')

lower = s.lower()
for token in ['godruin', 'lostruby']:
    if token in lower:
        raise SystemExit(f'plaintext coupon remains: {token}')

for required in ['CODE_REWARD_TABLE', 'hashRewardCode', 'attendanceDateSerial', 'claimAttendanceReward']:
    if required not in s:
        raise SystemExit(f'required token missing: {required}')

index_path.write_text(s, encoding='utf-8')
print('free rewards v3 patch applied')

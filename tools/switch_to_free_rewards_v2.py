from pathlib import Path
import re

src_path = Path('tools/switch_to_free_rewards.py')
src = src_path.read_text(encoding='utf-8')

fixed_line = "s, n = re.subn(r'async function claimAttendanceReward\\(\\)\\s*\\{.*?function kstTodayClient\\(\\)', new_attendance, s, count=1, flags=re.S)"
src, count = re.subn(
    r"s, n = re\.subn\(r'async function claimAttendanceReward.*?flags=re\.S\)",
    lambda m: fixed_line,
    src,
    count=1
)
if count != 1:
    raise SystemExit(f'could not patch attendance matcher: {count}')

exec(compile(src, str(src_path), 'exec'), {'__name__': '__main__'})

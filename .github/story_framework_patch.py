from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

old = '''    <p style="text-align:center;opacity:0.78;font-size:0.9rem;margin-bottom:14px;">콘텐츠를 선택한 뒤 직업을 정합니다</p>
    <button class="btn btn-gold" style="padding:17px 14px;" onclick="openModeClassSelect('story')">📜 메인 스토리<br><span style="font-size:0.78rem;font-weight:500;opacity:0.8;">스토리 강화 전투</span></button>'''
new = '''    <p style="text-align:center;opacity:0.78;font-size:0.9rem;margin-bottom:14px;">메인 스토리는 챕터와 스테이지를 순서대로 진행합니다</p>
    <button class="btn btn-gold" style="padding:17px 14px;" onclick="openStory()">📜 메인 스토리<br><span style="font-size:0.78rem;font-weight:500;opacity:0.8;">챕터 선택 · 스테이지 순차 진행</span></button>'''
if old not in s:
    raise SystemExit('main story button anchor missing')
s = s.replace(old, new, 1)

old = '''  <!-- 스토리 -->
  <div id="story-screen" class="screen">
    <h2 style="text-align:center;">📜 스토리</h2>
    <div id="story-list" style="overflow-y:auto; max-height:72vh; padding:4px 2px;"></div>
    <button class="btn" style="margin-top:12px;" onclick="showScreen('etc-screen')">← 기타로</button>
  </div>'''
new = '''  <!-- 메인 스토리 -->
  <div id="story-screen" class="screen">
    <h2 id="story-title" style="text-align:center;">📜 메인 스토리</h2>
    <p id="story-subtitle" style="text-align:center;opacity:0.72;font-size:0.84rem;margin:-4px 0 10px;"></p>
    <div id="story-list" style="overflow-y:auto; max-height:72vh; padding:4px 2px;"></div>
    <button id="story-back-btn" class="btn" style="margin-top:12px;" onclick="backFromStory()">← 메인 편으로</button>
  </div>'''
if old not in s:
    raise SystemExit('story screen anchor missing')
s = s.replace(old, new, 1)

old = "  if (mode === 'story' || mode === 'quick') {\n    challengeMode = false;"
new = "  if (mode === 'story') {\n    openStory();\n    return;\n  }\n  if (mode === 'quick') {\n    challengeMode = false;"
if old not in s:
    raise SystemExit('story route anchor missing')
s = s.replace(old, new, 1)

pat = re.compile(r"function openStory\(\) \{.*?\nfunction openBossMode\(\) \{", re.S)
block = r'''let storyViewChapter = null;
let storyReturnScreen = 'main-chapter-screen';

const STORY_CHAPTER_ORDER = Object.freeze([
  'earth1', 'delta1', 'ancient1', 'future1', 'earth2',
  'demon1', 'heaven1', 'space1', 'void'
]);

const STORY_CHAPTER_ICONS = Object.freeze({
  earth1: '🌍', delta1: '🔷', ancient1: '🏛️', future1: '🌆', earth2: '🌎',
  demon1: '😈', heaven1: '☁️', space1: '🌌', void: '🕳️'
});

const EARTH1_STAGE_TITLES = Object.freeze({
  1: '작전 개시',
  2: '외곽 경비병',
  3: '뱀의 둥지 전투원',
  4: '중간 간부',
  5: 'B.S.H 생포'
});

function storyActiveScreenId() {
  const el = document.querySelector('.screen.active');
  return el && el.id ? el.id : '';
}

function storyChapterUnlocked(id) {
  const idx = STORY_CHAPTER_ORDER.indexOf(id);
  if (idx < 0) return false;
  if (idx === 0) return true;
  return storyChapterCleared(STORY_CHAPTER_ORDER[idx - 1]);
}

function storyStageUnlocked(chapterId, stageNo) {
  if (!storyChapterUnlocked(chapterId)) return false;
  const meta = STORY_CHAPTER_META[chapterId];
  if (!meta || stageNo < 1 || stageNo > meta.stages) return false;
  const story = ensureStoryProgress();
  const cleared = Number(story.stages[chapterId]) || 0;
  return stageNo <= Math.min(meta.stages, cleared + 1);
}

function openStory() {
  if (!requireLogin()) return;
  const from = storyActiveScreenId();
  if (from && from !== 'story-screen') storyReturnScreen = from;
  ensureStoryProgress();
  storyViewChapter = null;
  renderStory();
  showScreen('story-screen');
}

function backFromStory() {
  if (storyViewChapter) {
    storyViewChapter = null;
    renderStory();
    return;
  }
  const target = $(storyReturnScreen) ? storyReturnScreen : 'main-chapter-screen';
  showScreen(target);
}

function renderStory() {
  const el = $('story-list');
  const title = $('story-title');
  const subtitle = $('story-subtitle');
  const back = $('story-back-btn');
  if (!el) return;
  ensureStoryProgress();

  if (storyViewChapter) {
    renderStoryChapter(storyViewChapter);
    return;
  }

  if (title) title.textContent = '📜 메인 스토리';
  if (subtitle) subtitle.textContent = '총 9개 챕터 · 73개 스테이지';
  if (back) back.textContent = '← 돌아가기';

  el.innerHTML = STORY_CHAPTER_ORDER.map((id, idx) => {
    const meta = STORY_CHAPTER_META[id];
    const story = ensureStoryProgress();
    const cleared = Math.max(0, Math.min(meta.stages, Number(story.stages[id]) || 0));
    const unlocked = storyChapterUnlocked(id);
    const complete = storyChapterCleared(id);
    const bossNote = id === 'ancient1'
      ? '<div style="font-size:0.75rem;color:#cbb8ff;margin-top:5px;">클리어 보상: 고대 마법사 보스전 해금</div>'
      : (id === 'demon1'
        ? '<div style="font-size:0.75rem;color:#ffaaa8;margin-top:5px;">클리어 보상: 몰락한 신 보스전 해금</div>'
        : '');
    return `<button class="btn" ${unlocked ? `onclick="openStoryChapter('${id}')"` : 'disabled'} style="text-align:left;padding:14px 15px;margin:7px 0;${complete ? 'border:1px solid #75ffad;' : ''}">
      <div style="display:flex;justify-content:space-between;gap:8px;align-items:center;">
        <span style="font-weight:900;">${complete ? '✅' : (unlocked ? STORY_CHAPTER_ICONS[id] : '🔒')} ${idx + 1}. ${meta.name}</span>
        <span style="font-size:0.76rem;opacity:0.78;white-space:nowrap;">${cleared}/${meta.stages}</span>
      </div>
      <div style="font-size:0.8rem;opacity:0.72;margin-top:4px;">${meta.stages} STAGE${unlocked ? '' : ' · 이전 챕터 클리어 필요'}</div>
      ${bossNote}
    </button>`;
  }).join('');
}

function openStoryChapter(id) {
  if (!STORY_CHAPTER_META[id]) return;
  if (!storyChapterUnlocked(id)) {
    alert('이전 챕터를 먼저 클리어하세요.');
    return;
  }
  storyViewChapter = id;
  renderStoryChapter(id);
  showScreen('story-screen');
}

function renderStoryChapter(id) {
  const meta = STORY_CHAPTER_META[id];
  const el = $('story-list');
  const title = $('story-title');
  const subtitle = $('story-subtitle');
  const back = $('story-back-btn');
  if (!meta || !el) return;
  const story = ensureStoryProgress();
  const cleared = Math.max(0, Math.min(meta.stages, Number(story.stages[id]) || 0));

  if (title) title.textContent = `${STORY_CHAPTER_ICONS[id] || '📖'} ${meta.name}`;
  if (subtitle) subtitle.textContent = `진행 ${cleared}/${meta.stages} · 스테이지는 순서대로 해금`;
  if (back) back.textContent = '← 챕터 선택으로';

  let html = '';
  for (let no = 1; no <= meta.stages; no++) {
    const done = no <= cleared;
    const unlocked = storyStageUnlocked(id, no);
    const stageTitle = id === 'earth1' ? (EARTH1_STAGE_TITLES[no] || `STAGE ${no}`) : `STAGE ${no}`;
    html += `<button class="btn" ${unlocked ? `onclick="openStoryStage('${id}', ${no})"` : 'disabled'} style="text-align:left;padding:13px 14px;margin:6px 0;${done ? 'border:1px solid #75ffad;' : ''}">
      <div style="font-weight:900;">${done ? '✅' : (unlocked ? '▶️' : '🔒')} ${no}. ${stageTitle}</div>
      <div style="font-size:0.78rem;opacity:0.7;margin-top:4px;">${done ? '클리어 완료' : (unlocked ? '도전 가능' : '앞 스테이지 클리어 필요')}</div>
    </button>`;
  }
  el.innerHTML = html;
}

function openStoryStage(chapterId, stageNo) {
  if (!storyStageUnlocked(chapterId, stageNo)) {
    alert('앞 스테이지를 먼저 클리어하세요.');
    return;
  }
  const meta = STORY_CHAPTER_META[chapterId];
  const stageName = chapterId === 'earth1'
    ? (EARTH1_STAGE_TITLES[stageNo] || `STAGE ${stageNo}`)
    : `STAGE ${stageNo}`;
  alert(`${meta.name} ${stageNo} · ${stageName}\n\n메인 스토리 전체 틀은 준비되었습니다.\n현재는 스테이지 전투/대사를 연결하기 전 단계입니다.`);
}

function openBossMode() {'''
s, n = pat.subn(block, s, count=1)
if n != 1:
    raise SystemExit(f'openStory/renderStory replacement count={n}')

p.write_text(s, encoding='utf-8')

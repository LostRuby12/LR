/* Lost Ruby - canonical story metadata/runtime fixes */
(() => {
  const META = Object.freeze({
    earth1:   Object.freeze({ name:'지구 I',  stages:5 }),
    delta1:   Object.freeze({ name:'델타 I',  stages:5 }),
    ancient1: Object.freeze({ name:'고대 I',  stages:8 }),
    future1:  Object.freeze({ name:'미래 I',  stages:8 }),
    earth2:   Object.freeze({ name:'지구 II', stages:8 }),
    demon1:   Object.freeze({ name:'마계 I',  stages:8 }),
    heaven1:  Object.freeze({ name:'천계 I',  stages:9 }),
    space1:   Object.freeze({ name:'우주 I',  stages:10 }),
    void:     Object.freeze({ name:'공허',    stages:10 })
  });
  const ICONS = Object.freeze({
    earth1:'🌍', delta1:'🔺', ancient1:'🏛️', future1:'🌆', earth2:'🌎',
    demon1:'😈', heaven1:'☁️', space1:'🌌', void:'🕳️'
  });
  const ORDER = Array.isArray(window.STORY_CHAPTER_ORDER) ? window.STORY_CHAPTER_ORDER :
    ['earth1','delta1','ancient1','future1','earth2','demon1','heaven1','space1','void'];

  window.LR_STORY_META = META;
  window.LR_STORY_TOTAL = ORDER.reduce((sum,id)=>sum+(META[id]?.stages||0),0);

  window.ensureStoryProgress = function() {
    if (!window.saveData) return { stages:{}, clearedChapters:{} };
    if (!saveData.story || typeof saveData.story !== 'object') saveData.story = {};
    if (!saveData.story.stages || typeof saveData.story.stages !== 'object') saveData.story.stages = {};
    if (!saveData.story.clearedChapters || typeof saveData.story.clearedChapters !== 'object') saveData.story.clearedChapters = {};
    Object.keys(META).forEach(id => {
      const max = META[id].stages;
      const cleared = Math.max(0, Math.min(max, Math.floor(Number(saveData.story.stages[id]) || 0)));
      saveData.story.stages[id] = cleared;
      if (cleared >= max) saveData.story.clearedChapters[id] = true;
      else delete saveData.story.clearedChapters[id];
    });
    return saveData.story;
  };

  window.storyChapterCleared = function(id) {
    const meta = META[id];
    if (!meta) return false;
    const story = ensureStoryProgress();
    return Number(story.stages[id] || 0) >= meta.stages;
  };

  window.storyChapterUnlocked = function(id) {
    const idx = ORDER.indexOf(id);
    if (idx < 0) return false;
    if (idx === 0) return true;
    return storyChapterCleared(ORDER[idx - 1]);
  };

  window.storyStageUnlocked = function(chapterId, stageNo) {
    const meta = META[chapterId];
    if (!meta || !storyChapterUnlocked(chapterId)) return false;
    stageNo = Number(stageNo) || 0;
    if (stageNo < 1 || stageNo > meta.stages) return false;
    const story = ensureStoryProgress();
    const cleared = Number(story.stages[chapterId]) || 0;
    return stageNo <= Math.min(meta.stages, cleared + 1);
  };

  window.renderStory = function() {
    const el = document.getElementById('story-list');
    const title = document.getElementById('story-title');
    const subtitle = document.getElementById('story-subtitle');
    const back = document.getElementById('story-back-btn');
    if (!el) return;
    const story = ensureStoryProgress();
    if (title) title.textContent = '📜 메인 스토리';
    if (subtitle) subtitle.textContent = `총 ${ORDER.length}개 챕터 · ${window.LR_STORY_TOTAL}개 스테이지`;
    if (back) back.textContent = '← 돌아가기';

    el.innerHTML = ORDER.map((id, idx) => {
      const meta = META[id];
      const cleared = Math.max(0, Math.min(meta.stages, Number(story.stages[id]) || 0));
      const unlocked = storyChapterUnlocked(id);
      const complete = storyChapterCleared(id);
      const icon = ICONS[id] || '📖';
      return `<button class="btn" ${unlocked ? `onclick="openStoryChapter('${id}')"` : 'disabled'} style="text-align:left;padding:14px 15px;margin:7px 0;${complete?'border:1px solid #75ffad;':''}">
        <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;">
          <span style="font-weight:900;">${complete?'✅':(unlocked?icon:'🔒')} ${idx+1}. ${meta.name}</span>
          <span style="font-size:.76rem;opacity:.78;white-space:nowrap;">${cleared}/${meta.stages}</span>
        </div>
        <div style="font-size:.8rem;opacity:.72;margin-top:4px;">${meta.stages} STAGE${unlocked?'':' · 이전 챕터 클리어 필요'}</div>
      </button>`;
    }).join('');
  };

  const prevRenderChapter = window.renderStoryChapter;
  if (typeof prevRenderChapter === 'function') {
    window.renderStoryChapter = function(id) {
      const result = prevRenderChapter.apply(this, arguments);
      const meta = META[id];
      if (meta) {
        const title = document.getElementById('story-title');
        const subtitle = document.getElementById('story-subtitle');
        if (title) title.textContent = `${ICONS[id] || '📖'} ${meta.name}`;
        if (subtitle && !/보물/.test(subtitle.textContent || '')) subtitle.textContent = `${meta.stages}개 스테이지 · 순차 진행`;
      }
      return result;
    };
  }

  function fixBadgeTypo(root) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let n;
    while ((n = walker.nextNode())) if ((n.nodeValue || '').includes('벳지')) nodes.push(n);
    nodes.forEach(node => { node.nodeValue = node.nodeValue.replace(/벳지/g, '뱃지'); });
  }
  fixBadgeTypo(document.body);
  const mo = new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(node => {
    if (node.nodeType === 3 && (node.nodeValue || '').includes('벳지')) node.nodeValue = node.nodeValue.replace(/벳지/g,'뱃지');
    else if (node.nodeType === 1) fixBadgeTypo(node);
  })));
  if (document.body) mo.observe(document.body,{childList:true,subtree:true});
})();

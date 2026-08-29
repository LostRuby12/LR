/* Lost Ruby - canonical story metadata/runtime fixes */
(() => {
  const META = Object.freeze({
    earth1:Object.freeze({name:'지구 I',stages:5}), delta1:Object.freeze({name:'델타 I',stages:5}),
    ancient1:Object.freeze({name:'고대 I',stages:8}), future1:Object.freeze({name:'미래 I',stages:8}),
    earth2:Object.freeze({name:'지구 II',stages:8}), demon1:Object.freeze({name:'마계 I',stages:8}),
    heaven1:Object.freeze({name:'천계 I',stages:9}), space1:Object.freeze({name:'우주 I',stages:10}),
    void:Object.freeze({name:'공허',stages:10})
  });
  const ICONS=Object.freeze({earth1:'🌍',delta1:'🔺',ancient1:'🏛️',future1:'🌆',earth2:'🌎',demon1:'😈',heaven1:'☁️',space1:'🌌',void:'🕳️'});
  const ORDER=['earth1','delta1','ancient1','future1','earth2','demon1','heaven1','space1','void'];
  window.LR_STORY_META=META;
  window.LR_STORY_TOTAL=ORDER.reduce((sum,id)=>sum+META[id].stages,0);

  window.ensureStoryProgress=function(){
    if(typeof saveData==='undefined'||!saveData)return{stages:{},clearedChapters:{}};
    if(!saveData.story||typeof saveData.story!=='object')saveData.story={};
    if(!saveData.story.stages||typeof saveData.story.stages!=='object')saveData.story.stages={};
    if(!saveData.story.clearedChapters||typeof saveData.story.clearedChapters!=='object')saveData.story.clearedChapters={};
    Object.keys(META).forEach(id=>{
      const max=META[id].stages;
      const cleared=Math.max(0,Math.min(max,Math.floor(Number(saveData.story.stages[id])||0)));
      saveData.story.stages[id]=cleared;
      if(cleared>=max)saveData.story.clearedChapters[id]=true;else delete saveData.story.clearedChapters[id];
    });
    return saveData.story;
  };
  window.storyChapterCleared=function(id){const m=META[id];if(!m)return false;const s=ensureStoryProgress();return Number(s.stages[id]||0)>=m.stages};
  window.storyChapterUnlocked=function(id){const i=ORDER.indexOf(id);if(i<0)return false;if(i===0)return true;return storyChapterCleared(ORDER[i-1])};
  window.storyStageUnlocked=function(id,no){const m=META[id];if(!m||!storyChapterUnlocked(id))return false;no=Number(no)||0;if(no<1||no>m.stages)return false;const s=ensureStoryProgress();return no<=Math.min(m.stages,(Number(s.stages[id])||0)+1)};

  window.renderStory=function(){
    const el=document.getElementById('story-list'),title=document.getElementById('story-title'),sub=document.getElementById('story-subtitle'),back=document.getElementById('story-back-btn');if(!el)return;
    const s=ensureStoryProgress();if(title)title.textContent='📜 메인 스토리';if(sub)sub.textContent=`총 ${ORDER.length}개 챕터 · ${window.LR_STORY_TOTAL}개 스테이지`;if(back)back.textContent='← 돌아가기';
    el.innerHTML=ORDER.map((id,i)=>{const m=META[id],c=Math.max(0,Math.min(m.stages,Number(s.stages[id])||0)),u=storyChapterUnlocked(id),done=storyChapterCleared(id),ic=ICONS[id];return`<button class="btn" ${u?`onclick="openStoryChapter('${id}')"`:'disabled'} style="text-align:left;padding:14px 15px;margin:7px 0;${done?'border:1px solid #75ffad;':''}"><div style="display:flex;justify-content:space-between;gap:10px"><b>${done?'✅':u?ic:'🔒'} ${i+1}. ${m.name}</b><span style="font-size:.76rem;opacity:.78">${c}/${m.stages}</span></div><div style="font-size:.8rem;opacity:.72;margin-top:4px">${m.stages} STAGE${u?'':' · 이전 챕터 클리어 필요'}</div></button>`}).join('');
  };

  const prev=window.renderStoryChapter;
  if(typeof prev==='function')window.renderStoryChapter=function(id){const r=prev.apply(this,arguments),m=META[id];if(m){const t=document.getElementById('story-title'),s=document.getElementById('story-subtitle');if(t)t.textContent=`${ICONS[id]} ${m.name}`;if(s&&!/보물/.test(s.textContent||''))s.textContent=`${m.stages}개 스테이지 · 순차 진행`}return r};

  function fix(root){if(!root)return;const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),a=[];let n;while((n=w.nextNode()))if((n.nodeValue||'').includes('벳지'))a.push(n);a.forEach(x=>x.nodeValue=x.nodeValue.replace(/벳지/g,'뱃지'))}
  fix(document.body);const mo=new MutationObserver(ms=>ms.forEach(m=>m.addedNodes.forEach(n=>{if(n.nodeType===3&&(n.nodeValue||'').includes('벳지'))n.nodeValue=n.nodeValue.replace(/벳지/g,'뱃지');else if(n.nodeType===1)fix(n)})));if(document.body)mo.observe(document.body,{childList:true,subtree:true});
})();

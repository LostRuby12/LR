/* Lost Ruby - Delta I production story module */
(() => {
  const TITLES = Object.freeze({
    1: '질서 정립',
    2: '감마 기지',
    3: '이상 징후',
    4: '무기고',
    5: '제3사령관'
  });

  const STAGE_DATA = Object.freeze({
    2: {
      player: { name:'주인공', maxHp:320, atk:35, weapon:'고스트', double:0.20, armorPct:0.30, desc:'암살용 권총 · 이중 공격 20%' },
      enemies: [
        { name:'델타 경비병 1', maxHp:120, atk:18, weapon:'제압봉' },
        { name:'델타 경비병 2', maxHp:120, atk:18, weapon:'제압봉' },
        { name:'델타 경계병', maxHp:140, atk:45, weapon:'권총', firearm:true }
      ]
    },
    3: {
      player: { name:'주인공', maxHp:500, atk:35, weapon:'백사의 침 +5', extra:20, extraRate:0.10, paralyze:0.35, armorPct:0.30, desc:'추가 20 피해 10% · 마비 35%' },
      enemies: [
        { name:'델타 전투원', maxHp:260, atk:70, weapon:'AK-47', firearm:true },
        { name:'델타 돌격병', maxHp:300, atk:80, weapon:'돌격소총', firearm:true }
      ]
    },
    5: {
      player: { name:'주인공', maxHp:500, atk:35, weapon:'백사의 침 +5', extra:20, extraRate:0.10, paralyze:0.35, armorPct:0.30, desc:'추가 20 피해 10% · 마비 35%' },
      enemies: [
        { name:'델타 제3사령관', maxHp:420, atk:80, weapon:'지휘관용 돌격소총', firearm:true, double:0.10 }
      ]
    }
  });

  let currentStage = 0;
  let battle = null;

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
  }

  function ensureUi() {
    if (!document.getElementById('delta1-style')) {
      const style = document.createElement('style');
      style.id = 'delta1-style';
      style.textContent = `
        #delta1-stage-screen{padding:18px;}
        .d1-card{background:rgba(0,0,0,.32);border:1px solid rgba(255,255,255,.10);border-radius:15px;padding:15px;margin:10px 0;line-height:1.7;}
        .d1-dialog{font-size:.95rem;white-space:pre-line;}
        .d1-speaker{font-weight:900;color:#ffd700;}
        .d1-secret{font-weight:900;letter-spacing:.12em;text-align:center;font-size:1.15rem;color:#f4e6b1;padding:10px 0;}
        .d1-battle-head{display:flex;gap:9px;align-items:stretch;margin-top:10px;}
        .d1-fighter{flex:1;background:rgba(0,0,0,.36);border-radius:12px;padding:11px;text-align:center;border:1px solid rgba(255,255,255,.10);min-width:0;}
        .d1-fighter.enemy{border-color:rgba(255,90,90,.42);}
        .d1-name{font-weight:900;font-size:.92rem;}
        .d1-weapon{font-size:.73rem;color:#ffd700;margin:3px 0 8px;min-height:2.3em;}
        .d1-hpbar{height:14px;background:#333;border-radius:8px;overflow:hidden;margin-top:5px;}
        .d1-hpfill{height:100%;background:linear-gradient(90deg,#00b09b,#96c93d);transition:width .25s;}
        .d1-hpfill.enemy{background:linear-gradient(90deg,#c31432,#ff4b2b);}
        .d1-hptext{font-size:.72rem;opacity:.85;margin-top:4px;}
        .d1-status{font-size:.7rem;color:#d8c7ff;min-height:1.2em;margin-top:4px;}
        .d1-log{background:rgba(0,0,0,.48);border-radius:12px;padding:11px;min-height:145px;max-height:245px;overflow-y:auto;margin:12px 0;font-size:.83rem;line-height:1.55;}
        .d1-log div{padding:3px 0;border-bottom:1px solid rgba(255,255,255,.04);}
        .d1-clear{color:#75ffad;font-weight:900;text-align:center;font-size:1.25rem;margin:12px 0;}
        .d1-fail{color:#ff8f8f;font-weight:900;text-align:center;font-size:1.2rem;margin:12px 0;}
      `;
      document.head.appendChild(style);
    }
    let screen = document.getElementById('delta1-stage-screen');
    if (!screen) {
      screen = document.createElement('div');
      screen.id = 'delta1-stage-screen';
      screen.className = 'screen';
      const app = document.getElementById('app');
      if (app) app.appendChild(screen);
    }
    return screen;
  }

  function showStageScreen(html) {
    const el = ensureUi();
    el.innerHTML = html;
    if (typeof showScreen === 'function') showScreen('delta1-stage-screen');
  }

  function top(stageNo, subtitle='') {
    return `<h2 style="text-align:center;margin-bottom:4px;">🔺 2-${stageNo} · ${esc(TITLES[stageNo])}</h2>
      <p style="text-align:center;opacity:.7;font-size:.8rem;margin-bottom:10px;">${esc(subtitle)}</p>`;
  }

  function storyButton(label, fn, cls='btn btn-gold') {
    const id = 'd1btn_' + Math.random().toString(36).slice(2);
    setTimeout(() => { const b=document.getElementById(id); if (b) b.onclick=fn; }, 0);
    return `<button id="${id}" class="${cls}">${esc(label)}</button>`;
  }

  function backButton() {
    return storyButton('← 스테이지 목록', () => {
      currentStage = 0; battle = null;
      if (typeof openStoryChapter === 'function') openStoryChapter('delta1');
    }, 'btn');
  }

  function getBSHChoice() {
    try { return saveData && saveData.story && saveData.story.earth1BSHChoice === 'release' ? 'release' : 'handover'; }
    catch (e) { return 'handover'; }
  }

  function completeStage(stageNo) {
    try {
      if (!saveData.story || typeof saveData.story !== 'object') saveData.story = {};
      if (!saveData.story.stages || typeof saveData.story.stages !== 'object') saveData.story.stages = {};
      if (!saveData.story.clearedChapters || typeof saveData.story.clearedChapters !== 'object') saveData.story.clearedChapters = {};
      saveData.story.stages.delta1 = Math.max(Number(saveData.story.stages.delta1) || 0, stageNo);
      if (stageNo >= 5) saveData.story.clearedChapters.delta1 = true;
      if (typeof persistSave === 'function') persistSave();
    } catch (e) { console.warn('delta1 progress save failed', e); }
  }

  function clearScene(stageNo, extraHtml='') {
    completeStage(stageNo);
    const next = stageNo < 5
      ? storyButton(`다음 · 2-${stageNo+1} ${TITLES[stageNo+1]}`, () => openStoryStage('delta1', stageNo+1), 'btn btn-success')
      : '';
    showStageScreen(`${top(stageNo)}<div class="d1-card">${extraHtml}<div class="d1-clear">STAGE CLEAR</div></div>${next}${backButton()}`);
  }

  function startStage1() {
    const release = getBSHChoice() === 'release';
    const briefing = release
      ? `<span class="d1-speaker">상관</span> : “임무에 실패하다니.”\n\n상관은 잠시 주인공을 바라본다.\n\n<span class="d1-speaker">상관</span> : “그래도 재능을 봐서 마지막 기회를 주지.”\n<span class="d1-speaker">상관</span> : “새 명령을 하달하지.”`
      : `<span class="d1-speaker">상관</span> : “B.S.H 건은 잘 처리했다.”\n<span class="d1-speaker">상관</span> : “새 명령을 하달하지.”`;
    showStageScreen(`${top(1,'킬 오브 킹 작전실')}
      <div class="d1-card d1-dialog">${briefing}

        <div class="d1-secret">작전명 : 질서 정립</div>
        감마 기지에 주둔 중인 <b>델타 제3사령부</b>를 기습한다.

        목표 1 — 중요 무기 탈취.
        목표 2 — 1급기밀 관련 정보 확보.

        자료의 일부에 적힌 단어가 화면에 나타난다.
        <div class="d1-secret">고대 동굴</div>
      </div>
      ${storyButton('감마 기지로 이동한다', () => clearScene(1, '<div class="d1-dialog">작전명 「질서 정립」. 주인공은 감마 기지로 향한다.</div>'))}
      ${backButton()}`);
  }

  function startStage2() {
    showStageScreen(`${top(2,'감마 기지 외곽')}
      <div class="d1-card d1-dialog">감마 기지 외곽.

        주인공은 소음성이 높은 암살용 권총 <b>「고스트」</b>를 꺼낸다.
        아직 기습이 들키지 않은 상태. 외곽 경비를 조용히 정리하고 제3사령부 내부 진입로를 확보해야 한다.

        경비병들은 상부의 목적을 알지 못한다. 다만 최근 기지 안에서 평소와 다른 물자 이동과 명령이 이어지고 있다.
      </div>
      ${storyButton('외곽 경비를 제압한다', () => beginBattleStage(2), 'btn btn-danger')}
      ${backButton()}`);
  }

  function stage2AfterBattle() {
    clearScene(2, `<div class="d1-dialog">외곽 경비를 모두 제압한다.

      쓰러진 경계병의 무전기에서 짧은 교신이 흘러나온다.

      “……제3사령부 내부 물자 이동 계속한다.”
      “목적은 묻지 마. 상부 명령이다.”

      주인공은 무전을 끄고 기지 안쪽으로 이동한다.</div>`);
  }

  function startStage3() {
    showStageScreen(`${top(3,'제3사령부 내부')}
      <div class="d1-card d1-dialog">제3사령부 내부로 들어서자 분위기가 달라진다.

        주인공은 고스트를 집어넣고 <b>「백사의 침」</b>을 꺼낸다.

        통신망에서는 제1사령부와 제2사령부, 그리고 델타기지라는 이름이 반복해서 들려온다. 그러나 현장 병사들조차 정확히 무슨 작전인지 모르는 듯하다.

        “명령이 또 바뀌었다고?”
        “알 필요 없어. 델타기지에서 내려온 지시다.”
      </div>
      ${storyButton('전투원들을 제압한다', () => beginBattleStage(3), 'btn btn-danger')}
      ${backButton()}`);
  }

  function stage3AfterBattle() {
    clearScene(3, `<div class="d1-dialog">전투원들을 제압한 뒤 통신 기록 일부를 확인한다.

      제1사령부 — 대기.
      제2사령부 — 대기.
      제3사령부 — 물자 이송 완료.
      최종 지시 — 델타기지.

      여러 사령부가 동시에 움직이고 있다. 하지만 목적은 기록되어 있지 않다.</div>`);
  }

  function startStage4() {
    showStageScreen(`${top(4,'제3사령부 무기고')}
      <div class="d1-card d1-dialog">주인공이 제3사령부 무기고 최심부에 도착한다.

        킬 오브 킹이 지정한 특수 무기를 보관했다는 격납고.
        하지만 봉인 컨테이너는 이미 비어 있다.

        보안 단말에 마지막 이송 기록이 남아 있다.
        <div class="d1-secret">특수 회수물 — 이송 완료\n목적지 — 델타기지</div>
        목표 무기는 이미 혼돈의 반란 본부로 옮겨졌다.
      </div>
      ${storyButton('이송 기록을 확인한다', () => clearScene(4, `<div class="d1-dialog">무기 탈취는 실패.

        하지만 이송 승인자가 <b>「델타 제3사령관」</b>이라는 사실을 확인한다.

        주인공은 두 번째 목표인 1급기밀의 실마리를 얻기 위해 곧바로 제3사령관실로 향한다.</div>`))}
      ${backButton()}`);
  }

  function startStage5() {
    showStageScreen(`${top(5,'제3사령관실')}
      <div class="d1-card d1-dialog">제3사령관실.

        주인공이 백사의 침을 들고 사령관 앞에 선다.

        <span class="d1-speaker">주인공</span> : “고대 동굴.”

        제3사령관의 표정이 처음으로 굳는다.

        <span class="d1-speaker">제3사령관</span> : “……그걸 어떻게 알고 있지?”

        말단 병사들이 알 수 없는 극비 정보라는 것이 확실해졌다.
        델타기지 지원 병력이 도착하기 전에 사령관을 제압하고 자료를 확보해야 한다.
      </div>
      ${storyButton('제3사령관을 제압한다', () => beginBattleStage(5), 'btn btn-danger')}
      ${backButton()}`);
  }

  function stage5AfterBattle() {
    completeStage(5);
    showStageScreen(`${top(5)}
      <div class="d1-card d1-dialog">제3사령관을 제압한다.

        델타기지 지원 병력이 오기 전, 주인공은 사령관의 보안 단말을 빠르게 뒤진다.

        <div class="d1-secret">1급기밀\n고대 동굴 — 좌표 확보</div>
        1차 탐사 — 실패
        2차 탐사 — 중단
        추가 탐사 — 금지

        그리고 특수 회수물의 출처 역시 같은 장소로 기록되어 있다.
        <div class="d1-secret">회수 장소 — 고대 동굴</div>
        멀리서 지원 병력의 접근 신호가 울린다.
        주인공은 무기 탈취를 포기하고 좌표만 확보해 감마 기지를 빠져나간다.

        얼마 뒤, 좌표가 가리키는 동굴 앞.
        주인공이 내부로 들어서자 현대의 흔적이 사라지고 오래된 구조물이 모습을 드러낸다.

        깊은 곳에서 정체불명의 빛이 번쩍인다.

        <div class="d1-clear">DELTA I CLEAR</div>
        <div style="text-align:center;font-weight:900;color:#cbb8ff;">—— 고대 I로 이어진다.</div>
      </div>
      ${backButton()}`);
  }

  function beginBattleStage(stageNo) {
    const data = STAGE_DATA[stageNo];
    if (!data) return;
    battle = {
      stageNo,
      encounter:0,
      player:{...data.player, hp:data.player.maxHp},
      enemies:data.enemies.map(e => ({...e, hp:e.maxHp})),
      enemyParalyzed:false,
      over:false
    };
    beginEncounter(0);
  }

  function beginEncounter(index) {
    if (!battle) return;
    battle.encounter=index;
    battle.player.hp=battle.player.maxHp;
    battle.enemyParalyzed=false;
    battle.over=false;
    const e=battle.enemies[index];
    e.hp=e.maxHp;
    renderBattle();
    log(`전투 시작 · ${e.name}`);
  }

  function hpPct(hp,max){ return Math.max(0,Math.min(100,(hp/max)*100)); }

  function renderBattle() {
    if (!battle) return;
    const p=battle.player, e=battle.enemies[battle.encounter], total=battle.enemies.length;
    const armor = p.armorPct ? `🦺 방탄복 · 총기 피해 -${Math.round(p.armorPct*100)}%` : '';
    showStageScreen(`${top(battle.stageNo,total>1?`전투 ${battle.encounter+1} / ${total}`:'1 VS 1')}
      <div class="d1-battle-head">
        <div class="d1-fighter">
          <div class="d1-name">${esc(p.name)}</div>
          <div class="d1-weapon">${esc(p.weapon)} · ATK ${p.atk}</div>
          <div class="d1-hpbar"><div id="d1-pfill" class="d1-hpfill" style="width:${hpPct(p.hp,p.maxHp)}%"></div></div>
          <div id="d1-php" class="d1-hptext">HP ${p.hp} / ${p.maxHp}</div>
          <div class="d1-status">${armor}</div>
        </div>
        <div style="align-self:center;font-weight:900;color:#ffd700;">VS</div>
        <div class="d1-fighter enemy">
          <div class="d1-name">${esc(e.name)}</div>
          <div class="d1-weapon">${esc(e.weapon)} · ATK ${e.atk}</div>
          <div class="d1-hpbar"><div id="d1-efill" class="d1-hpfill enemy" style="width:${hpPct(e.hp,e.maxHp)}%"></div></div>
          <div id="d1-ehp" class="d1-hptext">HP ${e.hp} / ${e.maxHp}</div>
          <div id="d1-estatus" class="d1-status"></div>
        </div>
      </div>
      <div id="d1-log" class="d1-log"></div>
      <button id="d1-attack" class="btn btn-gold">공격</button>
      ${backButton()}`);
    const btn=document.getElementById('d1-attack'); if(btn) btn.onclick=playerTurn;
  }

  function updateBars() {
    if (!battle) return;
    const p=battle.player,e=battle.enemies[battle.encounter];
    const pf=document.getElementById('d1-pfill'),ef=document.getElementById('d1-efill');
    const pt=document.getElementById('d1-php'),et=document.getElementById('d1-ehp');
    const es=document.getElementById('d1-estatus');
    if(pf)pf.style.width=hpPct(p.hp,p.maxHp)+'%';
    if(ef)ef.style.width=hpPct(e.hp,e.maxHp)+'%';
    if(pt)pt.textContent=`HP ${Math.max(0,p.hp)} / ${p.maxHp}`;
    if(et)et.textContent=`HP ${Math.max(0,e.hp)} / ${e.maxHp}`;
    if(es)es.textContent=battle.enemyParalyzed?'⚡ 마비':'';
  }

  function log(msg) {
    const el=document.getElementById('d1-log'); if(!el)return;
    const row=document.createElement('div'); row.textContent=msg; el.appendChild(row); el.scrollTop=el.scrollHeight;
  }

  function playerTurn() {
    if(!battle||battle.over)return;
    const btn=document.getElementById('d1-attack'); if(btn)btn.disabled=true;
    const p=battle.player,e=battle.enemies[battle.encounter];
    let hits=(p.double&&Math.random()<p.double)?2:1;
    let dmg=p.atk*hits;
    if(p.extraRate&&Math.random()<p.extraRate){ dmg+=p.extra||0; log(`백사의 침 추가 피해 +${p.extra||0}`); }
    e.hp=Math.max(0,e.hp-dmg);
    log(hits===2?`주인공의 이중 공격! ${dmg} 피해`:`주인공의 공격 · ${dmg} 피해`);
    if(p.paralyze&&e.hp>0&&Math.random()<p.paralyze){battle.enemyParalyzed=true;log(`⚡ ${e.name} 마비!`);}
    updateBars();
    if(e.hp<=0){battle.over=true;onEnemyDown();return;}
    enemyTurn();
    if(btn&&!battle.over)btn.disabled=false;
  }

  function enemyTurn() {
    if(!battle||battle.over)return;
    const p=battle.player,e=battle.enemies[battle.encounter];
    if(battle.enemyParalyzed){ battle.enemyParalyzed=false; log(`⚡ ${e.name}이 마비되어 공격하지 못했다.`); updateBars(); return; }
    let hits=(e.double&&Math.random()<e.double)?2:1;
    let raw=e.atk*hits;
    let dmg=raw;
    if(e.firearm&&p.armorPct){ dmg=Math.max(1,Math.round(raw*(1-p.armorPct))); log(`🦺 방탄복이 총기 피해를 ${raw-dmg} 감소시켰다.`); }
    p.hp=Math.max(0,p.hp-dmg);
    log(hits===2?`${e.name}의 연속 사격! ${dmg} 피해`:`${e.name}의 공격 · ${dmg} 피해`);
    updateBars();
    if(p.hp<=0){
      battle.over=true;
      const st=battle.stageNo;
      setTimeout(()=>showStageScreen(`${top(st)}<div class="d1-card"><div class="d1-fail">전투 패배</div><p style="text-align:center;opacity:.8;">스테이지 진행도는 유지되지 않습니다.</p></div>${storyButton('다시 도전',()=>beginBattleStage(st),'btn btn-danger')}${backButton()}`),250);
    }
  }

  function onEnemyDown() {
    if(!battle)return;
    const st=battle.stageNo,idx=battle.encounter,total=battle.enemies.length,e=battle.enemies[idx];
    log(`${e.name} 제압.`);
    if(idx+1<total){setTimeout(()=>beginEncounter(idx+1),550);return;}
    setTimeout(()=>{
      battle=null;
      if(st===2)stage2AfterBattle();
      else if(st===3)stage3AfterBattle();
      else if(st===5)stage5AfterBattle();
    },450);
  }

  // 델타 I은 본편 메타의 기존 7스테이지 대신 5스테이지로 판정한다.
  const originalStoryChapterCleared = typeof storyChapterCleared === 'function' ? storyChapterCleared : null;
  if (originalStoryChapterCleared) {
    storyChapterCleared = function(id) {
      if (id === 'delta1') {
        try {
          const s = saveData && saveData.story;
          return !!(s && s.clearedChapters && s.clearedChapters.delta1) || Number(s && s.stages && s.stages.delta1 || 0) >= 5;
        } catch(e) { return false; }
      }
      return originalStoryChapterCleared(id);
    };
  }

  // 메인 스토리 목록의 로마자 표기와 델타 I 5스테이지 표시를 보정한다.
  const originalRenderStory = typeof renderStory === 'function' ? renderStory : null;
  if (originalRenderStory) {
    renderStory = function() {
      const result = originalRenderStory();
      try {
        const subtitle=$('story-subtitle');
        if(subtitle && /73개 스테이지/.test(subtitle.textContent)) subtitle.textContent=subtitle.textContent.replace('73개 스테이지','71개 스테이지');
        const list=$('story-list');
        if(list){
          const replacements=[['지구 1','지구 I'],['델타 1','델타 I'],['고대 1','고대 I'],['미래 1','미래 I'],['지구 2','지구 II'],['마계 1','마계 I'],['천계 1','천계 I'],['우주 1','우주 I']];
          [...list.querySelectorAll('button')].forEach(btn=>{
            const click=btn.getAttribute('onclick')||'';
            replacements.forEach(([a,b])=>{ if(btn.innerHTML.includes(a)) btn.innerHTML=btn.innerHTML.split(a).join(b); });
            if(click.includes("openStoryChapter('delta1')")) btn.innerHTML=btn.innerHTML.replace(/(\d+)\s*\/\s*7/g,'$1 / 5');
          });
        }
      } catch(e) { console.warn('delta1 story list patch failed',e); }
      return result;
    };
  }

  const originalRenderStoryChapter = typeof renderStoryChapter === 'function' ? renderStoryChapter : null;
  if (originalRenderStoryChapter) {
    renderStoryChapter = function(id) {
      if(id!=='delta1') return originalRenderStoryChapter(id);
      const el=$('story-list'),title=$('story-title'),subtitle=$('story-subtitle'),back=$('story-back-btn');
      if(!el)return;
      if(title)title.textContent='🔺 델타 I';
      if(subtitle)subtitle.textContent='5개 스테이지 · 순차 진행';
      if(back)back.textContent='← 챕터 목록';
      let cleared=0;
      try{cleared=Math.max(0,Math.min(5,Number(saveData.story.stages.delta1)||0));}catch(e){}
      let html='';
      for(let no=1;no<=5;no++){
        const done=no<=cleared;
        const unlocked=storyChapterUnlocked('delta1') && no<=Math.min(5,cleared+1);
        html+=`<button class="btn" ${unlocked?`onclick="openStoryStage('delta1', ${no})"`:'disabled'} style="text-align:left;padding:13px 14px;margin:6px 0;${done?'border:1px solid #75ffad;':''}">
          <div style="font-weight:900;">${done?'✅':(unlocked?'▶️':'🔒')} 2-${no} ${esc(TITLES[no])}</div>
          <div style="font-size:.78rem;opacity:.7;margin-top:4px;">${done?'클리어 완료':(unlocked?'도전 가능':'앞 스테이지 클리어 필요')}</div>
        </button>`;
      }
      el.innerHTML=html;
    };
  }

  const originalOpenStoryStage = typeof openStoryStage === 'function' ? openStoryStage : null;
  openStoryStage = function(chapterId,stageNo) {
    if(chapterId!=='delta1'){
      if(originalOpenStoryStage)return originalOpenStoryStage(chapterId,stageNo);
      return;
    }
    let cleared=0;
    try{cleared=Math.max(0,Math.min(5,Number(saveData.story.stages.delta1)||0));}catch(e){}
    if(!storyChapterUnlocked('delta1') || stageNo<1 || stageNo>5 || stageNo>cleared+1){alert('앞 스테이지를 먼저 클리어하세요.');return;}
    currentStage=stageNo;
    if(stageNo===1)startStage1();
    else if(stageNo===2)startStage2();
    else if(stageNo===3)startStage3();
    else if(stageNo===4)startStage4();
    else if(stageNo===5)startStage5();
  };

  console.info('[Lost Ruby] Delta I story module loaded');
})();

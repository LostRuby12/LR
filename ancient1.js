/* Lost Ruby - Ancient I production story module */
(() => {
  const TITLES = Object.freeze({
    1: '고대 동굴',
    2: '밀림',
    3: '낯선 시대',
    4: '고대 마법사',
    5: '검의 군단',
    6: '봉인의식',
    7: '신의 저주',
    8: '고대의 가면'
  });

  const PLAYER = Object.freeze({
    name: '주인공', maxHp: 500, atk: 35, weapon: '백사의 침 +5',
    paralyze: 0.35, extra: 20, extraRate: 0.10
  });

  const STAGE_DATA = Object.freeze({
    2: Object.freeze({
      enemies: Object.freeze([
        Object.freeze({ name:'원숭이', maxHp:80, atk:5, weapon:'바나나' }),
        Object.freeze({ name:'원숭이', maxHp:120, atk:30, weapon:'돌' })
      ])
    }),
    7: Object.freeze({
      enemies: Object.freeze([
        Object.freeze({ name:'타락한 마법사', maxHp:230, atk:38, weapon:'마력탄', curse:0.12 }),
        Object.freeze({ name:'타락한 검사', maxHp:300, atk:45, weapon:'고대검', double:0.15 }),
        Object.freeze({ name:'타락한 상급 마법사', maxHp:350, atk:52, weapon:'저주 마법', curse:0.15, corrupt:0.15 })
      ])
    })
  });

  let battle = null;

  function esc(s) {
    return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/\"/g,'&quot;').replace(/'/g,'&#039;');
  }

  function ensureUi() {
    if (!document.getElementById('ancient1-style')) {
      const style = document.createElement('style');
      style.id = 'ancient1-style';
      style.textContent = `
        #ancient1-stage-screen{padding:18px;}
        .a1-story{position:relative;background:linear-gradient(180deg,rgba(35,31,67,.96),rgba(20,19,42,.97));border:1px solid rgba(255,215,0,.19);border-radius:18px;padding:18px 17px;margin:11px 0;line-height:1.82;white-space:pre-line;box-shadow:0 10px 26px rgba(0,0,0,.28);overflow:hidden;}
        .a1-story:before{content:'STORY';position:absolute;right:14px;top:0;padding:4px 9px 5px;border-radius:0 0 8px 8px;background:rgba(255,215,0,.12);color:#d9c675;font-size:.62rem;font-weight:900;letter-spacing:.14em;}
        .a1-story:after{content:'';position:absolute;left:0;top:16px;bottom:16px;width:3px;background:linear-gradient(180deg,#ffd700,rgba(142,45,226,.35));border-radius:0 5px 5px 0;}
        .a1-speaker{display:inline-block;color:#ffd700;font-weight:900;margin:5px 0 2px;padding:2px 7px;border:1px solid rgba(255,215,0,.24);border-radius:7px;background:rgba(255,215,0,.07);}
        .a1-ai{position:relative;color:#d9e7ff;font-weight:800;line-height:1.62;padding:12px 13px 12px 38px;margin:10px 0;border-radius:12px;border:1px solid rgba(120,176,255,.22);background:linear-gradient(145deg,rgba(37,70,114,.28),rgba(30,39,75,.35));white-space:pre-line;}
        .a1-ai:before{content:'AI';position:absolute;left:10px;top:10px;width:20px;height:20px;display:flex;align-items:center;justify-content:center;border-radius:6px;background:#4d6ca8;color:#fff;font-size:.56rem;font-weight:900;}
        .a1-relic{text-align:center;padding:15px 12px;margin:12px 0;border-radius:14px;background:radial-gradient(circle,rgba(255,215,0,.10),rgba(255,215,0,.02) 65%);border:1px solid rgba(255,215,0,.22);color:#ffe788;font-weight:900;font-size:1.08rem;letter-spacing:.06em;}
        .a1-system{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;margin:11px 0;padding:12px 13px;border-radius:10px;color:#a9d7ff;background:#111527;border:1px solid rgba(102,164,255,.18);font-size:.78rem;line-height:1.6;white-space:pre-line;}
        .a1-clear{color:#75ffad;font-weight:900;text-align:center;font-size:1.25rem;margin:12px 0;}
        .a1-battle-head{display:flex;gap:9px;align-items:stretch;margin-top:10px;}
        .a1-fighter{flex:1;min-width:0;background:rgba(0,0,0,.36);border-radius:12px;padding:11px;text-align:center;border:1px solid rgba(255,255,255,.10);}
        .a1-fighter.enemy{border-color:rgba(255,90,90,.42);}
        .a1-name{font-weight:900;font-size:.92rem;}.a1-weapon{font-size:.73rem;color:#ffd700;margin:3px 0 8px;min-height:2.3em;}
        .a1-hpbar{height:14px;background:#333;border-radius:8px;overflow:hidden;margin-top:5px;}.a1-hpfill{height:100%;background:linear-gradient(90deg,#00b09b,#96c93d);transition:width .25s;}.a1-hpfill.enemy{background:linear-gradient(90deg,#c31432,#ff4b2b);}
        .a1-hptext{font-size:.72rem;opacity:.85;margin-top:4px;}.a1-status{font-size:.7rem;color:#d8c7ff;min-height:1.2em;margin-top:4px;}
        .a1-log{background:rgba(0,0,0,.48);border-radius:12px;padding:11px;min-height:145px;max-height:245px;overflow-y:auto;margin:12px 0;font-size:.83rem;line-height:1.55;}.a1-log div{padding:3px 0;border-bottom:1px solid rgba(255,255,255,.04);}
      `;
      document.head.appendChild(style);
    }
    let screen = document.getElementById('ancient1-stage-screen');
    if (!screen) {
      screen = document.createElement('div');
      screen.id = 'ancient1-stage-screen';
      screen.className = 'screen';
      const app = document.getElementById('app');
      if (app) app.appendChild(screen);
    }
    return screen;
  }

  function showStageScreen(html) {
    const el = ensureUi();
    el.innerHTML = html;
    if (typeof showScreen === 'function') showScreen('ancient1-stage-screen');
  }

  function top(no, sub='') {
    return `<h2 style="text-align:center;margin-bottom:4px;">🏛️ 3-${no} · ${esc(TITLES[no])}</h2><p style="text-align:center;opacity:.7;font-size:.8rem;margin-bottom:10px;">${esc(sub)}</p>`;
  }

  function storyButton(label, fn, cls='btn btn-gold') {
    const id = 'a1btn_' + Math.random().toString(36).slice(2);
    setTimeout(() => { const b=document.getElementById(id); if (b) b.onclick=fn; }, 0);
    return `<button id="${id}" class="${cls}">${esc(label)}</button>`;
  }

  function backButton() {
    return storyButton('← 스테이지 목록', () => { battle=null; if (typeof openStoryChapter === 'function') openStoryChapter('ancient1'); }, 'btn');
  }

  function completeStage(no) {
    try {
      if (!saveData.story) saveData.story = {};
      if (!saveData.story.stages) saveData.story.stages = {};
      if (!saveData.story.clearedChapters) saveData.story.clearedChapters = {};
      saveData.story.stages.ancient1 = Math.max(Number(saveData.story.stages.ancient1)||0, no);
      if (no >= 8) saveData.story.clearedChapters.ancient1 = true;
      if (typeof persistSave === 'function') persistSave();
    } catch(e) { console.warn('ancient1 progress save failed', e); }
  }

  function clearScene(no, body='') {
    completeStage(no);
    const next = no < 8 ? storyButton(`다음 · 3-${no+1} ${TITLES[no+1]}`, () => openStoryStage('ancient1', no+1), 'btn btn-success') : '';
    showStageScreen(`${top(no)}<div class="a1-story">${body}<div class="a1-clear">STAGE CLEAR</div></div>${next}${backButton()}`);
  }

  function stage1() {
    showStageScreen(`${top(1,'델타에서 확보한 좌표')}<div class="a1-story">주인공은 델타 제3사령관실에서 확보한 좌표를 따라 외딴 동굴에 도착한다.

동굴 안쪽으로 들어갈수록 현대의 흔적은 사라지고 처음 보는 문양과 석조 구조물이 나타난다.

깊은 곳에서 공간이 뒤틀리기 시작한다.

<span class="a1-speaker">주인공</span>
“……뭐지?”

순간 강한 빛이 터진다.</div>${storyButton('빛 속으로 들어간다',()=>clearScene(1,'시야가 돌아왔을 때, 주인공 앞에는 처음 보는 숲과 거대한 나무들이 펼쳐져 있다.'))}${backButton()}`);
  }

  function stage2() {
    showStageScreen(`${top(2,'동굴 밖의 정글')}<div class="a1-story">동굴 밖으로 나오자 사방이 울창한 정글이다.

현대의 건물도, 도로도 보이지 않는다.

그때 나무 위에서 원숭이 두 마리가 내려온다.
첫 번째 원숭이는 바나나를 들고 있고, 두 번째 원숭이는 묵직한 돌을 집어 든다.</div>${storyButton('원숭이들을 상대한다',()=>beginBattle(2),'btn btn-danger')}${backButton()}`);
  }

  function stage2After() {
    clearScene(2, `원숭이 두 마리를 쫓아낸다.

멀리서 가느다란 연기가 올라오고 있다.

<span class="a1-speaker">주인공</span>
“사람이 있는 건가.”

주인공은 연기가 보이는 방향으로 이동한다.`);
  }

  function stage3() {
    showStageScreen(`${top(3,'처음 만난 고대인들')}<div class="a1-story">숲을 빠져나온 주인공은 낯선 복장을 한 사람들과 마주친다.

그들이 빠르게 무언가를 외치지만 전혀 알아들을 수 없다.
주인공은 킬 오브 킹 본부에서 지급받은 임무용 AI 통역기를 켠다.

<div class="a1-ai">[언어 데이터 부족]
[완전 번역 불가]
[문맥 추정 모드]</div>
고대인이 길게 말을 쏟아낸다.

<div class="a1-ai">“침입자… 어디에서 왔는지 묻는 것으로 추정.”</div>
주인공은 손을 들어 적의가 없음을 보인다.
다른 고대인이 멀리 있는 건축물을 가리킨다.

<div class="a1-ai">“마법사… 데려가겠다… 정도의 의미.”</div></div>${storyButton('그들을 따라간다',()=>clearScene(3,'완벽한 대화는 불가능하지만, 주인공은 통역기가 전달하는 단어와 맥락을 따라 이동한다.'))}${backButton()}`);
  }

  function stage4() {
    showStageScreen(`${top(4,'의식을 준비하는 자들')}<div class="a1-story">주인공은 거대한 석조 건물에 도착한다.

안에서는 수많은 마법사들이 바닥에 거대한 마법진을 그리고 있다.
고대 마법사 한 명이 주인공을 경계하며 말을 건다.

<div class="a1-ai">“봉인… 준비… 시간이 부족하다.”</div>
<span class="a1-speaker">주인공</span>
“뭘 봉인한다는 거지?”

마법사가 다시 설명하지만 통역기는 일부 단어만 잡아낸다.

<div class="a1-ai">[번역 신뢰도 낮음]
“위험… 깨어남… 막아야 한다.”</div>
대상이 무엇인지는 알 수 없다.</div>${storyButton('의식 준비를 지켜본다',()=>clearScene(4,'주인공은 이들이 매우 위험한 무언가를 봉인하려 한다는 사실만 이해한다.'))}${backButton()}`);
  }

  function stage5() {
    showStageScreen(`${top(5,'마법사들을 지키는 검사들')}<div class="a1-story">마법진 외곽에는 수많은 검사들이 배치되어 있다.

마법사들이 의식을 준비하는 동안 검사들은 주변을 경계하고 있다.
한 검사가 주인공의 무기를 바라본다.

<div class="a1-ai">“우리… 시간을 번다.”</div>
주인공은 검사들이 단순한 경비가 아니라 무언가가 벌어졌을 때 앞에서 막아서는 역할임을 눈치챈다.

마법사와 검사들이 협력하고 있지만 분위기는 무겁다.</div>${storyButton('검사 진영을 지나간다',()=>clearScene(5,'누구도 무엇이 올 것인지 말해주지 않는다. 다만 모두가 시간이 부족하다는 것만 반복한다.'))}${backButton()}`);
  }

  function stage6() {
    showStageScreen(`${top(6,'거대한 봉인의식')}<div class="a1-story">의식 준비가 막바지에 이른다.

거대한 마법진에 빛이 들어오기 시작하고 검사들은 외곽 방어선에 자리 잡는다.

그러나 주변의 공기가 갑자기 무거워진다.
동물들이 숲 밖으로 도망치고 하늘이 서서히 어두워진다.

<div class="a1-ai">[알 수 없는 에너지 간섭]
[번역 정확도 저하]</div>
마법사들이 다급하게 외친다.

<div class="a1-ai">“시간… 없다.”</div>
무엇을 봉인하려는지는 끝내 알 수 없다.</div>${storyButton('계속 지켜본다',()=>clearScene(6,'마법진이 완성되기 직전, 멀리서 비명이 들려온다.'))}${backButton()}`);
  }

  function stage7() {
    showStageScreen(`${top(7,'의식 직전 발생한 재앙')}<div class="a1-story">마법사 한 명이 갑자기 가슴을 움켜쥐고 쓰러진다.
검은 문양이 피부 위로 퍼지기 시작한다.

주변의 마법사와 검사들이 혼란에 빠진다.

<span class="a1-speaker">마법사</span>
“도망쳐!”

<span class="a1-speaker">검사</span>
“저쪽도 변하고 있어!”

<div class="a1-ai">[문맥 분석]
“저주… 또는 타락으로 추정.”</div>
쓰러졌던 마법사가 갑자기 일어나 주변 사람들에게 마법을 날린다.</div>${storyButton('타락한 자들을 막는다',()=>beginBattle(7),'btn btn-danger')}${backButton()}`);
  }

  function stage7After() {
    showStageScreen(`${top(7)}<div class="a1-story">마지막 타락한 상급 마법사가 바닥에 쓰러진다.
검은 문양이 잠시 옅어지며 눈에 의식이 돌아온다.

<span class="a1-speaker">타락한 상급 마법사</span>
“……의식에… 가까이 가지 마……”

<div class="a1-ai">[번역 신뢰도 41%]
“의식… 접근하지 말라는 의미로 추정.”</div>
말을 마치자 다시 검은 문양이 퍼지기 시작한다.

주변에서는 마법사와 검사들이 서로를 부축하며 현장을 빠져나가고 있다.
멀리서 고대 마법사 한 명이 주인공을 향해 손짓한다.</div>${storyButton('고대 마법사에게 간다',()=>clearScene(7,'주인공은 무너지는 의식장을 벗어나 그를 따라간다.'))}${backButton()}`);
  }

  function stage8() {
    showStageScreen(`${top(8,'현세로 돌아갈 방법')}<div class="a1-story">그는 이들을 이끌던 고대 마법사였다.
고대 마법사는 품에서 오래된 가면을 꺼내 주인공에게 건넨다.

<div class="a1-relic">🎭 고대의 가면</div>
그가 빠르게 설명하지만 통역기는 제대로 따라가지 못한다.

<div class="a1-ai">“시간… 길… 돌아가라.”</div>
<span class="a1-speaker">주인공</span>
“이걸 사용하면 돌아갈 수 있다는 건가?”

고대 마법사가 고개를 끄덕인다.
그리고 마지막 말을 전한다.

<div class="a1-ai">“기억하라…”
“…우리의…”
[번역 실패]</div>
주인공이 가면을 얼굴에 가져간다.
공간이 일그러지고 주변 풍경이 빠르게 사라진다.

<div class="a1-system">TIME COORDINATE SEARCHING…
ERROR
TARGET TIME : UNKNOWN</div>
강한 빛.

주인공이 다시 눈을 뜬다.
눈앞에는 정글도, 고대의 성벽도 없다.
하늘을 가르는 비행체와 처음 보는 거대한 도시가 펼쳐져 있다.

<span class="a1-speaker">주인공</span>
“……여기가 현세라고?”</div>${storyButton('고대 I 완료',finishAncient,'btn btn-success')}${backButton()}`);
  }

  function finishAncient() {
    completeStage(8);
    showStageScreen(`${top(8)}<div class="a1-story">고대의 가면은 주인공을 원래 시간대로 돌려보내지 못했다.

날짜 좌표가 어긋난 것인지, 주인공이 도착한 곳은 훨씬 먼 미래였다.

<div style="text-align:center;font-size:1.45rem;font-weight:900;color:#a9d7ff;margin:14px 0;">🌆 미래 I</div>
<div class="a1-clear">ANCIENT I CLEAR</div></div>${backButton()}`);
  }

  function beginBattle(stageNo) {
    const data = STAGE_DATA[stageNo];
    if (!data) return;
    battle = { stageNo, encounter:0, player:{...PLAYER,hp:PLAYER.maxHp,curseTurns:0,corruptTurns:0}, enemies:data.enemies.map(e=>({...e,hp:e.maxHp})), enemyParalyzed:false, over:false };
    beginEncounter(0);
  }

  function beginEncounter(index) {
    if (!battle) return;
    battle.encounter=index; battle.player.hp=battle.player.maxHp; battle.player.curseTurns=0; battle.player.corruptTurns=0; battle.enemyParalyzed=false; battle.over=false;
    const e=battle.enemies[index]; e.hp=e.maxHp; renderBattle(); log(`전투 시작 · ${e.name}`);
  }

  function hpPct(h,m){return Math.max(0,Math.min(100,(h/m)*100));}
  function renderBattle(){
    if(!battle)return; const p=battle.player,e=battle.enemies[battle.encounter],total=battle.enemies.length;
    showStageScreen(`${top(battle.stageNo,total>1?`전투 ${battle.encounter+1} / ${total}`:'1 VS 1')}<div class="a1-battle-head"><div class="a1-fighter"><div class="a1-name">${esc(p.name)}</div><div class="a1-weapon">${esc(p.weapon)} · ATK ${p.atk}</div><div class="a1-hpbar"><div id="a1-pfill" class="a1-hpfill" style="width:${hpPct(p.hp,p.maxHp)}%"></div></div><div id="a1-php" class="a1-hptext">HP ${p.hp} / ${p.maxHp}</div><div id="a1-pstatus" class="a1-status"></div></div><div style="align-self:center;font-weight:900;color:#ffd700;">VS</div><div class="a1-fighter enemy"><div class="a1-name">${esc(e.name)}</div><div class="a1-weapon">${esc(e.weapon)} · ATK ${e.atk}</div><div class="a1-hpbar"><div id="a1-efill" class="a1-hpfill enemy" style="width:${hpPct(e.hp,e.maxHp)}%"></div></div><div id="a1-ehp" class="a1-hptext">HP ${e.hp} / ${e.maxHp}</div><div id="a1-estatus" class="a1-status"></div></div></div><div id="a1-log" class="a1-log"></div><button id="a1-atk" class="btn btn-gold">공격</button>${backButton()}`);
    const b=document.getElementById('a1-atk'); if(b)b.onclick=playerTurn;
  }
  function updateBars(){if(!battle)return;const p=battle.player,e=battle.enemies[battle.encounter];const pf=document.getElementById('a1-pfill'),ef=document.getElementById('a1-efill'),pt=document.getElementById('a1-php'),et=document.getElementById('a1-ehp'),ps=document.getElementById('a1-pstatus'),es=document.getElementById('a1-estatus');if(pf)pf.style.width=hpPct(p.hp,p.maxHp)+'%';if(ef)ef.style.width=hpPct(e.hp,e.maxHp)+'%';if(pt)pt.textContent=`HP ${Math.max(0,p.hp)} / ${p.maxHp}`;if(et)et.textContent=`HP ${Math.max(0,e.hp)} / ${e.maxHp}`;if(ps){const a=[];if(p.curseTurns>0)a.push(`☠️ 저주 ${p.curseTurns}`);if(p.corruptTurns>0)a.push(`🌑 타락 ${p.corruptTurns}`);ps.textContent=a.join(' · ');}if(es)es.textContent=battle.enemyParalyzed?'⚡ 마비':'';}
  function log(msg){const el=document.getElementById('a1-log');if(!el)return;const d=document.createElement('div');d.textContent=msg;el.appendChild(d);el.scrollTop=el.scrollHeight;}

  function playerTurn(){
    if(!battle||battle.over)return;const btn=document.getElementById('a1-atk');if(btn)btn.disabled=true;const p=battle.player,e=battle.enemies[battle.encounter];
    let dmg=p.atk;if(p.extraRate&&Math.random()<p.extraRate){dmg+=p.extra;log(`백사의 침 추가 피해 +${p.extra}`);}e.hp=Math.max(0,e.hp-dmg);log(`주인공의 공격 · ${dmg} 피해`);if(p.paralyze&&e.hp>0&&Math.random()<p.paralyze){battle.enemyParalyzed=true;log(`⚡ ${e.name} 마비!`);}updateBars();if(e.hp<=0){battle.over=true;enemyDown();return;}enemyTurn();if(btn&&!battle.over)btn.disabled=false;
  }

  function enemyTurn(){
    if(!battle||battle.over)return;const p=battle.player,e=battle.enemies[battle.encounter];
    if(battle.enemyParalyzed){battle.enemyParalyzed=false;log(`⚡ ${e.name}이 마비되어 공격하지 못했다.`);tickStatus();updateBars();return;}
    let hits=(e.double&&Math.random()<e.double)?2:1;let dmg=e.atk*hits;if(p.curseTurns>0)dmg=Math.round(dmg*1.15);p.hp=Math.max(0,p.hp-dmg);log(hits===2?`${e.name}의 이중 공격! ${dmg} 피해`:`${e.name}의 공격 · ${dmg} 피해`);
    if(e.curse&&p.hp>0&&Math.random()<e.curse){p.curseTurns=2;log('☠️ 저주! 2턴 동안 받는 피해 +15%');}
    if(e.corrupt&&p.hp>0&&Math.random()<e.corrupt){p.corruptTurns=2;log('🌑 타락! 2턴 동안 12 추가 피해');}
    tickStatus();updateBars();if(p.hp<=0){battle.over=true;const st=battle.stageNo;setTimeout(()=>showStageScreen(`${top(st)}<div class="a1-story"><div style="text-align:center;color:#ff8f8f;font-weight:900;font-size:1.2rem;">전투 패배</div></div>${storyButton('다시 도전',()=>beginBattle(st),'btn btn-danger')}${backButton()}`),250);}
  }
  function tickStatus(){if(!battle)return;const p=battle.player;if(p.corruptTurns>0&&p.hp>0){p.hp=Math.max(0,p.hp-12);p.corruptTurns--;log('🌑 타락 피해 12');}if(p.curseTurns>0)p.curseTurns--;}
  function enemyDown(){if(!battle)return;const st=battle.stageNo,idx=battle.encounter,total=battle.enemies.length,e=battle.enemies[idx];log(`${e.name} 제압.`);if(idx+1<total){setTimeout(()=>beginEncounter(idx+1),500);return;}battle=null;setTimeout(()=>{if(st===2)stage2After();else if(st===7)stage7After();},420);}

  // 실제 스테이지 완료 수로만 챕터 클리어/다음 챕터 해금을 판정한다.
  const REQUIRED = Object.freeze({ earth1:5, delta1:5, ancient1:8, future1:8, earth2:8, demon1:8, heaven1:9, space1:10, void:10 });
  const originalStoryChapterCleared = typeof storyChapterCleared === 'function' ? storyChapterCleared : null;
  storyChapterCleared = function(id){
    if(Object.prototype.hasOwnProperty.call(REQUIRED,id)){
      try{return Number(saveData && saveData.story && saveData.story.stages && saveData.story.stages[id] || 0) >= REQUIRED[id];}catch(e){return false;}
    }
    return originalStoryChapterCleared ? originalStoryChapterCleared(id) : false;
  };
  storyChapterUnlocked = function(id){
    const idx = STORY_CHAPTER_ORDER.indexOf(id); if(idx<0)return false; if(idx===0)return true;
    return storyChapterCleared(STORY_CHAPTER_ORDER[idx-1]);
  };
  storyStageUnlocked = function(chapterId,stageNo){
    if(!storyChapterUnlocked(chapterId))return false;
    const max = REQUIRED[chapterId] || (STORY_CHAPTER_META[chapterId] && STORY_CHAPTER_META[chapterId].stages) || 0;
    if(stageNo<1||stageNo>max)return false;
    let cleared=0;try{cleared=Number(saveData.story.stages[chapterId])||0;}catch(e){}
    return stageNo<=Math.min(max,cleared+1);
  };

  // 고대 I 클리어로 고대 마법사 보스전이 열리지 않도록 차단한다.
  const originalRaidBossUnlocked = typeof raidBossUnlocked === 'function' ? raidBossUnlocked : null;
  raidBossUnlocked = function(id){ if(id==='ancient_mage')return false; return originalRaidBossUnlocked ? originalRaidBossUnlocked(id) : false; };
  const originalRaidBossUnlockText = typeof raidBossUnlockText === 'function' ? raidBossUnlockText : null;
  raidBossUnlockText = function(id){ if(id==='ancient_mage')return '아직 해금되지 않음'; return originalRaidBossUnlockText ? originalRaidBossUnlockText(id) : '스토리 진행 필요'; };

  const originalRenderStory = typeof renderStory === 'function' ? renderStory : null;
  if(originalRenderStory){renderStory=function(){const r=originalRenderStory();try{const el=$('story-list');if(el){[...el.querySelectorAll('div')].forEach(d=>{if(/클리어 보상:\s*고대 마법사 보스전 해금/.test(d.textContent||''))d.remove();});}}catch(e){}return r;};}

  const originalRenderStoryChapter = typeof renderStoryChapter === 'function' ? renderStoryChapter : null;
  if(originalRenderStoryChapter){renderStoryChapter=function(id){if(id!=='ancient1')return originalRenderStoryChapter(id);const el=$('story-list'),title=$('story-title'),subtitle=$('story-subtitle'),back=$('story-back-btn');if(!el)return;if(title)title.textContent='🏛️ 고대 I';if(subtitle)subtitle.textContent='8개 스테이지 · 순차 진행';if(back)back.textContent='← 챕터 목록';let cleared=0;try{cleared=Math.max(0,Math.min(8,Number(saveData.story.stages.ancient1)||0));}catch(e){}let html='';for(let no=1;no<=8;no++){const done=no<=cleared,unlocked=storyStageUnlocked('ancient1',no);html+=`<button class="btn" ${unlocked?`onclick="openStoryStage('ancient1', ${no})"`:'disabled'} style="text-align:left;padding:13px 14px;margin:6px 0;${done?'border:1px solid #75ffad;':''}"><div style="font-weight:900;">${done?'✅':(unlocked?'▶️':'🔒')} 3-${no} ${esc(TITLES[no])}</div><div style="font-size:.78rem;opacity:.7;margin-top:4px;">${done?'클리어 완료':(unlocked?'도전 가능':'앞 스테이지 클리어 필요')}</div></button>`;}el.innerHTML=html;};}

  const originalOpenStoryStage = typeof openStoryStage === 'function' ? openStoryStage : null;
  openStoryStage=function(chapterId,stageNo){if(chapterId!=='ancient1'){if(originalOpenStoryStage)return originalOpenStoryStage(chapterId,stageNo);return;}if(!storyStageUnlocked('ancient1',stageNo)){alert('앞 스테이지를 먼저 클리어하세요.');return;}if(stageNo===1)stage1();else if(stageNo===2)stage2();else if(stageNo===3)stage3();else if(stageNo===4)stage4();else if(stageNo===5)stage5();else if(stageNo===6)stage6();else if(stageNo===7)stage7();else if(stageNo===8)stage8();};

  console.info('[Lost Ruby] Ancient I story module loaded');
})();

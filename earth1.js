/* Lost Ruby - Earth 1 production story module */
(() => {
  const TITLES = Object.freeze({
    1: '폭풍전야',
    2: '외곽 경계선',
    3: '뱀의 소굴',
    4: '백사',
    5: '선택'
  });

  const STAGE_DATA = Object.freeze({
    2: {
      player: { name: '주인공', maxHp: 220, atk: 15, weapon: '암살 단검 +1' },
      enemies: [
        { name: '외곽 경비병', maxHp: 110, atk: 10, weapon: '삼단봉' },
        { name: '외곽 경비병', maxHp: 110, atk: 10, weapon: '삼단봉' },
        { name: '테이저 경비병', maxHp: 100, atk: 7, weapon: '테이저건', paralyze: 0.15 }
      ]
    },
    3: {
      player: { name: '주인공', maxHp: 220, atk: 15, weapon: '암살 단검 +1' },
      enemies: [
        { name: '경호원', maxHp: 170, atk: 14, weapon: '삼단봉' },
        { name: '경호원', maxHp: 170, atk: 14, weapon: '삼단봉' },
        { name: '테이저 경호원', maxHp: 150, atk: 10, weapon: '테이저건', paralyze: 0.25 }
      ]
    },
    4: {
      player: { name: '주인공', maxHp: 520, atk: 45, weapon: '쌍삼단봉', double: 0.40 },
      enemies: [
        { name: '백사', maxHp: 750, atk: 35, weapon: '백사의 침 +5', paralyze: 0.35, extra: 20, extraRate: 0.10 }
      ]
    },
    5: {
      player: { name: '주인공', maxHp: 520, atk: 10, weapon: '목검' },
      enemies: [
        { name: 'B.S.H', maxHp: 75, atk: 3, weapon: '맨손' }
      ]
    }
  });

  let currentStage = 0;
  let battle = null;

  // 암살자도 강화 1단계마다 HP +100으로 통일한다.
  if (typeof getHpPerEnhance === 'function') {
    getHpPerEnhance = function() { return 100; };
  }

  function ensureUi() {
    if (!document.getElementById('earth1-style')) {
      const style = document.createElement('style');
      style.id = 'earth1-style';
      style.textContent = `
        #earth1-stage-screen{padding:18px;}
        .e1-card{background:rgba(0,0,0,.32);border:1px solid rgba(255,255,255,.10);border-radius:15px;padding:15px;margin:10px 0;line-height:1.7;}
        .e1-dialog{font-size:.95rem;white-space:pre-line;}
        .e1-speaker{font-weight:900;color:#ffd700;margin-bottom:4px;}
        .e1-small{font-size:.78rem;opacity:.72;}
        .e1-battle-head{display:flex;gap:9px;align-items:stretch;margin-top:10px;}
        .e1-fighter{flex:1;background:rgba(0,0,0,.36);border-radius:12px;padding:11px;text-align:center;border:1px solid rgba(255,255,255,.10);}
        .e1-fighter.enemy{border-color:rgba(255,90,90,.42);}
        .e1-name{font-weight:900;font-size:.95rem;}
        .e1-weapon{font-size:.76rem;color:#ffd700;margin:3px 0 8px;min-height:1.2em;}
        .e1-hpbar{height:14px;background:#333;border-radius:8px;overflow:hidden;margin-top:5px;}
        .e1-hpfill{height:100%;background:linear-gradient(90deg,#00b09b,#96c93d);transition:width .25s;}
        .e1-hpfill.enemy{background:linear-gradient(90deg,#c31432,#ff4b2b);}
        .e1-hptext{font-size:.72rem;opacity:.85;margin-top:4px;}
        .e1-log{background:rgba(0,0,0,.48);border-radius:12px;padding:11px;min-height:145px;max-height:245px;overflow-y:auto;margin:12px 0;font-size:.83rem;line-height:1.55;}
        .e1-log div{padding:3px 0;border-bottom:1px solid rgba(255,255,255,.04);}
        .e1-clear{color:#75ffad;font-weight:900;text-align:center;font-size:1.25rem;margin:12px 0;}
        .e1-secret{font-weight:900;letter-spacing:.18em;text-align:center;font-size:1.35rem;color:#f4e6b1;padding:16px 0;}
      `;
      document.head.appendChild(style);
    }

    let screen = document.getElementById('earth1-stage-screen');
    if (!screen) {
      screen = document.createElement('div');
      screen.id = 'earth1-stage-screen';
      screen.className = 'screen';
      const app = document.getElementById('app');
      if (app) app.appendChild(screen);
    }
    return screen;
  }

  function esc(s) {
    return String(s ?? '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/\"/g, '&quot;').replace(/'/g, '&#039;');
  }

  function screen() { return ensureUi(); }

  function showStageScreen(html) {
    const el = screen();
    el.innerHTML = html;
    if (typeof showScreen === 'function') showScreen('earth1-stage-screen');
  }

  function top(stageNo, subtitle = '') {
    return `<h2 style="text-align:center;margin-bottom:4px;">🌍 지구 1-${stageNo} · ${esc(TITLES[stageNo])}</h2>
      <p style="text-align:center;opacity:.7;font-size:.8rem;margin-bottom:10px;">${esc(subtitle)}</p>`;
  }

  function storyButton(label, fn, cls = 'btn btn-gold') {
    const id = 'e1btn_' + Math.random().toString(36).slice(2);
    setTimeout(() => {
      const b = document.getElementById(id);
      if (b) b.onclick = fn;
    }, 0);
    return `<button id="${id}" class="${cls}">${esc(label)}</button>`;
  }

  function backButton() {
    return storyButton('← 스테이지 목록', () => {
      currentStage = 0;
      battle = null;
      if (typeof openStoryChapter === 'function') openStoryChapter('earth1');
    }, 'btn');
  }

  function completeStage(stageNo) {
    try {
      const story = typeof ensureStoryProgress === 'function' ? ensureStoryProgress() : (saveData.story || (saveData.story = {stages:{},clearedChapters:{}}));
      if (!story.stages) story.stages = {};
      if (!story.clearedChapters) story.clearedChapters = {};
      story.stages.earth1 = Math.max(Number(story.stages.earth1) || 0, stageNo);
      if (stageNo >= 5) story.clearedChapters.earth1 = true;
      if (typeof persistSave === 'function') persistSave();
    } catch (e) {
      console.warn('earth1 progress save failed', e);
    }
  }

  function clearScene(stageNo, extraHtml = '') {
    completeStage(stageNo);
    const next = stageNo < 5
      ? storyButton(`다음 · 1-${stageNo + 1} ${TITLES[stageNo + 1]}`, () => openStoryStage('earth1', stageNo + 1), 'btn btn-success')
      : '';
    showStageScreen(`${top(stageNo)}<div class="e1-card">${extraHtml}<div class="e1-clear">STAGE CLEAR</div></div>${next}${backButton()}`);
  }

  function startStage1() {
    showStageScreen(`${top(1, '작전 투입')}
      <div class="e1-card e1-dialog">
        킬 오브 킹 내부에 긴급 첩보가 들어온다.

        뱀의 둥지 외교단 부수장 <b>B.S.H</b>가 킬 오브 킹을 폭로할 수 있는 내부 자료와 과거 자료 일부를 확보했다.

        자료가 외부로 넘어가기 전, 블랙옵스 소속 주인공은 뱀의 둥지 본부가 아닌 외곽 지부 기지로 출동한다.

        아직 기지는 침입 사실을 눈치채지 못했다.
      </div>
      ${storyButton('기지로 침투한다', () => clearScene(1, '<div class="e1-dialog">주인공은 어둠을 틈타 지부 기지 외곽으로 접근한다.</div>'))}
      ${backButton()}`);
  }

  function startStage2() {
    showStageScreen(`${top(2, '지부 기지 외곽')}
      <div class="e1-card e1-dialog">
        외곽 경계는 예상보다 느슨하다.

        주인공은 일반 경비병을 빠르게 제압하며 기지 안쪽으로 파고든다.
      </div>
      ${storyButton('경계선을 돌파한다', () => beginBattleStage(2))}
      ${backButton()}`);
  }

  function startStage3() {
    showStageScreen(`${top(3, '뱀의 둥지 지부 기지 내부')}
      <div class="e1-card e1-dialog">
        기지 내부로 들어서자 B.S.H 주변을 지키던 경호원들이 주인공을 발견한다.

        외곽 경비보다 훈련된 인원들이지만, 아직 뱀의 둥지 핵심 전투원은 아니다.
      </div>
      ${storyButton('경호원들을 제압한다', () => beginBattleStage(3))}
      ${backButton()}`);
  }

  function stage3AfterBattle() {
    showStageScreen(`${top(3)}
      <div class="e1-card e1-dialog">
        경호원들을 모두 제압한 뒤, 주인공은 작은 자료 보관실을 발견한다.

        여러 문서 사이에서 유독 눈에 띄는 서류철 하나.
        표지에는 작성자도 내용도 없다.
        단 하나의 문구만 적혀 있다.
        <div class="e1-secret">1급기밀</div>
        주인공은 서류를 잠시 바라보다 다시 B.S.H를 추적한다.
      </div>
      ${storyButton('계속 이동한다', () => clearScene(3))}
      ${backButton()}`);
  }

  function startStage4() {
    showStageScreen(`${top(4, '중간 간부 · 백사')}
      <div class="e1-card e1-dialog">
        B.S.H가 있는 구역으로 향하던 주인공 앞을 뱀의 둥지 중간 간부 <b>백사</b>가 막아선다.

        <span class="e1-speaker">백사</span>
        여기까지 들어오다니. 킬 오브 킹도 꽤 급한 모양이군.

        <span class="e1-speaker">주인공</span>
        B.S.H는 어디 있지?

        <span class="e1-speaker">백사</span>
        지나갈 수 있다면 직접 찾아봐.

        주인공은 바닥에 떨어진 삼단봉 두 개를 집어 든다.

        <span class="e1-speaker">백사</span>
        그걸로 되겠어..?
      </div>
      ${storyButton('백사와 싸운다', () => beginBattleStage(4), 'btn btn-danger')}
      ${backButton()}`);
  }

  function stage4AfterBattle() {
    clearScene(4, `<div class="e1-dialog"><span class="e1-speaker">백사</span>
      B.S.H가 가진 걸 두려워하는 건…… 우리 쪽이 아닐 텐데.

      주인공은 잠시 멈추지만 대답하지 않고 마지막 구역으로 향한다.</div>`);
  }

  function startStage5() {
    showStageScreen(`${top(5, '기지 탈출구 직전')}
      <div class="e1-card e1-dialog">
        마지막 방.
        탈출을 준비하던 B.S.H가 주인공을 바라본다.

        <span class="e1-speaker">B.S.H</span>
        결국 여기까지 왔군.

        주인공이 목검을 들어 올린다.

        <span class="e1-speaker">B.S.H</span>
        ……무슨 목적이지..?
      </div>
      ${storyButton('B.S.H를 제압한다', () => beginBattleStage(5), 'btn btn-danger')}
      ${backButton()}`);
  }

  function stage5Choice() {
    showStageScreen(`${top(5)}
      <div class="e1-card e1-dialog">
        B.S.H가 바닥에 쓰러진다.
        주인공은 그의 손을 묶고, 챙겨둔 자료들을 확인한다.

        킬 오브 킹 내부 자료와 몇 개의 오래된 기록이 섞여 있다.

        <span class="e1-speaker">B.S.H</span>
        나도 저게 전부 무슨 의미인지는 모른다.
        하지만 킬 오브 킹이 감추고 있는 게 있다는 것 정도는 알 수 있지.

        <span class="e1-speaker">B.S.H</span>
        이제 어떻게 할 거지?
      </div>
      ${storyButton('B.S.H를 넘긴다', () => finishChoice('handover'), 'btn btn-danger')}
      ${storyButton('B.S.H를 풀어준다', () => finishChoice('release'), 'btn btn-success')}
      ${backButton()}`);
  }

  function finishChoice(choice) {
    try {
      if (!saveData.story) saveData.story = {};
      saveData.story.earth1BSHChoice = choice;
      if (typeof persistSave === 'function') persistSave();
    } catch (e) {}

    if (choice === 'release') {
      clearScene(5, `<div class="e1-dialog">
        주인공이 B.S.H의 포박을 풀어준다.

        <span class="e1-speaker">B.S.H</span>
        ……왜지?

        <span class="e1-speaker">주인공</span>
        훗날 다시 볼 것 같군…… 재밌었다.

        B.S.H는 잠시 주인공을 바라본 뒤 자료를 챙겨 기지를 빠져나간다.
      </div>`);
    } else {
      clearScene(5, `<div class="e1-dialog">
        주인공은 B.S.H를 묶어둔 채 회수 인력에게 넘긴다.

        끌려가기 전 B.S.H가 주인공을 바라본다.

        <span class="e1-speaker">B.S.H</span>
        언젠가는 네가 직접 알게 될 거다.
      </div>`);
    }
  }

  function beginBattleStage(stageNo) {
    const data = STAGE_DATA[stageNo];
    if (!data) return;
    currentStage = stageNo;
    battle = {
      stageNo,
      encounter: 0,
      player: { ...data.player, hp: data.player.maxHp },
      enemies: data.enemies.map(e => ({ ...e, hp: e.maxHp })),
      playerParalyzed: false,
      over: false
    };
    beginEncounter(0);
  }

  function beginEncounter(index) {
    if (!battle) return;
    battle.encounter = index;
    battle.player.hp = battle.player.maxHp;
    battle.playerParalyzed = false;
    battle.over = false;
    const enemy = battle.enemies[index];
    enemy.hp = enemy.maxHp;
    renderBattle();
    log(`전투 시작 · ${enemy.name}`);
  }

  function hpPct(hp, max) { return Math.max(0, Math.min(100, (hp / max) * 100)); }

  function renderBattle() {
    if (!battle) return;
    const p = battle.player;
    const e = battle.enemies[battle.encounter];
    const total = battle.enemies.length;
    showStageScreen(`${top(battle.stageNo, total > 1 ? `전투 ${battle.encounter + 1} / ${total}` : '1 VS 1')}
      <div class="e1-battle-head">
        <div class="e1-fighter">
          <div class="e1-name">${esc(p.name)}</div>
          <div class="e1-weapon">${esc(p.weapon)} · ATK ${p.atk}</div>
          <div class="e1-hpbar"><div id="e1-pfill" class="e1-hpfill" style="width:${hpPct(p.hp,p.maxHp)}%"></div></div>
          <div id="e1-php" class="e1-hptext">HP ${p.hp} / ${p.maxHp}</div>
        </div>
        <div style="align-self:center;font-weight:900;color:#ffd700;">VS</div>
        <div class="e1-fighter enemy">
          <div class="e1-name">${esc(e.name)}</div>
          <div class="e1-weapon">${esc(e.weapon)} · ATK ${e.atk}</div>
          <div class="e1-hpbar"><div id="e1-efill" class="e1-hpfill enemy" style="width:${hpPct(e.hp,e.maxHp)}%"></div></div>
          <div id="e1-ehp" class="e1-hptext">HP ${e.hp} / ${e.maxHp}</div>
        </div>
      </div>
      <div id="e1-log" class="e1-log"></div>
      <button id="e1-attack" class="btn btn-gold">공격</button>
      ${backButton()}`);
    const atk = document.getElementById('e1-attack');
    if (atk) atk.onclick = playerTurn;
  }

  function updateBars() {
    if (!battle) return;
    const p = battle.player;
    const e = battle.enemies[battle.encounter];
    const pf = document.getElementById('e1-pfill');
    const ef = document.getElementById('e1-efill');
    const pt = document.getElementById('e1-php');
    const et = document.getElementById('e1-ehp');
    if (pf) pf.style.width = hpPct(p.hp,p.maxHp) + '%';
    if (ef) ef.style.width = hpPct(e.hp,e.maxHp) + '%';
    if (pt) pt.textContent = `HP ${Math.max(0,p.hp)} / ${p.maxHp}`;
    if (et) et.textContent = `HP ${Math.max(0,e.hp)} / ${e.maxHp}`;
  }

  function log(msg) {
    const el = document.getElementById('e1-log');
    if (!el) return;
    const row = document.createElement('div');
    row.textContent = msg;
    el.appendChild(row);
    el.scrollTop = el.scrollHeight;
  }

  function playerTurn() {
    if (!battle || battle.over) return;
    const btn = document.getElementById('e1-attack');
    if (btn) btn.disabled = true;
    const p = battle.player;
    const e = battle.enemies[battle.encounter];

    if (battle.playerParalyzed) {
      battle.playerParalyzed = false;
      log('⚡ 몸이 굳어 움직이지 못했다.');
      enemyTurn();
      if (btn && !battle.over) btn.disabled = false;
      return;
    }

    let hits = 1;
    if (p.double && Math.random() < p.double) hits = 2;
    const dmg = p.atk * hits;
    e.hp = Math.max(0, e.hp - dmg);
    log(hits === 2 ? `주인공의 연속 공격! ${dmg} 피해` : `주인공의 공격 · ${dmg} 피해`);
    updateBars();

    if (e.hp <= 0) {
      battle.over = true;
      onEnemyDown();
      return;
    }

    enemyTurn();
    if (btn && !battle.over) btn.disabled = false;
  }

  function enemyTurn() {
    if (!battle || battle.over) return;
    const p = battle.player;
    const e = battle.enemies[battle.encounter];
    let dmg = e.atk;
    if (e.extraRate && Math.random() < e.extraRate) {
      dmg += e.extra || 0;
      log(`${e.name}의 백사의 침이 깊게 파고든다! 추가 피해 ${e.extra}`);
    }
    p.hp = Math.max(0, p.hp - dmg);
    log(`${e.name}의 공격 · ${dmg} 피해`);

    if (e.paralyze && p.hp > 0 && Math.random() < e.paralyze) {
      battle.playerParalyzed = true;
      log('⚡ 마비! 다음 행동을 할 수 없다.');
    }
    updateBars();

    if (p.hp <= 0) {
      battle.over = true;
      const st = battle.stageNo;
      setTimeout(() => {
        showStageScreen(`${top(st)}<div class="e1-card"><div style="text-align:center;font-weight:900;color:#ff8f8f;font-size:1.2rem;">전투 패배</div><p style="text-align:center;opacity:.8;margin-top:8px;">스테이지 진행도는 유지되지 않습니다.</p></div>${storyButton('다시 도전', () => beginBattleStage(st), 'btn btn-danger')}${backButton()}`);
      }, 250);
    }
  }

  function onEnemyDown() {
    if (!battle) return;
    const st = battle.stageNo;
    const idx = battle.encounter;
    const total = battle.enemies.length;
    const e = battle.enemies[idx];
    log(`${e.name} 제압.`);

    if (idx + 1 < total) {
      setTimeout(() => {
        beginEncounter(idx + 1);
      }, 550);
      return;
    }

    setTimeout(() => {
      battle = null;
      if (st === 2) clearScene(2, '<div class="e1-dialog">외곽 경비를 모두 제압했다. 주인공은 지부 기지 내부로 진입한다.</div>');
      else if (st === 3) stage3AfterBattle();
      else if (st === 4) stage4AfterBattle();
      else if (st === 5) stage5Choice();
    }, 450);
  }

  const originalRenderStoryChapter = typeof renderStoryChapter === 'function' ? renderStoryChapter : null;
  if (originalRenderStoryChapter) {
    renderStoryChapter = function(id) {
      if (id !== 'earth1') return originalRenderStoryChapter(id);
      const meta = STORY_CHAPTER_META[id];
      const el = $('story-list');
      const title = $('story-title');
      const subtitle = $('story-subtitle');
      const back = $('story-back-btn');
      if (!meta || !el) return;
      if (title) title.textContent = '🌍 지구 1';
      if (subtitle) subtitle.textContent = '5개 스테이지 · 순차 진행';
      if (back) back.textContent = '← 챕터 목록';

      const story = ensureStoryProgress();
      const cleared = Math.max(0, Math.min(meta.stages, Number(story.stages[id]) || 0));
      let html = '';
      for (let no = 1; no <= meta.stages; no++) {
        const done = no <= cleared;
        const unlocked = storyStageUnlocked(id, no);
        html += `<button class="btn" ${unlocked ? `onclick="openStoryStage('earth1', ${no})"` : 'disabled'} style="text-align:left;padding:13px 14px;margin:6px 0;${done ? 'border:1px solid #75ffad;' : ''}">
          <div style="font-weight:900;">${done ? '✅' : (unlocked ? '▶️' : '🔒')} ${no}. ${esc(TITLES[no])}</div>
          <div style="font-size:.78rem;opacity:.7;margin-top:4px;">${done ? '클리어 완료' : (unlocked ? '도전 가능' : '앞 스테이지 클리어 필요')}</div>
        </button>`;
      }
      el.innerHTML = html;
    };
  }

  const originalOpenStoryStage = typeof openStoryStage === 'function' ? openStoryStage : null;
  openStoryStage = function(chapterId, stageNo) {
    if (chapterId !== 'earth1') {
      if (originalOpenStoryStage) return originalOpenStoryStage(chapterId, stageNo);
      return;
    }
    if (!storyStageUnlocked('earth1', stageNo)) {
      alert('앞 스테이지를 먼저 클리어하세요.');
      return;
    }
    currentStage = stageNo;
    if (stageNo === 1) startStage1();
    else if (stageNo === 2) startStage2();
    else if (stageNo === 3) startStage3();
    else if (stageNo === 4) startStage4();
    else if (stageNo === 5) startStage5();
  };

  const assassinCard = document.getElementById('cls-assassin');
  if (assassinCard) {
    const desc = assassinCard.querySelector('.class-desc');
    if (desc) desc.innerHTML = '시작 체력 120<br>즉사·암살 특화';
  }

  console.info('[Lost Ruby] Earth 1 story module loaded');
})();

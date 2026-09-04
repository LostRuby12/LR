/* Lost Ruby - Noh Beom-su 3-phase production boss battle */
(()=>{
  const $ = id => document.getElementById(id);
  const CH='future1', STAGE=7;
  const TITLES=['','시간의 역전','오버드라이브','콘스탄티노폴리스','아크 지구','예루살렘','아틀란티스','달','타임오버'];
  const TR=['','시간칩','오버드라이브 엔진','시간 코어','아크 셀','성지순례','심해 결정체','월석 파편','시간선의 초월'];
  const GN=['없음','낡은','평범','최고급'];
  let run=null, seq=0;

  function ensureData(root=saveData){
    root.story??={}; root.story.stages??={}; root.story.clearedChapters??={}; root.story.future1Data??={};
    const d=root.story.future1Data; d.treasures??={}; d.lpRewarded??={};
    for(let i=1;i<=8;i++) d.treasures[i]=Math.max(0,Math.min(3,+d.treasures[i]||0));
    d.coreDestroyed=!!d.coreDestroyed;
    return d;
  }
  const treasure=()=>ensureData().treasures;
  const screen=()=>{
    let e=$('future1-stage-screen');
    if(!e){e=document.createElement('div');e.id='future1-stage-screen';e.className='screen';$('app')?.appendChild(e)}
    return e;
  };
  function css(){
    if($('noh-v6-style'))return;
    const s=document.createElement('style');s.id='noh-v6-style';s.textContent=`
      #future1-stage-screen{padding:18px}.nv6box{background:linear-gradient(180deg,#101827,#090e18);border:1px solid #314766;border-radius:14px;padding:13px;margin:9px 0}.nv6phase{text-align:center;border:1px solid #4c6790;border-radius:11px;padding:9px;color:#a9d7ff;font-weight:900;background:#0c1422}.nv6fighters{display:flex;gap:8px}.nv6fighter{flex:1;min-width:0;text-align:center;background:#070b12;border:1px solid #2c3d57;border-radius:10px;padding:9px}.nv6hp{height:13px;background:#303746;border-radius:8px;overflow:hidden;margin:6px 0}.nv6fill{height:100%;background:#48ca83;transition:width .2s}.nv6fill.e{background:#df4f62}.nv6log{height:150px;overflow:auto;background:#05080d;border-radius:10px;padding:9px;font-size:.77rem;line-height:1.5;margin:9px 0}.nv6good{color:#78ffad;font-weight:900}.nv6bad{color:#ff8797;font-weight:900}.nv6gold{color:#ffe26f;font-weight:900}.nv6sys{color:#a9d7ff;font-family:monospace}.nv6lanes{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.nv6lane{min-height:62px;background:#2b3448}.nv6lane.hint{background:#16573c!important;box-shadow:0 0 18px rgba(90,255,170,.55);outline:2px solid #62ffb3}.nv6track{height:78px;background:#05080d;border:1px solid #293a55;border-radius:10px;position:relative;overflow:hidden}.nv6safe{position:absolute;left:40%;width:20%;height:100%;background:rgba(58,186,116,.28)}.nv6perfect{position:absolute;left:47%;width:6%;height:100%;background:rgba(235,198,60,.38)}.nv6cursor{position:absolute;top:0;width:6px;height:100%;background:#ff5a72;box-shadow:0 0 12px #ff5a72}.nv6parry{height:118px;background:#05080d;border:1px solid #293a55;border-radius:12px;position:relative;overflow:hidden}.nv6core{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:52px;height:52px;border-radius:50%;border:3px solid #76c9ff;box-shadow:0 0 17px #3c9ddc;display:flex;align-items:center;justify-content:center;font-size:.67rem;color:#bde8ff}.nv6target{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:78px;height:78px;border-radius:50%;border:3px solid #5cffad;box-shadow:0 0 14px rgba(92,255,173,.55)}.nv6ring{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:190px;height:190px;border-radius:50%;border:4px solid #ff596d;opacity:.88}.nv6hint{text-align:center;font-size:.75rem;opacity:.75;margin:7px 0}`;
    document.head.appendChild(s);
  }
  function show(h){css();screen().innerHTML=h;if(typeof showScreen==='function')showScreen('future1-stage-screen')}
  const top=(sub='')=>`<h2 style="text-align:center">🌆 4-7 · 달</h2><p style="text-align:center;opacity:.7;font-size:.8rem">${sub}</p>`;
  function btn(label,fn,cls='btn btn-gold'){
    const id='nv6b'+Math.random().toString(36).slice(2);setTimeout(()=>{const b=$(id);if(b)b.onclick=fn},0);return `<button id="${id}" class="${cls}">${label}</button>`;
  }
  function alive(r=run){return !!r&&!r.done&&run===r}
  function later(fn,ms,r=run){const id=setTimeout(()=>{if(alive(r))fn()},ms);r?.timeouts?.push(id);return id}
  function clearTimers(r=run){if(!r)return;(r.timeouts||[]).forEach(clearTimeout);(r.intervals||[]).forEach(clearInterval);r.timeouts=[];r.intervals=[]}
  function stop(){if(run){run.done=true;clearTimers(run);run=null}if(typeof stopFutureStageBgm==='function')try{stopFutureStageBgm()}catch(_){} }
  function log(text,cls=''){if(!run)return;run.log.push({text,cls});if(run.log.length>40)run.log.shift()}
  function logHtml(){return (run?.log||[]).slice(-12).map(x=>`<div class="${x.cls||''}">${x.text}</div>`).join('')}
  function fighterHtml(){
    const r=run,p=r.p,e=r.e;
    return `<div class="nv6fighters"><div class="nv6fighter"><b>주인공</b><div style="font-size:.7rem;opacity:.75">${p.weapon} · ATK ${p.atk.toLocaleString()}</div><div class="nv6hp"><div class="nv6fill" style="width:${Math.max(0,p.hp/p.max*100)}%"></div></div>${Math.max(0,Math.ceil(p.hp)).toLocaleString()} / ${p.max.toLocaleString()}</div><div class="nv6fighter"><b>폭주한 노범수</b><div style="font-size:.7rem;opacity:.75">월면 중력포 · 강화 의수 · ATK ${e.atk.toLocaleString()}</div><div class="nv6hp"><div class="nv6fill e" style="width:${Math.max(0,e.hp/e.max*100)}%"></div></div>${Math.max(0,Math.ceil(e.hp)).toLocaleString()} / ${e.max.toLocaleString()}</div></div>`;
  }
  function shell(phase,body){
    if(!run)return;show(`${top('NEON SIGNAL')}<div class="nv6phase">${phase}</div><div class="nv6box">${fighterHtml()}<div class="nv6log">${logHtml()}</div>${body}</div>${btn('← 스테이지 목록',()=>{stop();openStoryChapter(CH)},'btn')}`);
    const l=document.querySelector('.nv6log');if(l)l.scrollTop=l.scrollHeight;
  }
  function lose(reason){if(!run||run.done)return;const r=run;r.done=true;clearTimers(r);show(`${top()}<div class="nv6box nv6bad" style="text-align:center;font-size:1.15rem">DEFEAT<div style="font-size:.78rem;margin-top:7px">${reason||''}</div></div>${btn('다시 도전',()=>window.openStoryStage(CH,STAGE),'btn btn-danger')}${btn('← 스테이지 목록',()=>openStoryChapter(CH),'btn')}`);run=null}

  function checkRevive(){
    const r=run;if(!r||r.p.hp>0)return false;
    if(treasure()[5]===3&&!r.p.revived){r.p.revived=true;r.p.hp=Math.max(1,Math.round(r.p.max*.30));log('✦ 성지순례 · HP 30% 부활','nv6gold');return true}
    return false;
  }
  function bossHit(mult=1){
    const r=run;if(!alive(r))return false;
    if(r.guard>0){r.guard--;log(`🌊 심해 결정체 · 공격 완전 방어 (${r.guard}회 남음)`,'nv6good');return false}
    if(Math.random()<.15){log('💨 미래형 전투복 · 공격 회피','nv6good');return false}
    const dm=Math.round(r.e.atk*.4*mult);r.p.hp-=dm;log(`노범수 공격 · ${dm.toLocaleString()} 피해`,'nv6bad');
    if(r.p.hp<=0){if(checkRevive())return false;lose('노범수의 공격에 쓰러졌다.');return true}
    if(r.phase===2&&!r.arcCheck&&r.p.hp/r.p.max<.15){
      r.arcCheck=true;log('ARC CORE CRITICAL · HP 15% 미만','nv6sys');
      if(Math.random()<.5){r.e.hp=0;log('💥 반중력 폭발 · 노범수 즉사','nv6gold');later(()=>victory('반중력 폭발'),250,r);return true}
      log('반중력 폭발 실패','nv6bad');
    }
    return false;
  }
  function titanCounter(perfect=false){
    const r=run;if(!alive(r))return true;
    let dm=Math.round(r.p.atk*30*(perfect?1.20:1));
    if(Math.random()<.20){dm=Math.round(dm*1.8);log('🌀 중력 붕괴 · 1.8배','nv6gold')}
    r.e.hp-=dm;log(`⚡ ARC TITAN 반격 · ${dm.toLocaleString()} 피해`,perfect?'nv6gold':'nv6good');
    if(r.e.hp<=0){r.e.hp=0;later(()=>victory('ARC TITAN'),260,r);return true}
    return false;
  }

  function phase1(){
    const r=run;if(!alive(r))return;r.phase=1;r.round++;
    if(r.round>3){log('[ARC SYNC : 100%]','nv6sys');log('⚡ ARC TITAN 동기화 완료','nv6gold');r.phase=2;r.round=0;return later(phase2,600,r)}
    const safe=Math.floor(Math.random()*3),names=['LUNAR-A','LUNAR-B','LUNAR-C'];
    shell(`PHASE 1 · GRAVITY FIELD ${r.round}/3`,`<div style="text-align:center;margin-bottom:8px">안전 구역이 잠깐 초록색으로 점멸한다.</div><div class="nv6lanes">${names.map((n,i)=>`<button id="nv6lane${i}" class="btn nv6lane" disabled>${n}</button>`).join('')}</div><div id="nv6msg" class="nv6hint">SCAN...</div>`);
    let picked=false,canPick=false;
    names.forEach((_,i)=>{const b=$('nv6lane'+i);if(b)b.onclick=()=>{if(!alive(r)||picked||!canPick)return;picked=true;clearTimers(r);const ok=i===safe;if(ok)log(`${names[i]} 진입 · 중력장 회피 성공`,'nv6good');else{log(`잘못된 구역 · 안전구역 ${names[safe]}`,'nv6bad');if(bossHit(1))return}later(phase1,380,r)}});
    later(()=>{const b=$('nv6lane'+safe);if(b)b.classList.add('hint');const m=$('nv6msg');if(m)m.textContent='SAFE SIGNAL DETECTED'},300,r);
    later(()=>{names.forEach((_,i)=>{const b=$('nv6lane'+i);if(b){b.classList.remove('hint');b.disabled=false}});canPick=true;const m=$('nv6msg');if(m)m.textContent='지금 선택 · 제한시간 약 2초'},760,r);
    later(()=>{if(picked)return;picked=true;log('안전구역 선택 시간 초과','nv6bad');if(!bossHit(1))later(phase1,380,r)},2800,r);
  }

  const ATTACKS=[{name:'GRAVITY SPEAR',speed:2.8,mult:1},{name:'LUNAR RUSH',speed:3.5,mult:1.05},{name:'ARM BREAKER',speed:4.1,mult:1.15}];
  function phase2(){
    const r=run;if(!alive(r))return;r.phase=2;r.round++;
    if(r.round>3){
      log('[ARC TITAN OUTPUT : END]','nv6sys');
      if(r.e.hp/r.e.max>.35)return lose('ARC TITAN이 종료됐지만 노범수의 체력이 너무 많이 남았다.');
      r.phase=3;r.round=0;log('노범수의 최후 공격이 시작된다.','nv6gold');return later(phase3,650,r)
    }
    const a=ATTACKS[r.round-1];let pos=0,dir=1,locked=false;
    shell(`PHASE 2 · DIRECT ASSAULT ${r.round}/3`,`<div style="text-align:center;margin-bottom:8px"><b>${a.name}</b><br><span style="font-size:.75rem;opacity:.75">빨간 표식이 초록 범위에 들어올 때 회피</span></div><div class="nv6track"><div class="nv6safe"></div><div class="nv6perfect"></div><div id="nv6cursor" class="nv6cursor"></div></div><button id="nv6dodge" class="btn btn-super" style="margin-top:8px">💨 회피</button><div class="nv6hint">초록 = 성공 · 가운데 노랑 = PERFECT · 좌↔우 왕복</div>`);
    const d=$('nv6dodge');if(d)d.onclick=()=>{if(!alive(r)||locked)return;locked=true;clearTimers(r);d.disabled=true;const ok=pos>=40&&pos<=60,perfect=pos>=47&&pos<=53;if(ok){log(`${a.name} · ${perfect?'PERFECT DODGE':'회피 성공'}`,perfect?'nv6gold':'nv6good');if(titanCounter(perfect))return}else{log(`${a.name} · 회피 실패`,'nv6bad');if(bossHit(a.mult))return}later(phase2,430,r)};
    const iv=setInterval(()=>{if(!alive(r)||locked)return;pos+=dir*a.speed;if(pos>=99){pos=99;dir=-1}if(pos<=0){pos=0;dir=1}const c=$('nv6cursor');if(c)c.style.left=pos+'%'},20);r.intervals.push(iv);
    later(()=>{if(locked)return;locked=true;clearTimers(r);log(`${a.name} · 회피 타이밍 놓침`,'nv6bad');if(!bossHit(a.mult))later(phase2,430,r)},3200,r);
  }

  function phase3(){
    const r=run;if(!alive(r))return;r.phase=3;r.round++;
    if(r.round>3)return victory('FINAL STRIKE 3회 전부 튕겨내기');
    let size=190,locked=false;
    shell(`PHASE 3 · FINAL PARRY ${r.round}/3`,`<div style="text-align:center;margin-bottom:8px">빨간 충격파가 <b style="color:#5cffad">초록 링</b>과 겹칠 때 튕겨내기</div><div class="nv6parry"><div class="nv6target"></div><div class="nv6core">ARC</div><div id="nv6ring" class="nv6ring"></div></div><button id="nv6parry" class="btn btn-success" style="margin-top:8px">🛡️ 튕겨내기</button><div class="nv6hint">3회 전부 성공하면 노범수의 남은 HP와 관계없이 승리</div>`);
    const p=$('nv6parry');if(p)p.onclick=()=>{if(!alive(r)||locked)return;locked=true;clearTimers(r);p.disabled=true;const perfect=size>=60&&size<=74,ok=size>=50&&size<=88;if(!ok){log(`FINAL STRIKE ${r.round} · 튕겨내기 실패`,'nv6bad');return lose('최후의 공격을 튕겨내지 못했다.')}log(`FINAL STRIKE ${r.round} · ${perfect?'PERFECT PARRY':'PARRY 성공'}`,perfect?'nv6gold':'nv6good');if(perfect){let dm=Math.round(r.p.atk*30*.30);r.e.hp=Math.max(1,r.e.hp-dm);log(`PERFECT 반격 · ${dm.toLocaleString()} 피해`,'nv6good')}later(phase3,430,r)};
    const iv=setInterval(()=>{if(!alive(r)||locked)return;size-=3.1+r.round*.25;const x=$('nv6ring');if(x){x.style.width=size+'px';x.style.height=size+'px'}if(size<=44){locked=true;clearTimers(r);log(`FINAL STRIKE ${r.round} · 직격`,'nv6bad');lose('최후의 공격을 튕겨내지 못했다.')}},22);r.intervals.push(iv);
  }

  function rollTreasure7(){const d=ensureData(),old=d.treasures[7]||0,x=Math.random(),g=x<.10?3:x<.30?2:x<.65?1:0;let first=false;if(g>old){d.treasures[7]=g;first=old===0}return{g,cur:d.treasures[7],first,old}}
  const cloud=()=>typeof useCloud!=='undefined'&&useCloud&&typeof fbDb!=='undefined'&&fbDb&&typeof fbUserId!=='undefined'&&fbUserId;
  async function rewardLp50(){
    const local=ensureData();if(local.lpRewarded[7])return 0;
    if(!cloud()){local.lpRewarded[7]=true;saveData.lp=Math.max(0,+saveData.lp||0)+50;return 50}
    let out=null;const ref=fbDb.collection('profiles').doc(fbUserId);
    await fbDb.runTransaction(async tx=>{const snap=await tx.get(ref);if(!snap.exists)throw Error('PROFILE_NOT_FOUND');const profile=snap.data()||{},base=Object.assign(defaultSaveData(profile.nick||saveData.nick||''),profile.data||{}),fd=ensureData(base),now=ensureData();base.story.stages.future1=Math.max(+base.story.stages.future1||0,7);for(let i=1;i<=8;i++)fd.treasures[i]=Math.max(+fd.treasures[i]||0,+now.treasures[i]||0);let lpv=Math.max(0,+(profile.lp!==undefined?profile.lp:base.lp)||0),ok=false;if(!fd.lpRewarded[7]){fd.lpRewarded[7]=true;lpv+=50;ok=true}base.lp=lpv;base.lr=Math.max(0,+(profile.lr!==undefined?profile.lr:base.lr)||0);tx.set(ref,{nick:base.nick||profile.nick||'',lr:base.lr,lp:base.lp,data:base,updated_at:firebase.firestore.FieldValue.serverTimestamp()},{merge:true});out={base,ok}});
    if(out){saveData=Object.assign(defaultSaveData(out.base.nick||saveData.nick||''),out.base);ensureData().lpRewarded[7]=true}
    return out?.ok?50:0;
  }
  async function finishClear(reason){
    const r=run;if(!r||r.finishing)return;r.finishing=true;r.done=true;clearTimers(r);
    saveData.story??={};saveData.story.stages??={};saveData.story.clearedChapters??={};saveData.story.stages.future1=Math.max(+saveData.story.stages.future1||0,7);
    const drop=rollTreasure7();let gain=0,err=false;
    if(drop.cur===3&&!ensureData().lpRewarded[7])try{gain=await rewardLp50()}catch(e){console.warn('noh v6 LP reward',e);err=true}
    let badge=false;if([1,2,3,4,5,6,7,8].every(i=>ensureData().treasures[i]===3))try{badge=!!unlockBadge('future_treasure_master')}catch(_){}
    try{persistSave()}catch(_){}
    let z=drop.g?`${GN[drop.g]} ${TR[7]} 등장`:'보물 없음';if(drop.cur>drop.g&&drop.g)z+=` · 기존 ${GN[drop.cur]} 유지`;if(drop.first)z+='<br><span class="nv6good">최초 획득 · 미래편 공격력 +15%</span>';if(gain)z+=`<br><b>LP +${gain}</b>`;if(err)z+='<br><span class="nv6bad">LP 지급 실패 · 다음 클리어 때 재시도</span>';if(badge)z+='<br>🏅 시간선의 정복자';
    show(`${top()}<div class="nv6box"><div class="nv6gold">폭주한 노범수를 격파했다.</div><div style="margin-top:8px">${reason||''}</div><div class="nv6good" style="text-align:center;font-size:1.2rem;margin-top:12px">STAGE CLEAR</div></div><div class="nv6box nv6gold" style="text-align:center">💎 ${z}<div style="font-size:.72rem;opacity:.7">없음 35% · 낡은 35% · 평범 20% · 최고급 10%</div></div>${btn('다음 · 4-8 '+TITLES[8],()=>window.openStoryStage(CH,8),'btn btn-success')}${btn('← 스테이지 목록',()=>openStoryChapter(CH),'btn')}`);
    run=null;
  }
  function victory(reason){if(!run||run.finishing)return;run.e.hp=0;finishClear(reason)}

  function startNoh(){
    stop();const stats=window.LRFuture1?.getBossStats?.();const ps=window.LRFuture1?.getPlayerStats?.(7);if(!stats||!ps){alert('미래편 전투 데이터를 불러오지 못했습니다.');return}
    const r={id:++seq,done:false,finishing:false,phase:1,round:0,timeouts:[],intervals:[],guard:treasure()[6]===3?2:0,arcCheck:false,log:[],p:{max:+ps.maxHp||800,hp:+ps.maxHp||800,atk:+ps.attack||350,weapon:ps.weapon?.name||'오버레이 반중력포',revived:false},e:{max:+stats.hp,hp:+stats.hp,atk:+stats.atk,m:+stats.m}};run=r;
    log(`[BOSS MULTIPLIER : ×${r.e.m}]`,'nv6sys');log('노범수 : “……돌아가.”');log('NEURAL LIMITER : FAILURE','nv6bad');
    if(typeof startFutureStageBgm==='function')try{startFutureStageBgm(7)}catch(_){}
    shell('BOSS READY',`<div style="text-align:center;line-height:1.7"><b>폭주한 노범수</b><br>HP ${r.e.max.toLocaleString()} · ATK ${r.e.atk.toLocaleString()}<br><span style="font-size:.75rem;opacity:.72">1단계 구역 회피 → 2단계 직접공격 회피/반격 → 3단계 최후의 튕겨내기</span></div>${btn('⚡ 전투 시작',()=>{if(alive(r)){r.round=0;phase1()}},'btn btn-danger')}`);
  }

  const oldOpen=window.openStoryStage;
  window.openStoryStage=function(ch,n){
    if(ch!==CH||+n!==STAGE)return oldOpen?.apply(this,arguments);
    if(typeof storyStageUnlocked==='function'&&!storyStageUnlocked(CH,STAGE))return alert('앞 스테이지를 먼저 클리어하세요.');
    startNoh();
  };
  window.LRNohBossV6={start:startNoh,stop};
})();

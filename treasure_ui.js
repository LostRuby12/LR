/* Lost Ruby - Treasure collection UI */
(() => {
  const STAGES = [
    { no:1, title:'시간의 역전', treasure:'시간칩', effect:'최고급: 미래 I 최대 HP +5%', boss:true },
    { no:2, title:'오버드라이브', treasure:'오버드라이브 엔진', effect:'노범수 배율 감소 대상', boss:true },
    { no:3, title:'콘스탄티노폴리스', treasure:'시간 코어', effect:'노범수 배율 감소 대상', boss:true },
    { no:4, title:'아크 지구', treasure:'아크 셀', effect:'최고급: 미래 I 최대 HP +10%', boss:true },
    { no:5, title:'예루살렘', treasure:'성지순례', effect:'최고급: 사망 시 1회 HP 30%로 부활', boss:true },
    { no:6, title:'아틀란티스', treasure:'심해 결정체', effect:'최고급: 노범수전 첫 2회 공격 완전 방어', boss:true },
    { no:7, title:'달', treasure:'월석 파편', effect:'최고급 최초 획득: LP +50', boss:false },
    { no:8, title:'타임오버', treasure:'시간선의 초월', effect:'최고급 최초 획득: LP +100', boss:false }
  ];
  const GRADES=['없음','낡은','평범','최고급'];

  function futureData(){
    try {
      const story=saveData && saveData.story;
      const d=story && story.future1Data;
      const t=d && d.treasures;
      return t && typeof t==='object' ? t : {};
    } catch(_) { return {}; }
  }
  function grade(no){return Math.max(0,Math.min(3,Number(futureData()[no])||0));}
  function count(){let n=0;for(let i=1;i<=8;i++)if(grade(i)>0)n++;return n;}
  function bestCount(){let n=0;for(let i=1;i<=8;i++)if(grade(i)===3)n++;return n;}
  function bossMult(){
    const vals=[1,2,3,4,5,6].map(grade);
    if(vals.every(v=>v>=3))return 1;
    if(vals.every(v=>v>=2))return 5;
    if(vals.every(v=>v>=1))return 10;
    return 100;
  }
  function gradeStyle(g){
    if(g===3)return 'color:#ffe16b;border-color:#d2ac35;background:rgba(255,215,0,.12)';
    if(g===2)return 'color:#b9dcff;border-color:#5987b4;background:rgba(90,145,200,.12)';
    if(g===1)return 'color:#d6a675;border-color:#8a6745;background:rgba(160,105,55,.10)';
    return 'color:#8f98ab;border-color:#3f4659;background:rgba(255,255,255,.03)';
  }

  function ensureScreen(){
    const app=document.getElementById('app'); if(!app)return null;
    let el=document.getElementById('treasure-screen');
    if(!el){el=document.createElement('div');el.id='treasure-screen';el.className='screen';app.appendChild(el);}
    if(!document.getElementById('treasure-ui-style')){
      const s=document.createElement('style');s.id='treasure-ui-style';s.textContent=`
        .tr-summary{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px;margin:12px 0 15px}.tr-sum{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.10);border-radius:13px;padding:11px;text-align:center}.tr-sum b{display:block;color:#ffd700;font-size:1.05rem}.tr-item{background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.10);border-radius:14px;padding:13px;margin:9px 0}.tr-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.tr-name{font-weight:900;color:#fff}.tr-stage{font-size:.72rem;opacity:.62;margin-top:2px}.tr-grade{border:1px solid;border-radius:999px;padding:5px 9px;font-size:.72rem;font-weight:900;white-space:nowrap}.tr-effect{font-size:.78rem;line-height:1.5;opacity:.82;margin-top:9px}.tr-global{background:linear-gradient(135deg,rgba(79,54,150,.35),rgba(25,79,110,.35));border:1px solid rgba(150,155,255,.22);border-radius:14px;padding:13px;margin:11px 0;font-size:.8rem;line-height:1.65}`;document.head.appendChild(s);
    }
    return el;
  }

  function render(){
    const el=ensureScreen(); if(!el)return;
    const c=count(),bc=bestCount(),m=bossMult();
    let items='';
    STAGES.forEach(s=>{const g=grade(s.no);items+=`<div class="tr-item"><div class="tr-head"><div><div class="tr-name">💎 ${s.treasure}</div><div class="tr-stage">4-${s.no} ${s.title}</div></div><div class="tr-grade" style="${gradeStyle(g)}">${GRADES[g]}</div></div><div class="tr-effect">${s.effect}${s.boss?' · 4-1~4-6 배율 판정 포함':''}</div></div>`;});
    el.innerHTML=`<h2 style="text-align:center;">💎 보물</h2><p style="text-align:center;opacity:.7;font-size:.82rem;margin-bottom:8px;">미래 I 보물 도감</p>
      <div class="tr-summary"><div class="tr-sum"><span>획득 보물</span><b>${c}/8</b></div><div class="tr-sum"><span>최고급</span><b>${bc}/8</b></div><div class="tr-sum"><span>미래편 공격력</span><b>+${c*15}%</b></div><div class="tr-sum"><span>노범수</span><b>${m}배율</b></div></div>
      <div class="tr-global"><b style="color:#ffd700">보물 공통 규칙</b><br>각 스테이지 보물을 <b>처음 획득할 때마다 미래 I 공격력 +15%</b>.<br>노범수 배율은 <b>4-1~4-6 보물만</b> 사용합니다.<br>드롭률: 없음 35% · 낡은 35% · 평범 20% · 최고급 10% · 천장 없음.</div>
      ${items}<div style="flex:1;min-height:30px"></div><button class="btn" onclick="showScreen('etc-screen')">← 기타로</button>`;
  }

  function openTreasure(){if(typeof requireLogin==='function'&&!requireLogin())return;render();if(typeof showScreen==='function')showScreen('treasure-screen');}
  function patchEtc(){
    const etc=document.getElementById('etc-screen');if(!etc)return;
    const grid=etc.querySelector('div[style*="grid-template-columns"]');if(!grid||document.getElementById('etc-treasure-btn'))return;
    const b=document.createElement('button');b.id='etc-treasure-btn';b.className='btn';b.style.cssText='margin:0;min-height:74px;padding:12px 8px;font-size:.98rem;background:linear-gradient(135deg,#8a6a18,#c49b2c);';b.innerHTML='💎<br>보물';b.onclick=openTreasure;grid.appendChild(b);
  }
  window.openTreasure=openTreasure;
  patchEtc();
})();

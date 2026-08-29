/* Lost Ruby - Shop UI v2 */
(() => {
  let activeCategory='all';
  const META={
    lr_to_lp_100:{cat:'exchange',icon:'🔄',tag:'교환'},
    lr_to_lp_1000:{cat:'exchange',icon:'🔄',tag:'교환'},
    lr_to_lp_10000:{cat:'exchange',icon:'🔄',tag:'교환'},
    gold_nick:{cat:'style',icon:'✨',tag:'영구'},
    nick_change:{cat:'style',icon:'✏️',tag:'소모'},
    unlock_priest:{cat:'class',icon:'⛪',tag:'직업'},
    unlock_archer:{cat:'class',icon:'🏹',tag:'직업'},
    unlock_as:{cat:'class',icon:'🗡️',tag:'직업'}
  };
  const CATS=[['all','전체'],['exchange','교환소'],['style','꾸미기'],['class','직업']];

  function owned(it){
    try{
      if(it.id==='gold_nick')return !!saveData.shop.goldNick;
      if(it.id==='unlock_as')return !!saveData.shop.assassin;
      if(it.id==='unlock_priest')return !!saveData.shop.priest;
      if(it.id==='unlock_archer')return !!saveData.shop.archer;
    }catch(_){}
    return false;
  }
  function currencyText(it){return `${Number(it.price||0).toLocaleString()} ${it.currency==='lp'?'LP':'LR'}`;}
  function ensureStyle(){
    if(document.getElementById('shop-v2-style'))return;
    const s=document.createElement('style');s.id='shop-v2-style';s.textContent=`
      .sv2-wallet{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin:8px 0 13px}.sv2-money{border-radius:13px;padding:11px;text-align:center;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1)}.sv2-money span{display:block;font-size:.72rem;opacity:.65}.sv2-money b{font-size:1.12rem;color:#ffd700}.sv2-tabs{display:flex;gap:6px;overflow-x:auto;padding:2px 0 8px}.sv2-tab{width:auto!important;min-width:72px!important;margin:0!important;padding:8px 11px!important;font-size:.78rem!important;white-space:nowrap;background:#34384e!important;box-shadow:none!important}.sv2-tab.on{background:linear-gradient(135deg,#6a36dd,#a33de1)!important;border:1px solid rgba(255,255,255,.25)}.sv2-card{display:flex;gap:11px;align-items:flex-start;background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.10);border-radius:15px;padding:13px;margin:9px 0}.sv2-icon{width:44px;height:44px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:rgba(255,255,255,.07);font-size:1.45rem;flex:0 0 auto}.sv2-body{min-width:0;flex:1}.sv2-title{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.sv2-name{font-weight:900;color:#fff}.sv2-tag{font-size:.64rem;padding:3px 6px;border-radius:999px;background:rgba(255,215,0,.12);color:#ffe16b;border:1px solid rgba(255,215,0,.2)}.sv2-desc{font-size:.76rem;line-height:1.5;opacity:.72;margin:5px 0 9px}.sv2-buy{display:flex;gap:8px;align-items:center}.sv2-price{font-size:.78rem;font-weight:900;color:#ffd700;white-space:nowrap}.sv2-buy .btn{margin:0;padding:8px 10px;font-size:.78rem;min-height:0}.sv2-note{font-size:.7rem;opacity:.58;text-align:center;margin:8px 0 2px;line-height:1.45}`;document.head.appendChild(s);
  }
  function render(){
    if(typeof ensureShopSave==='function')ensureShopSave();
    const screen=document.getElementById('shop-screen');if(!screen)return;
    ensureStyle();
    const list=(typeof SHOP_ITEMS!=='undefined'?SHOP_ITEMS:[]).filter(it=>activeCategory==='all'||(META[it.id]?.cat===activeCategory));
    const tabs=CATS.map(([id,name])=>`<button class="btn sv2-tab ${activeCategory===id?'on':''}" data-cat="${id}">${name}</button>`).join('');
    const cards=list.map(it=>{
      const m=META[it.id]||{cat:'all',icon:'🛒',tag:it.type||'상품'};const o=owned(it);
      const disabled=o||(it.id==='nick_change'&&typeof useCloud!=='undefined'&&useCloud);
      const label=o?'보유 중':(it.id==='nick_change'&&typeof useCloud!=='undefined'&&useCloud?'서버계정 사용불가':(it.type==='exchange'?'교환':'구매'));
      return `<div class="sv2-card"><div class="sv2-icon">${m.icon}</div><div class="sv2-body"><div class="sv2-title"><span class="sv2-name">${it.name}</span><span class="sv2-tag">${m.tag}</span></div><div class="sv2-desc">${it.desc||''}</div><div class="sv2-buy"><span class="sv2-price">${currencyText(it)}</span><button class="btn ${o?'':'btn-gold'}" data-buy="${it.id}" ${disabled?'disabled':''}>${label}</button></div></div></div>`;
    }).join('');
    screen.innerHTML=`<h2 style="text-align:center;">🛒 상점</h2><div class="sv2-wallet"><div class="sv2-money"><span>LR</span><b>${Math.max(0,Number(saveData.lr)||0).toLocaleString()}</b></div><div class="sv2-money"><span>LP</span><b>${Math.max(0,Number(saveData.lp)||0).toLocaleString()}</b></div></div><div class="sv2-tabs">${tabs}</div><div id="shop-list" style="overflow-y:auto;max-height:62vh">${cards||'<div style="text-align:center;opacity:.6;padding:30px">상품 없음</div>'}</div><div class="sv2-note">직업·영구 상품 가격은 기존 밸런스를 유지했습니다. 교환 비율도 기존과 동일합니다.</div><button class="btn" style="margin-top:10px" onclick="showScreen('select-screen')">← 메인으로</button>`;
    screen.querySelectorAll('[data-cat]').forEach(b=>b.onclick=()=>{activeCategory=b.dataset.cat;render();});
    screen.querySelectorAll('[data-buy]').forEach(b=>b.onclick=()=>{if(typeof buyShopItem==='function')buyShopItem(b.dataset.buy);});
  }
  try{renderShop=render;}catch(_){window.renderShop=render;}
  const open=function(){if(typeof requireLogin==='function'&&!requireLogin())return;if(typeof ensureShopSave==='function')ensureShopSave();render();if(typeof showScreen==='function')showScreen('shop-screen');};
  try{openShop=open;}catch(_){window.openShop=open;}
})();

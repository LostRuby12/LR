/* Lost Ruby - Economy guard v1
 * Normal gameplay hardening: currency normalization + Firestore transaction based shop purchases.
 * NOTE: full anti-cheat still requires restrictive Firestore rules / trusted backend.
 */
(() => {
  const MAX_CURRENCY = Number.MAX_SAFE_INTEGER;
  const CATALOG = Object.freeze({
    lr_to_lp_100:Object.freeze({name:'LR → LP 교환',cost:100,currency:'lr',lpGain:10,type:'exchange'}),
    lr_to_lp_1000:Object.freeze({name:'LR → LP 교환',cost:1000,currency:'lr',lpGain:100,type:'exchange'}),
    lr_to_lp_10000:Object.freeze({name:'LR → LP 교환',cost:10000,currency:'lr',lpGain:1000,type:'exchange'}),
    gold_nick:Object.freeze({name:'골드 닉네임',cost:150,currency:'lp',type:'perm',flag:'goldNick'}),
    nick_change:Object.freeze({name:'닉네임 변경권',cost:100,currency:'lp',type:'consumable'}),
    unlock_priest:Object.freeze({name:'성직자 해금',cost:500,currency:'lp',type:'unlock',flag:'priest'}),
    unlock_archer:Object.freeze({name:'궁수 해금',cost:500,currency:'lp',type:'unlock',flag:'archer'}),
    unlock_as:Object.freeze({name:'암살자 해금',cost:6767,currency:'lp',type:'unlock',flag:'assassin'})
  });

  function safeCurrency(v){v=Number(v);if(!Number.isFinite(v))return 0;return Math.max(0,Math.min(MAX_CURRENCY,Math.floor(v)));}
  function sanitize(target){
    if(!target||typeof target!=='object')return target;
    target.lr=safeCurrency(target.lr);target.lp=safeCurrency(target.lp);
    if(!target.shop||typeof target.shop!=='object')target.shop={goldNick:false,assassin:false,priest:false,archer:false};
    target.shop.goldNick=!!target.shop.goldNick;target.shop.assassin=!!target.shop.assassin;target.shop.priest=!!target.shop.priest;target.shop.archer=!!target.shop.archer;
    return target;
  }
  function owned(data,item){return !!(item.flag&&data.shop&&data.shop[item.flag]);}
  function pushAudit(data,row){
    if(!Array.isArray(data.economyAudit))data.economyAudit=[];
    data.economyAudit.push(row);
    if(data.economyAudit.length>30)data.economyAudit=data.economyAudit.slice(-30);
  }

  const originalPersist = typeof persistSave==='function' ? persistSave : null;
  if(originalPersist){
    persistSave=function(){sanitize(saveData);return originalPersist.apply(this,arguments);};
  }

  const originalBuy = typeof buyShopItem==='function' ? buyShopItem : null;
  async function cloudBuy(id){
    const item=CATALOG[id];if(!item)return;
    if(id==='nick_change'){alert('서버 계정에서는 닉네임 변경권을 현재 사용할 수 없습니다.');return;}
    sanitize(saveData);
    if(owned(saveData,item)){alert(item.type==='unlock'?'이미 해금됨':'이미 보유 중');return;}
    if(item.currency==='lr'&&saveData.lr<item.cost){alert('LR이 부족합니다!');return;}
    if(item.currency==='lp'&&saveData.lp<item.cost){alert('LP가 부족합니다!');return;}
    if(!fbDb||!fbUserId)throw new Error('클라우드 계정 연결이 없습니다.');

    const ref=fbDb.collection('profiles').doc(fbUserId);let updated=null;
    await fbDb.runTransaction(async tx=>{
      const snap=await tx.get(ref);if(!snap.exists)throw new Error('프로필을 찾을 수 없습니다.');
      const profile=snap.data()||{};
      const base=Object.assign(defaultSaveData(profile.nick||saveData.nick||''),profile.data||{});
      sanitize(base);
      base.lr=safeCurrency(profile.lr!==undefined?profile.lr:base.lr);
      base.lp=safeCurrency(profile.lp!==undefined?profile.lp:base.lp);
      if(owned(base,item))throw new Error('ALREADY_OWNED');
      let lrDelta=0,lpDelta=0;
      if(item.type==='exchange'){
        if(base.lr<item.cost)throw new Error('NOT_ENOUGH_LR');
        base.lr-=item.cost;base.lp=safeCurrency(base.lp+item.lpGain);lrDelta=-item.cost;lpDelta=item.lpGain;
      }else{
        if(item.currency==='lr'){
          if(base.lr<item.cost)throw new Error('NOT_ENOUGH_LR');base.lr-=item.cost;lrDelta=-item.cost;
        }else{
          if(base.lp<item.cost)throw new Error('NOT_ENOUGH_LP');base.lp-=item.cost;lpDelta=-item.cost;
        }
        if(item.flag){if(!base.shop)base.shop={};base.shop[item.flag]=true;}
      }
      pushAudit(base,{kind:'shop',item:id,lrDelta,lpDelta,at:new Date().toISOString()});
      sanitize(base);
      tx.set(ref,{nick:base.nick||profile.nick||'',lr:base.lr,lp:base.lp,data:base,updated_at:firebase.firestore.FieldValue.serverTimestamp()},{merge:true});
      updated=base;
    });
    if(updated){
      saveData=Object.assign(defaultSaveData(updated.nick||saveData.nick||''),updated);sanitize(saveData);
      try{if(typeof STORAGE_KEY!=='undefined')localStorage.setItem(STORAGE_KEY,JSON.stringify(saveData));}catch(_){}
      try{if(typeof normalizeMissions==='function')normalizeMissions();}catch(_){}
      try{if(typeof upsertRankBoard==='function')upsertRankBoard(saveData.nick||'나',saveData.lr);}catch(_){}
      try{if(typeof updateRecordSummary==='function')updateRecordSummary();}catch(_){}
      if(typeof renderShop==='function')renderShop();
      alert(item.type==='exchange'?`교환 완료! +${item.lpGain.toLocaleString()} LP`:`${item.name} 구매 완료!`);
    }
  }

  if(originalBuy){
    buyShopItem=async function(id){
      sanitize(saveData);
      try{
        if(typeof useCloud!=='undefined'&&useCloud&&typeof fbDb!=='undefined'&&fbDb&&typeof fbUserId!=='undefined'&&fbUserId)return await cloudBuy(id);
      }catch(e){
        const key=String(e&&e.message||e);
        if(key.includes('ALREADY_OWNED'))alert('이미 보유 중입니다.');
        else if(key.includes('NOT_ENOUGH_LR'))alert('서버 기준 LR이 부족합니다.');
        else if(key.includes('NOT_ENOUGH_LP'))alert('서버 기준 LP가 부족합니다.');
        else{console.warn('secure shop transaction failed',e);alert('상점 서버 처리에 실패했습니다. 잠시 후 다시 시도하세요.');}
        try{if(typeof reloadRewardData==='function')await reloadRewardData();}catch(_){}
        if(typeof renderShop==='function')renderShop();return;
      }
      return originalBuy.apply(this,arguments);
    };
  }

  window.LREconomyGuard={sanitize:()=>sanitize(saveData),mode:()=>typeof useCloud!=='undefined'&&useCloud?'cloud-transaction':'local'};
})();

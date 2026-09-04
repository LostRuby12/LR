/* Lost Ruby - private reward codes and hidden badge */
(()=>{
  const BADGE_ID='hd_noh_secret';
  const BADGE_DEF={id:BADGE_ID,icon:'🌙',name:'연딸은 위험해',desc:'미래 I 클리어 후 비밀 코드를 입력',cat:'hidden'};
  try{if(typeof BADGE_DEFS!=='undefined'&&!BADGE_DEFS.some(x=>x.id===BADGE_ID))BADGE_DEFS.push(BADGE_DEF)}catch(e){console.warn('special badge register failed',e)}
  const $=id=>document.getElementById(id);
  const oldRedeem=window.redeemCode;
  const cloudReady=()=>typeof useCloud!=='undefined'&&useCloud&&typeof fbDb!=='undefined'&&fbDb&&typeof fbUserId!=='undefined'&&fbUserId;
  function msg(t,ok=false){if(typeof setCodeMessage==='function')setCodeMessage(t,ok);else{const e=$('redeem-code-msg');if(e){e.textContent=t;e.style.color=ok?'#75ffad':'#ff9a9a'}}}
  function futureDone(data=saveData){return !!(data?.story?.clearedChapters?.future1||(+data?.story?.stages?.future1||0)>=8)}
  function normalizeBase(profile){const base=Object.assign(defaultSaveData(profile?.nick||saveData.nick||''),profile?.data||saveData||{});base.badges=Object.assign({},base.badges||{});base.redeemedCodes=Object.assign({},base.redeemedCodes||{});base.missions=Object.assign(defaultSaveData('').missions,base.missions||{});base.missions.badgePaid=Object.assign({},base.missions.badgePaid||{});return base}
  async function code3301(input){
    if(!cloudReady()){msg('로그인 정보를 확인한 뒤 다시 시도하세요.');return}
    const ref=fbDb.collection('profiles').doc(fbUserId);let out=null;
    await fbDb.runTransaction(async tx=>{const snap=await tx.get(ref);if(!snap.exists)throw Error('PROFILE_NOT_FOUND');const profile=snap.data()||{},base=normalizeBase(profile),id='secret_3301_lr3000';if(base.redeemedCodes[id])throw Error('CODE_ALREADY_USED');base.redeemedCodes[id]=new Date().toISOString();base.lr=Math.max(0,+(profile.lr!==undefined?profile.lr:base.lr)||0)+3000;base.lp=Math.max(0,+(profile.lp!==undefined?profile.lp:base.lp)||0);tx.set(ref,{nick:base.nick||profile.nick||'',lr:base.lr,lp:base.lp,data:base,updated_at:firebase.firestore.FieldValue.serverTimestamp()},{merge:true});out=base});
    saveData=Object.assign(defaultSaveData(out.nick||saveData.nick||''),out);try{upsertRankBoard(saveData.nick||'나',saveData.lr||0)}catch(_){}try{updateRecordSummary()}catch(_){}if(input)input.value='';msg('코드 사용 완료! +3,000 LR',true);
  }
  async function secretBadge(input){
    if(!cloudReady()){msg('로그인 정보를 확인한 뒤 다시 시도하세요.');return}
    if(!futureDone()){msg('미래 I을 클리어한 뒤 사용할 수 있는 코드입니다.');return}
    const ref=fbDb.collection('profiles').doc(fbUserId);let out=null,already=false;
    await fbDb.runTransaction(async tx=>{const snap=await tx.get(ref);if(!snap.exists)throw Error('PROFILE_NOT_FOUND');const profile=snap.data()||{},base=normalizeBase(profile);if(!futureDone(base))throw Error('FUTURE_NOT_CLEARED');if(base.badges[BADGE_ID]){already=true;out=base;return}base.badges[BADGE_ID]=Date.now();if(!base.missions.badgePaid[BADGE_ID]){base.missions.badgePaid[BADGE_ID]=true;base.lr=Math.max(0,+(profile.lr!==undefined?profile.lr:base.lr)||0)+10}else base.lr=Math.max(0,+(profile.lr!==undefined?profile.lr:base.lr)||0);base.lp=Math.max(0,+(profile.lp!==undefined?profile.lp:base.lp)||0);tx.set(ref,{nick:base.nick||profile.nick||'',lr:base.lr,lp:base.lp,data:base,updated_at:firebase.firestore.FieldValue.serverTimestamp()},{merge:true});out=base});
    if(out)saveData=Object.assign(defaultSaveData(out.nick||saveData.nick||''),out);try{updateRecordSummary()}catch(_){}if(input)input.value='';if(already){msg('이미 획득한 히든 벳지입니다.');return}try{if(typeof pendingNewBadges!=='undefined')pendingNewBadges.push(BADGE_DEF)}catch(_){}msg('히든 벳지 획득! 연딸은 위험해 · 벳지 보상 +10 LR',true);
  }
  window.redeemCode=async function(){
    if(typeof requireLogin==='function'&&!requireLogin())return;
    const input=$('redeem-code-input'),btn=$('redeem-code-btn'),raw=((input&&input.value)||'').trim();
    if(raw!=='3301'&&raw!=='폭딸한 노범수')return oldRedeem?.apply(this,arguments);
    if(!raw){msg('코드를 입력하세요.');return}
    if(btn)btn.disabled=true;msg('코드 확인 중...');
    try{if(raw==='3301')await code3301(input);else await secretBadge(input)}catch(e){if(e?.message==='CODE_ALREADY_USED')msg('이미 사용한 코드입니다.');else if(e?.message==='FUTURE_NOT_CLEARED')msg('미래 I을 클리어한 뒤 사용할 수 있는 코드입니다.');else{console.warn('special code failed',e);msg('코드 지급 중 오류가 발생했습니다. 잠시 후 다시 시도하세요.')}}finally{if(btn)btn.disabled=false}
  };
})();

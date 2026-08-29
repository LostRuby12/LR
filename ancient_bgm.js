/* Lost Ruby - story chapter menu BGM (Ancient I / Future I) */
(() => {
  const SETTINGS_KEY='lr_audio_settings_v1';
  const TRACKS=Object.freeze({
    ancient1:'kyaPf_IUxwA',
    future1:'26Pw22ovfNs'
  });
  let activeChapter=null,frame=null;

  function readSettings(){
    try{const s=JSON.parse(localStorage.getItem(SETTINGS_KEY)||'{}');return{on:s.musicEnabled!==false,vol:Math.max(0,Math.min(100,Number(s.musicVolume??38)))}}catch(_){return{on:true,vol:38}}
  }
  function command(func,args=[]){
    if(!frame||!frame.contentWindow)return;
    try{frame.contentWindow.postMessage(JSON.stringify({event:'command',func,args}),'https://www.youtube.com')}catch(_){}
  }
  function destroy(){if(frame){try{frame.remove()}catch(_){}frame=null}}
  function makePlayer(chapter){
    const id=TRACKS[chapter];if(!id)return null;
    if(frame&&frame.dataset.chapter===chapter&&document.body.contains(frame))return frame;
    destroy();frame=document.createElement('iframe');frame.id='lr-story-menu-bgm';frame.dataset.chapter=chapter;frame.title=`${chapter} BGM`;frame.allow='autoplay; encrypted-media';frame.setAttribute('allowfullscreen','false');
    frame.style.cssText='position:fixed;width:1px;height:1px;left:-9999px;top:-9999px;border:0;opacity:.01;pointer-events:none;';
    const origin=encodeURIComponent(location.origin);
    frame.src=`https://www.youtube.com/embed/${id}?autoplay=1&loop=1&playlist=${id}&controls=0&rel=0&playsinline=1&enablejsapi=1&origin=${origin}`;
    document.body.appendChild(frame);frame.addEventListener('load',()=>{if(activeChapter===chapter)apply()});return frame;
  }
  function apply(){const s=readSettings();if(!s.on){command('pauseVideo');return}command('unMute');command('setVolume',[s.vol]);if(activeChapter)command('playVideo')}
  function start(chapter){if(!TRACKS[chapter]){stop();return}try{if(typeof storyChapterUnlocked==='function'&&!storyChapterUnlocked(chapter)){stop();return}}catch(_){}activeChapter=chapter;const s=readSettings();if(!s.on)return;makePlayer(chapter);apply()}
  function stop(){activeChapter=null;command('pauseVideo');destroy()}

  window.startStoryMenuBgm=start;window.stopStoryMenuBgm=stop;
  window.startAncientBgm=()=>start('ancient1');window.stopAncientBgm=stop;
  window.startFutureMenuBgm=()=>start('future1');window.applyAncientBgmSettings=apply;

  const prevOpenChapter=window.openStoryChapter;
  if(typeof prevOpenChapter==='function')window.openStoryChapter=function(id){if(TRACKS[id])start(id);else stop();return prevOpenChapter.apply(this,arguments)};
  const prevOpenStage=window.openStoryStage;
  if(typeof prevOpenStage==='function')window.openStoryStage=function(){stop();return prevOpenStage.apply(this,arguments)};
  const prevRenderStory=window.renderStory;
  if(typeof prevRenderStory==='function')window.renderStory=function(){stop();return prevRenderStory.apply(this,arguments)};
  const prevShowScreen=window.showScreen;
  if(typeof prevShowScreen==='function')window.showScreen=function(id){if(activeChapter&&id!=='story-screen')stop();return prevShowScreen.apply(this,arguments)};

  window.addEventListener('lr-audio-settings-changed',()=>{const s=readSettings();if(!s.on){command('pauseVideo');return}if(activeChapter){makePlayer(activeChapter);apply()}});
  document.addEventListener('visibilitychange',()=>{if(!activeChapter)return;if(document.hidden||!readSettings().on)command('pauseVideo');else apply()});
})();

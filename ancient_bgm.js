/* Lost Ruby - Ancient I stage-list BGM */
(() => {
  const VIDEO_ID = 'kyaPf_IUxwA';
  let ancientActive = false;
  let frame = null;

  function playerCommand(func) {
    if (!frame || !frame.contentWindow) return;
    try {
      frame.contentWindow.postMessage(JSON.stringify({
        event: 'command',
        func,
        args: []
      }), 'https://www.youtube.com');
    } catch (_) {}
  }

  function makePlayer() {
    if (frame && document.body.contains(frame)) return frame;
    frame = document.createElement('iframe');
    frame.id = 'lr-ancient-bgm-player';
    frame.title = 'Ancient I BGM';
    frame.allow = 'autoplay; encrypted-media';
    frame.setAttribute('allowfullscreen', 'false');
    frame.style.cssText = 'position:fixed;width:1px;height:1px;left:-9999px;top:-9999px;border:0;opacity:.01;pointer-events:none;';
    const origin = encodeURIComponent(location.origin);
    frame.src = `https://www.youtube.com/embed/${VIDEO_ID}?autoplay=1&loop=1&playlist=${VIDEO_ID}&controls=0&rel=0&playsinline=1&enablejsapi=1&origin=${origin}`;
    document.body.appendChild(frame);
    frame.addEventListener('load', () => {
      if (ancientActive) {
        playerCommand('unMute');
        playerCommand('setVolume');
        try {
          frame.contentWindow.postMessage(JSON.stringify({event:'command',func:'setVolume',args:[38]}),'https://www.youtube.com');
        } catch (_) {}
        playerCommand('playVideo');
      }
    });
    return frame;
  }

  function startAncientBgm() {
    ancientActive = true;
    const p = makePlayer();
    if (p) {
      playerCommand('unMute');
      try {
        p.contentWindow.postMessage(JSON.stringify({event:'command',func:'setVolume',args:[38]}),'https://www.youtube.com');
      } catch (_) {}
      playerCommand('playVideo');
    }
  }

  function stopAncientBgm() {
    ancientActive = false;
    playerCommand('pauseVideo');
    if (frame) {
      try { frame.remove(); } catch (_) {}
      frame = null;
    }
  }

  window.startAncientBgm = startAncientBgm;
  window.stopAncientBgm = stopAncientBgm;

  const previousOpenStoryChapter = window.openStoryChapter;
  if (typeof previousOpenStoryChapter === 'function') {
    window.openStoryChapter = function(id) {
      if (id === 'ancient1') startAncientBgm();
      else stopAncientBgm();
      return previousOpenStoryChapter.apply(this, arguments);
    };
  }

  const previousOpenStoryStage = window.openStoryStage;
  if (typeof previousOpenStoryStage === 'function') {
    window.openStoryStage = function(chapterId, stageNo) {
      // 고대 I 스테이지 선택 화면 전용 BGM. 스테이지 진입 시 정지.
      stopAncientBgm();
      return previousOpenStoryStage.apply(this, arguments);
    };
  }

  const previousRenderStory = window.renderStory;
  if (typeof previousRenderStory === 'function') {
    window.renderStory = function() {
      stopAncientBgm();
      return previousRenderStory.apply(this, arguments);
    };
  }

  const previousShowScreen = window.showScreen;
  if (typeof previousShowScreen === 'function') {
    window.showScreen = function(id) {
      if (ancientActive && id !== 'story-screen') stopAncientBgm();
      return previousShowScreen.apply(this, arguments);
    };
  }

  document.addEventListener('visibilitychange', () => {
    if (!ancientActive) return;
    if (document.hidden) playerCommand('pauseVideo');
    else playerCommand('playVideo');
  });
})();

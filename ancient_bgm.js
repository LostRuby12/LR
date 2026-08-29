/* Lost Ruby - Ancient I stage-list BGM */
(() => {
  const VIDEO_ID = 'kyaPf_IUxwA';
  const SETTINGS_KEY = 'lr_audio_settings_v1';
  let ancientActive = false;
  let frame = null;

  function readAudioSettings() {
    try {
      const s = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}');
      return {
        musicEnabled: s.musicEnabled !== false,
        musicVolume: Math.max(0, Math.min(100, Number(s.musicVolume ?? 38)))
      };
    } catch (_) {
      return { musicEnabled: true, musicVolume: 38 };
    }
  }

  function command(func, args = []) {
    if (!frame || !frame.contentWindow) return;
    try {
      frame.contentWindow.postMessage(JSON.stringify({ event:'command', func, args }), 'https://www.youtube.com');
    } catch (_) {}
  }

  function applyVolume() {
    const s = readAudioSettings();
    if (!s.musicEnabled) {
      command('pauseVideo');
      return;
    }
    command('unMute');
    command('setVolume', [s.musicVolume]);
    if (ancientActive) command('playVideo');
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
      if (ancientActive) applyVolume();
    });
    return frame;
  }

  function startAncientBgm() {
    ancientActive = true;
    const s = readAudioSettings();
    if (!s.musicEnabled) return;
    makePlayer();
    applyVolume();
  }

  function stopAncientBgm() {
    ancientActive = false;
    command('pauseVideo');
    if (frame) {
      try { frame.remove(); } catch (_) {}
      frame = null;
    }
  }

  window.startAncientBgm = startAncientBgm;
  window.stopAncientBgm = stopAncientBgm;
  window.applyAncientBgmSettings = applyVolume;

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

  window.addEventListener('lr-audio-settings-changed', () => {
    const s = readAudioSettings();
    if (!s.musicEnabled) {
      command('pauseVideo');
      return;
    }
    if (ancientActive) {
      makePlayer();
      applyVolume();
    }
  });

  document.addEventListener('visibilitychange', () => {
    if (!ancientActive) return;
    const s = readAudioSettings();
    if (document.hidden || !s.musicEnabled) command('pauseVideo');
    else applyVolume();
  });
})();

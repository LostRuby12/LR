/* Lost Ruby - Settings UI */
(() => {
  const KEY = 'lr_audio_settings_v1';
  const DEFAULTS = Object.freeze({ musicEnabled: true, musicVolume: 38, sfxVolume: 70 });

  function clamp(v, min, max) {
    v = Number(v);
    return Number.isFinite(v) ? Math.max(min, Math.min(max, v)) : min;
  }

  function loadSettings() {
    try {
      const raw = JSON.parse(localStorage.getItem(KEY) || '{}');
      return {
        musicEnabled: raw.musicEnabled !== false,
        musicVolume: clamp(raw.musicVolume ?? DEFAULTS.musicVolume, 0, 100),
        sfxVolume: clamp(raw.sfxVolume ?? DEFAULTS.sfxVolume, 0, 100)
      };
    } catch (_) {
      return { ...DEFAULTS };
    }
  }

  let settings = loadSettings();

  function saveSettings() {
    try { localStorage.setItem(KEY, JSON.stringify(settings)); } catch (_) {}
    window.LRAudioSettings = { ...settings };
    window.dispatchEvent(new CustomEvent('lr-audio-settings-changed', { detail: { ...settings } }));
  }

  function ensureSettingsScreen() {
    const app = document.getElementById('app');
    if (!app) return null;
    let screen = document.getElementById('settings-screen');
    if (screen) return screen;

    screen = document.createElement('div');
    screen.id = 'settings-screen';
    screen.className = 'screen';
    screen.innerHTML = `
      <h2 style="text-align:center;">⚙️ 설정</h2>
      <div style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.10);border-radius:16px;padding:16px;margin-top:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px;">
          <div>
            <div style="font-weight:900;font-size:1.05rem;">🎵 음악</div>
            <div style="opacity:.68;font-size:.78rem;margin-top:3px;">스토리 BGM 켜기 / 끄기</div>
          </div>
          <button id="settings-music-toggle" class="btn" style="width:auto;min-width:92px;margin:0;padding:10px 14px;"></button>
        </div>

        <label for="settings-music-volume" style="font-weight:800;display:block;">BGM 볼륨 <span id="settings-music-value"></span></label>
        <input id="settings-music-volume" type="range" min="0" max="100" step="1" style="width:100%;margin:9px 0 20px;">

        <label for="settings-sfx-volume" style="font-weight:800;display:block;">효과음 볼륨 <span id="settings-sfx-value"></span></label>
        <input id="settings-sfx-volume" type="range" min="0" max="100" step="1" style="width:100%;margin:9px 0 4px;">
        <div style="opacity:.62;font-size:.75rem;line-height:1.5;">효과음 설정은 이후 추가되는 전투·UI 효과음에도 공통 적용됩니다.</div>
      </div>

      <button id="settings-code-btn" class="btn btn-gold" style="margin-top:16px;">🎁 코드 입력</button>
      <div style="flex:1;min-height:50px;"></div>
      <button class="btn" onclick="showScreen('etc-screen')">← 기타로</button>
    `;
    app.appendChild(screen);

    const toggle = screen.querySelector('#settings-music-toggle');
    const musicVol = screen.querySelector('#settings-music-volume');
    const sfxVol = screen.querySelector('#settings-sfx-volume');
    const codeBtn = screen.querySelector('#settings-code-btn');

    toggle.addEventListener('click', () => {
      settings.musicEnabled = !settings.musicEnabled;
      saveSettings();
      renderSettings();
    });
    musicVol.addEventListener('input', () => {
      settings.musicVolume = clamp(musicVol.value, 0, 100);
      saveSettings();
      renderSettings();
    });
    sfxVol.addEventListener('input', () => {
      settings.sfxVolume = clamp(sfxVol.value, 0, 100);
      saveSettings();
      renderSettings();
    });
    codeBtn.addEventListener('click', () => {
      if (typeof openCodeTab === 'function') openCodeTab();
    });
    return screen;
  }

  function renderSettings() {
    const screen = ensureSettingsScreen();
    if (!screen) return;
    const toggle = screen.querySelector('#settings-music-toggle');
    const musicVol = screen.querySelector('#settings-music-volume');
    const musicValue = screen.querySelector('#settings-music-value');
    const sfxVol = screen.querySelector('#settings-sfx-volume');
    const sfxValue = screen.querySelector('#settings-sfx-value');

    toggle.textContent = settings.musicEnabled ? 'ON' : 'OFF';
    toggle.style.background = settings.musicEnabled
      ? 'linear-gradient(145deg,#00b09b,#96c93d)'
      : 'linear-gradient(145deg,#555,#222)';
    musicVol.value = settings.musicVolume;
    musicVol.disabled = !settings.musicEnabled;
    musicVol.style.opacity = settings.musicEnabled ? '1' : '.45';
    musicValue.textContent = `${settings.musicVolume}%`;
    sfxVol.value = settings.sfxVolume;
    sfxValue.textContent = `${settings.sfxVolume}%`;
  }

  function openSettings() {
    if (typeof requireLogin === 'function' && !requireLogin()) return;
    renderSettings();
    if (typeof showScreen === 'function') showScreen('settings-screen');
  }

  function patchEtcMenu() {
    const etc = document.getElementById('etc-screen');
    if (!etc) return;
    const grid = etc.querySelector('div[style*="grid-template-columns"]');
    if (!grid) return;

    grid.querySelectorAll('button').forEach(btn => {
      const on = btn.getAttribute('onclick') || '';
      if (on.includes('openCodeTab')) btn.remove();
    });

    if (!document.getElementById('etc-settings-btn')) {
      const btn = document.createElement('button');
      btn.id = 'etc-settings-btn';
      btn.className = 'btn';
      btn.style.cssText = 'margin:0;min-height:64px;padding:12px 8px;font-size:.98rem;background:linear-gradient(135deg,#3a3d5c,#60658a);';
      btn.innerHTML = '⚙️<br>설정';
      btn.onclick = openSettings;
      grid.appendChild(btn);
    }
  }

  function patchCodeBackButton() {
    const screen = document.getElementById('code-screen');
    if (!screen) return;
    const buttons = screen.querySelectorAll('button');
    buttons.forEach(btn => {
      if ((btn.textContent || '').includes('기타로')) {
        btn.textContent = '← 설정으로';
        btn.removeAttribute('onclick');
        btn.onclick = openSettings;
      }
    });
  }

  window.openSettings = openSettings;
  window.getLRAudioSettings = () => ({ ...settings });
  window.getLRSfxVolume = () => settings.sfxVolume / 100;
  window.LRAudioSettings = { ...settings };

  ensureSettingsScreen();
  patchEtcMenu();
  patchCodeBackButton();
  saveSettings();
})();

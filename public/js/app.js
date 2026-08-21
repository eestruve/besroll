// BesTube (Бесроллинг) — 2007 Nostalgic Engine & Dynamic Trap Studio

const BESLAN_REEL_ID = 'DcQU8MDAMpV';
const BESLAN_REEL_URL = `https://www.instagram.com/reel/${BESLAN_REEL_ID}/`;
const BESLAN_EMBED_URL = `https://www.instagram.com/reel/${BESLAN_REEL_ID}/embed/`;

// State
let currentTrapData = {
  t: "🔥 Срочная новость — эксклюзивные подробности",
  d: "Материал только что опубликовали. Нажмите, чтобы открыть публикацию.",
  i: "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800",
  u: ""
};

let viewsCount = 1337420;

// Presets (Nostalgia 35+ / Детство 90-х и 2000-х)
const PRESETS = {
  vhs_archive: {
    t: "📼 Найдена редкая видеозапись с кассеты VHS 1997 года (Школьная дискотека)",
    d: "Уникальная оцифровка плёнки, которую искали более 20 лет. Посмотри, пока не удалили!",
    i: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=800",
    domain: "retro-archive.ru"
  },
  childhood_taste: {
    t: "🍬 Объявили о возвращении легендарных продуктов и сладостей 90-х",
    d: "Официально возобновляют продажу жвачек Turbo с вкладышами, соков Yupi, Zuko и сундучков Milky Way!",
    i: "https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?w=800",
    domain: "nostalgia90.ru"
  },
  tape_song: {
    t: "📻 Найдена та самая песня с магнитофона, которую искали 25 лет!",
    d: "Легендарный трек, звучавший из всех ларьков и на кассетах в конце 90-х. Нажмите, чтобы послушать оригинал.",
    i: "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=800",
    domain: "cassette-music.ru"
  },
  dendy_sega: {
    t: "🕹 Запустили бесплатный онлайн-архив всех 1000 игр Dendy и Sega прямо в браузере",
    d: "Танчики, Черепашки-Ниндзя, Чип и Дейл, Mortal Kombat 3 — теперь можно играть без скачивания!",
    i: "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=800",
    domain: "dendy-online.ru"
  },
  school_album: {
    t: "📸 Оцифровали архив школьных альбомов и списков выпускников 1995–2005",
    d: "Открытая база данных школьных выпускников. Проверьте, есть ли ваши старые фотографии из класса.",
    i: "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800",
    domain: "school-archive.ru"
  }
};

// Preload video
function initPreload() {
  const videoEl = document.getElementById('beslan-video');
  const dropVideoEl = document.getElementById('beslan-drop-video');
  if (videoEl) { videoEl.preload = 'auto'; videoEl.load(); }
  if (dropVideoEl) { dropVideoEl.preload = 'auto'; dropVideoEl.load(); }
}

// 100% Unmuted Autoplay Trigger via Cookie Consent Screen (User Gesture)
function acceptCookieAndPlay() {
  const gateEl = document.getElementById('cookie-gate');
  if (gateEl) {
    gateEl.classList.add('fade-out');
    setTimeout(() => {
      gateEl.style.display = 'none';
    }, 350);
  }

  // Trigger playback in exact user click frame (unlocks audio)
  triggerBesroll();
}

function openCookieGateTest() {
  const gateEl = document.getElementById('cookie-gate');
  if (gateEl) {
    gateEl.classList.remove('fade-out');
    gateEl.style.display = 'flex';
  }
}

// Trigger Besroll
function triggerBesroll() {
  const videoEl = document.getElementById('beslan-video');
  const iframeEl = document.getElementById('beslan-iframe');
  const overlay = document.getElementById('play-overlay');

  playDropSound();

  // Hide overlay
  if (overlay) overlay.style.display = 'none';

  // Increment views
  viewsCount++;
  const viewsDisplay = document.getElementById('views-count-display');
  if (viewsDisplay) viewsDisplay.innerText = `${viewsCount.toLocaleString('ru-RU')} просмотров`;

  if (videoEl) {
    videoEl.style.display = 'block';
    videoEl.muted = false;
    videoEl.volume = 1.0;
    videoEl.currentTime = 0;

    const playPromise = videoEl.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        if (iframeEl) iframeEl.style.display = 'none';
      }).catch(() => {
        fallbackToIframe();
      });
    }
  } else {
    fallbackToIframe();
  }

  showToast('👑 Вы были заБЕСроллены! You just got Beslaned!');
}

function fallbackToIframe() {
  const videoEl = document.getElementById('beslan-video');
  const iframeEl = document.getElementById('beslan-iframe');
  if (videoEl) videoEl.style.display = 'none';
  if (iframeEl) {
    iframeEl.style.display = 'block';
    if (!iframeEl.src || iframeEl.src === 'about:blank') {
      iframeEl.src = BESLAN_EMBED_URL;
    }
  }
}

function closeBesroll() {
  const dropContainer = document.getElementById('drop-container');
  const dropVideoEl = document.getElementById('beslan-drop-video');
  if (dropContainer) dropContainer.style.display = 'none';
  if (dropVideoEl) {
    dropVideoEl.pause();
    dropVideoEl.currentTime = 0;
  }
}

// 2007 Star Rating Click
function rateVideo() {
  showToast('⭐ Спасибо за оценку 5/5! Видео поднялось в топ рейтинга 2008!');
}

// Retro Tabs
function switchTab(tabId) {
  const tabs = ['tab-generator', 'tab-comments', 'tab-about'];
  tabs.forEach(t => {
    const btn = document.getElementById(`tab-btn-${t.replace('tab-', '')}`);
    const content = document.getElementById(`tab-content-${t.replace('tab-', '')}`);
    if (btn) btn.classList.remove('active');
    if (content) content.style.display = 'none';
  });

  const activeBtn = document.getElementById(`tab-btn-${tabId.replace('tab-', '')}`);
  const activeContent = document.getElementById(`tab-content-${tabId.replace('tab-', '')}`);
  if (activeBtn) activeBtn.classList.add('active');
  if (activeContent) activeContent.style.display = 'block';
}

// Web Audio API punchy sound effect
function playDropSound() {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(180, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(45, ctx.currentTime + 0.4);
    
    gain.gain.setValueAtTime(0.9, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.start();
    osc.stop(ctx.currentTime + 0.4);
  } catch (_) {}
}

// ----------------------------------------------------
// SMART URL SCRAPER & GENERATOR ENGINE
// ----------------------------------------------------

function utf8ToBase64(str) {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
    function toSolidBytes(match, p1) {
      return String.fromCharCode('0x' + p1);
  })).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function scrapeAndGenerate() {
  const inputEl = document.getElementById('target-url-input');
  const btnEl = document.getElementById('btn-scrape');
  if (!inputEl) return;

  const url = inputEl.value.trim();
  if (!url) {
    showToast('⚠️ Вставьте ссылку на новость или статью!');
    inputEl.focus();
    return;
  }

  const originalBtnText = btnEl ? btnEl.innerHTML : '';
  if (btnEl) {
    btnEl.disabled = true;
    btnEl.innerHTML = '⏳ Распаковка...';
  }

  try {
    const res = await fetch(`/api/scrape?url=${encodeURIComponent(url)}`);
    const data = await res.json();

    if (data.success) {
      currentTrapData.t = data.title || "Срочная новость";
      currentTrapData.d = data.description || "Подробности по ссылке...";
      currentTrapData.i = data.image || "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800";
      currentTrapData.u = data.url || url;

      updateFormFields();
      updateLivePreview(data.domain);
      showToast('🎉 Превью новости готово! Ссылка сгенерирована.');
    } else {
      let domain = "news.ru";
      try { domain = new URL(url.startsWith('http') ? url : 'https://' + url).hostname; } catch(_) {}
      currentTrapData.t = `Эксклюзивный материал на ${domain}`;
      currentTrapData.d = "Нажмите, чтобы прочитать подробности публикации.";
      currentTrapData.u = url;
      updateFormFields();
      updateLivePreview(domain);
      showToast('⚡️ Ссылка подготовлена!');
    }
  } catch (err) {
    let domain = "news.ru";
    try { domain = new URL(url.startsWith('http') ? url : 'https://' + url).hostname; } catch(_) {}
    currentTrapData.t = `Эксклюзив на ${domain}`;
    currentTrapData.d = "Подробности по ссылке...";
    currentTrapData.u = url;
    updateFormFields();
    updateLivePreview(domain);
    showToast('⚡️ Ловушка создана!');
  } finally {
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.innerHTML = originalBtnText || '⚡️ Распаковать';
    }
  }
}

function updateFormFields() {
  const titleInput = document.getElementById('custom-title');
  const descInput = document.getElementById('custom-desc');
  const imgInput = document.getElementById('custom-img');

  if (titleInput) titleInput.value = currentTrapData.t;
  if (descInput) descInput.value = currentTrapData.d;
  if (imgInput) imgInput.value = currentTrapData.i;
}

// Local file upload & auto-compression
async function handleImageFileUpload(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;

  const statusEl = document.getElementById('upload-status');
  if (statusEl) statusEl.innerText = '⏳ Обработка фото...';

  // 1. Instant local preview via FileReader & HTML5 Canvas
  const reader = new FileReader();
  reader.onload = (event) => {
    const rawDataUrl = event.target.result;
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      let w = img.width;
      let h = img.height;
      const maxW = 800;
      if (w > maxW) {
        h = Math.round((h * maxW) / w);
        w = maxW;
      }
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, w, h);
      const optimizedDataUrl = canvas.toDataURL('image/jpeg', 0.85);

      // Update input and live card preview instantly
      const imgInput = document.getElementById('custom-img');
      const prevImg = document.getElementById('preview-img');
      if (imgInput) imgInput.value = optimizedDataUrl;
      if (prevImg) prevImg.src = optimizedDataUrl;
      currentTrapData.i = optimizedDataUrl;
      generateTrapUrl();

      // 2. Upload to public free temporary host for bot crawlers (Telegram/WhatsApp)
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        try {
          if (statusEl) statusEl.innerText = '☁️ Загрузка в сеть...';
          const fd = new FormData();
          fd.append('file', blob, 'cover.jpg');
          
          const uploadRes = await fetch('https://tmpfiles.org/api/v1/upload', {
            method: 'POST',
            body: fd
          });
          const json = await uploadRes.json();
          if (json && json.data && json.data.url) {
            const publicUrl = json.data.url.replace('tmpfiles.org/', 'tmpfiles.org/dl/');
            if (imgInput) imgInput.value = publicUrl;
            if (prevImg) prevImg.src = publicUrl;
            currentTrapData.i = publicUrl;
            generateTrapUrl();
            if (statusEl) statusEl.innerText = '✅ Фото готово для мессенджеров!';
            showToast('✅ Фото загружено и готово для Telegram и WhatsApp!');
          } else {
            if (statusEl) statusEl.innerText = '✅ Готово (локально)';
          }
        } catch (_) {
          if (statusEl) statusEl.innerText = '✅ Готово';
        }
      }, 'image/jpeg', 0.85);
    };
    img.src = rawDataUrl;
  };
  reader.readAsDataURL(file);
}

function updateLivePreview(customDomain) {
  const titleInput = document.getElementById('custom-title');
  const descInput = document.getElementById('custom-desc');
  const imgInput = document.getElementById('custom-img');

  if (titleInput) currentTrapData.t = titleInput.value.trim() || "🔥 Срочная новость";
  if (descInput) currentTrapData.d = descInput.value.trim() || "Подробности по ссылке...";
  if (imgInput) {
    const rawVal = imgInput.value.trim();
    currentTrapData.i = rawVal || "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800";
  }

  const prevTitle = document.getElementById('preview-title');
  const prevDesc = document.getElementById('preview-desc');
  const prevImg = document.getElementById('preview-img');
  const prevDomain = document.getElementById('preview-domain');

  if (prevTitle) prevTitle.textContent = currentTrapData.t;
  if (prevDesc) prevDesc.textContent = currentTrapData.d;
  if (prevImg) {
    prevImg.src = currentTrapData.i;
  }
  
  if (prevDomain) {
    if (customDomain) {
      prevDomain.textContent = customDomain;
    } else if (currentTrapData.u) {
      try { prevDomain.textContent = new URL(currentTrapData.u).hostname; } catch(_) {}
    } else {
      prevDomain.textContent = "ria.ru";
    }
  }

  generateTrapUrl();
}

function generateTrapUrl() {
  const payloadStr = JSON.stringify(currentTrapData);
  const encoded = utf8ToBase64(payloadStr);
  const origin = window.location.origin;
  const fullTrapUrl = `${origin}/r/${encoded}`;

  const linkInput = document.getElementById('generated-link');
  const dropLinkInput = document.getElementById('drop-generated-link');
  if (linkInput) linkInput.value = fullTrapUrl;
  if (dropLinkInput) dropLinkInput.value = fullTrapUrl;
  return fullTrapUrl;
}

function applyPreset(key) {
  const preset = PRESETS[key];
  if (!preset) return;

  currentTrapData.t = preset.t;
  currentTrapData.d = preset.d;
  currentTrapData.i = preset.i;
  currentTrapData.u = "";

  const titleInput = document.getElementById('custom-title');
  const descInput = document.getElementById('custom-desc');
  const imgInput = document.getElementById('custom-img');
  const urlInput = document.getElementById('target-url-input');

  if (titleInput) titleInput.value = preset.t;
  if (descInput) descInput.value = preset.d;
  if (imgInput) imgInput.value = preset.i;
  if (urlInput) urlInput.value = "";

  switchTab('tab-generator');
  updateLivePreview(preset.domain);
  
  const studio = document.getElementById('generator-section');
  if (studio) studio.scrollIntoView({ behavior: 'smooth' });

  showToast(`🎯 Пресет «${preset.t.slice(0, 25)}...» применен!`);
}

function copyGeneratedLink() {
  const linkInput = document.getElementById('generated-link');
  const fullUrl = linkInput && linkInput.value ? linkInput.value : generateTrapUrl();

  // Copy EXCLUSIVELY the pure URL (no title) so Telegram/WhatsApp crawlers show the card preview cleanly!
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(fullUrl).then(() => {
      showToast('✅ Чистая ссылка скопирована! Отправь её в Telegram или WhatsApp.');
    }).catch(() => {
      copyFallback(fullUrl);
    });
  } else {
    copyFallback(fullUrl);
  }
}

function copyFallback(text) {
  const ta = document.createElement('textarea');
  ta.value = text;
  ta.style.position = 'fixed';
  ta.style.left = '-9999px';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try {
    document.execCommand('copy');
    showToast('✅ Чистая ссылка скопирована!');
  } catch (_) {
    prompt('Скопируйте ссылку:', text);
  }
  document.body.removeChild(ta);
}

function shareToTelegram() {
  const url = generateTrapUrl();
  // Pass ONLY the URL parameter so Telegram's crawler displays the OpenGraph preview card cleanly!
  window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}`, '_blank');
}

function shareToWhatsApp() {
  const url = generateTrapUrl();
  window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(url)}`, '_blank');
}

function shareToVK() {
  const url = generateTrapUrl();
  const text = currentTrapData.t;
  window.open(`https://vk.com/share.php?url=${encodeURIComponent(url)}&title=${encodeURIComponent(text)}`, '_blank');
}

function copyDirectReel() {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(BESLAN_REEL_URL).then(() => {
      showToast(`🎵 Ссылка на Reels Беслана скопирована!`);
    });
  } else {
    prompt('Скопируйте ссылку:', BESLAN_REEL_URL);
  }
}

// Drop modal handlers
async function scrapeFromDrop() {
  const input = document.getElementById('drop-target-url');
  if (!input || !input.value.trim()) {
    showToast('⚠️ Вставьте ссылку на новость!');
    return;
  }
  const targetInput = document.getElementById('target-url-input');
  if (targetInput) targetInput.value = input.value.trim();
  await scrapeAndGenerate();
}

function copyDropLink() {
  copyGeneratedLink();
}

function scrollToStudioFromDrop() {
  closeBesroll();
  switchTab('tab-generator');
  const studio = document.getElementById('generator-section');
  if (studio) studio.scrollIntoView({ behavior: 'smooth' });
}

// ----------------------------------------------------
// DVD BOUNCING MEME BADGE (Floating Screensaver Engine)
// ----------------------------------------------------
const DvdBouncer = {
  el: null,
  x: 30,
  y: 60,
  vx: 1.8,
  vy: 1.4,
  baseVx: 1.8,
  baseVy: 1.4,
  multiplier: 1.0,
  turboTimer: null,
  colors: ['#ff0055', '#00f2fe', '#ffe600', '#00ff88', '#b5179e', '#ff5400', '#7209b7', '#06d6a0'],
  colorIdx: 0,
  isPaused: false,

  init() {
    let pill = document.getElementById('dvd-pill');
    if (!pill) {
      pill = document.createElement('div');
      pill.id = 'dvd-pill';
      pill.innerHTML = '👑 <span>Вы были заБЕСроллены!</span>';
      document.body.appendChild(pill);
    }
    this.el = pill;

    // Random initial direction
    this.vx = (Math.random() > 0.5 ? 1 : -1) * this.baseVx;
    this.vy = (Math.random() > 0.5 ? 1 : -1) * this.baseVy;
    this.applyColor();

    // Click on pill triggers turbo boost
    this.el.addEventListener('click', () => {
      this.accelerate(3.5, 3000);
      showToast('🚀 Не поймаешь! Бесроллинг активен!');
    });

    // Start 60fps loop
    requestAnimationFrame(() => this.loop());
  },

  applyColor() {
    if (!this.el) return;
    const color = this.colors[this.colorIdx];
    this.el.style.borderColor = color;
    this.el.style.boxShadow = `0 4px 20px ${color}, inset 0 1px 0 rgba(255,255,255,0.3)`;
  },

  nextColor() {
    this.colorIdx = (this.colorIdx + 1) % this.colors.length;
    this.applyColor();
  },

  accelerate(factor = 3.5, duration = 3000) {
    this.multiplier = factor;
    if (this.el) this.el.classList.add('turbo');
    clearTimeout(this.turboTimer);
    this.turboTimer = setTimeout(() => {
      this.multiplier = 1.0;
      if (this.el) this.el.classList.remove('turbo');
    }, duration);
  },

  loop() {
    if (!this.el) return;

    const width = this.el.offsetWidth || 220;
    const height = this.el.offsetHeight || 38;
    const maxX = window.innerWidth - width - 6;
    const maxY = window.innerHeight - height - 6;

    this.x += this.vx * this.multiplier;
    this.y += this.vy * this.multiplier;

    let hit = false;

    // Bounce X
    if (this.x <= 4) {
      this.x = 4;
      this.vx = Math.abs(this.vx);
      hit = true;
    } else if (this.x >= maxX) {
      this.x = maxX;
      this.vx = -Math.abs(this.vx);
      hit = true;
    }

    // Bounce Y
    if (this.y <= 4) {
      this.y = 4;
      this.vy = Math.abs(this.vy);
      hit = true;
    } else if (this.y >= maxY) {
      this.y = maxY;
      this.vy = -Math.abs(this.vy);
      hit = true;
    }

    if (hit) {
      this.nextColor();
    }

    this.el.style.transform = `translate3d(${this.x}px, ${this.y}px, 0)`;

    requestAnimationFrame(() => this.loop());
  }
};

function showToast(message) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.className = 'show';
  setTimeout(() => {
    toast.className = '';
  }, 3500);
}

// Hook video pause attempts to accelerate DVD & refuse pausing
function setupAntiPause() {
  const videoEl = document.getElementById('beslan-video');
  if (videoEl) {
    videoEl.addEventListener('pause', (e) => {
      if (!videoEl.ended) {
        // Refuse pause and accelerate DVD!
        videoEl.play();
        DvdBouncer.accelerate(4.0, 3500);
        showToast('⚡️ Бесроллинг нельзя остановить!');
      }
    });

    videoEl.addEventListener('click', () => {
      DvdBouncer.accelerate(3.5, 3000);
    });
  }

  const wrapper = document.getElementById('video-wrapper');
  if (wrapper) {
    wrapper.addEventListener('click', () => {
      DvdBouncer.accelerate(3.5, 3000);
    });
  }
}

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
  initPreload();
  DvdBouncer.init();
  setupAntiPause();

  const titleInput = document.getElementById('custom-title');
  if (titleInput && !titleInput.value) titleInput.value = currentTrapData.t;
  const descInput = document.getElementById('custom-desc');
  if (descInput && !descInput.value) descInput.value = currentTrapData.d;
  const imgInput = document.getElementById('custom-img');
  if (imgInput && !imgInput.value) imgInput.value = currentTrapData.i;

  updateLivePreview();
});

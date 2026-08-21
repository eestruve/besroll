// Бесроллинг (Besrolling) — Ultra-Fast Instant Playback & Viral Trap Studio

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

// Preset database
const PRESETS = {
  gta6: {
    t: "Слив 15 минут геймплея GTA 6 в 4K (YouTube)",
    d: "В сеть утек полный видеоролик прохождения сюжетной миссии в Вайс-Сити.",
    i: "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=800",
    domain: "youtube.com"
  },
  tg_premium: {
    t: "🎁 Вам отправлен подарок: Telegram Premium на 1 год",
    d: "Нажмите, чтобы активировать подарочную подписку на ваш аккаунт.",
    i: "https://images.unsplash.com/photo-1614680376593-902f749f7ffc?w=800",
    domain: "t.me"
  },
  gossip: {
    t: "Жесть... Это реально про тебя тут выложили пост? 😳",
    d: "Смотри скорее, пока автор не удалил публикацию в канале!",
    i: "https://images.unsplash.com/photo-1577563908411-5077b6dc7624?w=800",
    domain: "telegram.org"
  },
  exam: {
    t: "📊 Таблица с предварительными баллами и списками премий",
    d: "Официальный документ закрытого доступа. Проверьте свою фамилию.",
    i: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
    domain: "docs.google.com"
  }
};

// Preload video immediately
function initPreload() {
  const videoEl = document.getElementById('beslan-video');
  if (videoEl) {
    videoEl.preload = 'auto';
    videoEl.load();
  }
}

// Trigger the Drop / Jumpscare (0 ms latency)
function triggerBesroll() {
  const dropContainer = document.getElementById('drop-container');
  const mainContainer = document.querySelector('.container');
  const baitView = document.getElementById('bait-view');
  const videoEl = document.getElementById('beslan-video');
  const iframeEl = document.getElementById('beslan-iframe');

  playDropSound();

  if (dropContainer) dropContainer.style.display = 'flex';
  if (mainContainer) mainContainer.style.display = 'none';
  if (baitView) baitView.style.display = 'none';

  if (videoEl) {
    videoEl.style.display = 'block';
    videoEl.muted = false;
    videoEl.volume = 1.0;
    videoEl.currentTime = 0;
    
    const playPromise = videoEl.play();
    if (playPromise !== undefined) {
      playPromise.then(() => {
        if (iframeEl) iframeEl.style.display = 'none';
      }).catch(err => {
        console.warn("Video autoplay failed, fallback to embed:", err);
        fallbackToIframe();
      });
    }
  } else {
    fallbackToIframe();
  }

  fireConfetti();
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
  const mainContainer = document.querySelector('.container');
  const baitView = document.getElementById('bait-view');
  const videoEl = document.getElementById('beslan-video');
  const iframeEl = document.getElementById('beslan-iframe');

  if (dropContainer) dropContainer.style.display = 'none';
  if (mainContainer) mainContainer.style.display = 'flex';
  if (baitView) baitView.style.display = 'flex';

  if (videoEl) {
    videoEl.pause();
    videoEl.currentTime = 0;
  }
  if (iframeEl) iframeEl.src = 'about:blank';
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
    osc.frequency.exponentialRampToValueAtTime(45, ctx.currentTime + 0.45);
    
    gain.gain.setValueAtTime(0.95, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.45);
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.start();
    osc.stop(ctx.currentTime + 0.45);
  } catch (_) {}
}

// ----------------------------------------------------
// SMART URL SCRAPER & GENERATOR ENGINE
// ----------------------------------------------------

// Safe base64 encoding for Unicode
function utf8ToBase64(str) {
  return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g,
    function toSolidBytes(match, p1) {
      return String.fromCharCode('0x' + p1);
  })).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function base64ToUtf8(str) {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  return decodeURIComponent(Array.prototype.map.call(atob(str), function(c) {
    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));
}

// Scrape URL on the fly
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
    btnEl.innerHTML = '⏳ Распаковываем...';
  }

  try {
    const res = await fetch(`/api/scrape?url=${encodeURIComponent(url)}`);
    const data = await res.json();

    if (data.success) {
      currentTrapData.t = data.title || "Срочная новость";
      currentTrapData.d = data.description || "Подробности по ссылке...";
      currentTrapData.i = data.image || "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800";
      currentTrapData.u = data.url || url;

      // Update form fields
      const titleInput = document.getElementById('custom-title');
      const descInput = document.getElementById('custom-desc');
      const imgInput = document.getElementById('custom-img');

      if (titleInput) titleInput.value = currentTrapData.t;
      if (descInput) descInput.value = currentTrapData.d;
      if (imgInput) imgInput.value = currentTrapData.i;

      updateLivePreview(data.domain);
      showToast('🎉 Новость успешно распакована! Ссылка готова.');
    } else {
      // Fallback: use domain / basic heuristic
      let domain = "news.ru";
      try { domain = new URL(url.startsWith('http') ? url : 'https://' + url).hostname; } catch(_) {}
      currentTrapData.t = `Эксклюзивная публикация на ${domain}`;
      currentTrapData.d = "Нажмите, чтобы прочитать полный текст материала.";
      currentTrapData.u = url;

      updateFormAndPreview(domain);
      showToast('⚡️ Ссылка подготовлена! Можете отредактировать заголовок.');
    }
  } catch (err) {
    console.warn("Scrape error, falling back locally:", err);
    let domain = "news.ru";
    try { domain = new URL(url.startsWith('http') ? url : 'https://' + url).hostname; } catch(_) {}
    currentTrapData.t = `Эксклюзив на ${domain}`;
    currentTrapData.d = "Подробности по ссылке...";
    currentTrapData.u = url;
    updateFormAndPreview(domain);
    showToast('⚡️ Ловушка создана!');
  } finally {
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.innerHTML = originalBtnText || '⚡️ Распаковать';
    }
  }
}

function updateFormAndPreview(domain) {
  const titleInput = document.getElementById('custom-title');
  const descInput = document.getElementById('custom-desc');
  const imgInput = document.getElementById('custom-img');

  if (titleInput) titleInput.value = currentTrapData.t;
  if (descInput) descInput.value = currentTrapData.d;
  if (imgInput) imgInput.value = currentTrapData.i;

  updateLivePreview(domain);
}

// Live update of the Telegram/WhatsApp preview box
function updateLivePreview(customDomain) {
  const titleInput = document.getElementById('custom-title');
  const descInput = document.getElementById('custom-desc');
  const imgInput = document.getElementById('custom-img');

  if (titleInput && titleInput.value) currentTrapData.t = titleInput.value;
  if (descInput && descInput.value) currentTrapData.d = descInput.value;
  if (imgInput && imgInput.value) currentTrapData.i = imgInput.value;

  const prevTitle = document.getElementById('preview-title');
  const prevDesc = document.getElementById('preview-desc');
  const prevImg = document.getElementById('preview-img');
  const prevDomain = document.getElementById('preview-domain');

  if (prevTitle) prevTitle.textContent = currentTrapData.t;
  if (prevDesc) prevDesc.textContent = currentTrapData.d;
  if (prevImg) prevImg.src = currentTrapData.i;
  
  if (prevDomain) {
    if (customDomain) {
      prevDomain.textContent = customDomain;
    } else if (currentTrapData.u) {
      try { prevDomain.textContent = new URL(currentTrapData.u).hostname; } catch(_) {}
    } else {
      prevDomain.textContent = "ria.ru";
    }
  }

  // Generate URL
  generateTrapUrl();
}

// Encode trap payload into URL
function generateTrapUrl() {
  const payloadStr = JSON.stringify(currentTrapData);
  const encoded = utf8ToBase64(payloadStr);
  const origin = window.location.origin;
  const fullTrapUrl = `${origin}/r/${encoded}`;

  const linkInput = document.getElementById('generated-link');
  if (linkInput) {
    linkInput.value = fullTrapUrl;
  }
  return fullTrapUrl;
}

// Apply Preset
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

  updateLivePreview(preset.domain);
  
  // Scroll to studio
  const studio = document.getElementById('generator-section') || document.getElementById('hunter-studio');
  if (studio) {
    studio.scrollIntoView({ behavior: 'smooth' });
  }

  showToast(`🎯 Пресет «${preset.t.slice(0, 25)}...» применен!`);
}

// Sharing Actions
function copyGeneratedLink() {
  const linkInput = document.getElementById('generated-link');
  const fullUrl = linkInput && linkInput.value ? linkInput.value : generateTrapUrl();
  const shareText = `${currentTrapData.t}\n${fullUrl}`;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(shareText).then(() => {
      showToast('✅ Ссылка скопирована! Отправь её другу в Telegram или WhatsApp.');
    }).catch(() => {
      prompt('Скопируйте ссылку вручную:', shareText);
    });
  } else {
    prompt('Скопируйте ссылку вручную:', shareText);
  }
}

function shareToTelegram() {
  const url = generateTrapUrl();
  const text = currentTrapData.t;
  window.open(`https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}`, '_blank');
}

function shareToWhatsApp() {
  const url = generateTrapUrl();
  const text = `${currentTrapData.t}\n${url}`;
  window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank');
}

function shareToVK() {
  const url = generateTrapUrl();
  const text = currentTrapData.t;
  window.open(`https://vk.com/share.php?url=${encodeURIComponent(url)}&title=${encodeURIComponent(text)}`, '_blank');
}

// Toast notification
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

// Confetti effect
function fireConfetti() {
  const colors = ['#00f2fe', '#9d4edd', '#ffb703', '#ff0055', '#ffffff'];
  for (let i = 0; i < 60; i++) {
    const confetti = document.createElement('div');
    confetti.style.position = 'fixed';
    confetti.style.width = Math.random() * 8 + 6 + 'px';
    confetti.style.height = Math.random() * 12 + 8 + 'px';
    confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    confetti.style.left = Math.random() * 100 + 'vw';
    confetti.style.top = '-20px';
    confetti.style.zIndex = '10001';
    confetti.style.borderRadius = '3px';
    confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
    confetti.style.transition = `top ${Math.random() * 2 + 1.5}s ease-out, transform 2s ease-out, opacity 2s ease`;
    
    document.body.appendChild(confetti);

    setTimeout(() => {
      confetti.style.top = Math.random() * 80 + 20 + 'vh';
      confetti.style.transform = `rotate(${Math.random() * 720}deg)`;
      confetti.style.opacity = '0';
    }, 20);

    setTimeout(() => {
      confetti.remove();
    }, 2500);
  }
}

// Initialize on DOM load
window.addEventListener('DOMContentLoaded', () => {
  initPreload();

  // Initialize initial preview
  const titleInput = document.getElementById('custom-title');
  if (titleInput && !titleInput.value) {
    titleInput.value = currentTrapData.t;
  }
  const descInput = document.getElementById('custom-desc');
  if (descInput && !descInput.value) {
    descInput.value = currentTrapData.d;
  }
  const imgInput = document.getElementById('custom-img');
  if (imgInput && !imgInput.value) {
    imgInput.value = currentTrapData.i;
  }

  updateLivePreview();
});

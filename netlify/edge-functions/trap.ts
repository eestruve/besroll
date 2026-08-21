export default async (request: Request) => {
  const url = new URL(request.url);
  const pathParts = url.pathname.split("/").filter(Boolean); // e.g. ["r", "<payload>"]
  
  let title = "🔥 Срочная новость — смотреть подробности";
  let description = "Эксклюзивные подробности уже в сети. Нажмите, чтобы открыть публикацию.";
  let image = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800";
  let originalUrl = "";

  // 1. Try extracting payload from path: /r/<base64>
  if (pathParts.length >= 2 && pathParts[0] === "r") {
    const rawPayload = pathParts[1];
    try {
      // Decode base64 URL safe
      const decodedStr = decodeURIComponent(escape(atob(rawPayload.replace(/-/g, "+").replace(/_/g, "/"))));
      const parsed = JSON.parse(decodedStr);
      if (parsed.t) title = parsed.t;
      if (parsed.d) description = parsed.d;
      if (parsed.i) image = parsed.i;
      if (parsed.u) originalUrl = parsed.u;
    } catch (_) {
      // If direct base64 decode fails, try query params fallback
    }
  }

  // 2. Query param overrides if provided
  if (url.searchParams.get("t")) title = url.searchParams.get("t")!;
  if (url.searchParams.get("d")) description = url.searchParams.get("d")!;
  if (url.searchParams.get("i")) image = url.searchParams.get("i")!;
  if (url.searchParams.get("u")) originalUrl = url.searchParams.get("u")!;

  // Escape HTML helper
  const esc = (s: string) => s.replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const html = `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <!-- Dynamic OpenGraph for Telegram, WhatsApp, VK, Instagram, Discord -->
  <title>${esc(title)}</title>
  <meta property="og:title" content="${esc(title)}">
  <meta property="og:description" content="${esc(description)}">
  <meta property="og:image" content="${esc(image)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Новостной вестник">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${esc(title)}">
  <meta name="twitter:description" content="${esc(description)}">
  <meta name="twitter:image" content="${esc(image)}">

  <link rel="stylesheet" href="/css/style.css">
</head>
<body class="trap-page">

  <div class="container" id="bait-view">
    <div class="glass-card bait-card">
      <div class="header-badge">⚡️ Эксклюзивный материал</div>
      <h1 class="bait-title">${esc(title)}</h1>
      <div class="bait-image-box">
        <img src="${esc(image)}" alt="Preview" class="bait-img" />
        <div class="play-overlay" onclick="triggerBesroll()">
          <div class="play-pulse-btn">▶</div>
          <span>Нажмите для воспроизведения</span>
        </div>
      </div>
      <p class="bait-desc">${esc(description)}</p>
      
      <button class="pulse-button" onclick="triggerBesroll()" style="margin-top: 20px;">
        <span>🔥 Читать / Смотреть материал</span>
      </button>
    </div>
  </div>

  <!-- Fullscreen Besroll Player & Hunter Studio -->
  <div id="drop-container" style="display: none;">
    <div class="beslan-banner">
      <div class="beslan-title">👑 ВЫ БЫЛИ ЗАБЕСЛАНЕНЫ! 👑</div>
      <div class="beslan-subtitle">You just got Beslaned by @besikraev</div>
    </div>

    <div class="video-frame">
      <video id="beslan-video" src="/assets/beslan.mp4" playsinline loop preload="auto"></video>
      <iframe id="beslan-iframe" src="about:blank" width="100%" height="100%" frameborder="0" scrolling="no" allowtransparency="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>
    </div>

    <div class="action-bar">
      <a href="#hunter-studio" class="btn btn-primary" onclick="scrollToHunterStudio()">
        😈 Разыграть друга (Создать ловушку)
      </a>
      <a href="https://www.instagram.com/reel/DcQU8MDAMpV/" target="_blank" class="btn btn-secondary">
        🎵 Полный трек в Instagram
      </a>
    </div>

    <!-- The Hunter Studio (Create Your Own Trap in the same window) -->
    <div id="hunter-studio" class="glass-card" style="margin-top: 30px; width: 100%; max-width: 680px; text-align: left;">
      <div class="header-badge" style="background: rgba(0, 242, 254, 0.2); color: #00f2fe;">🎯 Очередь за тобой</div>
      <h2 style="font-size: 1.5rem; margin-top: 8px;">Разыграй друга за 5 секунд</h2>
      <p class="subtitle" style="font-size: 0.95rem; margin-bottom: 16px;">
        Вставь ссылку на любую новость или видео — мессенджер покажет настоящее превью, а при клике друг увидит Беслана!
      </p>

      <!-- Smart URL Scraper Input -->
      <div class="generator-box">
        <label style="font-size: 0.85rem; font-weight: 600; color: var(--text-dim);">ССЫЛКА НА ЛЮБУЮ НОВОСТЬ / СТАТЬЮ:</label>
        <div style="display: flex; gap: 8px; margin-top: 6px; flex-wrap: wrap;">
          <input type="text" id="target-url-input" class="input-field" placeholder="https://ria.ru/..., https://tass.ru/... или https://habr.com/..." style="flex: 1; min-width: 240px;">
          <button class="btn btn-primary" id="btn-scrape" onclick="scrapeAndGenerate()">
            ⚡️ Распаковать
          </button>
        </div>
      </div>

      <!-- Live Customizer Form -->
      <div id="customizer-form" style="margin-top: 18px;">
        <div style="margin-bottom: 12px;">
          <label style="font-size: 0.85rem; color: var(--text-dim);">Заголовок новости:</label>
          <input type="text" id="custom-title" class="input-field" placeholder="Сенсационный заголовок..." oninput="updateLivePreview()">
        </div>
        <div style="margin-bottom: 12px;">
          <label style="font-size: 0.85rem; color: var(--text-dim);">Краткое описание:</label>
          <input type="text" id="custom-desc" class="input-field" placeholder="Текст превью..." oninput="updateLivePreview()">
        </div>
        <div style="margin-bottom: 12px;">
          <label style="font-size: 0.85rem; color: var(--text-dim);">Ссылка на картинку (обложка):</label>
          <input type="text" id="custom-img" class="input-field" placeholder="https://..." oninput="updateLivePreview()">
        </div>
      </div>

      <!-- Live Telegram Preview Box -->
      <div style="margin-top: 20px;">
        <label style="font-size: 0.85rem; color: var(--text-dim); margin-bottom: 6px; display: block;">👁 Как превью будет выглядеть в Telegram / WhatsApp:</label>
        <div class="telegram-preview-card">
          <div class="tg-domain" id="preview-domain">news.yandex.ru</div>
          <div class="tg-title" id="preview-title">Сенсационный заголовок появится здесь</div>
          <div class="tg-desc" id="preview-desc">Краткое описание публикации...</div>
          <img id="preview-img" src="https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800" class="tg-img" alt="Preview">
        </div>
      </div>

      <!-- Generated Share Actions -->
      <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1);">
        <label style="font-size: 0.85rem; color: #00f2fe; font-weight: 600;">🔗 Твоя ссылка-ловушка готова:</label>
        <input type="text" id="generated-link" class="input-field" readonly style="margin-top: 6px; background: rgba(0,0,0,0.4); color: #00f2fe;" onclick="this.select()">
        
        <div style="display: flex; gap: 8px; margin-top: 12px; flex-wrap: wrap;">
          <button class="btn btn-primary" onclick="copyGeneratedLink()" style="flex: 1;">
            📋 Скопировать ссылку
          </button>
          <button class="btn btn-secondary" onclick="shareToTelegram()">
            ✈️ В Telegram
          </button>
          <button class="btn btn-secondary" onclick="shareToWhatsApp()">
            💬 В WhatsApp
          </button>
        </div>
      </div>
    </div>
  </div>

  <script src="/js/app.js"></script>
  <script>
    // Auto-trigger video when arriving via trap link on user click
    window.addEventListener('DOMContentLoaded', () => {
      // If direct click anywhere on the bait card
      document.getElementById('bait-view')?.addEventListener('click', triggerBesroll);
    });

    function scrollToHunterStudio() {
      const studio = document.getElementById('hunter-studio');
      if (studio) {
        studio.scrollIntoView({ behavior: 'smooth' });
      }
    }
  </script>
</body>
</html>`;

  return new Response(html, {
    headers: {
      "Content-Type": "text/html; charset=UTF-8",
      "Cache-Control": "public, max-age=300",
    },
  });
};

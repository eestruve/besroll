import http.server
import os
import urllib.parse
import urllib.request
import json
import base64
import re
import html

PORT = 8080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

class BesrollHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_HEAD(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        if path.startswith('/r/') or path == '/api/scrape':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
        else:
            super().do_HEAD()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # 1. API: /api/scrape?url=...
        if path == '/api/scrape':
            query = urllib.parse.parse_qs(parsed_url.query)
            target_url = query.get('url', [''])[0]
            if not target_url:
                self.send_json({'success': False, 'error': 'Missing url parameter'}, status=400)
                return

            if not target_url.startswith(('http://', 'https://')):
                target_url = 'https://' + target_url

            try:
                req = urllib.request.Request(
                    target_url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
                    }
                )
                with urllib.request.urlopen(req, timeout=4) as response:
                    raw_html = response.read().decode('utf-8', errors='ignore')

                def get_meta(prop, name_fallback=None):
                    m = re.search(rf'<meta[^>]*property=["\']{prop}["\'][^>]*content=["\']([^"\']+)["\']', raw_html, re.I)
                    if not m:
                        m = re.search(rf'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']{prop}["\']', raw_html, re.I)
                    if not m and name_fallback:
                        m = re.search(rf'<meta[^>]*name=["\']{name_fallback}["\'][^>]*content=["\']([^"\']+)["\']', raw_html, re.I)
                        if not m:
                            m = re.search(rf'<meta[^>]*content=["\']([^"\']+)["\'][^>]*name=["\']{name_fallback}["\']', raw_html, re.I)
                    return html.unescape(m.group(1).strip()) if m else ''

                title = get_meta('og:title', 'twitter:title')
                if not title:
                    tm = re.search(r'<title[^>]*>([^<]+)</title>', raw_html, re.I)
                    title = html.unescape(tm.group(1).strip()) if tm else ''

                desc = get_meta('og:description', 'description') or get_meta('twitter:description')
                img = get_meta('og:image', 'twitter:image')
                domain = urllib.parse.urlparse(target_url).netloc

                if img and not img.startswith(('http://', 'https://')):
                    img = urllib.parse.urljoin(target_url, img)

                self.send_json({
                    'success': True,
                    'url': target_url,
                    'title': title or domain,
                    'description': desc or 'Нажмите, чтобы прочитать подробности...',
                    'image': img or 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800',
                    'domain': domain
                })
            except Exception:
                domain = urllib.parse.urlparse(target_url).netloc
                self.send_json({
                    'success': True,
                    'url': target_url,
                    'title': f'Материал на {domain}',
                    'description': 'Нажмите для перехода к публикации...',
                    'image': 'https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800',
                    'domain': domain
                })
            return

        # 2. Dynamic Trap Route: /r/<payload>
        if path.startswith('/r/'):
            raw_payload = path[3:]
            title = "🔥 Срочная новость — смотреть подробности"
            description = "Эксклюзивные подробности уже в сети. Нажмите, чтобы открыть публикацию."
            image = "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800"

            try:
                padded = raw_payload.replace('-', '+').replace('_', '/')
                while len(padded) % 4 != 0:
                    padded += '='
                decoded_bytes = base64.b64decode(padded)
                data = json.loads(urllib.parse.unquote(decoded_bytes.decode('utf-8', errors='ignore')))
                if data.get('t'): title = data['t']
                if data.get('d'): description = data['d']
                if data.get('i'): image = data['i']
            except Exception:
                pass

            trap_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:image" content="{html.escape(image)}">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Новостной вестник">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  <meta name="twitter:image" content="{html.escape(image)}">
  <link rel="stylesheet" href="/css/style.css">
  <link rel="preload" as="video" href="/assets/beslan.mp4" type="video/mp4">

  <!-- Yandex.Metrika counter -->
  <script type="text/javascript">
      (function(m,e,t,r,i,k,a){{
          m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
          m[i].l=1*new Date();
          for (var j = 0; j < document.scripts.length; j++) {{if (document.scripts[j].src === r) {{ return; }}}}
          k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
      }})(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=111840556', 'ym');

      ym(111840556, 'init', {{ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true}});
  </script>
  <noscript><div><img src="https://mc.yandex.ru/watch/111840556" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
  <!-- /Yandex.Metrika counter -->
</head>
<body>

  <!-- STEP 1: COOKIE & NEWS BAIT SCREEN (100% UNMUTED AUTOPLAY UNLOCK) -->
  <div id="cookie-gate" class="cookie-gate-overlay">
    <div class="fake-news-page">
      <div class="news-topbar">
        <div class="news-logo">🔴 СРОЧНЫЙ ВЫПУСК НОВОСТЕЙ</div>
        <div class="news-date">Эксклюзив • Прямой эфир</div>
      </div>

      <div class="news-article-preview">
        <div class="news-category">ГЛАВНОЕ СОБЫТИЕ ДНЯ</div>
        <h1 class="news-title">{html.escape(title)}</h1>
        <div class="news-image-box" onclick="acceptCookieAndPlay()" style="cursor: pointer;">
          <img src="{html.escape(image)}" class="news-img" alt="News Image">
        </div>
      </div>

      <div class="cookie-consent-modal">
        <div class="cookie-modal-header">
          <span style="font-size: 20px;">🍪</span>
          <strong>Уведомление об использовании файлов Cookie</strong>
        </div>
        <p class="cookie-modal-text">
          Для доступа к эксклюзивным материалам и продолжения чтения статьи подтвердите согласие на обработку файлов cookie.
        </p>
        <div class="cookie-modal-actions">
          <button class="cookie-accept-btn" onclick="acceptCookieAndPlay()">
            ✅ Принять cookies и продолжить чтение
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 2: 2007 RETRO YOUTUBE PLAYER & HUNTER STUDIO (Plays unmuted on reveal) -->
  <header class="retro-header">
    <div class="retro-header-inner">
      <a href="/index.html" class="yt-logo">Bes<span class="logo-box">Roll</span></a>
      <div class="header-search">
        <input type="text" id="header-search-box" placeholder="Поиск по мемам 2008..." onkeydown="if(event.key==='Enter') searchMeme()">
        <button class="glossy-btn" onclick="searchMeme()">Поиск</button>
      </div>
      <div class="retro-nav-links">
        <a href="/index.html">Главная</a> |
        <a href="https://www.instagram.com/besikraev/" target="_blank">@besikraev</a>
      </div>
    </div>
  </header>

  <div class="page-container">
    <main class="main-column">
      <div class="video-player-card">
        <div class="video-screen-wrapper" id="video-wrapper" onclick="triggerBesroll()">
          <video id="beslan-video" src="/assets/beslan.mp4" playsinline loop preload="auto"></video>
          <iframe id="beslan-iframe" src="about:blank" width="100%" height="100%" frameborder="0" scrolling="no" allow="autoplay; clipboard-write; encrypted-media" style="display: none;"></iframe>
          <div class="play-overlay-screen" id="play-overlay" style="display: none;">
            <div class="retro-big-play-btn">▶</div>
          </div>
        </div>
        <div class="retro-player-bar">
          <div class="player-controls-left">
            <button class="play-toggle-btn" onclick="triggerBesroll()">► Play</button>
            <span class="time-counter">0:00 / 0:15</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="hq-badge">HQ</span>
            <span style="cursor: pointer;" onclick="triggerBesroll()">🔊 100%</span>
          </div>
        </div>
      </div>

      <div class="retro-box video-meta-section">
        <h1 class="video-headline">Besik Raev — «Останься музыка» (HQ Official 2008)</h1>
        <div class="video-sub-bar">
          <div class="author-badge">
            <div class="author-avatar" style="background: url('/assets/beslan_avatar.png') center/cover;"></div>
            <div>
              <a href="https://www.instagram.com/besikraev/" target="_blank" class="author-name">Besik Raev (@besikraev)</a>
              <div style="font-size: 11px; color: var(--text-muted);">Добавлено: 15 апр. 2008 г.</div>
            </div>
            <a href="https://www.instagram.com/besikraev/" target="_blank" class="glossy-btn glossy-btn-yellow" style="margin-left: 8px;">
              + Подписаться
            </a>
          </div>
          <div class="stats-box">
            <div class="stars-rating" onclick="rateVideo()"><span>★</span><span>★</span><span>★</span><span>★</span><span>★</span></div>
            <div class="views-count" id="views-count-display">1 337 421 просмотр</div>
          </div>
        </div>
        <p style="color: #444; font-size: 12px; line-height: 1.5; margin-bottom: 10px;">
          👑 <strong>Вы были заБЕСроллены!</strong> Вы искали «{html.escape(title)}», но попались на легендарный Бесролл трека Besik Raev «Останься музыка»!
        </p>
        <!-- Action Buttons (2007 Style) -->
        <div class="action-buttons-group">
          <div class="action-buttons-primary">
            <a href="https://moscow.qtickets.events/242585-puteshestvie-v-detstvo" target="_blank" class="glossy-btn glossy-btn-red main-action-btn">
              🎟 Билеты на концерт «В детство» (19 сен) 🚂
            </a>
            <a href="#generator-section" class="glossy-btn glossy-btn-accent main-action-btn" onclick="switchTab('tab-generator')">
              😈 Разыграть друга (Создать ловушку)
            </a>
          </div>
          <div class="action-buttons-social">
            <a href="https://t.me/besik_raev" target="_blank" class="glossy-btn social-action-btn">
              ✈️ Telegram @besik_raev
            </a>
            <a href="https://www.instagram.com/besikraev/" target="_blank" class="glossy-btn social-action-btn">
              📸 Instagram @besikraev
            </a>
          </div>
        </div>
      </div>

      <!-- TABS SECTION: GENERATOR STUDIO & COMMENTS -->
      <div class="retro-box" id="generator-section">
        
        <!-- Tab Headers -->
        <div class="retro-tabs">
          <div class="retro-tab-item active" id="tab-btn-generator" onclick="switchTab('tab-generator')">
            ⚡️ Студия Ловушек (Генератор)
          </div>
          <div class="retro-tab-item" id="tab-btn-comments" onclick="switchTab('tab-comments')">
            💬 Комментарии (42)
          </div>
          <div class="retro-tab-item" id="tab-btn-about" onclick="switchTab('tab-about')">
            ℹ️ О проекте «Бесроллинг»
          </div>
        </div>

        <!-- TAB 1: GENERATOR -->
        <div id="tab-content-generator">
          <p style="color: #444; margin-bottom: 12px; font-size: 12px;">
            Вставьте ссылку на <strong>любую новость</strong> или статью — мы скопируем её официальное превью в Telegram/WhatsApp, а при открытии друг словит мгновенный Бесролл!
          </p>

          <!-- Scraper Form -->
          <div style="background: #fbf9f4; border: 1px solid #dcdad5; padding: 10px; border-radius: 4px; margin-bottom: 12px;">
            <label style="font-weight: bold; font-size: 11px; color: #555; display: block; margin-bottom: 4px;">
              🔗 ССЫЛКА НА ЛЮБУЮ НОВОСТЬ / СТАТЬЮ:
            </label>
            <div style="display: flex; gap: 6px;">
              <input type="text" id="target-url-input" class="bevel-input" placeholder="https://tass.ru/..., https://ria.ru/... или https://youtube.com/...">
              <button class="glossy-btn glossy-btn-red" id="btn-scrape" onclick="scrapeAndGenerate()">
                ⚡️ Распаковать
              </button>
            </div>
          </div>

          <!-- Quick Presets -->
          <div style="margin-bottom: 14px;">
            <div style="font-size: 11px; font-weight: bold; color: #666; margin-bottom: 4px;">ИЛИ ВЫБЕРИТЕ ШАБЛОН НОСТАЛЬГИИ:</div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
              <button class="glossy-btn" onclick="applyPreset('vhs_archive')">📼 VHS Архив 90-х</button>
              <button class="glossy-btn" onclick="applyPreset('childhood_taste')">🍬 Вкус детства</button>
              <button class="glossy-btn" onclick="applyPreset('tape_song')">📻 Песня с кассеты</button>
              <button class="glossy-btn" onclick="applyPreset('dendy_sega')">🕹 Dendy & Sega</button>
              <button class="glossy-btn" onclick="applyPreset('school_album')">📸 Школьный архив</button>
            </div>
          </div>

          <!-- Customizer Inputs -->
          <div style="display: grid; grid-template-columns: 1fr; gap: 8px; margin-bottom: 12px;">
            <div>
              <label style="font-size: 11px; font-weight: bold; color: #666;">Заголовок (будет видно в чате):</label>
              <input type="text" id="custom-title" class="bevel-input" placeholder="Сенсационный заголовок..." oninput="updateLivePreview()">
            </div>
            <div>
              <label style="font-size: 11px; font-weight: bold; color: #666;">Краткое описание:</label>
              <input type="text" id="custom-desc" class="bevel-input" placeholder="Текст превью новости..." oninput="updateLivePreview()">
            </div>
            <div>
              <label style="font-size: 11px; font-weight: bold; color: #666; display: flex; justify-content: space-between; align-items: center;">
                <span>Ссылка на картинку (обложка):</span>
                <span id="upload-status" style="font-weight: normal; color: #0033cc; font-size: 10px;"></span>
              </label>
              <div style="display: flex; gap: 6px; margin-top: 2px;">
                <input type="text" id="custom-img" class="bevel-input" placeholder="https://... или выберите файл" oninput="updateLivePreview()" onpaste="setTimeout(updateLivePreview, 50)" onchange="updateLivePreview()" style="flex: 1;">
                <input type="file" id="image-file-input" accept="image/*" style="display: none;" onchange="handleImageFileUpload(event)">
                <button type="button" class="glossy-btn" onclick="document.getElementById('image-file-input').click()" style="white-space: nowrap;">
                  📁 Загрузить фото
                </button>
              </div>
            </div>
          </div>

          <!-- Live Messenger Preview -->
          <div style="margin-bottom: 14px;">
            <label style="font-size: 11px; font-weight: bold; color: #666; display: flex; justify-content: space-between; align-items: center;">
              <span>👁 Предпросмотр карточки (Telegram / WhatsApp / VK):</span>
              <span style="font-weight: normal; color: #0033cc; font-size: 10px; cursor: pointer;" onclick="document.getElementById('image-file-input').click()">📁 Заменить фото</span>
            </label>
            <div class="retro-preview-bubble">
              <div class="retro-preview-domain" id="preview-domain">tass.ru</div>
              <div class="retro-preview-title" id="preview-title">Сенсационный заголовок появится здесь</div>
              <div class="retro-preview-desc" id="preview-desc">Краткое описание публикации...</div>
              <div class="retro-preview-img-box" onclick="document.getElementById('image-file-input').click()" title="Нажмите, чтобы загрузить свою картинку">
                <img id="preview-img" referrerpolicy="no-referrer" loading="lazy" src="https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800" class="retro-preview-img" alt="Preview" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800';">
                <div class="retro-preview-upload-badge">📁 Нажмите, чтобы изменить фото</div>
              </div>
            </div>
          </div>

          <!-- Share Result -->
          <div style="background: #eef4fb; border: 1px solid #b6d1f2; padding: 12px; border-radius: 4px;">
            <label style="font-size: 11px; font-weight: bold; color: #0033cc; display: block; margin-bottom: 4px;">
              🚀 ГОТОВАЯ ССЫЛКА-ЛОВУШКА ДЛЯ ДРУГА:
            </label>
            <input type="text" id="generated-link" class="bevel-input" readonly style="font-weight: bold; color: #0033cc; background: #ffffff;" onclick="this.select()">
            
            <div style="display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap;">
              <button class="glossy-btn glossy-btn-red" onclick="copyGeneratedLink()" style="flex: 1;">
                📋 Скопировать ссылку
              </button>
              <button class="glossy-btn" onclick="shareToTelegram()">
                ✈️ В Telegram
              </button>
              <button class="glossy-btn" onclick="shareToWhatsApp()">
                💬 В WhatsApp
              </button>
              <button class="glossy-btn" onclick="shareToVK()">
                📱 В VK
              </button>
            </div>
          </div>
        </div>

        <!-- TAB 2: COMMENTS (2008 SLANG) -->
        <div id="tab-content-comments" style="display: none;">
          <div class="retro-comment">
            <div class="comment-user-box">👤</div>
            <div>
              <span class="comment-author">xX_ShadowGamer_Xx</span>
              <span class="comment-date">10 минут назад</span>
              <div class="comment-text">Первый нах!!!! реально думал что слив той записи vhs 🤣🤣</div>
            </div>
          </div>

          <div class="retro-comment">
            <div class="comment-user-box">🎸</div>
            <div>
              <span class="comment-author">RockStar_2008</span>
              <span class="comment-date">2 часа назад</span>
              <div class="comment-text">Скинул другу в аську (ICQ) под видом таблицы сессии, он чуть со стула не упал! Беслан легенда!</div>
            </div>
          </div>

          <div class="retro-comment">
            <div class="comment-user-box">🎧</div>
            <div>
              <span class="comment-author">MusicLover_99</span>
              <span class="comment-date">вчера</span>
              <div class="comment-text">Трек у Беслана реально качает, когда в iTunes релиз? Ставлю 5 звёзд ⭐⭐⭐⭐⭐</div>
            </div>
          </div>
        </div>

        <!-- TAB 3: ABOUT -->
        <div id="tab-content-about" style="display: none;">
          <div style="background: linear-gradient(135deg, #fffdf8 0%, #fff7ea 100%); border: 2px dashed #e29547; border-radius: 8px; padding: 16px; margin-bottom: 16px; position: relative;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px dashed #e29547; padding-bottom: 8px;">
              <span style="font-size: 16px; font-weight: bold; color: #b45309;">🚂 БИЛЕТ В ДЕТСТВО</span>
              <span style="background: #cc181e; color: #fff; font-size: 10px; font-weight: bold; padding: 2px 6px; border-radius: 3px;">BESIK RAEV</span>
            </div>
            
            <h3 style="font-size: 16px; font-weight: 800; color: #1e293b; margin-bottom: 8px;">У нас есть билеты в детство! ✨</h3>
            <p style="font-size: 13px; color: #334155; line-height: 1.6; margin-bottom: 12px;">
              <strong>Поезд отправляется 19 сентября в 17:00 🚂</strong><br>
              📍 <strong>Место сбора:</strong> КДЦ «Полярный», зал «Зрительный» (ул. Полярная, 9).<br><br>
              Берите с собой хорошее настроение и пустые карманы — мы наполним их музыкой и улыбками.
            </p>

            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <a href="https://moscow.qtickets.events/242585-puteshestvie-v-detstvo" target="_blank" class="glossy-btn glossy-btn-red" style="font-weight: bold; padding: 8px 16px;">
                🎟 Плацкарт уже ждёт вас (Купить билет) 👈
              </a>
              <a href="https://t.me/besik_raev" target="_blank" class="glossy-btn" style="padding: 8px 14px;">
                ✈️ Telegram-канал @besik_raev
              </a>
            </div>
          </div>

          <div style="font-size: 12px; color: #555; line-height: 1.6;">
            <strong>Бесроллинг</strong> — это трибьют эпохе золотого интернета 2007-2008 годов и легендарному Рикроллу (Rickrolling).<br>
            Проект создан для вирусного продвижения авторского трека артиста <strong>Besik Raev</strong> «Останься музыка».<br><br>
            Официальные страницы артиста:
            <a href="https://t.me/besik_raev" target="_blank" style="color: var(--text-link); font-weight: bold;">Telegram @besik_raev</a> •
            <a href="https://www.instagram.com/besikraev/" target="_blank" style="color: var(--text-link); font-weight: bold;">Instagram @besikraev</a>.
          </div>
        </div>

      </div>

    </main>

    <aside class="side-column">
      <div class="retro-box">
        <div class="retro-box-header"><span>Артист проекта</span></div>
        <div style="text-align: center; padding: 6px 0;">
          <img src="/assets/beslan_avatar.png" style="width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 2px solid #cc181e; box-shadow: 0 2px 8px rgba(0,0,0,0.2); margin-bottom: 8px;" alt="Besik Raev">
          <div style="font-size: 15px; font-weight: bold; color: #111;">Besik Raev</div>
          <div style="color: #666; font-size: 11px; margin-top: 2px;">Концерт «Путешествие в детство» 🚂</div>
          <div style="font-size: 11px; color: #b45309; font-weight: bold; margin-top: 4px; background: #fff7ea; border: 1px dashed #e29547; border-radius: 4px; padding: 4px;">
            19 сентября • 17:00 • КДЦ «Полярный»
          </div>
          <a href="https://moscow.qtickets.events/242585-puteshestvie-v-detstvo" target="_blank" class="glossy-btn glossy-btn-red" style="margin-top: 10px; width: 100%; justify-content: center; font-weight: 800;">
            🎟 Купить билет (Плацкарт)
          </a>
          <a href="https://t.me/besik_raev" target="_blank" class="glossy-btn" style="margin-top: 6px; width: 100%; justify-content: center;">
            ✈️ Telegram @besik_raev
          </a>
        </div>
      </div>

      <!-- Related Videos (Presets) -->
      <div class="retro-box">
        <div class="retro-box-header">
          <span>Похожие видео (Шаблоны)</span>
        </div>

        <div class="related-video-item" onclick="applyPreset('vhs_archive')">
          <div class="related-thumb-box">
            <img src="https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=200" class="related-thumb-img">
            <span class="related-timestamp">4:20</span>
          </div>
          <div>
            <div class="related-title">📼 VHS 1997: Школьная дискотека 11 «Б»</div>
            <div class="related-author">АрхивРетро90</div>
            <div class="related-views">1,240,500 просмотров</div>
          </div>
        </div>

        <div class="related-video-item" onclick="applyPreset('childhood_taste')">
          <div class="related-thumb-box">
            <img src="https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?w=200" class="related-thumb-img">
            <span class="related-timestamp">3:15</span>
          </div>
          <div>
            <div class="related-title">🍬 Вкус 90-х: Возвращение жвачек Turbo и Yupi</div>
            <div class="related-author">Ностальгия90</div>
            <div class="related-views">890,200 просмотров</div>
          </div>
        </div>

        <div class="related-video-item" onclick="applyPreset('tape_song')">
          <div class="related-thumb-box">
            <img src="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=200" class="related-thumb-img">
            <span class="related-timestamp">3:45</span>
          </div>
          <div>
            <div class="related-title">📻 Та самая песня с кассеты из 1999 года</div>
            <div class="related-author">КассетныйМагнитофон</div>
            <div class="related-views">3,420,100 просмотров</div>
          </div>
        </div>

        <div class="related-video-item" onclick="applyPreset('dendy_sega')">
          <div class="related-thumb-box">
            <img src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=200" class="related-thumb-img">
            <span class="related-timestamp">5:12</span>
          </div>
          <div>
            <div class="related-title">🕹 1000 игр Dendy и Sega онлайн в браузере</div>
            <div class="related-author">DendyClub_Old</div>
            <div class="related-views">1,670,300 просмотров</div>
          </div>
        </div>

        <div class="related-video-item" onclick="applyPreset('school_album')">
          <div class="related-thumb-box">
            <img src="https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=200" class="related-thumb-img">
            <span class="related-timestamp">1:50</span>
          </div>
          <div>
            <div class="related-title">📸 Оцифрованный архив выпускников 1995–2005</div>
            <div class="related-author">ШкольныйАрхив</div>
            <div class="related-views">980,500 просмотров</div>
          </div>
        </div>

      </div>
    </aside>
  </div>

  <!-- DVD Screensaver Floating Meme Pill -->
  <div id="dvd-pill">👑 <span>Вы были заБЕСроллены!</span></div>

  <script src="/js/app.js"></script>
</body>
</html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(trap_html.encode('utf-8'))
            return

        super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)

                # Forward multipart body to tmpfiles.org
                req = urllib.request.Request(
                    'https://tmpfiles.org/api/v1/upload',
                    data=body,
                    headers={
                        'Content-Type': content_type,
                        'User-Agent': 'Mozilla/5.0'
                    }
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    res_json = json.loads(resp.read().decode('utf-8'))
                    if res_json and res_json.get('data') and res_json['data'].get('url'):
                        public_url = res_json['data']['url'].replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                        self.send_json({'success': True, 'url': public_url})
                        return
                self.send_json({'success': False, 'error': 'Upload failed'}, 502)
            except Exception as e:
                self.send_json({'success': False, 'error': str(e)}, 500)
            return

        self.send_json({'error': 'Not found'}, 404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

if __name__ == '__main__':
    server_address = ('', PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, BesrollHandler)
    print(f"==================================================", flush=True)
    print(f"🚀 Retro 2008 «BesTube» запущен на http://localhost:{PORT}", flush=True)
    print(f"==================================================", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.", flush=True)

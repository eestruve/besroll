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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

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
        <div class="cookie-modal-subtext">
          Нажимая кнопку, вы подтверждаете согласие на воспроизведение медиаматериалов (18+).
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 2: 2007 RETRO YOUTUBE PLAYER & HUNTER STUDIO (Plays unmuted on reveal) -->
  <header class="retro-header">
    <div class="retro-header-inner">
      <a href="/index.html" class="yt-logo">Bes<span class="logo-box">Roll</span></a>
      <div class="header-search">
        <input type="text" value="{html.escape(title)}" readonly>
        <button class="glossy-btn">Поиск</button>
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
          <iframe id="beslan-iframe" src="about:blank" width="100%" height="100%" frameborder="0" scrolling="no" allow="autoplay; clipboard-write; encrypted-media"></iframe>
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
          👑 <strong>Вы были забесролены!</strong> Вы искали «{html.escape(title)}», но попались на легендарный Бесролл трека Besik Raev «Останься музыка»!
        </p>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <a href="https://moscow.qtickets.events/242585-puteshestvie-v-detstvo" target="_blank" class="glossy-btn glossy-btn-red" style="font-weight: 800; padding: 6px 16px;">
            🎟 Билеты на концерт «В детство» (19 сен) 🚂
          </a>
          <a href="#hunter-studio" class="glossy-btn glossy-btn-yellow" style="font-weight: bold;">
            😈 Разыграть друга этой ссылкой
          </a>
          <a href="https://t.me/besik_raev" target="_blank" class="glossy-btn">
            ✈️ Telegram @besik_raev
          </a>
        </div>
      </div>

      <div class="retro-box" id="hunter-studio">
        <div class="retro-box-header"><span>⚡️ Очередь за тобой: Разыграй друга за 5 секунд!</span></div>
        <p style="color: #444; font-size: 12px; margin-bottom: 10px;">Вставь ссылку на любую новость — мы создадим точно такое же превью, а друг попадет на Бесролл!</p>
        <div style="background: #fbf9f4; border: 1px solid #dcdad5; padding: 10px; border-radius: 4px; margin-bottom: 10px;">
          <label style="font-size: 11px; font-weight: bold; color: #555; display: block; margin-bottom: 4px;">ССЫЛКА НА НОВОСТЬ:</label>
          <div style="display: flex; gap: 6px;">
            <input type="text" id="target-url-input" class="bevel-input" placeholder="https://ria.ru/... или https://tass.ru/...">
            <button class="glossy-btn glossy-btn-red" id="btn-scrape" onclick="scrapeAndGenerate()">⚡️ Распаковать</button>
          </div>
        </div>
        <div style="background: #eef4fb; border: 1px solid #b6d1f2; padding: 10px; border-radius: 4px;">
          <label style="font-size: 11px; font-weight: bold; color: #0033cc; display: block; margin-bottom: 4px;">ГОТОВАЯ ССЫЛКА ДЛЯ ДРУГА:</label>
          <input type="text" id="generated-link" class="bevel-input" readonly style="color: #0033cc; font-weight: bold; background: #fff;" onclick="this.select()">
          <div style="display: flex; gap: 6px; margin-top: 8px;">
            <button class="glossy-btn glossy-btn-red" onclick="copyGeneratedLink()" style="flex: 1;">📋 Скопировать</button>
            <button class="glossy-btn" onclick="shareToTelegram()">✈️ Telegram</button>
            <button class="glossy-btn" onclick="shareToWhatsApp()">💬 WhatsApp</button>
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

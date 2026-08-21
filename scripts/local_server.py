import http.server
import os
import urllib.parse
import urllib.request
import json
import base64
import re
import html
import sys

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
            except Exception as e:
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
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  <meta name="twitter:image" content="{html.escape(image)}">
  <link rel="stylesheet" href="/css/style.css">
</head>
<body class="trap-page">
  <div class="container" id="bait-view">
    <div class="glass-card bait-card">
      <div class="header-badge">⚡️ Эксклюзивный материал</div>
      <h1 class="bait-title">{html.escape(title)}</h1>
      <div class="bait-image-box" onclick="triggerBesroll()">
        <img src="{html.escape(image)}" alt="Preview" class="bait-img" />
        <div class="play-overlay">
          <div class="play-pulse-btn">▶</div>
          <span>Нажмите для просмотра</span>
        </div>
      </div>
      <p class="bait-desc">{html.escape(description)}</p>
      <button class="pulse-button" onclick="triggerBesroll()" style="margin-top: 20px; width: 100%; justify-content: center;">
        <span>🔥 Читать / Смотреть материал</span>
      </button>
    </div>
  </div>

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
      <a href="#hunter-studio" class="btn btn-primary" onclick="document.getElementById('hunter-studio').scrollIntoView({{behavior:'smooth'}})">
        😈 Разыграть друга (Создать ловушку)
      </a>
      <a href="https://www.instagram.com/reel/DcQU8MDAMpV/" target="_blank" class="btn btn-secondary">
        🎵 Полный трек в Instagram
      </a>
    </div>
    <div id="hunter-studio" class="glass-card" style="margin-top: 20px; width: 100%; max-width: 680px; text-align: left;">
      <div class="header-badge" style="background: rgba(0, 242, 254, 0.2); color: #00f2fe;">🎯 Очередь за тобой</div>
      <h2>Разыграй друга за 5 секунд</h2>
      <p class="subtitle" style="font-size: 0.95rem;">Вставь ссылку на любую новость — мы создадим точно такое же превью, а друг попадет на Беслана!</p>
      <div style="background: rgba(0,0,0,0.3); padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.08);">
        <label class="input-label">ССЫЛКА НА НОВОСТЬ:</label>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
          <input type="text" id="target-url-input" class="input-field" placeholder="https://ria.ru/... или https://tass.ru/..." style="flex: 1; min-width: 200px;">
          <button class="btn btn-primary" id="btn-scrape" onclick="scrapeAndGenerate()">⚡️ Распаковать</button>
        </div>
      </div>
      <div style="margin-top: 14px;">
        <label class="input-label">ГОТОВАЯ ССЫЛКА-ЛОВУШКА ДЛЯ ДРУГА:</label>
        <input type="text" id="generated-link" class="input-field" readonly style="color: var(--accent-cyan); background: rgba(0,0,0,0.5);" onclick="this.select()">
        <div style="display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;">
          <button class="btn btn-primary" onclick="copyGeneratedLink()" style="flex: 1;">📋 Скопировать ссылку</button>
          <button class="btn btn-secondary" onclick="shareToTelegram()">✈️ В Telegram</button>
          <button class="btn btn-secondary" onclick="shareToWhatsApp()">💬 В WhatsApp</button>
        </div>
      </div>
    </div>
  </div>

  <script src="/js/app.js"></script>
</body>
</html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(trap_html.encode('utf-8'))
            return

        # 3. Default static files
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
    print(f"🚀 Сервер «Бесроллинг» запущен на http://localhost:{PORT}", flush=True)
    print(f"==================================================", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.", flush=True)

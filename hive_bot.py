import os
import time
import urllib.request
import xml.etree.ElementTree as ET
import html
import re
from beem import Hive

# --- CONFIGURACIÓN ---
USERNAME = "predathorhaley" # Tu usuario de Hive
POSTING_KEY = os.environ.get("HIVE_POSTING_KEY")

if not POSTING_KEY:
    print("❌ Error: Falta la HIVE_POSTING_KEY en las variables de entorno.")
    exit(1)

hive = Hive(keys=[POSTING_KEY], node="https://api.hive.blog")

def get_news():
    """Descarga las últimas noticias de un feed RSS de cripto."""
    url = "https://cointelegraph.com/rss"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        data = urllib.request.urlopen(req, timeout=15).read()
        root = ET.fromstring(data)
        item = root.find(".//item") # Toma la primera noticia
        
        title = item.findtext("title")
        link = item.findtext("link")
        desc = item.findtext("description")
        
        # Limpiar el HTML de la descripción
        desc_clean = html.unescape(re.sub(r"<[^>]+>", " ", desc or ""))
        desc_clean = re.sub(r"\s+", " ", desc_clean).strip()
        
        return title, link, desc_clean
    except Exception as e:
        print(f"Error obteniendo noticias: {e}")
        return None, None, None

def publish_to_hive():
    title, link, desc = get_news()
    if not title:
        print("No se encontraron noticias nuevas.")
        return

    # Armar el cuerpo del post para Hive
    body = f"""
**{title}**

{desc}

🔗 **Lee la noticia completa aquí:** [{link}]({link})

---
*Este post fue publicado automáticamente por mi bot de Termux usando la librería `beem`.*
#bitcoin #crypto #news #criptomonedas
"""
    
    # Generar un permlink único (URL del post) seguro para Hive
    clean_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    permlink = f"{clean_title[:40]}-{int(time.time())}"
    tags = ["bitcoin", "crypto", "news", "criptomonedas", "leofinance"]

    try:
        print(f"🚀 Publicando noticia: {title}")
        hive.post(
            title=title[:100], # Hive limita el título a 100 caracteres
            body=body,
            author=USERNAME,
            permlink=permlink,
            tags=tags,
            app="hive-auto-bot/1.0"
        )
        print(f"✅ Publicado con éxito: https://ecency.com/@{USERNAME}/{permlink}")
        
        # Votar por nuestro propio post para ganar curación (opcional)
        time.sleep(3) # Pequeña pausa para evitar errores en la blockchain
        hive.vote(weight=10000, identifier=f"@{USERNAME}/{permlink}")
        print("👍 Voto propio emitido.")
        
    except Exception as e:
        print(f"❌ Error al publicar: {e}")

if __name__ == "__main__":
    publish_to_hive()

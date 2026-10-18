import os
import time
import json
import urllib.request
import xml.etree.ElementTree as ET
import html
import re
import random
from beem import Hive
from beem.account import Account

USERNAME = "predathorhaley"
POSTING_KEY = os.environ.get("HIVE_POSTING_KEY")
REPO_URL = "https://raw.githubusercontent.com/alfrexo95/Hive-Auto-Bot/main/media/"
STATE_FILE = "hive_state.json"

if not POSTING_KEY:
    exit(1)

hive = Hive(keys=[POSTING_KEY], node="https://api.hive.blog")
account = Account(USERNAME, blockchain_instance=hive)

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"media_index": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def check_rc():
    rc = account.get_rc_manabar()
    rc_pct = (rc['current_mana'] / rc['max_mana']) * 100
    print(f"🔋 RC: {rc_pct:.2f}%")
    return rc_pct > 15.0 # Requiere al menos 15% de RC

def get_news():
    url = "https://cointelegraph.com/rss"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        root = ET.fromstring(data)
        item = root.find(".//item")
        title, link, desc = item.findtext("title"), item.findtext("link"), item.findtext("description")
        desc_clean = html.unescape(re.sub(r"<[^>]+>", " ", desc or ""))
        return title, link, re.sub(r"\s+", " ", desc_clean).strip()
    except Exception as e:
        return None, None, None

def post_news():
    title, link, desc = get_news()
    if not title: return
    body = f"**{title}**\n\n{desc}\n\n🔗 **Source:** [{link}]({link})\n\n---\n*Automated crypto news by @predathorhaley.*\n#bitcoin #crypto #news #leofinance"
    clean_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    permlink = f"{clean_title[:40]}-{int(time.time())}"
    try:
        print(f"🚀 Noticia: {title[:50]}")
        hive.post(title=title[:100], body=body, author=USERNAME, permlink=permlink, tags=["bitcoin", "crypto", "news", "leofinance"], app="hive-bot/1.0")
        time.sleep(3)
        hive.vote(weight=10000, identifier=f"@{USERNAME}/{permlink}")
    except Exception as e:
        print(f"❌ Error: {e}")

def post_cuba_campaign():
    state = load_state()
    
    # Buscar archivos multimedia válidos
    valid_ext = ('.jpg', '.jpeg', '.png', '.gif', '.mp4')
    try:
        files = sorted([f for f in os.listdir('media') if f.lower().endswith(valid_ext)])
    except FileNotFoundError:
        files = []
        
    media_markdown = ""
    
    if files:
        # Rotar la imagen (bucle infinito)
        idx = state["media_index"] % len(files)
        selected_file = files[idx]
        media_url = f"{REPO_URL}{selected_file}"
        
        if selected_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            media_markdown = f"![Evidence]({media_url})\n\n"
        elif selected_file.lower().endswith('.mp4'):
            media_markdown = f"[Ver Video de Evidencia]({media_url})\n\n"
            
        state["media_index"] = idx + 1
        save_state(state)
        print(f"📸 Adjuntando evidencia: {selected_file}")

    body = f"""🚨 **Help Cuban Families Survive the Crisis** 🇨🇺\n\n{media_markdown}The blockade makes traditional international transfers almost impossible. We rely on decentralized money and social networks to deliver food, medicine, and shelter directly to those in need.\n\nIf you want to support this cause, please **upvote this post**. Every vote helps this message reach more people and generates funds for the community.\n\n⚡ **Lightning:** olivinepug15@primal.net\n\n*Follow me for more updates on freedom tech and crypto.*\n\n#cuba #solidarity #bitcoin #hive #leofinance"""
    
    permlink = f"help-cuban-families-{int(time.time())}"
    try:
        print("🚀 Publicando campaña con evidencia...")
        hive.post(title="Help Cuban Families: Freedom From Blockade", body=body, author=USERNAME, permlink=permlink, tags=["cuba", "solidarity", "bitcoin", "hive", "leofinance"], app="hive-bot/1.0")
        time.sleep(3)
        hive.vote(weight=10000, identifier=f"@{USERNAME}/{permlink}")
    except Exception as e:
        print(f"❌ Error en campaña: {e}")

def engage_elite():
    try:
        results = hive.get_discussions("created", "leofinance", limit=5)
        for post in results:
            if post["author"] == USERNAME: continue
            comment_body = random.choice([
                "This is a great perspective on decentralized finance. The future is bright! 🚀",
                "Excellent analysis. It's amazing to see how fast the crypto ecosystem is evolving. ⚡",
                "Thanks for sharing this. I believe freedom tech like this is crucial for global adoption. 🌍"
            ])
            print(f"💬 Comentando en @{post['author']}...")
            hive.post(title="", body=comment_body, author=USERNAME, permlink=f"re-{post['author']}-{int(time.time())}", reply_identifier=f"@{post['author']}/{post['permlink']}", tags=["hive"])
            time.sleep(2)
            hive.vote(weight=5000, identifier=f"@{post['author']}/{post['permlink']}")
            break
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if not check_rc(): exit(0)
    hora = time.gmtime().tm_hour
    if hora < 8: post_news()
    elif hora < 16: engage_elite()
    else: post_cuba_campaign()

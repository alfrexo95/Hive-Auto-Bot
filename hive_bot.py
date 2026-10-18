import os
import sys
import time
import json
import urllib.request
import urllib.parse
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
    print("❌ Error: Falta HIVE_POSTING_KEY")
    exit(1)

hive = Hive(keys=[POSTING_KEY], node="https://api.hive.blog")
account = Account(USERNAME, blockchain_instance=hive)

# --- TEXTOS Y CONTENIDO ---
MY_BIO = {
    "name": "PredathorHaley 🇨🇺",
    "about": "Ex-special forces, close protection, MMA & Muay Thai. Building freedom tech with Termux on low resources from Cuba. Documenting the reality of the blockade and using crypto to help vulnerable families. ⚡ #Bitcoin #Nostr #Hive",
    "location": "Cuba",
    "website": "https://primal.net/p/npub1..."
}

CUBA_MESSAGES = [
    "The economic crisis in Cuba is pushing vulnerable families to the brink. Famine and lack of medicine are daily realities. Your support saves lives.",
    "Traditional aid is often blocked. We use decentralized tech to deliver food and medicine directly to families in need.",
    "Every sat goes directly to families in Cuba. We document everything with photos and videos because transparency is key.",
    "Poverty and hunger should not exist. Support our mission to bring food and medicine to vulnerable Cubans by upvoting this post."
]

TERMUX_STORIES = [
    "People ask me how I build tech in Cuba. The answer: Termux on a cheap Android phone. No expensive servers, just pure curiosity and the power of Linux in my pocket. We build freedom tech with whatever we have. 💻⚡",
    "The economic blockade limits our access to hardware and software. But open-source tools like Termux and Python break the barriers. I can automate bots, run nodes, and connect to the global crypto economy from my phone. Tech resilience is real. 🛠️🌍",
    "Resilience means finding a way when there is no clear path. With Termux, I turned a basic smartphone into a development environment. Now I run automated scripts, interact with blockchains, and build communities. Never underestimate the power of a phone and an internet connection. 🇨🇺🚀",
    "I'm an enthusiast of technology and crypto. In Cuba, having access to a smartphone is a blessing, but knowing how to use it to build and generate income is the real game-changer. Termux is my gateway to the decentralized world. 🔑💻"
]

FINANCIAL_QUOTES = [
    "“Bitcoin is the first time we have a truly scarce digital asset. It's the hardest money ever created.” - Saifedean Ammous",
    "“The root problem with conventional currency is all the trust that's required to make it work.” - Satoshi Nakamoto",
    "“Privacy is not something that I'm merely entitled to, it's an absolute prerequisite.” - Marlon Brando (Relevant for Crypto)",
    "“Not your keys, not your coins. Self-custody is the only way to true financial freedom.”",
    "“Decentralization is not just a buzzword; it's the architecture of freedom.”",
    "“In a world of inflation, saving in Bitcoin is an act of rebellion.”"
]

HIVE_LEADERS = ["@leofinance", "@khaleelkazi", "@theycallmedan", "@taskmaster4450"]

# --- FUNCIONES DEL SISTEMA ---
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"media_index": 0, "action_index": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def check_rc():
    rc = account.get_rc_manabar()
    rc_pct = (rc['current_mana'] / rc['max_mana']) * 100
    print(f"🔋 RC: {rc_pct:.2f}%")
    # Si el RC baja del 20%, abortamos para no bloquear la cuenta
    if rc_pct < 20.0:
        print("⚠️ RC muy bajos. Se cancela la acción para proteger la cuenta.")
        return False
    return True

# --- FUNCIONES DE PUBLICACIÓN ---
def update_profile():
    print("👤 Actualizando perfil con la bio...")
    try:
        account.update_profile(MY_BIO)
        print("✅ Perfil actualizado correctamente.")
    except Exception as e:
        print(f"❌ Error al actualizar perfil: {e}")

def get_news(url):
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
    title, link, desc = get_news("https://cointelegraph.com/rss")
    if not title: return
    body = f"**{title}**\n\n{desc}\n\n🔗 **Source:** [{link}]({link})\n\n---\n*Automated crypto news by @predathorhaley.*\n#bitcoin #crypto #news #leofinance"
    clean_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    permlink = f"news-{clean_title[:40]}-{int(time.time())}"
    try:
        print(f"🚀 Noticia: {title[:50]}")
        hive.post(title=title[:100], body=body, author=USERNAME, permlink=permlink, tags=["bitcoin", "crypto", "news", "leofinance"], app="hive-bot/2.0")
        time.sleep(2)
        hive.vote(weight=10000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
    except Exception as e:
        print(f"❌ Error: {e}")

def post_termux_story():
    story = random.choice(TERMUX_STORIES)
    permlink = f"termux-journey-{int(time.time())}"
    body = f"{story}\n\n---\n*Building freedom tech from Cuba.*\n#termux #linux #crypto #hive #freedomtech"
    try:
        print("🚀 Publicando historia de Termux/Resiliencia...")
        hive.post(title="Building Tech with Termux from Cuba", body=body, author=USERNAME, permlink=permlink, tags=["termux", "linux", "crypto", "hive", "freedomtech"], app="hive-bot/2.0")
        time.sleep(2)
        hive.vote(weight=10000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
    except Exception as e:
        print(f"❌ Error: {e}")

def post_financial_quote():
    quote = random.choice(FINANCIAL_QUOTES)
    permlink = f"crypto-wisdom-{int(time.time())}"
    body = f"💡 **Crypto & Financial Wisdom**\n\n> {quote}\n\n---\n*Stay humble, stack sats.*\n#crypto #bitcoin #finance #hive #leofinance"
    try:
        print("🚀 Publicando frase financiera...")
        hive.post(title="Daily Crypto Wisdom", body=body, author=USERNAME, permlink=permlink, tags=["crypto", "bitcoin", "finance", "hive", "leofinance"], app="hive-bot/2.0")
        time.sleep(2)
        hive.vote(weight=10000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
    except Exception as e:
        print(f"❌ Error: {e}")

def post_cuba_campaign():
    state = load_state()
    valid_ext = ('.jpg', '.jpeg', '.png', '.gif', '.mp4')
    
    try:
        files = sorted([f for f in os.listdir('media') if f.lower().endswith(valid_ext) and f != 'LEEME.txt'])
    except FileNotFoundError:
        print("❌ Carpeta media no encontrada.")
        return
        
    if not files:
        print("❌ No hay archivos multimedia en media/")
        return
        
    idx = state.get("media_index", 0) % len(files)
    selected_file = files[idx]
    
    # Corrección de nombres con espacios o tildes
    safe_filename = urllib.parse.quote(selected_file)
    media_url = f"{REPO_URL}{safe_filename}"
    
    if selected_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        media_markdown = f"![Evidence]({media_url})\n\n"
    else:
        media_markdown = f"[▶️ **Watch Video Evidence Here**]({media_url})\n\n"
        
    message = random.choice(CUBA_MESSAGES)
    leaders_str = " ".join(random.sample(HIVE_LEADERS, 2))
    
    body = f"""🚨 **Help Cuban Families Survive the Crisis** 🇨🇺\n\n{message}\n\n{media_markdown}**How you can help:**\nIf you want to support this cause, please **upvote this post**. Every vote helps this message reach more people and generates funds.\n\n⚡ **Lightning Donations:** olivinepug15@primal.net\n\nCc: {leaders_str}\n\n#cuba #solidarity #bitcoin #hive #leofinance #humanitarian"""
    
    permlink = f"help-cuban-families-{int(time.time())}"
    try:
        print(f"🚀 Campaña Cuba con evidencia: {selected_file}")
        hive.post(title="Help Cuban Families: The Reality of the Crisis", body=body, author=USERNAME, permlink=permlink, tags=["cuba", "solidarity", "bitcoin", "hive", "leofinance"], app="hive-bot/2.0")
        time.sleep(2)
        hive.vote(weight=10000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
        
        state["media_index"] = idx + 1
        save_state(state)
    except Exception as e:
        print(f"❌ Error en campaña: {e}")

def engage_elite():
    try:
        # Buscamos posts populares en las etiquetas top de Hive
        results = hive.get_discussions("created", "leofinance", limit=5)
        for post in results:
            if post["author"] == USERNAME: continue
            
            comment_body = random.choice([
                "This is a great perspective on decentralized finance. The future is bright! 🚀",
                "Excellent analysis. It's amazing to see how fast the crypto ecosystem is evolving. ⚡",
                "Thanks for sharing this. I believe freedom tech like this is crucial for global adoption. 🌍",
                "Spot on. The separation of money and state is inevitable. Upvoted! 💯"
            ])
            print(f"💬 Comentando e interactuando con @{post['author']}...")
            hive.post(title="", body=comment_body, author=USERNAME, permlink=f"re-{post['author']}-{int(time.time())}", reply_identifier=f"@{post['author']}/{post['permlink']}", tags=["hive"])
            time.sleep(2)
            hive.vote(weight=5000, identifier=f"@{post['author']}/{post['permlink']}", voter=USERNAME)
            break
    except Exception as e:
        print(f"❌ Error en interacción: {e}")

# --- LÓGICA DE EJECUCIÓN EN BUCLE INFINITO ---
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "update_profile":
        update_profile()
        exit(0)

    if not check_rc(): exit(0)
    
    # Lista de acciones en el orden del bucle
    actions = [
        post_news,
        post_termux_story,
        engage_elite,
        post_financial_quote,
        post_cuba_campaign
    ]
    
    state = load_state()
    current_action = state.get("action_index", 0)
    
    # Ejecutar la acción correspondiente
    print(f"🔄 Ejecutando acción {current_action + 1}/{len(actions)} del bucle...")
    actions[current_action]()
    
    # Avanzar el índice para la próxima vez (bucle infinito)
    state["action_index"] = (current_action + 1) % len(actions)
    save_state(state)
    print(f"✅ Acción completada. Próxima acción: {state['action_index'] + 1}")

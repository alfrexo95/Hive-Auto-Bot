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
from beem.comment import Comment
from beem.vote import Vote

USERNAME = "predathorhaley"
POSTING_KEY = os.environ.get("HIVE_POSTING_KEY")
REPO_URL = "https://raw.githubusercontent.com/alfrexo95/Hive-Auto-Bot/main/media/"
STATE_FILE = "hive_state.json"

if not POSTING_KEY:
    print("❌ Error: Falta HIVE_POSTING_KEY")
    exit(1)

hive = Hive(keys=[POSTING_KEY], node="https://api.hive.blog")
account = Account(USERNAME, blockchain_instance=hive)

# --- CONFIGURACIÓN DEL BOT ---
MIN_VOTING_POWER = 80.0  
MIN_RC = 15.0            
MAX_POST_AGE_HOURS = 3   
TARGET_COMMUNITIES = ["hive-167922", "hive-150207", "hive-148441"] 

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
    "“Not your keys, not your coins. Self-custody is the only way to true financial freedom.”",
    "“Decentralization is not just a buzzword; it's the architecture of freedom.”",
    "“In a world of inflation, saving in Bitcoin is an act of rebellion.”"
]

ELITE_COMMENTS = [
    "This is a really interesting take on the current state of DeFi. I appreciate the depth of analysis here, especially regarding liquidity. It makes me think about how these mechanisms will evolve. Thanks for sharing this!",
    "Great breakdown of the technical challenges. I've been following this project for a while and your analysis adds a lot of nuance to the conversation. The part about scalability is spot on.",
    "I hadn't considered this angle before. The way you connected the economic incentives with the technical implementation is brilliant. This is the kind of content that makes Hive such a valuable platform. Upvoted!",
    "Thanks for putting this together. The data you shared really highlights the potential we're looking at. Do you think this trend will continue into the next quarter? I'd love to hear your thoughts.",
    "Excellent write-up! It's refreshing to see such a well-researched post. I especially agree with your point about user adoption being the key factor. Keep up the great work!"
]

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"media_index": 0, "action_index": 0}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_voting_power():
    vp = account.get_voting_power()
    print(f"🗳️ Voting Power: {vp:.2f}%")
    return vp

def get_rc_percentage():
    rc = account.get_rc_manabar()
    rc_pct = (rc['current_mana'] / rc['max_mana']) * 100
    print(f"🔋 Resource Credits: {rc_pct:.2f}%")
    return rc_pct

def check_health():
    vp = get_voting_power()
    rc_pct = get_rc_percentage()
    
    if vp < MIN_VOTING_POWER:
        print(f"⚠️ Voting Power por debajo del {MIN_VOTING_POWER}%. Se posponen las acciones.")
        return False
    if rc_pct < MIN_RC:
        print(f"⚠️ Resource Credits por debajo del {MIN_RC}%. Se cancelan las acciones.")
        return False
    
    print("✅ Salud de la cuenta óptima. Procediendo.")
    return True

def post_with_community(title, body, permlink, tags, community_id):
    try:
        full_body = f"{body}\n\n---\n*Published via Hive Auto Bot. Created by PredathorHaley.*"
        account.post(
            title=title[:100],
            body=full_body,
            permlink=permlink,
            tags=tags,
            app="hive-bot/2.0",
            beneficiaries=[{"account": USERNAME, "weight": 10000}] 
        )
        print(f"✅ Publicado en la comunidad {community_id} con éxito.")
        return True
    except Exception as e:
        print(f"❌ Error al publicar en comunidad: {e}")
        return False

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
    if not title:
        print("❌ No se pudo obtener la noticia.")
        return False
    
    body = f"**{title}**\n\n{desc}\n\n🔗 **Source:** [{link}]({link})\n\n#bitcoin #crypto #news #leofinance"
    clean_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    permlink = f"news-{clean_title[:40]}-{int(time.time())}"
    
    success = post_with_community(title, body, permlink, ["bitcoin", "crypto", "news", "leofinance", "hive-167922"], "hive-167922")
    if success:
        account.vote(weight=5000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
        print("👍 Voto propio emitido.")
    return success

def post_termux_story():
    story = random.choice(TERMUX_STORIES)
    permlink = f"termux-journey-{int(time.time())}"
    body = f"{story}\n\n#termux #linux #crypto #hive #freedomtech"
    
    success = post_with_community("Building Tech with Termux from Cuba", body, permlink, ["termux", "linux", "crypto", "hive", "freedomtech"], "hive-148441")
    if success:
        account.vote(weight=5000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
        print("👍 Voto propio emitido.")
    return success

def post_financial_quote():
    quote = random.choice(FINANCIAL_QUOTES)
    permlink = f"crypto-wisdom-{int(time.time())}"
    body = f"💡 **Crypto & Financial Wisdom**\n\n> {quote}\n\n#crypto #bitcoin #finance #leofinance"
    
    success = post_with_community("Daily Crypto Wisdom", body, permlink, ["crypto", "bitcoin", "finance", "leofinance", "hive-167922"], "hive-167922")
    if success:
        account.vote(weight=5000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
        print("👍 Voto propio emitido.")
    return success

def post_cuba_campaign():
    state = load_state()
    valid_ext = ('.jpg', '.jpeg', '.png', '.gif', '.mp4')
    
    try:
        files = sorted([f for f in os.listdir('media') if f.lower().endswith(valid_ext) and f != 'LEEME.txt'])
    except FileNotFoundError:
        print("❌ Carpeta media no encontrada.")
        return False
    
    if not files:
        print("❌ No hay archivos multimedia en media/")
        return False
    
    idx = state.get("media_index", 0) % len(files)
    selected_file = files[idx]
    safe_filename = urllib.parse.quote(selected_file)
    media_url = f"{REPO_URL}{safe_filename}"
    
    if selected_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        media_markdown = f"![Evidence]({media_url})\n\n"
    else:
        media_markdown = f"[▶️ **Watch Video Evidence Here**]({media_url})\n\n"
    
    message = random.choice(CUBA_MESSAGES)
    
    body = f"""🚨 **Help Cuban Families Survive the Crisis** 🇨🇺\n\n{message}\n\n{media_markdown}**How you can help:**\nIf you want to support this cause, please **upvote this post**. Every vote helps this message reach more people.\n\n⚡ **Lightning Donations:** olivinepug15@primal.net\n\n#cuba #solidarity #bitcoin #hive #humanitarian"""
    
    permlink = f"help-cuban-families-{int(time.time())}"
    success = post_with_community("Help Cuban Families: The Reality of the Crisis", body, permlink, ["cuba", "solidarity", "bitcoin", "hive", "humanitarian"], "hive-148441")
    if success:
        account.vote(weight=5000, identifier=f"@{USERNAME}/{permlink}", voter=USERNAME)
        state["media_index"] = idx + 1
        save_state(state)
        print("✅ Campaña publicada y auto-votada.")
    return success

def engage_elite():
    try:
        for community in TARGET_COMMUNITIES:
            results = hive.get_discussions("created", community, limit=3)
            for post in results:
                if post["author"] == USERNAME:
                    continue
                
                post_age_seconds = time.time() - post["created"].timestamp()
                post_age_hours = post_age_seconds / 3600
                
                if post_age_hours > MAX_POST_AGE_HOURS:
                    print(f"⏳ Post de @{post['author']} es muy antiguo. Saltando.")
                    continue
                
                comment_body = random.choice(ELITE_COMMENTS)
                print(f"💬 Comentando en el post de @{post['author']} en {community}...")
                
                account.post(
                    title="",
                    body=comment_body,
                    permlink=f"re-{post['author']}-{int(time.time())}",
                    reply_identifier=f"@{post['author']}/{post['permlink']}",
                    tags=["hive"]
                )
                time.sleep(3)
                account.vote(weight=3000, identifier=f"@{post['author']}/{post['permlink']}", voter=USERNAME)
                print("✅ Interacción completada (comentario + voto).")
                return True
        
        print("No se encontraron posts nuevos para interactuar.")
        return False
    except Exception as e:
        print(f"❌ Error en interacción: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "update_profile":
        account.update_profile({
            "name": "PredathorHaley 🇨🇺",
            "about": "Ex-special forces, close protection, MMA & Muay Thai. Building freedom tech with Termux on low resources from Cuba. Documenting the reality of the blockade and using crypto to help vulnerable families. ⚡ #Bitcoin #Nostr #Hive",
            "location": "Cuba",
            "website": "https://primal.net/p/npub1..."
        })
        exit(0)

    if not check_health():
        exit(0)

    actions = [
        post_news,
        post_termux_story,
        engage_elite,
        post_financial_quote,
        post_cuba_campaign
    ]

    state = load_state()
    current_action = state.get("action_index", 0)

    print(f"🔄 Ejecutando acción {current_action + 1}/{len(actions)} del bucle...")
    success = actions[current_action]()

    if success:
        state["action_index"] = (current_action + 1) % len(actions)
        save_state(state)
        print(f"✅ Acción completada. Próxima acción: {state['action_index'] + 1}")
    else:
        print("⚠️ La acción falló o fue pospuesta. No se avanza de paso.")

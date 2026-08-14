from flask import Flask, jsonify
import requests, os, time
from datetime import datetime, timezone

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN") or os.environ.get("CLASH_OF_CLANS_TOKEN")
BASE_URL = "https://api.clashofclans.com/v1"
CLAN_DEFAULT = os.environ.get("CLAN_TAG") or "#2PR8R9G82" # <-- PON TU CLAN DE COC AQUÍ

session = requests.Session()
if TOKEN:
    session.headers.update({"Authorization": f"Bearer {TOKEN}"})

CACHE = {}
CACHE_TTL = 90

def api_fast(endpoint):
    if endpoint in CACHE and time.time() - CACHE[endpoint][1] < CACHE_TTL:
        return CACHE[endpoint][0]
    try:
        r = session.get(f"{BASE_URL}{endpoint}", timeout=10)
        data = r.json()
        if r.status_code == 200:
            CACHE[endpoint] = (data, time.time())
        else:
            data["status_code"] = r.status_code
        return data
    except Exception as e:
        return {"error": str(e)}

def clean_tag(tag):
    return tag.replace("#","").strip().upper()

@app.route("/")
def home():
    return jsonify({"status":"Bot CoC PRO V4 TURBO - Cache 90s", "clan_default": CLAN_DEFAULT, "token_ok": bool(TOKEN), "ip": "74.220.48.29"})

@app.route("/ip")
def ip_route():
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
        return jsonify({"ip_render": ip})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/clan/<tag>")
def clan(tag):
    return jsonify(api_fast(f"/clans/%23{clean_tag(tag)}"))

@app.route("/player/<tag>")
@app.route("/perfil/<tag>")
def player(tag):
    return jsonify(api_fast(f"/players/%23{clean_tag(tag)}"))

@app.route("/guerra")
@app.route("/guerra/<tag>")
def guerra(tag=None):
    t = clean_tag(tag) if tag else clean_tag(CLAN_DEFAULT)
    return jsonify(api_fast(f"/clans/%23{t}/currentwar"))

@app.route("/faltan")
@app.route("/faltan/<tag>")
def faltan(tag=None):
    t = clean_tag(tag) if tag else clean_tag(CLAN_DEFAULT)
    war = api_fast(f"/clans/%23{t}/currentwar")
    if war.get("state") == "notInWar":
        return jsonify({"error": "No están en guerra", "raw": war})
    faltan_lista = []
    for m in war.get("clan", {}).get("members", []):
        if m.get("attacks") is None or len(m.get("attacks", [])) < war.get("attacksPerMember", 2):
            faltan_lista.append({"name": m["name"], "attacks_used": len(m.get("attacks", [])), "mapPosition": m.get("mapPosition")})
    return jsonify({"clan": war.get("clan", {}).get("name"), "faltan": len(faltan_lista), "faltan_lista": faltan_lista})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

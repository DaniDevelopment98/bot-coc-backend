from flask import Flask, jsonify
import requests, os, time, re
from datetime import datetime, timezone

app = Flask(__name__)

TOKEN = os.environ.get("TOKEN") or os.environ.get("CLASH_OF_CLANS_TOKEN")
BASE_URL = "https://api.clashofclans.com/v1"
CLAN_DEFAULT = os.environ.get("CLAN_TAG") or "#2PR8R9G82"

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

def parse_coc_time(timestr):
    return datetime.strptime(timestr, "%Y%m%dT%H%M%S.000Z").replace(tzinfo=timezone.utc)

@app.route("/faltan")
@app.route("/faltan/<tag>")
def faltan(tag=None):
    try:
        t = clean_tag(tag) if tag else clean_tag(CLAN_DEFAULT)
        war = api_fast(f"/clans/%23{t}/currentwar")
        if war.get("state") == "notInWar" or war.get("reason"):
            return jsonify({"error": "No están en guerra", "raw": war})
        end_time = parse_coc_time(war["endTime"])
        ahora = datetime.now(timezone.utc)
        diff = (end_time - ahora).total_seconds()
        if diff < 0: diff = 0
        horas = int(diff // 3600)
        mins = int((diff % 3600) // 60)
        faltan_lista = []
        for m in war["clan"]["members"]:
            if m.get("attacks") is None or len(m.get("attacks", [])) < 2:
                usados = 0 if m.get("attacks") is None else len(m.get("attacks", []))
                faltan_lista.append({
                    "name": m["name"],
                    "mapPosition": m["mapPosition"],
                    "attacks_used": usados,
                    "faltan": 2 - usados
                })
        return jsonify({
            "clan": war["clan"]["name"],
            "faltan": len(faltan_lista),
            "faltan_lista": faltan_lista,
            "tiempo_restante_seg": diff,
            "tiempo_texto": f"{horas}h {mins}m",
            "endTime": war["endTime"]
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# --- UNICO CAMBIO: ESTA FUNCION CAPITAL ARREGLADA ---
@app.route('/capital')
def capital():
    try:
        t = clean_tag(CLAN_DEFAULT)
        data = api_fast(f"/clans/%23{t}/capitalraidseasons?limit=1")
        if not data.get("items"):
            return jsonify({"en_curso": False, "msg": "Sin historial"})

        season = data["items"][0]
        if season.get("state")!= "ongoing":
            return jsonify({"en_curso": False, "msg": "No hay asalto activo"})

        end_time = parse_coc_time(season["endTime"])
        ahora = datetime.now(timezone.utc)
        diff = (end_time - ahora).total_seconds()
        if diff < 0: diff = 0
        horas = int(diff // 3600)
        mins = int((diff % 3600) // 60)

        raid_members = { m["tag"]: m for m in season.get("members", []) }
        clan_data = api_fast(f"/clans/%23{t}")
        clan_members = clan_data.get("memberList", [])

        faltan_lista = []
        for cm in clan_members:
            rm = raid_members.get(cm["tag"])
            if not rm:
                faltan_lista.append({"name": cm["name"], "usados": 0, "faltan": 6, "limite": 6})
            else:
                ataques = rm.get("attacks", 0)
                limite = rm.get("attackLimit", 5) + rm.get("bonusAttackLimit", 0)
                faltan = limite - ataques
                if faltan > 0:
                    faltan_lista.append({"name": rm["name"], "usados": ataques, "faltan": faltan, "limite": limite})

        faltan_lista.sort(key=lambda x: x["faltan"])

        return jsonify({
            "en_curso": True,
            "clan": clan_data.get("name", "TopLand"),
            "faltan": len(faltan_lista),
            "faltan_lista": faltan_lista,
            "total_saques": season.get("capitalTotalLoot", 0),
            "tiempo_texto": f"{horas}h {mins}m",
            "tiempo_restante_seg": diff,
            "fin": season["endTime"],
            "participaron": len(raid_members)
        })
    except Exception as e:
        return jsonify({"error": str(e), "en_curso": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

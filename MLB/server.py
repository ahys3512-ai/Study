from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

MLB_BASE  = "https://statsapi.mlb.com/api/v1"
ODDS_BASE = "https://api.the-odds-api.com/v4"

# ─── MLB Stats ────────────────────────────────────────────

@app.route("/api/schedule")
def schedule():
    date = request.args.get("date")
    url = f"{MLB_BASE}/schedule?sportId=1&date={date}&hydrate=probablePitcher,linescore,teams"
    return jsonify(requests.get(url).json())

@app.route("/api/pitcher_era")
def pitcher_era():
    pid = request.args.get("id")
    if not pid:
        return jsonify({})
    # 투구 스탯 + 투구손 정보
    url = f"{MLB_BASE}/people/{pid}/stats?stats=season&season=2026&group=pitching"
    return jsonify(requests.get(url).json())

@app.route("/api/pitcher_info")
def pitcher_info():
    """투수 기본 정보 (투구손 포함)"""
    pid = request.args.get("id")
    if not pid:
        return jsonify({})
    url = f"{MLB_BASE}/people/{pid}"
    return jsonify(requests.get(url).json())

def date_range(target_str, days_back):
    target = datetime.strptime(target_str, "%Y-%m-%d")
    start  = target - timedelta(days=days_back)
    return start.strftime("%Y-%m-%d"), target.strftime("%Y-%m-%d")

def fetch_team_range(tid, start, end, group, extra=""):
    url = (f"{MLB_BASE}/teams/{tid}/stats?stats=byDateRange&season=2026"
           f"&group={group}&startDate={start}&endDate={end}{extra}")
    return requests.get(url).json()

@app.route("/api/team_stats")
def team_stats():
    tid  = request.args.get("id")
    date = request.args.get("date", datetime.today().strftime("%Y-%m-%d"))
    s5, e5   = date_range(date, 5)
    s10, e10 = date_range(date, 10)

    hit_season  = requests.get(f"{MLB_BASE}/teams/{tid}/stats?stats=season&season=2026&group=hitting").json()
    bull_season = requests.get(f"{MLB_BASE}/teams/{tid}/stats?stats=season&season=2026&group=pitching&pitchingType=relief").json()
    hit5   = fetch_team_range(tid, s5,  e5,  "hitting")
    bull5  = fetch_team_range(tid, s5,  e5,  "pitching", "&pitchingType=relief")
    hit10  = fetch_team_range(tid, s10, e10, "hitting")
    bull10 = fetch_team_range(tid, s10, e10, "pitching", "&pitchingType=relief")

    return jsonify({
        "hitting": hit_season,
        "pitching": bull_season,
        "hitting_last5": hit5,
        "pitching_last5": bull5,
        "hitting_last10": hit10,
        "pitching_last10": bull10,
    })

# ─── Odds API ─────────────────────────────────────────────

@app.route("/api/odds")
def odds():
    api_key = request.args.get("apiKey")
    if not api_key:
        return jsonify({"error": "API 키가 없습니다"}), 400
    try:
        url = (f"{ODDS_BASE}/sports/baseball_mlb/odds"
               f"?apiKey={api_key}&regions=us,uk,eu&markets=h2h"
               f"&oddsFormat=decimal")
        resp = requests.get(url, timeout=10)
        data = resp.json()

        remaining = resp.headers.get("x-requests-remaining", "?")
        used      = resp.headers.get("x-requests-used", "?")

        if not isinstance(data, list):
            return jsonify({"error": str(data), "remaining": remaining, "used": used}), 400

        all_bk_keys = set()
        for game in data:
            for bk in game.get("bookmakers", []):
                all_bk_keys.add(bk["key"])

        print(f"\n[Odds API] 북마커: {sorted(all_bk_keys)}")
        print(f"[Odds API] {len(data)}경기, 잔여 {remaining}회\n")

        return jsonify({
            "games": data,
            "remaining": remaining,
            "used": used,
            "available_bookmakers": sorted(all_bk_keys),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)

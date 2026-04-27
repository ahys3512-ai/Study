from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

BASE = "https://statsapi.mlb.com/api/v1"

@app.route("/api/schedule")
def schedule():
    date = request.args.get("date")
    url = f"{BASE}/schedule?sportId=1&date={date}&hydrate=probablePitcher,linescore,teams"
    return jsonify(requests.get(url).json())

@app.route("/api/pitcher_era")
def pitcher_era():
    pid = request.args.get("id")
    if not pid:
        return jsonify({})
    url = f"{BASE}/people/{pid}/stats?stats=season&season=2026&group=pitching"
    return jsonify(requests.get(url).json())

@app.route("/api/team_stats")
def team_stats():
    tid = request.args.get("id")
    hit  = requests.get(f"{BASE}/teams/{tid}/stats?stats=season&season=2026&group=hitting").json()
    bull = requests.get(f"{BASE}/teams/{tid}/stats?stats=season&season=2026&group=pitching&pitchingType=relief").json()
    return jsonify({"hitting": hit, "pitching": bull})

if __name__ == "__main__":
    app.run(port=5000, debug=True)

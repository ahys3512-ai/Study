import requests

BASE = "https://statsapi.mlb.com/api/v1"

def get_pitcher_era(person_id):
    url = f"{BASE}/people/{person_id}/stats?stats=season&season=2026&group=pitching"
    data = requests.get(url).json()
    stats = data.get('stats', [])
    if stats and stats[0].get('splits'):
        era = stats[0]['splits'][0]['stat'].get('era', '-')
        return era
    return '-'

def get_team_season_stats(team_id):
    # 팀 타격 (OPS)
    url_hit = f"{BASE}/teams/{team_id}/stats?stats=season&season=2026&group=hitting"
    hit_data = requests.get(url_hit).json()
    ops = '-'
    try:
        ops = hit_data['stats'][0]['splits'][0]['stat'].get('ops', '-')
        if ops != '-':
            ops = f"{float(ops):.3f}"
    except:
        pass

    # 불펜 방어율 (relief pitching)
    url_bull = f"{BASE}/teams/{team_id}/stats?stats=season&season=2026&group=pitching&pitchingType=relief"
    bull_data = requests.get(url_bull).json()
    bull_era = '-'
    try:
        bull_era = bull_data['stats'][0]['splits'][0]['stat'].get('era', '-')
    except:
        pass

    return ops, bull_era

def get_schedule(date: str):
    m, d, y = date.split('/')
    api_date = f"{y}-{m}-{d}"

    url = f"{BASE}/schedule?sportId=1&date={api_date}&hydrate=probablePitcher,linescore,teams"
    data = requests.get(url).json()

    dates = data.get('dates', [])
    if not dates:
        print("해당 날짜에 경기가 없습니다.")
        return

    games = dates[0]['games']
    print(f"\n{date} MLB 경기 (총 {len(games)}경기)\n")

    for g in games:
        away_team = g['teams']['away']['team']
        home_team = g['teams']['home']['team']
        away_name = away_team['name']
        home_name = home_team['name']
        status = g['status']['detailedState']

        # 선발투수 정보
        away_sp_info = g['teams']['away'].get('probablePitcher', {})
        home_sp_info = g['teams']['home'].get('probablePitcher', {})
        away_sp = away_sp_info.get('fullName', '미정')
        home_sp = home_sp_info.get('fullName', '미정')

        # 선발 ERA
        away_era = get_pitcher_era(away_sp_info['id']) if away_sp_info else '-'
        home_era = get_pitcher_era(home_sp_info['id']) if home_sp_info else '-'

        # 팀 OPS / 불펜 ERA
        away_ops, away_bull = get_team_season_stats(away_team['id'])
        home_ops, home_bull = get_team_season_stats(home_team['id'])

        # 경기 결과 출력
        print("=" * 60)
        if status in ('Final', 'Game Over'):
            aw = g['teams']['away'].get('score', 0)
            hw = g['teams']['home'].get('score', 0)
            winner = "<-" if aw > hw else "->"
            print(f"  {away_name:28} {aw} : {hw}  {home_name}  {winner}")
        elif 'Progress' in status:
            aw = g['teams']['away'].get('score', 0)
            hw = g['teams']['home'].get('score', 0)
            inning = g.get('linescore', {}).get('currentInningOrdinal', '')
            print(f"  {away_name:28} {aw} : {hw}  {home_name}  [진행중 {inning}]")
        else:
            print(f"  {away_name:28} vs  {home_name}  [{status}]")

        print(f"  {'':4}{'원정':^30}{'홈':^28}")
        print(f"  {'선발':<6}{away_sp:^30}{home_sp:^28}")
        print(f"  {'ERA':<6}{str(away_era):^30}{str(home_era):^28}")
        print(f"  {'OPS':<6}{away_ops:^30}{home_ops:^28}")
        print(f"  {'불펜ERA':<6}{away_bull:^30}{home_bull:^28}")
        print()

get_schedule('04/27/2026')
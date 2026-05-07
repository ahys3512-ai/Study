import asyncio
import aiohttp

BASE = "https://statsapi.mlb.com/api/v1"

async def fetch(session, url):
    async with session.get(url) as res:
        return await res.json()

async def get_pitcher_era(session, person_id):
    if not person_id:
        return '-'
    url = f"{BASE}/people/{person_id}/stats?stats=season&season=2026&group=pitching"
    data = await fetch(session, url)
    try:
        return data['stats'][0]['splits'][0]['stat'].get('era', '-')
    except:
        return '-'

async def get_team_stats(session, team_id):
    url_hit  = f"{BASE}/teams/{team_id}/stats?stats=season&season=2026&group=hitting"
    url_bull = f"{BASE}/teams/{team_id}/stats?stats=season&season=2026&group=pitching&pitchingType=relief"

    # 타격/불펜 동시 요청
    hit_data, bull_data = await asyncio.gather(
        fetch(session, url_hit),
        fetch(session, url_bull)
    )

    try:
        ops = float(hit_data['stats'][0]['splits'][0]['stat'].get('ops', 0))
        ops = f"{ops:.3f}"
    except:
        ops = '-'

    try:
        bull_era = bull_data['stats'][0]['splits'][0]['stat'].get('era', '-')
    except:
        bull_era = '-'

    return ops, bull_era

async def enrich_game(session, g):
    """경기 1개에 필요한 모든 API를 동시에 호출"""
    away_team = g['teams']['away']['team']
    home_team = g['teams']['home']['team']
    away_sp   = g['teams']['away'].get('probablePitcher', {})
    home_sp   = g['teams']['home'].get('probablePitcher', {})

    # 선발 ERA x2, 팀 스탯 x2 → 총 4~5개 요청 동시에
    away_era, home_era, away_stats, home_stats = await asyncio.gather(
        get_pitcher_era(session, away_sp.get('id')),
        get_pitcher_era(session, home_sp.get('id')),
        get_team_stats(session, away_team['id']),
        get_team_stats(session, home_team['id']),
    )

    return {
        'game': g,
        'away_sp':   away_sp.get('fullName', '미정'),
        'home_sp':   home_sp.get('fullName', '미정'),
        'away_era':  away_era,
        'home_era':  home_era,
        'away_ops':  away_stats[0],
        'home_ops':  home_stats[0],
        'away_bull': away_stats[1],
        'home_bull': home_stats[1],
    }

async def get_schedule(date: str):
    m, d, y = date.split('/')
    api_date = f"{y}-{m}-{d}"
    url = f"{BASE}/schedule?sportId=1&date={api_date}&hydrate=probablePitcher,linescore,teams"

    async with aiohttp.ClientSession() as session:
        data = await fetch(session, url)
        dates = data.get('dates', [])
        if not dates:
            print("해당 날짜에 경기가 없습니다.")
            return

        games = dates[0]['games']
        print(f"\n{date} MLB 경기 (총 {len(games)}경기)\n")

        # 모든 경기 동시에 처리
        results = await asyncio.gather(*[enrich_game(session, g) for g in games])

    for r in results:
        g = r['game']
        status = g['status']['detailedState']
        away_name = g['teams']['away']['team']['name']
        home_name = g['teams']['home']['team']['name']

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
        print(f"  {'선발':<6}{r['away_sp']:^30}{r['home_sp']:^28}")
        print(f"  {'ERA':<6}{str(r['away_era']):^30}{str(r['home_era']):^28}")
        print(f"  {'OPS':<6}{r['away_ops']:^30}{r['home_ops']:^28}")
        print(f"  {'불펜ERA':<6}{r['away_bull']:^30}{r['home_bull']:^28}")
        print()

asyncio.run(get_schedule('04/27/2026'))
import statsapi
import requests

def get_schedule(date: str):
    # 날짜 형식 변환 MM/DD/YYYY -> YYYY-MM-DD
    m, d, y = date.split('/')
    api_date = f"{y}-{m}-{d}"
    
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={api_date}&hydrate=probablePitcher,linescore,teams"
    data = requests.get(url).json()
    
    dates = data.get('dates', [])
    if not dates:
        print("해당 날짜에 경기가 없습니다.")
        return
    
    games = dates[0]['games']
    print(f"\n{date} MLB 경기 (총 {len(games)}경기)\n" + "="*50)
    
    for g in games:
        away = g['teams']['away']['team']['name']
        home = g['teams']['home']['team']['name']
        status = g['status']['detailedState']
        
        # 선발투수
        away_sp = g['teams']['away'].get('probablePitcher', {}).get('fullName', '미정')
        home_sp = g['teams']['home'].get('probablePitcher', {}).get('fullName', '미정')
        
        # 점수
        if status in ('Final', 'Game Over'):
            aw = g['teams']['away'].get('score', 0)
            hw = g['teams']['home'].get('score', 0)
            winner = "<-" if aw > hw else "->"
            print(f"{away:30} {aw} : {hw} {home}  {winner}")
        elif 'Progress' in status:
            aw = g['teams']['away'].get('score', 0)
            hw = g['teams']['home'].get('score', 0)
            inning = g.get('linescore', {}).get('currentInningOrdinal', '')
            print(f"{away:30} {aw} : {hw} {home}  [진행중 {inning}]")
        else:
            print(f"{away:30} vs {home}  [{status}]")
        
        print(f"  선발: {away_sp:30} vs {home_sp}")
        print()

get_schedule('04/27/2026')
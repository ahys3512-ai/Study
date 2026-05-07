import statsapi

def get_schedule(date: str):
    """date 형식: 'MM/DD/YYYY'"""
    games = statsapi.schedule(date=date)
    
    if not games:
        print("해당 날짜에 경기가 없습니다.")
        return
    
    print(f"\n📅 {date} MLB 경기 결과 (총 {len(games)}경기)\n" + "="*45)
    
    for g in games:
        away = g['away_name']
        home = g['home_name']
        status = g['status']
        
        if status == 'Final':
            aw, hw = g['away_score'], g['home_score']
            winner = "←" if aw > hw else "→"
            print(f"{away:25} {aw} : {hw} {home}  {winner}")
        elif 'Progress' in status:
            print(f"{away:25} {g['away_score']} : {g['home_score']} {home}  [진행중 {g.get('current_inning_ordinal','')}]")
        else:
            print(f"{away:25} vs {home}  [{status}]")

# 실행
get_schedule('04/27/2026')
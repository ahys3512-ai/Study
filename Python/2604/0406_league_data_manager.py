# 팀 데이터 리스트 (List of Dictionaries)
teams = [
    {"name": "Team Seoul", "wins": 12, "losses": 5, "ops": 0.850},
    {"name": "Team Daejeon", "wins": 8, "losses": 9, "ops": 0.780},
    {"name": "Team Busan", "wins": 15, "losses": 3, "ops": 0.910},
    {"name": "Team Gwangju", "wins": 6, "losses": 11, "ops": 0.720}
]

def analyze_high_performers(team_list, min_win_rate):
    """
    승률이 기준치 이상인 팀들을 분석하여 출력합니다.
    Analyzes and prints teams with a win rate above the threshold.
    """
    print(f"--- Teams with Win Rate > {min_win_rate:.1f} ---")
    
    for team in team_list:
        win_rate = team["wins"] / (team["wins"] + team["losses"])
        
        if win_rate >= min_win_rate:
            # 어제 배운 :.3f와 문자열 반복을 섞어 활용해보세요!
            print(f"Match Found: {team['name']}")
            print(f"Win Rate: {win_rate:.3f} | OPS: {team['ops']}")
            print("-" * 20)

# 실행: 승률 0.6(60%) 이상인 팀 찾기
analyze_high_performers(teams, 0.6)
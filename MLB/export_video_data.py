"""
YouTube 영상용 데이터 추출

실행: python export_video_data.py
출력: video_data.txt (복사해서 PPT에 붙여넣기)
"""

import pandas as pd
from datetime import datetime, timedelta

CSV_FILE = 'predictions.csv'

def export_video_data():
    df = pd.read_csv(CSV_FILE)
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    output = []
    output.append("="*60)
    output.append(f"📹 MLB 승부예측 - {datetime.now().strftime('%m월 %d일')}")
    output.append("="*60)
    
    # 1. 어제 성적
    yesterday_games = df[df['date'] == yesterday]
    if len(yesterday_games) > 0:
        yesterday_correct = yesterday_games['correct'].dropna()
        if len(yesterday_correct) > 0:
            wins = int(yesterday_correct.sum())
            total = len(yesterday_correct)
            accuracy = (wins / total * 100) if total > 0 else 0
            
            output.append(f"\n📊 어제 성적 ({yesterday})")
            output.append(f"   {wins}승 {total-wins}패 (정답률 {accuracy:.1f}%)")
    
    # 2. 주간 성적
    week_games = df[(df['date'] >= week_ago) & (df['correct'].notna())]
    if len(week_games) > 0:
        week_wins = int(week_games['correct'].sum())
        week_total = len(week_games)
        week_accuracy = (week_wins / week_total * 100) if week_total > 0 else 0
        
        output.append(f"\n📈 최근 7일 누적")
        output.append(f"   {week_wins}승 {week_total-week_wins}패 (정답률 {week_accuracy:.1f}%)")
    
    # 3. 어제 베스트픽 결과
    yesterday_picks = yesterday_games[
        ((yesterday_games['model_away_prob'] >= 60) & (yesterday_games['away_edge'] >= 5)) |
        ((yesterday_games['model_home_prob'] >= 60) & (yesterday_games['home_edge'] >= 5))
    ]
    
    if len(yesterday_picks) > 0:
        output.append(f"\n🎯 어제 베스트픽 결과")
        for _, row in yesterday_picks.iterrows():
            if row['model_away_prob'] >= 60 and row['away_edge'] >= 5:
                predicted = row['away_team']
                prob = row['model_away_prob']
                edge = row['away_edge']
            else:
                predicted = row['home_team']
                prob = row['model_home_prob']
                edge = row['home_edge']
            
            result = "✅ 승" if (row['correct'] == 1) else "❌ 패" if (row['correct'] == 0) else "⏳ 대기"
            output.append(f"   {result} {predicted} ({prob:.1f}%, Edge {edge:+.1f}%p)")
    
    # 4. 오늘 베스트픽
    today_games = df[df['date'] == today]
    
    if len(today_games) > 0:
        output.append(f"\n🔥 오늘의 베스트픽 TOP 3")
        output.append("-"*60)
        
        # 추천 필터링
        picks = []
        for _, row in today_games.iterrows():
            # 원정팀 체크
            if (row['model_away_prob'] >= 60 and 
                row.get('away_edge') is not None and 
                row['away_edge'] >= 5 and
                row['away_sp_confirmed']):
                picks.append({
                    'team': row['away_team'],
                    'opponent': row['home_team'],
                    'prob': row['model_away_prob'],
                    'edge': row['away_edge'],
                    'sp': row['away_sp'],
                    'opp_sp': row['home_sp'],
                    'location': '원정'
                })
            
            # 홈팀 체크
            if (row['model_home_prob'] >= 60 and 
                row.get('home_edge') is not None and 
                row['home_edge'] >= 5 and
                row['home_sp_confirmed']):
                picks.append({
                    'team': row['home_team'],
                    'opponent': row['away_team'],
                    'prob': row['model_home_prob'],
                    'edge': row['home_edge'],
                    'sp': row['home_sp'],
                    'opp_sp': row['away_sp'],
                    'location': '홈'
                })
        
        # Edge 높은 순 정렬
        picks.sort(key=lambda x: x['edge'], reverse=True)
        
        if len(picks) > 0:
            for i, pick in enumerate(picks[:3], 1):
                rank = ["🥇", "🥈", "🥉"][i-1]
                output.append(f"\n{rank} {i}순위: {pick['team']} vs {pick['opponent']}")
                output.append(f"   위치: {pick['location']}")
                output.append(f"   승률: {pick['prob']:.1f}%")
                output.append(f"   Edge: {pick['edge']:+.1f}%p")
                output.append(f"   선발: {pick['sp']} vs {pick['opp_sp']}")
        else:
            output.append("\n   오늘은 베스트픽 기준(승률60%+, Edge5%+)을 만족하는")
            output.append("   경기가 없습니다.")
    
    output.append("\n" + "="*60)
    output.append("자세한 스탯은 predictions.csv 참고")
    output.append("="*60)
    
    # 파일로 저장
    result = '\n'.join(output)
    with open('video_data.txt', 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(result)
    print("\n💾 video_data.txt 파일로 저장되었습니다!")
    print("   이 내용을 복사해서 PPT에 붙여넣으세요.")

if __name__ == "__main__":
    export_video_data()

"""
상대 전적 점수를 predictions.csv에 통합

analyze_matchups.py 실행 후 이 스크립트를 실행하면
matchup_scores.csv의 점수를 predictions.csv에 반영하여
최종 승률을 재계산합니다.

사용법:
python merge_matchup_scores.py
"""

import pandas as pd
from datetime import datetime

CSV_FILE = 'predictions.csv'
MATCHUP_FILE = 'matchup_scores.csv'
MATCHUP_WEIGHT = 0.15  # 상대 전적 가중치 15%

def merge_matchup_scores():
    """상대 전적 점수를 predictions.csv에 통합"""
    
    print("="*70)
    print("상대 전적 점수 통합")
    print("="*70)
    
    # 파일 존재 확인
    try:
        pred_df = pd.read_csv(CSV_FILE)
        matchup_df = pd.read_csv(MATCHUP_FILE)
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없습니다: {e}")
        return
    
    print(f"\n✅ predictions.csv: {len(pred_df)}개 경기")
    print(f"✅ matchup_scores.csv: {len(matchup_df)}개 경기\n")
    
    # 오늘 날짜
    today = datetime.now().strftime('%Y-%m-%d')
    today_preds = pred_df[pred_df['date'] == today]
    
    if len(today_preds) == 0:
        print(f"⚠️ {today} 예측이 없습니다.")
        return
    
    print(f"🎯 {today} 경기 {len(today_preds)}개 처리 중...\n")
    
    updated_count = 0
    
    for idx, pred_row in today_preds.iterrows():
        game_id = pred_row['game_id']
        
        # matchup_scores에서 해당 경기 찾기
        matchup_row = matchup_df[matchup_df['game_id'] == game_id]
        
        if len(matchup_row) == 0:
            continue
        
        matchup_row = matchup_row.iloc[0]
        
        away_matchup_score = matchup_row['away_matchup_score']
        home_matchup_score = matchup_row['home_matchup_score']
        
        # 기존 승률
        base_away_prob = pred_row['model_away_prob']
        base_home_prob = pred_row['model_home_prob']
        
        # 상대 전적 반영
        away_adjustment = away_matchup_score * MATCHUP_WEIGHT
        home_adjustment = home_matchup_score * MATCHUP_WEIGHT
        
        new_away_prob = base_away_prob + away_adjustment
        new_home_prob = base_home_prob + home_adjustment
        
        # 정규화 (합이 100이 되도록)
        total = new_away_prob + new_home_prob
        new_away_prob = (new_away_prob / total) * 100
        new_home_prob = (new_home_prob / total) * 100
        
        # CSV 업데이트
        pred_df.loc[idx, 'away_matchup_avg'] = matchup_row['away_vs_pitcher_avg']
        pred_df.loc[idx, 'home_matchup_avg'] = matchup_row['home_vs_pitcher_avg']
        pred_df.loc[idx, 'away_matchup_score'] = away_matchup_score
        pred_df.loc[idx, 'home_matchup_score'] = home_matchup_score
        pred_df.loc[idx, 'model_away_prob'] = round(new_away_prob, 1)
        pred_df.loc[idx, 'model_home_prob'] = round(new_home_prob, 1)
        
        # Edge 재계산
        if pd.notna(pred_row.get('pinn_away_prob')):
            pred_df.loc[idx, 'away_edge'] = round(new_away_prob - pred_row['pinn_away_prob'], 1)
            pred_df.loc[idx, 'home_edge'] = round(new_home_prob - pred_row['pinn_home_prob'], 1)
        
        print(f"✓ {pred_row['away_team']} @ {pred_row['home_team']}")
        print(f"   원정: {base_away_prob:.1f}% → {new_away_prob:.1f}% ({away_matchup_score:+d}점)")
        print(f"   홈: {base_home_prob:.1f}% → {new_home_prob:.1f}% ({home_matchup_score:+d}점)\n")
        
        updated_count += 1
    
    # 저장
    pred_df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
    
    print("="*70)
    print(f"✅ 완료! {updated_count}개 경기 업데이트")
    print(f"📂 {CSV_FILE} 저장됨")
    print("="*70)

if __name__ == "__main__":
    merge_matchup_scores()

def calculate_team_score(stats, weights):
    """
    가중치를 적용하여 팀의 종합 점수를 계산합니다.
    Calculates the team's total score by applying weights to statistics.
    """
    return sum(s * w for s, w in zip(stats, weights))

def predict_winner(team_a_name, team_a_stats, team_b_name, team_b_stats, weights):
    """
    두 팀의 점수를 비교하여 승리 확률이 더 높은 팀을 예측합니다.
    Compares two teams and predicts the winner with a higher probability.
    """
    score_a = calculate_team_score(team_a_stats, weights)
    score_b = calculate_team_score(team_b_stats, weights)
    
    print(f"[{team_a_name}] Total Score: {score_a:.3f}")
    print(f"[{team_b_name}] Total Score: {score_b:.3f}")
    print("-" * 30)
    
    if score_a > score_b:
        print(f"Result: {team_a_name} is more likely to win.")
    elif score_b > score_a:
        print(f"Result: {team_b_name} is more likely to win.")
    else:
        print("Result: Both teams have the same winning probability.")

# 임의의 데이터 설정 (예: 타자 OPS, 선발 방어율 역산 등)
# Randomly assigned data (e.g., Batter OPS, Inverse of ERA, etc.)
# 가중치 설정: 지표 1에 60%, 지표 2에 40% 부여
# Weights: 60% for Metric 1, 40% for Metric 2
analysis_weights = [0.6, 0.4]

# 팀 A와 팀 B의 임의 통계치
# Mock statistics for Team A and Team B
team_1_data = [0.820, 0.750]  # Team Seoul
team_2_data = [0.780, 0.880]  # Team Daejeon

# 실행 (Execution)
predict_winner("Team Seoul", team_1_data, "Team Daejeon", team_2_data, analysis_weights)
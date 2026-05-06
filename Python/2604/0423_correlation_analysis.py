import statistics

# 데이터 세트 (Example Data)
# X: 하루 학습 시간 (Hours studied)
# Y: 테스트 점수 (Test scores)
study_hours = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
test_scores = [45, 50, 60, 65, 70, 80, 75, 90, 95, 100]

def analyze_correlation(x, y):
    """
    두 데이터 집합 간의 상관관계를 계산합니다.
    Calculates the correlation between two data sets.
    """
    if len(x) != len(y):
        return "Error: Data lengths must be equal."

    # 상관계수 계산 (Pearson correlation coefficient)
    # 결과값은 -1에서 1 사이입니다.
    correlation = statistics.correlation(x, y)
    
    print(f"--- Correlation Analysis ---")
    print(f"Variable X: {x}")
    print(f"Variable Y: {y}")
    print("-" * 30)
    print(f"Correlation Coefficient (상관계수): {correlation:.4f}")
    
    # 결과 해석 (Interpretation)
    if correlation > 0.7:
        print("Result: Strong positive relationship (강한 양의 상관관계)")
    elif correlation < -0.7:
        print("Result: Strong negative relationship (강한 음의 상관관계)")
    else:
        print("Result: Weak or no clear linear relationship (약하거나 관계없음)")

# 실행 (Execution)
analyze_correlation(study_hours, test_scores)
def min_max_normalize(data):
    """
    데이터를 0과 1 사이의 값으로 정규화합니다.
    Normalizes data to values between 0 and 1.
    """
    min_val = min(data)
    max_val = max(data)
    
    # 모든 값이 같을 경우(분모가 0이 되는 경우) 처리
    if max_val - min_val == 0:
        return [0.0] * len(data)
    
    # 공식: (현재값 - 최소값) / (최대값 - 최소값)
    normalized = [(x - min_val) / (max_val - min_val) for x in data]
    return normalized

# 분석 데이터 예시: [팀 점수, 서버 응답시간, 유저수 등]
raw_data = [10, 20, 30, 40, 50, 100, 500]

normalized_data = min_max_normalize(raw_data)

print(f"--- Data Normalization (Min-Max Scaling) ---")
print(f"Original Data: {raw_data}")
print("-" * 40)
for original, norm in zip(raw_data, normalized_data):
    print(f"Original: {original:>3} -> Normalized: {norm:.4f}")
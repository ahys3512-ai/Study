import statistics

# 분석할 데이터 세트 (예: 최근 10일간의 서버 응답 시간(ms) 또는 팀 점수)
# Data set: Server response times (ms) or team scores over the last 10 days
data_samples = [120, 150, 120, 180, 200, 150, 120, 300, 210, 150]

def analyze_central_tendency(data):
    """
    데이터의 평균, 중앙값, 최빈값을 계산하여 출력합니다.
    Calculates and prints the mean, median, and mode of the data.
    """
    mean_val = statistics.mean(data)     # 산술 평균
    median_val = statistics.median(data) # 중앙값 (데이터를 한 줄로 세웠을 때 가운데 값)
    mode_val = statistics.mode(data)     # 최빈값 (가장 자주 등장하는 값)
    
    print(f"--- Data Analysis Results ---")
    print(f"Dataset: {data}")
    print(f"Mean (평균): {mean_val:.2f}")
    print(f"Median (중앙값): {median_val}")
    print(f"Mode (최빈값): {mode_val}")
    print("-" * 30)

    # 데이터의 변동성(범위) 확인
    data_range = max(data) - min(data)
    print(f"Range (데이터 범위): {data_range}")

# 실행 (Execution)
analyze_central_tendency(data_samples)
import statistics

# 분석 데이터: 서버 응답 시간(ms) - 500ms는 평소보다 아주 느린 이상치입니다.
# Data: Server response times (ms) - 500ms is an outlier.
response_times = [120, 125, 130, 115, 110, 120, 500, 118, 122, 128]

def find_outliers(data, threshold=2):
    """
    평균과 표준편차를 사용하여 이상치를 찾습니다.
    Detects outliers using mean and standard deviation.
    """
    mean_val = statistics.mean(data)
    stdev_val = statistics.stdev(data) # 표준 편차 (Standard Deviation)
    
    print(f"--- Analysis Summary ---")
    print(f"Average: {mean_val:.2f}ms | Std Dev: {stdev_val:.2f}")
    print("-" * 30)

    outliers = []
    clean_data = []

    for value in data:
        # 평균으로부터 (표준편차 * 임계값) 이상 떨어진 값을 이상치로 판단
        z_score = abs(value - mean_val) / stdev_val  
        
        if z_score > threshold:
            outliers.append(value)
            print(f"[!] Outlier Detected: {value}ms (Z-Score: {z_score:.2f})")
        else:
            clean_data.append(value)
        #분기 처리를 통해 원본 데이터를 오염시키지 않고 정상 데이터(Clean Data)만 따로 추출하는 기법을 익힘.

    return outliers, clean_data

# 실행: 임계값 2를 기준으로 이상치 탐지
outliers, clean = find_outliers(response_times, threshold=2)

print("-" * 30)
print(f"Identified Outliers: {outliers}")
print(f"Clean Data Count: {len(clean)}")
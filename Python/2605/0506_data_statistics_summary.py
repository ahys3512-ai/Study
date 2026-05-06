import statistics

def get_data_summary(name, data):
    """
    데이터의 주요 통계 지표를 계산하여 딕셔너리로 반환합니다.
    Calculates key statistical indicators and returns them as a dictionary.
    """
    summary = {
        "count": len(data),
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "stdev": statistics.stdev(data) if len(data) > 1 else 0,
        "min": min(data),
        "max": max(data)
    }
    
    print(f"=== Statistics Summary: {name} ===")
    for key, value in summary.items():
        print(f"{key.capitalize():<8}: {value:.4f}")
    print("-" * 35)
    return summary

def min_max_normalize(data):
    """데이터 정규화 (Min-Max Scaling)"""
    low, high = min(data), max(data)
    if high - low == 0: return [0.0] * len(data)
    return [(x - low) / (high - low) for x in data]

# 분석 데이터: 서버 트래픽 (단위: Mbps)
traffic_data = [120, 450, 800, 230, 560, 1100, 95]

# 1. 원본 데이터 요약 (Original Data Summary)
get_data_summary("Raw Traffic", traffic_data)

# 2. 정규화 진행 (Normalization)
norm_traffic = min_max_normalize(traffic_data)

# 3. 정규화 데이터 요약 (Normalized Data Summary)
get_data_summary("Normalized Traffic", norm_traffic)
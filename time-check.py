def is_time_in_range(target, start, end):
    # 1. 시작 시각과 종료 시각이 같은 경우
    # 조건: "시작과 종료가 같으면 포함된다고 판단할 것"
    if start == end:
        return target == start

    # 2. 일반적인 경우 (예: 6시 ~ 18시 / 낮 시간대)
    # 시작 시각이 종료 시각보다 숫자가 작을 때
    if start < end:
        # 시작 시각은 포함(<=), 종료 시각은 미포함(<)
        return start <= target < end

    # 3. 날짜가 넘어가는 경우 (예: 22시 ~ 5시 / 밤~새벽 시간대)
    # 시작 시각이 종료 시각보다 숫자가 클 때
    else:
        # target이 밤 시간대(22시 이상)이거나 
        # target이 새벽 시간대(5시 미만)이면 포함됨
        return target >= start or target < end

# --- 테스트 케이스 확인 ---
if __name__ == "__main__":
    print(f"Case 1 (15시 in 14~18시): {is_time_in_range(15, 14, 18)}") # Expected: True
    print(f"Case 2 (23시 in 22~5시): {is_time_in_range(23, 22, 5)}")   # Expected: True (밤 시간)
    print(f"Case 3 (3시 in 22~5시): {is_time_in_range(3, 22, 5)}")     # Expected: True (새벽 시간)
    print(f"Case 4 (7시 in 22~5시): {is_time_in_range(7, 22, 5)}")     # Expected: False
    print(f"Case 5 (10시 in 10~10시): {is_time_in_range(10, 10, 10)}") # Expected: True
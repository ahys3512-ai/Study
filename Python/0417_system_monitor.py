pip install psutil # need to install this library
import psutil
import datetime

def monitor_cpu(threshold=50):
    """
    CPU 사용량을 체크하고 기준치를 넘으면 로그를 남깁니다.
    Checks CPU usage and logs it if it exceeds the threshold.
    """
    # 현재 CPU 사용량 확인 (1초 동안 측정)
    cpu_usage = psutil.cpu_percent(interval=1)
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[{current_time}] Current CPU Usage: {cpu_usage}%")
    
    if cpu_usage >= threshold:
        log_message = f"[ALERT] High CPU Usage Detected: {cpu_usage}% at {current_time}\n"
        
        # 어제 배운 파일 쓰기(Append) 활용
        with open("system_log.txt", "a", encoding="utf-8") as f:
            f.write(log_message)
        print("⚠️ Warning: High resource usage logged!")
    else:
        print("✅ System stable.")

# 실행: CPU 사용량이 50%를 넘으면 기록
monitor_cpu(threshold=50)
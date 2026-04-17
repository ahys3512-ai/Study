## 📅 2026-04-17

### 📂 오늘 업로드한 코드 (Today's Code)
- **파일명 (File)**: `0417_system_monitor.py`
- **주요 기능 (Key Feature)**: 시스템 CPU 점유율 모니터링 및 임계값 초과 시 로그 기록
  (Monitoring system CPU usage and logging alerts when exceeding thresholds)

### 📝 학습 내용 (What I Learned)

#### 1. 외부 라이브러리 활용 (Using External Libraries)
- `psutil` 라이브러리를 통해 하드웨어 자원(CPU, Memory 등)의 상태 정보를 파이썬으로 가져오는 법을 익혔습니다.
- Learned how to retrieve hardware resource status (CPU, Memory, etc.) using the `psutil` library.

#### 2. 조건부 로깅 (Conditional Logging)
- 단순히 모든 데이터를 저장하는 것이 아니라, 특정 조건(임계값 초과)이 발생했을 때만 파일을 기록하는 효율적인 로직을 구현했습니다.
- Implemented efficient logic that logs data only when specific conditions (exceeding thresholds) occur, rather than saving all data.

#### 3. 실무 응용 능력 (Practical Application)
- 이 스크립트는 클라우드 인프라(AWS EC2 등)의 상태를 점검하고 자동 알람을 보내는 시스템의 기초가 됩니다.
- This script serves as the foundation for systems that monitor cloud infrastructure status and send automated alerts.

### 💡 느낀 점 (Reflections)
- 일주일 동안 꾸준히 코드를 올리면서, 파이썬이 단순히 계산기가 아니라 내 시스템과 상호작용하는 강력한 도구라는 것을 깨달았습니다.
- Through a week of consistent uploading, I realized that Python is a powerful tool for interacting with my system, not just a calculator.
- 앞으로는 CPU뿐만 아니라 메모리, 디스크 공간까지 감시하는 종합 모니터링 도구로 확장해보고 싶습니다.
- I want to expand this into a comprehensive monitoring tool that watches memory and disk space as well.
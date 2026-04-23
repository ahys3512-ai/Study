## 📅 2026-04-22 (Day 9)

### 📂 오늘 업로드한 코드 (Today's Code)
- **파일명 (File)**: `0422_outlier_detector.py`
- **주요 기능 (Key Feature)**: 표준 편차를 활용한 데이터 이상치(Outlier) 탐지 로직
  (Outlier detection logic using standard deviation)

### 📝 학습 내용 (What I Learned)

#### 1. 표준 편차(Standard Deviation)의 이해
- 데이터가 평균을 중심으로 얼마나 퍼져 있는지를 나타내는 수치입니다. `statistics.stdev()`를 통해 쉽게 계산할 수 있습니다.
- A numerical value that indicates how spread out the data is around the mean. Easily calculated with `statistics.stdev()`.

#### 2. 이상치 탐지 원리 (Z-Score Concept)
- 평균에서 일정 거리(표준 편차의 배수) 이상 떨어진 데이터를 '이상치'로 간주하여 분석의 정확도를 높이는 방법을 익혔습니다.
- Learned how to identify 'outliers' that are a certain distance (multiples of standard deviation) away from the mean to improve analysis accuracy.

#### 3. 리스트 필터링 (List Filtering)
- 원본 데이터 리스트를 순회하며 이상치와 정상 데이터를 분리하여 각각 새로운 리스트에 담는 구조를 연습했습니다.
- Practiced a structure that iterates through the original list and separates outliers from clean data into new lists.

### 💡 느낀 점 (Reflections)
- 어제 배운 평균값에 '표준 편차'라는 개념을 더하니, 어떤 데이터가 정말 문제가 있는 값인지 통계적으로 판단할 수 있게 되었습니다.
- By adding the concept of 'standard deviation' to the mean I learned yesterday, I can now statistically determine which data points are truly problematic.
- 클라우드 엔지니어로서 서버의 비정상적인 부하나 네트워크 트래픽 이상을 감지하는 모니터링 시스템의 원리를 이해하는 데 큰 도움이 되었습니다.
- As a cloud engineer, this helped me understand the principles behind monitoring systems that detect abnormal server loads or network traffic anomalies.
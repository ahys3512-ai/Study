## 📅 2026-04-25 (Day 12)

### 📂 오늘 업로드한 코드 (Today's Code)
- **파일명 (File)**: `0425_data_statistics_summary.py`
- **주요 기능 (Key Feature)**: 데이터의 기술 통계량 요약 및 정규화 전후 비교
  (Summarizing descriptive statistics and comparing before/after normalization)

### 📝 학습 내용 (What I Learned)

#### 1. 기술 통계(Descriptive Statistics)의 통합
- 평균, 중앙값, 표준편차 등을 개별적으로 구하는 것이 아니라, 하나의 함수에서 딕셔너리 구조로 묶어 관리하는 법을 익혔습니다.
- Learned how to manage mean, median, and standard deviation together using a dictionary structure.

#### 2. 정규화의 통계적 특성 확인
- 데이터를 정규화(`Min-Max Scaling`)하면 평균과 표준편차는 변하지만, 데이터의 전체적인 분포(상대적 위치)는 유지된다는 점을 확인했습니다.
- Confirmed that while mean and standard deviation change after normalization, the overall distribution remains consistent.

#### 3. 가독성 높은 출력 (Formatting)
- `f-string`의 정렬 기능(`:<8`)을 사용하여 출력 결과의 레이아웃을 깔끔하게 맞추는 법을 연습했습니다.
- Practiced aligning output layout cleanly using f-string formatting.

### 💡 느낀 점 (Reflections)
- 데이터 분석의 시작은 항상 이 '요약 통계'에서 시작된다는 점을 배웠습니다. 
- I learned that data analysis always starts with this 'descriptive summary'.
- 클라우드 엔지니어링 업무에서 수천 대 서버의 리소스 데이터를 일일이 보기 힘들 때, 이와 같은 요약 통계 스크립트로 전체 시스템의 건강 상태를 빠르게 파악할 수 있을 것 같습니다.
- This script will be useful for quickly assessing the health of entire systems when dealing with resource data from thousands of servers.
## 📅 2026-04-21 (Day 8)

### 📂 오늘 업로드한 코드 (Today's Code)
- **파일명 (File)**: `0421_basic_data_analysis.py`
- **주요 기능 (Key Feature)**: 기초 통계 지표(평균, 중앙값, 최빈값) 계산 및 분석
  (Calculating and analyzing basic statistical indicators: Mean, Median, Mode)

### 📝 학습 내용 (What I Learned)

#### 1. 중심 경향성 이해 (Understanding Central Tendency)
- **Mean (평균)**: 모든 값의 합을 개수로 나눈 값으로, 전체적인 흐름을 파악하기 좋습니다.
- **Median (중앙값)**: 데이터를 크기순으로 나열했을 때 중앙에 위치한 값입니다. 이상치(Outlier)가 있는 데이터에서 평균보다 더 신뢰할 수 있는 지표가 됩니다.
- **Mode (최빈값)**: 데이터 세트에서 가장 자주 발생하는 값입니다.

#### 2. `statistics` 라이브러리 활용
- 별도의 복잡한 수식 없이 파이썬 내장 모듈인 `statistics`를 사용하여 정확하고 빠르게 통계치를 산출하는 법을 익혔습니다.
- Learned how to accurately and quickly calculate statistical values using Python's built-in `statistics` module.

#### 3. 데이터 범위(Range) 파악
- `max()`와 `min()` 함수를 활용해 데이터의 확산 정도(최댓값과 최솟값의 차이)를 계산하는 법을 배웠습니다.
- Learned how to calculate the spread of data (the difference between max and min values) using `max()` and `min()` functions.

### 💡 느낀 점 (Reflections)
- 단순한 평균 계산 외에도 중앙값과 최빈값을 함께 확인하니 데이터의 특징이 훨씬 입체적으로 보인다는 점이 흥미로웠습니다.
- It was interesting to see how the characteristics of the data became much more multi-dimensional by checking the median and mode along with the mean.
- 클라우드 인프라의 성능 데이터나 비용 분석 시, 평균의 함정에 빠지지 않기 위해 이러한 기초 통계 지식이 필수적임을 깨달았습니다.
- I realized that basic statistical knowledge is essential to avoid the "flaw of averages" when analyzing cloud infrastructure performance or costs.
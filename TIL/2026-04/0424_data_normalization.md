## 📅 2026-04-24 (Day 11)

### 📂 오늘 업로드한 코드 (Today's Code)
- **파일명 (File)**: `0424_data_normalization.py`
- **주요 기능 (Key Feature)**: 데이터를 0과 1 사이의 범위로 변환하는 Min-Max 정규화
  (Min-Max Normalization converting data to a range between 0 and 1)

### 📝 학습 내용 (What I Learned)

#### 1. 정규화(Normalization)의 필요성
- 서로 다른 단위(Unit)나 범위를 가진 데이터를 동일한 기준으로 비교하기 위해 필수적인 전처리 과정임을 배웠습니다.
- Learned that it is an essential preprocessing step to compare data with different units or ranges on the same scale.

#### 2. Min-Max Scaling 공식 이해
- `(x - min) / (max - min)` 공식을 통해 최솟값은 0, 최댓값은 1이 되도록 설계하는 법을 익혔습니다.
- Mastered the formula to set the minimum value to 0 and the maximum to 1.

#### 3. 리스트 컴프리헨션(List Comprehension) 활용
- 파이썬의 리스트 컴프리헨션을 사용하여 반복문보다 간결하게 리스트 내 모든 요소를 연산하는 법을 복습했습니다.
- Reviewed how to perform operations on all elements in a list concisely using list comprehension.

### 💡 느낀 점 (Reflections)
- 데이터 분석에서 숫자 그 자체보다 '비율'이나 '상대적 위치'가 중요할 때가 많다는 것을 깨달았습니다.
- I realized that the 'ratio' or 'relative position' is often more important than the number itself in data analysis.
- 클라우드 엔지니어링 관점에서, 서로 다른 사양을 가진 서버들의 CPU 사용량과 메모리 사용량을 하나의 대시보드에서 비교 분석할 때 정규화 기술을 응용할 수 있을 것 같습니다.
- From a cloud engineering perspective, normalization can be applied when comparing CPU and memory usage of servers with different specifications on a single dashboard.
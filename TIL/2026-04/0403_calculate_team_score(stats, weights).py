## 📅 2026-04-03 (Day 2)

### 📂 오늘 업로드한 코드 (Today's Code)
- **파일명 (File)**: `win_predictor.py`
- **주요 기능 (Key Feature)**: 가중치를 적용한 두 팀의 승리 확률 비교 시뮬레이션
  (Win probability simulation comparing two teams using weighted averages)

### 📝 학습 내용 (What I Learned)

#### 1. 가중 평균 로직 구현 (Weighted Average Logic)
- 단순 평균이 아닌, 각 지표(예: 타율, 방어율 등)의 중요도에 따라 비중을 다르게 부여하는 방식을 익혔습니다.
- I learned how to assign different levels of importance to each metric using weights, rather than using a simple average.

#### 2. 파이썬 출력 포맷팅 (Python Output Formatting)
- **`:.3f`**: 실수를 출력할 때 소수점 셋째 자리까지 반올림하여 표시하는 법을 배웠습니다. 데이터 분석 결과의 가독성을 높여줍니다.
- **`:.3f`**: Learned how to round and display floating-point numbers to three decimal places, improving the readability of data analysis results.
- **`"-" * 30`**: 문자열 반복 연산을 통해 출력 화면에 깔끔한 구분선을 만드는 법을 익혔습니다.
- **`"-" * 30`**: Learned how to create clean dividers in the output console using string multiplication.

#### 3. 팀별 데이터 비교 (Team Comparison)
- 함수를 모듈화(`calculate_team_score`)하여 여러 팀의 데이터를 동일한 로직으로 처리하고 비교하는 구조를 설계했습니다.
- Designed a modular structure by creating a separate function (`calculate_team_score`) to process and compare data for multiple teams using the same logic.

### 💡 느낀 점 (Reflections)
- 파이썬의 기초적인 문법만으로도 데이터를 수치화하고 결과를 도출하는 '분석 도구'의 뼈대를 만들 수 있다는 점이 흥미로웠습니다.
- It was fascinating to see how basic Python syntax can be used to build the framework of an 'analysis tool' that quantifies data and derives results.
- 앞으로 클라우드 인프라 모니터링 수치나 실제 스포츠 통계 데이터를 접목해보고 싶습니다.
- I look forward to integrating actual cloud infrastructure monitoring metrics or real-world sports statistics in the future.
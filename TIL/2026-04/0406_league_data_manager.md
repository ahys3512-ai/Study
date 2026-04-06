## 📅 2026-04-06 (Day 5)

### 📂 오늘 업로드한 코드 (Today's Code)
- **파일명 (File)**: `0406_league_data_manager.py`
- **주요 기능 (Key Feature)**: 딕셔너리 리스트를 활용한 팀 데이터 필터링 및 승률 분석
  (Filtering team data and analyzing win rates using a list of dictionaries)

### 📝 학습 내용 (What I Learned)

#### 1. 복합 자료구조 활용 (Using Complex Data Structures)
- **List of Dictionaries**: 여러 개의 팀 정보를 각각의 딕셔너리로 만들고, 이를 하나의 리스트로 묶어 관리하는 구조를 익혔습니다. 이는 JSON 데이터나 API 응답 형식을 다룰 때 필수적인 스킬입니다.
- I learned how to manage multiple team information by grouping dictionaries into a single list. This is an essential skill when handling JSON data or API responses.

#### 2. 데이터 순회 및 조건문 (Iteration & Conditionals)
- `for` 문을 통해 리스트 내의 각 딕셔너리에 접근하고, 특정 조건(승률 기준치)에 맞는 데이터만 추출하는 로직을 구현했습니다.
- Implemented logic to access each dictionary within a list using a `for` loop and extract only the data that meets specific conditions (win rate threshold).

#### 3. 동적 수치 계산 (Dynamic Numerical Calculation)
- 승수(wins)와 패수(losses)를 활용해 실시간으로 승률을 계산하고, 이를 어제 배운 `:.3f` 포맷팅을 적용해 출력했습니다.
- Calculated win rates in real-time using wins and losses, and applied the `:.3f` formatting learned yesterday for the output.

### 💡 느낀 점 (Reflections)
- 단순한 변수 사용에서 벗어나 데이터를 구조화(Structuring)하니 코드가 훨씬 체계적으로 변했습니다. 
- It was great to see the code become more organized by structuring data instead of just using simple variables.
- 이러한 구조는 나중에 클라우드 환경에서 수많은 서버(EC2) 상태 데이터를 관리하거나 로그를 분석할 때 매우 유용하게 쓰일 것 같습니다.
- This structure will be very useful later when managing numerous server (EC2) status data or analyzing logs in a cloud environment.
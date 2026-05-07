# MLB 예측 자동화 - 최종 워크플로우

## ⏰ 매일 오후 5시 루틴 (올인원)

```bash
python predict.py daily
```

**실행 내용:**
1. ✅ 어제 경기 결과 업데이트 + 정답률 계산
2. 🔮 오늘 경기 예측 생성 (선발 미정도 포함)
3. 📊 최근 7일 통계 출력

**출력 예시:**
```
==========================================
🌅 매일 오후 5시 루틴 시작
==========================================

📝 STEP 1: 2026-05-06 경기 결과 업데이트
✅ Tampa Bay Rays 5 - 3 Cleveland Guardians
✅ New York Yankees 8 - 2 Boston Red Sox
...
✅ 15개 경기 결과 업데이트 완료

🔮 STEP 2: 2026-05-07 경기 예측 생성
1. Seattle Mariners @ Oakland Athletics
   선발: Logan Gilbert vs 미정 [Oakland Athletics 선발 미정]
   예측: Seattle Mariners 58.3% vs Oakland Athletics 41.7%

2. Chicago Cubs @ Pittsburgh Pirates  
   선발: Shota Imanaga vs Paul Skenes
   예측: Chicago Cubs 52.1% vs Pittsburgh Pirates 47.9%
...
💾 15개 예측 저장 완료 → predictions.csv

📊 STEP 3: 최근 성적 확인
==========================================
📊 최근 7일 통계
==========================================
총 예측: 47경기
적중: 29경기
정답률: 61.7%
==========================================

✅ 루틴 완료! 영상 제작을 시작하세요.
```

---

## 🎯 선발 미정 처리 로직

### 가중치 자동 조정

**선발 확정 시 (기본):**
```
선발 ERA:        25%
시즌 OPS:        20%
최근 5일 OPS:    20%
불펜 ERA:        15%
최근 5일 불펜:   15%
최근 10일 OPS:    5%
```

**선발 미정 시 (타격+불펜만):**
```
선발 ERA:         0%  ← 제외
시즌 OPS:        27%  ← 재분배 (20/0.75)
최근 5일 OPS:    27%  ← 재분배 (20/0.75)
불펜 ERA:        20%  ← 재분배 (15/0.75)
최근 5일 불펜:   20%  ← 재분배 (15/0.75)
최근 10일 OPS:    6%  ← 재분배 (5/0.75)
```

**양팀 모두 미정인 경우:**
- 타격력 54% (시즌27% + 최근5일27%)
- 불펜력 40% (시즌20% + 최근5일20%)
- 최근 흐름 6%

---

## 📅 타임라인 (한국시간)

```
17:00  스크립트 실행
       ├─ 어제(5/6) 경기 결과 반영
       ├─ 정답률 계산
       └─ 오늘(5/7) 경기 예측

17:05  predictions.csv 확인
       ├─ 어제 성적
       ├─ 이번주 누적 정답률
       └─ 오늘 베스트픽 TOP 3

17:10  영상 제작 시작
       ├─ 웹페이지 스크린샷
       ├─ PPT 슬라이드 작성
       └─ 나레이션 녹음

18:00  YouTube 업로드

22:00  프로토 마감 (MLB 경기 구매)
       └─ 구매자들이 영상 참고
```

---

## 📊 CSV 파일 구조 업데이트

**predictions.csv 신규 컬럼:**

| 컬럼 | 설명 | 예시 |
|------|------|------|
| away_sp_confirmed | 원정 선발 확정 여부 | True / False |
| home_sp_confirmed | 홈 선발 확정 여부 | True / False |

**활용 예시:**
```python
import pandas as pd

df = pd.read_csv('predictions.csv')

# 선발 미정 경기만 필터
tbd_games = df[(df['away_sp_confirmed'] == False) | (df['home_sp_confirmed'] == False)]

# 선발 미정 경기의 정답률 (타격+불펜만으로 예측한 경우)
tbd_accuracy = tbd_games['correct'].mean() * 100
```

---

## 🎬 영상 스크립트 예시

```
안녕하세요, MLB 승부예측입니다.

어제(5/6) 15경기 중 10경기 적중!
이번주 누적 정답률 61.7%를 기록 중입니다.

오늘은 오늘(5/7) 경기 중 베스트픽 3경기를 소개합니다.

━━━━━━━━━━━━━━━━━━━━━━

🥇 1순위: Yankees vs Red Sox
내 모델: Yankees 65.3%
선발 매치업: Cole(ERA 2.89) vs Bello(ERA 4.12)
→ 양키스 타선 최근 5일 OPS 0.856 폭발 중!

━━━━━━━━━━━━━━━━━━━━━━

🥈 2순위: Dodgers vs Giants  
내 모델: Dodgers 58.7%
⚠️ 주의: Giants 선발 미정
→ 다저스 불펜 ERA 3.12 vs 자이언츠 3.98

━━━━━━━━━━━━━━━━━━━━━━

🥉 3순위: Astros vs Mariners
내 모델: Astros 54.2%
선발 매치업: Verlander vs Gilbert
→ 최근 5일 불펜: 휴스턴 1.89 vs 시애틀 4.21

━━━━━━━━━━━━━━━━━━━━━━

자세한 스탯은 설명란의 CSV 파일에서 확인하세요.
내일 결과도 업데이트해드리겠습니다!
```

---

## 🔧 수동 커맨드 (필요시)

```bash
# 특정 날짜 예측만
python predict.py generate 2026-05-10

# 특정 날짜 결과만
python predict.py update 2026-05-06

# 최근 30일 통계
python predict.py stats 30
```

---

## 📈 주간 분석 루틴 (일요일)

```python
import pandas as pd

df = pd.read_csv('predictions.csv')
df = df[df['correct'].notna()]

# 1. 선발 확정 vs 미정 정답률 비교
confirmed = df[(df['away_sp_confirmed']) & (df['home_sp_confirmed'])]
tbd = df[(~df['away_sp_confirmed']) | (~df['home_sp_confirmed'])]

print(f"선발 확정 경기: {confirmed['correct'].mean()*100:.1f}%")
print(f"선발 미정 경기: {tbd['correct'].mean()*100:.1f}%")

# 2. 가중치 조정 필요성 판단
if tbd['correct'].mean() < 0.50:
    print("⚠️ 선발 미정 시 정답률 낮음 → 타격 가중치 상향 고려")
```

---

## 🚀 자동화 (Windows 작업 스케줄러)

**작업 이름:** MLB Daily Routine  
**트리거:** 매일 오후 5:00  
**동작:**
- 프로그램: `python.exe`
- 인수: `C:\path\to\predict.py daily`
- 시작 위치: `C:\path\to\`

---

## ✅ 체크리스트

**첫 실행 전:**
- [ ] server.py 실행 중인지 확인
- [ ] predictions.csv 백업 (있다면)

**매일:**
- [ ] 오후 5시 스크립트 실행
- [ ] CSV 확인 (어제 결과 반영됐는지)
- [ ] 영상 제작 (5~6시)
- [ ] YouTube 업로드 (6시 전)

**매주 일요일:**
- [ ] 주간 통계 분석
- [ ] 가중치 조정 필요성 검토
- [ ] 다음주 개선 계획 수립

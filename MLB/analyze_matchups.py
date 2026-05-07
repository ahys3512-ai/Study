"""
MLB 상대 전적 데이터 추출 및 분석

각 경기의 투수 vs 타자 상대 전적을 추출하여
승률 예측에 반영할 점수를 계산합니다.

사용법:
python analyze_matchups.py

출력: matchup_scores.csv (각 경기별 상대 전적 점수)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime

CSV_FILE = 'predictions.csv'

def setup_driver(headless=True):
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def extract_matchup_data(driver, game_id):
    """
    경기의 투수 vs 타자 상대 전적 추출
    
    Returns:
    {
        'away_pitcher': 'Lowder',
        'home_pitcher': 'Imanaga',
        'away_vs_home_pitcher': 0.150,  # 원정 타자들의 홈 투수 상대 평균 타율
        'home_vs_away_pitcher': 0.280   # 홈 타자들의 원정 투수 상대 평균 타율
    }
    """
    
    try:
        url = f"https://www.mlb.com/gameday/{game_id}"
        driver.get(url)
        time.sleep(3)
        
        # 쿠키 닫기
        try:
            cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'OK')]")
            cookie_btn.click()
            time.sleep(0.5)
        except:
            pass
        
        # Preview 탭 클릭 (있으면)
        try:
            preview_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Preview')]"))
            )
            preview_tab.click()
            time.sleep(2)
        except:
            pass
        
        # Matchups 테이블 찾기
        matchup_tables = driver.find_elements(By.XPATH, "//table")
        
        if len(matchup_tables) < 2:
            return None
        
        # 원정팀 vs 홈 투수
        away_vs_home_pitcher = extract_batting_avg(matchup_tables[0])
        
        # 홈팀 vs 원정 투수
        home_vs_away_pitcher = extract_batting_avg(matchup_tables[1])
        
        # 투수 이름
        pitcher_names = driver.find_elements(By.XPATH, "//div[contains(@class, 'pitcher')]//div[contains(@class, 'name')]")
        
        return {
            'away_vs_home_pitcher_avg': away_vs_home_pitcher,
            'home_vs_away_pitcher_avg': home_vs_away_pitcher
        }
    
    except Exception as e:
        print(f"      ⚠️ 데이터 추출 실패: {e}")
        return None

def extract_batting_avg(table):
    """테이블에서 타율(AVG) 추출 및 평균 계산"""
    try:
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        batting_avgs = []
        
        for row in rows[1:]:  # 헤더 제외
            cells = row.find_elements(By.TAG_NAME, "td")
            
            if len(cells) >= 5:  # AVG 컬럼이 있는지 확인
                avg_text = cells[4].text.strip()  # AVG는 보통 5번째 컬럼
                
                if avg_text and avg_text != '-':
                    try:
                        avg = float(avg_text)
                        batting_avgs.append(avg)
                    except:
                        continue
        
        if batting_avgs:
            return round(sum(batting_avgs) / len(batting_avgs), 3)
        else:
            return None
    
    except Exception as e:
        return None

def calculate_matchup_score(away_avg, home_avg):
    """
    상대 전적 기반 점수 계산
    
    Returns:
    away_score: 원정팀 점수 (-15 ~ +15)
    home_score: 홈팀 점수 (-15 ~ +15)
    """
    
    # 원정팀 점수 (홈 투수 상대 타율)
    if away_avg is None:
        away_score = 0
    elif away_avg < 0.200:
        away_score = -10  # 원정 타선이 홈 투수한테 매우 약함
    elif away_avg < 0.250:
        away_score = -5
    elif away_avg < 0.280:
        away_score = 0
    elif away_avg < 0.320:
        away_score = +5
    else:
        away_score = +10  # 원정 타선이 홈 투수한테 매우 강함
    
    # 홈팀 점수 (원정 투수 상대 타율)
    if home_avg is None:
        home_score = 0
    elif home_avg < 0.200:
        home_score = -10  # 홈 타선이 원정 투수한테 매우 약함
    elif home_avg < 0.250:
        home_score = -5
    elif home_avg < 0.280:
        home_score = 0
    elif home_avg < 0.320:
        home_score = +5
    else:
        home_score = +10  # 홈 타선이 원정 투수한테 매우 강함
    
    return away_score, home_score

def analyze_all_games():
    """오늘 모든 경기 분석"""
    
    print("="*70)
    print("MLB 상대 전적 분석")
    print("="*70)
    
    # 오늘 경기 가져오기
    try:
        df = pd.read_csv(CSV_FILE)
        today = datetime.now().strftime('%Y-%m-%d')
        today_games = df[df['date'] == today]
        
        if len(today_games) == 0:
            print("오늘 경기가 없습니다.")
            return
        
        print(f"\n총 {len(today_games)}개 경기 분석 중...\n")
    
    except Exception as e:
        print(f"❌ 에러: {e}")
        return
    
    driver = setup_driver(headless=True)
    
    results = []
    
    try:
        for idx, row in today_games.iterrows():
            game_id = row['game_id']
            away_team = row['away_team']
            home_team = row['home_team']
            
            print(f"📊 [{len(results)+1}/{len(today_games)}] {away_team} @ {home_team}")
            print(f"    Game ID: {game_id}")
            
            matchup_data = extract_matchup_data(driver, game_id)
            
            if matchup_data:
                away_avg = matchup_data['away_vs_home_pitcher_avg']
                home_avg = matchup_data['home_vs_away_pitcher_avg']
                
                away_score, home_score = calculate_matchup_score(away_avg, home_avg)
                
                print(f"    원정 타선 vs 홈 투수: {away_avg if away_avg else 'N/A'} → {away_score:+d}점")
                print(f"    홈 타선 vs 원정 투수: {home_avg if home_avg else 'N/A'} → {home_score:+d}점")
                
                results.append({
                    'game_id': game_id,
                    'away_team': away_team,
                    'home_team': home_team,
                    'away_vs_pitcher_avg': away_avg,
                    'home_vs_pitcher_avg': home_avg,
                    'away_matchup_score': away_score,
                    'home_matchup_score': home_score
                })
            else:
                print(f"    ⚠️ 데이터 없음")
                results.append({
                    'game_id': game_id,
                    'away_team': away_team,
                    'home_team': home_team,
                    'away_vs_pitcher_avg': None,
                    'home_vs_pitcher_avg': None,
                    'away_matchup_score': 0,
                    'home_matchup_score': 0
                })
            
            print()
            time.sleep(2)
    
    finally:
        driver.quit()
    
    # 결과 저장
    result_df = pd.DataFrame(results)
    result_df.to_csv('matchup_scores.csv', index=False, encoding='utf-8-sig')
    
    print("="*70)
    print(f"✅ 완료! matchup_scores.csv 저장됨")
    print("="*70)
    
    # 요약 출력
    print("\n📊 요약:")
    avg_away = result_df['away_matchup_score'].mean()
    avg_home = result_df['home_matchup_score'].mean()
    print(f"   평균 원정팀 점수: {avg_away:+.1f}")
    print(f"   평균 홈팀 점수: {avg_home:+.1f}")

if __name__ == "__main__":
    analyze_all_games()

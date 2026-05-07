"""
MLB 각 경기별 Matchup 스크린샷 자동 촬영

predictions.csv에서 오늘 경기 game_id를 읽어서
각 경기의 Matchup 페이지를 자동으로 캡처합니다.

사용법:
python capture_game_matchups.py

출력: screenshots/matchups/ 폴더에 각 경기별 이미지
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import pandas as pd
from datetime import datetime

CSV_FILE = 'predictions.csv'

def setup_driver(headless=False):
    """Chrome 드라이버 설정"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # User-Agent 설정 (봇 차단 우회)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def get_today_games():
    """오늘 경기 목록 가져오기 (predictions.csv에서)"""
    try:
        df = pd.read_csv(CSV_FILE)
        today = datetime.now().strftime('%Y-%m-%d')
        
        today_games = df[df['date'] == today]
        
        if len(today_games) == 0:
            print(f"⚠️ {today} 경기가 predictions.csv에 없습니다.")
            print("   먼저 'python predict.py daily'를 실행하세요.")
            return []
        
        games = []
        for _, row in today_games.iterrows():
            games.append({
                'game_id': row['game_id'],
                'away_team': row['away_team'],
                'home_team': row['home_team']
            })
        
        return games
    
    except FileNotFoundError:
        print(f"❌ {CSV_FILE} 파일을 찾을 수 없습니다.")
        return []
    except Exception as e:
        print(f"❌ 에러: {e}")
        return []

def capture_game_matchup(driver, game_id, away_team, home_team, index, total):
    """각 경기의 Matchup 페이지 캡처"""
    
    # 팀명 간소화 (파일명용)
    away_short = away_team.split()[-1]  # "New York Yankees" → "Yankees"
    home_short = home_team.split()[-1]
    
    filename = f"game_{index:02d}_{away_short}_vs_{home_short}.png"
    output_path = os.path.join('screenshots', 'matchups', filename)
    
    print(f"\n📸 [{index}/{total}] {away_team} @ {home_team}")
    print(f"   Game ID: {game_id}")
    
    try:
        # 경기 페이지 접속
        url = f"https://www.mlb.com/gameday/{game_id}"
        print(f"   🌐 {url}")
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # 쿠키 팝업 닫기
        try:
            # 여러 가능한 쿠키 닫기 버튼 시도
            cookie_buttons = [
                "//button[contains(text(), 'OK')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Close')]",
                "//button[@aria-label='Close']",
                "//*[@id='onetrust-accept-btn-handler']",
                "//button[contains(@class, 'accept')]"
            ]
            
            for selector in cookie_buttons:
                try:
                    cookie_btn = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    cookie_btn.click()
                    print("   ✅ 쿠키 팝업 닫음")
                    time.sleep(0.5)
                    break
                except:
                    continue
        except:
            pass  # 쿠키 팝업 없으면 넘어가기
        
        # Preview 탭 찾기 및 클릭
        try:
            # 여러 가능한 셀렉터 시도
            selectors = [
                "//button[contains(text(), 'Preview')]",
                "//a[contains(text(), 'Preview')]",
                "//button[contains(@class, 'preview')]",
                "//*[contains(text(), 'Matchups')]"
            ]
            
            preview_clicked = False
            for selector in selectors:
                try:
                    preview_tab = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    preview_tab.click()
                    preview_clicked = True
                    print("   ✅ Preview 탭 클릭")
                    time.sleep(2)
                    break
                except:
                    continue
            
            if not preview_clicked:
                print("   ⚠️ Preview 탭을 찾을 수 없음 (경기 전이 아닐 수 있음)")
        
        except Exception as e:
            print(f"   ⚠️ Preview 탭 클릭 실패: {e}")
        
        # 페이지 스크롤 (Matchups 섹션까지)
        try:
            # Matchups 섹션 찾기
            matchups_section = driver.find_element(By.XPATH, "//*[contains(text(), 'Matchups')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", matchups_section)
            time.sleep(1)
            
            # 약간 위로 스크롤 (헤더 보이게)
            driver.execute_script("window.scrollBy(0, -150);")
            time.sleep(0.5)
            
            print("   📜 Matchups 섹션으로 스크롤")
        except:
            print("   ⚠️ Matchups 섹션 못 찾음, 전체 페이지 캡처")
        
        # 스크린샷
        driver.save_screenshot(output_path)
        print(f"   💾 저장: {filename}")
        
        return True
    
    except Exception as e:
        print(f"   ❌ 에러: {e}")
        return False

def main():
    print("="*70)
    print("MLB 경기별 Matchup 스크린샷 자동 촬영")
    print("="*70)
    
    # 출력 폴더 생성
    output_dir = os.path.join('screenshots', 'matchups')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 오늘 경기 가져오기
    print("\n📋 오늘 경기 목록 확인 중...")
    games = get_today_games()
    
    if not games:
        return
    
    print(f"✅ 총 {len(games)}개 경기 발견\n")
    
    # 헤드리스 모드 여부 선택
    headless_mode = input("백그라운드 실행? (y/n, 기본 n): ").lower() == 'y'
    
    print("\n🌐 Chrome 브라우저 시작...")
    driver = setup_driver(headless=headless_mode)
    
    success_count = 0
    
    try:
        for idx, game in enumerate(games, 1):
            result = capture_game_matchup(
                driver,
                game['game_id'],
                game['away_team'],
                game['home_team'],
                idx,
                len(games)
            )
            
            if result:
                success_count += 1
            
            # 다음 경기 전 대기 (서버 부하 방지)
            if idx < len(games):
                time.sleep(2)
    
    finally:
        print("\n🔚 브라우저 종료...")
        driver.quit()
    
    print("\n" + "="*70)
    print(f"✅ 완료! {success_count}/{len(games)} 경기 캡처 성공")
    print(f"📂 저장 위치: {output_dir}/")
    print("="*70)

if __name__ == "__main__":
    main()

"""
MLB 예측 자동 기록 시스템

매일 아침 실행: 오늘 경기 예측 생성 → CSV 저장
매일 밤 실행: 실제 결과 업데이트
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os

MLB_API = "http://localhost:5000/api"

# ─── 가중치 (현재 모델) ───────────────────────────────────

# 선발 확정 시
WEIGHTS_WITH_SP = {
    'sp_era': 0.25,
    'ops_season': 0.20,
    'bull_era': 0.15,
    'ops_5d': 0.20,
    'bull_5d': 0.15,
    'ops_10d': 0.05,
}

# 선발 미정 시 (타격+불펜만)
WEIGHTS_NO_SP = {
    'sp_era': 0.00,
    'ops_season': 0.27,  # 20/0.75
    'bull_era': 0.20,    # 15/0.75
    'ops_5d': 0.27,      # 20/0.75
    'bull_5d': 0.20,     # 15/0.75
    'ops_10d': 0.06,     # 5/0.75
}

def normalize_era(era, avg=4.00):
    if not era or era == '—':
        return 0.5
    try:
        val = float(era)
        return max(0, min(1, (avg * 2 - val) / (avg * 2)))
    except:
        return 0.5

def normalize_ops(ops, avg=0.720):
    if not ops or ops == '—':
        return 0.5
    try:
        val = float(ops)
        return max(0, min(1, (val - 0.600) / 0.300))
    except:
        return 0.5

def calc_team_score(stats, has_starter=True):
    """
    팀 점수 계산
    has_starter: 선발투수 확정 여부
    """
    weights = WEIGHTS_WITH_SP if has_starter else WEIGHTS_NO_SP
    
    score = 0
    score += normalize_era(stats.get('era', '—')) * weights['sp_era']
    score += normalize_ops(stats.get('ops', '—')) * weights['ops_season']
    score += normalize_era(stats.get('bullEra', '—')) * weights['bull_era']
    score += normalize_ops(stats.get('ops5', '—')) * weights['ops_5d']
    score += normalize_era(stats.get('bullEra5', '—')) * weights['bull_5d']
    score += normalize_ops(stats.get('ops10', '—')) * weights['ops_10d']
    return score

def calc_win_prob(away_stats, home_stats, away_has_sp=True, home_has_sp=True):
    """
    승률 계산
    away_has_sp, home_has_sp: 각 팀 선발 확정 여부
    """
    away_score = calc_team_score(away_stats, away_has_sp)
    home_score = calc_team_score(home_stats, home_has_sp)
    total = away_score + home_score
    if total == 0:
        return 50.0, 50.0
    return (away_score / total) * 100, (home_score / total) * 100

# ─── API 호출 ─────────────────────────────────────────────

def fetch_schedule(date_str):
    """날짜별 경기 일정 가져오기 (YYYY-MM-DD)"""
    url = f"{MLB_API}/schedule?date={date_str}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    dates = data.get('dates', [])
    if not dates or not dates[0].get('games'):
        return []
    return dates[0]['games']

def fetch_odds(api_key):
    """Pinnacle 배당 가져오기"""
    if not api_key:
        return {}
    
    try:
        url = f"{MLB_API}/odds?apiKey={api_key}"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if not isinstance(data.get('games'), list):
            return {}
        
        # Sharp 북마커 우선순위
        SHARP_PRIORITY = ['pinnacle', 'lowvig', 'matchbook', 'smarkets']
        available = data.get('available_bookmakers', [])
        sharp_key = next((k for k in SHARP_PRIORITY if k in available), None)
        
        if not sharp_key:
            return {}
        
        odds_map = {}
        
        for game in data['games']:
            away_team = game['away_team']
            home_team = game['home_team']
            
            # Sharp 북마커 배당 찾기
            sharp_bk = None
            for bk in game.get('bookmakers', []):
                if bk['key'] == sharp_key:
                    sharp_bk = bk
                    break
            
            if not sharp_bk:
                continue
            
            h2h = next((m for m in sharp_bk.get('markets', []) if m['key'] == 'h2h'), None)
            if not h2h:
                continue
            
            # 팀별 배당
            for outcome in h2h['outcomes']:
                team_name = outcome['name']
                decimal = outcome['price']
                implied_prob = (1 / decimal) * 100  # 내재확률 (vig 포함)
                odds_map[team_name] = implied_prob
        
        return odds_map
    
    except Exception as e:
        print(f"   ⚠️ Odds API 에러: {e}")
        return {}

def fetch_pitcher_era(pid):
    if not pid:
        return '—'
    url = f"{MLB_API}/pitcher_era?id={pid}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    try:
        return str(data['stats'][0]['splits'][0]['stat']['era'])
    except:
        return '—'

def fetch_team_stats(tid, date_str):
    url = f"{MLB_API}/team_stats?id={tid}&date={date_str}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    def extract_ops(d):
        try:
            return str(round(float(d['stats'][0]['splits'][0]['stat']['ops']), 3))
        except:
            return '—'
    
    def extract_era(d):
        try:
            return str(d['stats'][0]['splits'][0]['stat']['era'])
        except:
            return '—'
    
    return {
        'ops': extract_ops(data.get('hitting', {})),
        'bullEra': extract_era(data.get('pitching', {})),
        'ops5': extract_ops(data.get('hitting_last5', {})),
        'bullEra5': extract_era(data.get('pitching_last5', {})),
        'ops10': extract_ops(data.get('hitting_last10', {})),
        'bullEra10': extract_era(data.get('pitching_last10', {})),
    }

# ─── 1. 예측 생성 (매일 아침) ─────────────────────────────

def generate_predictions(date_str, api_key=None):
    """
    오늘 경기 예측 생성 (선발 미정도 포함)
    date_str: 'YYYY-MM-DD'
    api_key: Odds API key (선택)
    """
    print(f"\n{'='*60}")
    print(f"📊 {date_str} 예측 생성 중...")
    print(f"{'='*60}\n")
    
    games = fetch_schedule(date_str)
    
    if not games:
        print("❌ 해당 날짜에 경기가 없습니다.")
        return []
    
    # Pinnacle 배당 가져오기
    odds_map = {}
    if api_key:
        print("🔄 Pinnacle 배당 불러오는 중...")
        odds_map = fetch_odds(api_key)
        if odds_map:
            print(f"✅ {len(odds_map)}개 팀 배당 확보\n")
        else:
            print("⚠️ 배당 데이터 없음 (Edge 계산 불가)\n")
    
    predictions = []
    
    # 팀명 매칭용 헬퍼
    def find_odds(team_name):
        # 정확한 이름 매칭
        if team_name in odds_map:
            return odds_map[team_name]
        # 마지막 단어로 퍼지 매칭 (e.g., "Tampa Bay Rays" -> "Rays")
        last_word = team_name.split()[-1].lower()
        for key in odds_map:
            if key.lower().endswith(last_word):
                return odds_map[key]
        return None
    
    for idx, game in enumerate(games, 1):
        away_team = game['teams']['away']['team']
        home_team = game['teams']['home']['team']
        away_sp = game['teams']['away'].get('probablePitcher', {})
        home_sp = game['teams']['home'].get('probablePitcher', {})
        
        away_name = away_team['name']
        home_name = home_team['name']
        
        # 선발 확정 여부
        away_sp_name = away_sp.get('fullName')
        home_sp_name = home_sp.get('fullName')
        away_has_sp = bool(away_sp_name)
        home_has_sp = bool(home_sp_name)
        
        print(f"{idx}. {away_name} @ {home_name}")
        
        # 투수 ERA
        away_era = fetch_pitcher_era(away_sp.get('id')) if away_has_sp else '—'
        home_era = fetch_pitcher_era(home_sp.get('id')) if home_has_sp else '—'
        
        # 팀 스탯
        away_stats = fetch_team_stats(away_team['id'], date_str)
        home_stats = fetch_team_stats(home_team['id'], date_str)
        
        away_stats['era'] = away_era
        home_stats['era'] = home_era
        
        # 승률 계산 (선발 미정이면 타격+불펜만)
        model_away_prob, model_home_prob = calc_win_prob(
            away_stats, home_stats, 
            away_has_sp, home_has_sp
        )
        
        # Pinnacle 승률 & Edge 계산
        pinn_away_prob = find_odds(away_name)
        pinn_home_prob = find_odds(home_name)
        
        away_edge = None
        home_edge = None
        
        if pinn_away_prob is not None and pinn_home_prob is not None:
            away_edge = round(model_away_prob - pinn_away_prob, 1)
            home_edge = round(model_home_prob - pinn_home_prob, 1)
        
        # 선발 미정 표시
        sp_status = ''
        if not away_has_sp and not home_has_sp:
            sp_status = ' [양팀 선발 미정]'
        elif not away_has_sp:
            sp_status = f' [{away_name} 선발 미정]'
        elif not home_has_sp:
            sp_status = f' [{home_name} 선발 미정]'
        
        pred = {
            'date': date_str,
            'game_id': game['gamePk'],
            'away_team': away_name,
            'home_team': home_name,
            'away_sp': away_sp_name or '미정',
            'home_sp': home_sp_name or '미정',
            'away_sp_confirmed': away_has_sp,
            'home_sp_confirmed': home_has_sp,
            'model_away_prob': round(model_away_prob, 1),
            'model_home_prob': round(model_home_prob, 1),
            'pinn_away_prob': round(pinn_away_prob, 1) if pinn_away_prob else None,
            'pinn_home_prob': round(pinn_home_prob, 1) if pinn_home_prob else None,
            'away_edge': away_edge,
            'home_edge': home_edge,
            'actual_winner': None,
            'correct': None,
            'away_score': None,
            'home_score': None,
        }
        
        predictions.append(pred)
        print(f"   선발: {away_sp_name or '미정'} vs {home_sp_name or '미정'}{sp_status}")
        print(f"   예측: {away_name} {model_away_prob:.1f}% vs {home_name} {model_home_prob:.1f}%")
        
        if away_edge is not None:
            edge_str = f"Edge: {away_name} {away_edge:+.1f}%p, {home_name} {home_edge:+.1f}%p"
            print(f"   {edge_str}")
        
        print()
    
    return predictions
    
    return predictions

# ─── 2. 결과 업데이트 (매일 밤) ───────────────────────────

def update_results(date_str):
    """
    경기 결과 업데이트
    """
    print(f"\n{'='*60}")
    print(f"🔄 {date_str} 결과 업데이트 중...")
    print(f"{'='*60}\n")
    
    games = fetch_schedule(date_str)
    
    if not games:
        print("❌ 경기 데이터 없음")
        return {}
    
    results = {}
    
    for game in games:
        game_id = game['gamePk']
        status = game['status']['detailedState']
        
        if status not in ('Final', 'Game Over'):
            continue
        
        away_score = game['teams']['away'].get('score', 0)
        home_score = game['teams']['home'].get('score', 0)
        
        if away_score > home_score:
            winner = game['teams']['away']['team']['name']
        elif home_score > away_score:
            winner = game['teams']['home']['team']['name']
        else:
            winner = 'TIE'
        
        results[game_id] = {
            'actual_winner': winner,
            'away_score': away_score,
            'home_score': home_score,
        }
        
        print(f"✅ {game['teams']['away']['team']['name']} {away_score} - {home_score} {game['teams']['home']['team']['name']}")
    
    return results

# ─── 3. CSV 저장/로드 ────────────────────────────────────

# CSV 파일 경로 (환경변수 또는 기본값)
# 변경 방법:
#   1. 환경변수: set MLB_CSV_PATH=C:\Users\soldesk\Documents\predictions.csv
#   2. 또는 아래 직접 수정: CSV_FILE = 'C:\\원하는\\경로\\predictions.csv'
CSV_FILE = os.environ.get('MLB_CSV_PATH', 'predictions.csv')

# 폴더 자동 생성
csv_dir = os.path.dirname(CSV_FILE)
if csv_dir and not os.path.exists(csv_dir):
    try:
        os.makedirs(csv_dir, exist_ok=True)
        print(f"📁 폴더 생성: {csv_dir}")
    except Exception as e:
        print(f"⚠️ 폴더 생성 실패: {e}")
        print(f"   현재 디렉토리에 저장합니다.")
        CSV_FILE = 'predictions.csv'

def save_predictions(predictions):
    """예측 저장 (추가 모드)"""
    df = pd.DataFrame(predictions)
    
    if os.path.exists(CSV_FILE):
        try:
            existing = pd.read_csv(CSV_FILE)
            df = pd.concat([existing, df], ignore_index=True)
        except PermissionError:
            print(f"\n⚠️ {CSV_FILE} 파일이 다른 프로그램에서 사용 중입니다.")
            print("   Excel을 닫고 다시 시도하거나, 잠시 후 자동 재시도합니다...")
            import time
            time.sleep(3)
            # 재시도
            try:
                existing = pd.read_csv(CSV_FILE)
                df = pd.concat([existing, df], ignore_index=True)
            except PermissionError:
                # 백업 파일로 저장
                backup_file = CSV_FILE.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
                df.to_csv(backup_file, index=False, encoding='utf-8-sig')
                print(f"\n⚠️ 원본 파일 사용 불가 → 백업 파일로 저장: {backup_file}")
                print(f"   Excel 닫은 후 수동으로 병합해주세요.")
                return
    
    try:
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        print(f"\n💾 {len(predictions)}개 예측 저장 완료 → {CSV_FILE}")
    except PermissionError:
        backup_file = CSV_FILE.replace('.csv', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df.to_csv(backup_file, index=False, encoding='utf-8-sig')
        print(f"\n⚠️ {CSV_FILE} 사용 중 → 백업: {backup_file}")

def update_predictions_with_results(date_str, results):
    """결과 업데이트"""
    if not os.path.exists(CSV_FILE):
        print("❌ predictions.csv 파일이 없습니다.")
        return
    
    try:
        df = pd.read_csv(CSV_FILE)
    except PermissionError:
        print(f"\n⚠️ {CSV_FILE} 파일이 Excel 등에서 열려있습니다.")
        print("   파일을 닫고 다시 실행해주세요.")
        return
    
    # 문자열 컬럼 타입 강제 변환 (dtype 에러 방지)
    for col in ['actual_winner', 'away_team', 'home_team', 'away_sp', 'home_sp']:
        if col in df.columns:
            df[col] = df[col].astype('object')
    
    updated = 0
    for game_id, result in results.items():
        mask = (df['date'] == date_str) & (df['game_id'] == game_id)
        if mask.any():
            df.loc[mask, 'actual_winner'] = result['actual_winner']
            df.loc[mask, 'away_score'] = result['away_score']
            df.loc[mask, 'home_score'] = result['home_score']
            
            # 정답 체크
            row = df[mask].iloc[0]
            if result['actual_winner'] == row['away_team']:
                predicted_winner = 'away' if row['model_away_prob'] > row['model_home_prob'] else 'home'
                df.loc[mask, 'correct'] = 1 if predicted_winner == 'away' else 0
            elif result['actual_winner'] == row['home_team']:
                predicted_winner = 'away' if row['model_away_prob'] > row['model_home_prob'] else 'home'
                df.loc[mask, 'correct'] = 1 if predicted_winner == 'home' else 0
            else:
                df.loc[mask, 'correct'] = None  # TIE
            
            updated += 1
    
    try:
        df.to_csv(CSV_FILE, index=False, encoding='utf-8-sig')
        print(f"\n✅ {updated}개 경기 결과 업데이트 완료")
    except PermissionError:
        backup_file = CSV_FILE.replace('.csv', f'_updated_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df.to_csv(backup_file, index=False, encoding='utf-8-sig')
        print(f"\n⚠️ {CSV_FILE} 사용 중 → 업데이트 결과를 백업 파일로 저장: {backup_file}")
        print(f"   Excel 닫은 후 원본 파일을 이 파일로 교체해주세요.")

# ─── 4. 통계 리포트 ──────────────────────────────────────

def show_stats(days=7):
    """최근 N일 통계"""
    if not os.path.exists(CSV_FILE):
        print("❌ 데이터 없음")
        return
    
    df = pd.read_csv(CSV_FILE)
    df = df[df['correct'].notna()]  # 결과 있는 것만
    
    if len(df) == 0:
        print("📊 아직 완료된 경기가 없습니다.")
        return
    
    # 최근 N일
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    recent = df[df['date'] >= cutoff]
    
    total = len(recent)
    correct = recent['correct'].sum()
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print(f"\n{'='*60}")
    print(f"📊 최근 {days}일 통계")
    print(f"{'='*60}")
    print(f"총 예측: {total}경기")
    print(f"적중: {int(correct)}경기")
    print(f"정답률: {accuracy:.1f}%")
    print(f"{'='*60}\n")

# ─── 메인 실행 ────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python predict.py daily            # 매일 오후 5시 실행")
        print("  python predict.py generate [날짜]  # 예측만 생성 (기본: 오늘)")
        print("  python predict.py update [날짜]    # 결과만 업데이트 (기본: 어제)")
        print("  python predict.py stats [일수]     # 통계")
        print("\n예시:")
        print("  python predict.py daily            # 어제 결과 + 오늘 예측")
        print("\n옵션:")
        print("  ODDS_API_KEY 환경변수 설정 시 Edge 자동 계산")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Odds API Key (환경변수 또는 직접 입력)
    odds_api_key = os.environ.get('ODDS_API_KEY')
    
    if command == 'daily':
        """
        매일 오후 5시 루틴:
        1. 어제 경기 결과 업데이트
        2. 오늘 경기 예측 생성
        3. 통계 출력
        """
        # 어제 날짜
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        # 오늘 날짜
        today = datetime.now().strftime('%Y-%m-%d')
        
        print("\n" + "="*60)
        print("🌅 매일 오후 5시 루틴 시작")
        print("="*60)
        
        # API 키 없으면 입력 요청
        if not odds_api_key:
            print("\n💡 Odds API 키를 입력하면 Edge 계산이 포함됩니다.")
            odds_api_key = input("Odds API Key (Enter=건너뛰기): ").strip()
            if not odds_api_key:
                odds_api_key = None
        
        # 1. 어제 결과 업데이트
        print(f"\n📝 STEP 1: {yesterday} 경기 결과 업데이트")
        results = update_results(yesterday)
        if results:
            update_predictions_with_results(yesterday, results)
        else:
            print("   → 업데이트할 결과 없음")
        
        # 2. 오늘 예측 생성
        print(f"\n🔮 STEP 2: {today} 경기 예측 생성")
        predictions = generate_predictions(today, odds_api_key)
        if predictions:
            save_predictions(predictions)
        else:
            print("   → 예측할 경기 없음")
        
        # 3. 통계
        print(f"\n📊 STEP 3: 최근 성적 확인")
        show_stats(7)
        
        print("\n✅ 루틴 완료! 영상 제작을 시작하세요.\n")
    
    elif command == 'generate':
        # 오늘 날짜 기본값
        date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y-%m-%d')
        
        if not odds_api_key:
            odds_api_key = input("Odds API Key (Enter=건너뛰기): ").strip() or None
        
        predictions = generate_predictions(date_str, odds_api_key)
        if predictions:
            save_predictions(predictions)
            show_stats()
    
    elif command == 'update':
        # 어제 날짜 기본값
        date_str = sys.argv[2] if len(sys.argv) > 2 else (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        results = update_results(date_str)
        if results:
            update_predictions_with_results(date_str, results)
            show_stats()
    
    elif command == 'stats':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        show_stats(days)
    
    else:
        print(f"❌ 알 수 없는 명령: {command}")

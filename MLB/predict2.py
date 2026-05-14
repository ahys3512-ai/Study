"""
MLB 예측 자동 기록 시스템 v2
상대 전적 통합 버전 (MLB API 직접 호출)

매일 아침 실행: 오늘 경기 예측 생성 → CSV 저장
매일 밤 실행: 실제 결과 업데이트
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

MLB_API = "http://localhost:5000/api"
MLB_STATS_API = "https://statsapi.mlb.com/api/v1"

# ─── 가중치 (상대 전적 포함) ───────────────────────────────────

# 선발 확정 시 (상대 전적 20% 추가)
WEIGHTS_WITH_SP = {
    'sp_era': 0.20,        # 25% → 20%
    'ops_season': 0.15,    # 20% → 15%
    'bull_era': 0.12,      # 15% → 12%
    'ops_5d': 0.15,        # 20% → 15%
    'bull_5d': 0.12,       # 15% → 12%
    'ops_10d': 0.04,       # 5% → 4%
    'matchup': 0.20,       # 새로 추가!
}

# 선발 미정 시 (타격+불펜만, 상대 전적 제외)
WEIGHTS_NO_SP = {
    'sp_era': 0.00,
    'ops_season': 0.27,
    'bull_era': 0.20,
    'ops_5d': 0.27,
    'bull_5d': 0.20,
    'ops_10d': 0.06,
    'matchup': 0.00,       # 선발 없으면 상대 전적도 없음
}

# ─── 캐시 (API 호출 최소화) ───────────────────────────────────

matchup_cache = {}  # {(batter_id, pitcher_id): data}

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

# ─── 상대 전적 함수들 ───────────────────────────────────────

def get_batter_vs_pitcher(batter_id, pitcher_id, timeout=30):
    """
    타자 vs 투수 상대 전적 조회
    
    Returns:
        {'avg': 0.250, 'ab': 20, 'h': 5} 또는 None
    """
    # 캐시 확인
    cache_key = (batter_id, pitcher_id)
    if cache_key in matchup_cache:
        return matchup_cache[cache_key]
    
    try:
        url = f"{MLB_STATS_API}/people/{batter_id}/stats"
        params = {
            'stats': 'vsPlayer',
            'opposingPlayerId': pitcher_id,
            'group': 'hitting'
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        
        if response.status_code != 200:
            matchup_cache[cache_key] = None
            return None
        
        data = response.json()
        
        # 데이터 파싱
        if 'stats' in data and len(data['stats']) > 0:
            splits = data['stats'][0].get('splits', [])
            if splits:
                stat = splits[0]['stat']
                result = {
                    'avg': float(stat.get('avg', 0)),
                    'ab': int(stat.get('atBats', 0)),
                    'h': int(stat.get('hits', 0))
                }
                matchup_cache[cache_key] = result
                return result
        
        matchup_cache[cache_key] = None
        return None
    
    except Exception as e:
        # print(f"      상대전적 조회 실패: {e}")
        matchup_cache[cache_key] = None
        return None

def get_probable_lineup(team_id, date_str, timeout=30):
    """
    예상 라인업 가져오기 (타순대로)
    
    Returns:
        [{'id': 123, 'name': 'Player', 'order': 1}, ...]
    """
    try:
        # 오늘 경기에서 팀 라인업 가져오기
        url = f"{MLB_STATS_API}/schedule"
        params = {
            'sportId': 1,
            'date': date_str,
            'teamId': team_id,
            'hydrate': 'lineups'
        }
        
        response = requests.get(url, params=params, timeout=timeout)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if 'dates' not in data or not data['dates']:
            return None
        
        games = data['dates'][0].get('games', [])
        if not games:
            return None
        
        game = games[0]
        
        # 원정/홈 팀 확인
        away_team_id = game['teams']['away']['team']['id']
        home_team_id = game['teams']['home']['team']['id']
        
        if team_id == away_team_id:
            lineup_data = game['teams']['away'].get('lineup', [])
        elif team_id == home_team_id:
            lineup_data = game['teams']['home'].get('lineup', [])
        else:
            return None
        
        # 타순별로 정렬
        lineup = []
        for player in lineup_data:
            lineup.append({
                'id': player['id'],
                'name': player['fullName'],
                'order': player.get('battingOrder', 99)
            })
        
        lineup.sort(key=lambda x: x['order'])
        return lineup[:9]  # 상위 9명만
    
    except Exception as e:
        # print(f"      라인업 조회 실패: {e}")
        return None

def convert_avg_to_score(avg, ab):
    """
    타율을 0~1 점수로 변환
    
    샘플 크기 고려:
    - 10타수 이상: 100% 신뢰
    - 5-10타수: 70% 신뢰
    - 5타수 미만: 30% 신뢰
    """
    # 기본 점수 (타율 기반)
    if avg <= 0.150:
        base_score = 0.9  # 투수 압도
    elif avg >= 0.350:
        base_score = 0.1  # 타자 압도
    else:
        # 선형 변환 (0.150~0.350 → 0.9~0.1)
        base_score = 0.9 - ((avg - 0.150) / 0.200) * 0.8
    
    # 신뢰도 반영
    if ab >= 10:
        confidence = 1.0
    elif ab >= 5:
        confidence = 0.7
    else:
        confidence = 0.3
    
    # 중립(0.5)과 가중평균
    final_score = base_score * confidence + 0.5 * (1 - confidence)
    
    return final_score

def calculate_matchup_score(away_lineup, home_lineup, away_pitcher_id, home_pitcher_id):
    """
    상대 전적 점수 계산 (병렬 처리)
    
    Returns:
        (away_matchup_score, home_matchup_score): 각각 0.0~1.0
    """
    if not away_lineup or not home_lineup:
        return 0.5, 0.5
    
    if not away_pitcher_id or not home_pitcher_id:
        return 0.5, 0.5
    
    # 원정 타선 vs 홈 투수 (병렬)
    away_scores = []
    
    def fetch_away_matchup(batter):
        matchup = get_batter_vs_pitcher(batter['id'], home_pitcher_id)
        if matchup and matchup['ab'] >= 3:  # 최소 3타수
            score = convert_avg_to_score(matchup['avg'], matchup['ab'])
            
            # 타순 가중치 (1-3번: 1.5, 4-6번: 1.0, 7-9번: 0.7)
            if batter['order'] <= 3:
                weight = 1.5
            elif batter['order'] <= 6:
                weight = 1.0
            else:
                weight = 0.7
            
            return score * weight, weight
        return None
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_away_matchup, b) for b in away_lineup]
        for future in as_completed(futures):
            result = future.result()
            if result:
                away_scores.append(result)
    
    # 홈 타선 vs 원정 투수 (병렬)
    home_scores = []
    
    def fetch_home_matchup(batter):
        matchup = get_batter_vs_pitcher(batter['id'], away_pitcher_id)
        if matchup and matchup['ab'] >= 3:
            score = convert_avg_to_score(matchup['avg'], matchup['ab'])
            
            if batter['order'] <= 3:
                weight = 1.5
            elif batter['order'] <= 6:
                weight = 1.0
            else:
                weight = 0.7
            
            return score * weight, weight
        return None
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_home_matchup, b) for b in home_lineup]
        for future in as_completed(futures):
            result = future.result()
            if result:
                home_scores.append(result)
    
    # 가중 평균 계산
    if away_scores:
        total_score = sum(s[0] for s in away_scores)
        total_weight = sum(s[1] for s in away_scores)
        away_matchup = total_score / total_weight
    else:
        away_matchup = 0.5  # 데이터 없으면 중립
    
    if home_scores:
        total_score = sum(s[0] for s in home_scores)
        total_weight = sum(s[1] for s in home_scores)
        home_matchup = total_score / total_weight
    else:
        home_matchup = 0.5
    
    return away_matchup, home_matchup

# ─── 기존 함수들 (동일) ───────────────────────────────────────

def fetch_pitcher_era(pitcher_id, timeout=60):
    """투수 ERA 가져오기"""
    if not pitcher_id:
        return '—'
    try:
        url = f"{MLB_API}/pitcher_era?pitcher_id={pitcher_id}"
        resp = requests.get(url, timeout=timeout)
        data = resp.json()
        return data.get('era', '—')
    except:
        return '—'

def fetch_team_stats(team_id, date_str, timeout=60):
    """팀 스탯 가져오기"""
    url = f"{MLB_API}/team_stats?team_id={team_id}&date={date_str}"
    
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=timeout)
            return resp.json()
        except requests.exceptions.ReadTimeout:
            if attempt < 2:
                print(f"   ⚠️ 타임아웃, 재시도 {attempt+1}/3")
                time.sleep(2)
                continue
            else:
                raise

def calc_win_prob(away_stats, home_stats, away_has_sp, home_has_sp):
    """승률 계산 (기존과 동일)"""
    weights = WEIGHTS_WITH_SP if (away_has_sp and home_has_sp) else WEIGHTS_NO_SP
    
    away_score = (
        normalize_era(away_stats.get('era')) * weights['sp_era'] +
        normalize_ops(away_stats.get('ops_season')) * weights['ops_season'] +
        normalize_era(away_stats.get('bull_era')) * weights['bull_era'] +
        normalize_ops(away_stats.get('ops_5d')) * weights['ops_5d'] +
        normalize_era(away_stats.get('bull_5d')) * weights['bull_5d'] +
        normalize_ops(away_stats.get('ops_10d')) * weights['ops_10d']
    )
    
    home_score = (
        normalize_era(home_stats.get('era')) * weights['sp_era'] +
        normalize_ops(home_stats.get('ops_season')) * weights['ops_season'] +
        normalize_era(home_stats.get('bull_era')) * weights['bull_era'] +
        normalize_ops(home_stats.get('ops_5d')) * weights['ops_5d'] +
        normalize_era(home_stats.get('bull_5d')) * weights['bull_5d'] +
        normalize_ops(home_stats.get('ops_10d')) * weights['ops_10d']
    )
    
    # 상대 전적 추가 (matchup_score 키가 있으면)
    if 'matchup_score' in away_stats:
        away_score += away_stats['matchup_score'] * weights['matchup']
    if 'matchup_score' in home_stats:
        home_score += home_stats['matchup_score'] * weights['matchup']
    
    total = away_score + home_score
    if total == 0:
        return 50.0, 50.0
    
    away_prob = (away_score / total) * 100
    home_prob = (home_score / total) * 100
    
    return away_prob, home_prob

def fetch_schedule(date_str, timeout=60):
    """경기 일정 가져오기 (수정됨)"""
    url = f"{MLB_API}/schedule?date={date_str}"
    
    print(f"🔍 경기 일정 조회: {url}")
    
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=timeout)
            
            print(f"   📡 응답 코드: {resp.status_code}")
            
            if resp.status_code != 200:
                print(f"   ❌ 서버 에러: {resp.status_code}")
                return []
            
            data = resp.json()
            
            # 🔧 수정: dates 배열 안에 games가 있음!
            if 'dates' in data and len(data['dates']) > 0:
                games = data['dates'][0].get('games', [])
            else:
                games = data.get('games', [])
            
            print(f"   ✅ {len(games)}개 경기 발견")
            
            return games
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Flask 서버 연결 실패!")
            return []
            
        except requests.exceptions.ReadTimeout:
            if attempt < 2:
                print(f"   ⚠️ 타임아웃, 재시도 {attempt+1}/3")
                time.sleep(2)
                continue
            else:
                print(f"   ❌ 3번 시도 모두 타임아웃")
                return []
                
        except Exception as e:
            print(f"   ❌ 예상치 못한 에러: {type(e).__name__}")
            print(f"   상세: {str(e)}")
            return []
    
    return []

def fetch_odds(api_key):
    """Odds API에서 배당 가져오기"""
    url = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds"
    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'decimal'
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        odds_map = {}
        
        for game in data:
            for bookmaker in game.get('bookmakers', []):
                if bookmaker['key'].lower() == 'pinnacle':
                    for market in bookmaker.get('markets', []):
                        if market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                team_name = outcome['name']
                                decimal_odd = outcome['price']
                                implied_prob = (1 / decimal_odd) * 100
                                odds_map[team_name] = implied_prob
                    break
        
        if not odds_map:
            for game in data:
                for bookmaker in game.get('bookmakers', []):
                    if bookmaker['key'] in ['lowvig', 'matchbook', 'smarkets']:
                        for market in bookmaker.get('markets', []):
                            if market['key'] == 'h2h':
                                for outcome in market['outcomes']:
                                    team_name = outcome['name']
                                    decimal_odd = outcome['price']
                                    implied_prob = (1 / decimal_odd) * 100
                                    odds_map[team_name] = implied_prob
                        break
                if odds_map:
                    break
        
        return odds_map
    
    except Exception as e:
        print(f"⚠️ Odds API 에러: {e}")
        return {}

# ─── 메인 예측 함수 (상대 전적 통합) ───────────────────────────

def generate_predictions(date_str, odds_api_key=None):
    """오늘 경기 예측 생성 (상대 전적 포함)"""
    
    print("="*60)
    print(f"📊 {date_str} 예측 생성 중... (상대 전적 포함)")
    print("="*60)
    print()
    
    games = fetch_schedule(date_str)
    
    if not games:
        print("❌ 해당 날짜에 경기가 없습니다.")
        return []
    
    # Pinnacle 배당
    odds_map = {}
    if odds_api_key:
        print("🔄 Pinnacle 배당 불러오는 중...")
        odds_map = fetch_odds(odds_api_key)
        if odds_map:
            print(f"✅ {len(odds_map)}개 팀 배당 확보\n")
    
    predictions = []
    
    def find_odds(team_name):
        if team_name in odds_map:
            return odds_map[team_name]
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
        
        # 🆕 상대 전적 계산 (선발 확정 시만)
        if away_has_sp and home_has_sp:
            print("   🎯 상대 전적 분석 중...")
            
            # 라인업 가져오기
            away_lineup = get_probable_lineup(away_team['id'], date_str)
            home_lineup = get_probable_lineup(home_team['id'], date_str)
            
            if away_lineup and home_lineup:
                away_matchup, home_matchup = calculate_matchup_score(
                    away_lineup, home_lineup,
                    away_sp.get('id'), home_sp.get('id')
                )
                
                away_stats['matchup_score'] = away_matchup
                home_stats['matchup_score'] = home_matchup
                
                print(f"      원정 타선: {away_matchup:.2f} / 홈 타선: {home_matchup:.2f}")
            else:
                print("      ⚠️ 라인업 없음 (중립 처리)")
                away_stats['matchup_score'] = 0.5
                home_stats['matchup_score'] = 0.5
        else:
            away_stats['matchup_score'] = 0.5
            home_stats['matchup_score'] = 0.5
        
        # 승률 계산
        model_away_prob, model_home_prob = calc_win_prob(
            away_stats, home_stats,
            away_has_sp, home_has_sp
        )
        
        # Pinnacle Edge
        pinn_away_prob = find_odds(away_name)
        pinn_home_prob = find_odds(home_name)
        
        away_edge = None
        home_edge = None
        
        if pinn_away_prob and pinn_home_prob:
            away_edge = round(model_away_prob - pinn_away_prob, 1)
            home_edge = round(model_home_prob - pinn_home_prob, 1)
        
        pred = {
            'date': date_str,
            'game_id': game['gamePk'],
            'away_team': away_name,
            'home_team': home_name,
            'away_sp': away_sp_name or '미정',
            'home_sp': home_sp_name or '미정',
            'away_sp_confirmed': away_has_sp,
            'home_sp_confirmed': home_has_sp,
            'away_matchup_score': round(away_stats.get('matchup_score', 0.5), 3),
            'home_matchup_score': round(home_stats.get('matchup_score', 0.5), 3),
            'model_away_prob': round(model_away_prob, 1),
            'model_home_prob': round(model_home_prob, 1),
            'pinn_away_prob': round(pinn_away_prob, 1) if pinn_away_prob else None,
            'pinn_home_prob': round(pinn_home_prob, 1) if pinn_home_prob else None,
            'away_edge': away_edge,
            'home_edge': home_edge,
            'actual_winner': None,
            'correct': None,
            'away_score': None,
            'home_score': None
        }
        
        predictions.append(pred)
        
        # 출력
        print(f"   모델: {away_name} {model_away_prob:.1f}% vs {home_name} {model_home_prob:.1f}%")
        if away_edge is not None:
            print(f"   Edge: {away_name} {away_edge:+.1f}%p / {home_name} {home_edge:+.1f}%p")
        print()
    
    return predictions

def save_predictions(predictions):
    """예측을 CSV에 저장"""
    csv_file = 'predictions_v2.csv'  # 직접 지정
    
    new_df = pd.DataFrame(predictions)
    
    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df
        print(f"📝 새 파일 생성: {csv_file}")
    
    combined_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"✅ {len(predictions)}개 예측 저장: {csv_file}")

def update_results(date_str):
    """경기 결과 업데이트"""
    csv_file = 'predictions_v2.csv'  # 직접 지정
    
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} 파일이 없습니다.")
        print("   먼저 'python predict2.py generate' 실행하세요.")
        return
    
    print("="*60)
    print(f"🔄 {date_str} 결과 업데이트 중...")
    print("="*60)
    print()
    
    df = pd.read_csv(csv_file)
    
    target_games = df[df['date'] == date_str]
    
    if len(target_games) == 0:
        print(f"⚠️ {date_str} 예측이 없습니다.")
        return
    
    updated_count = 0
    
    for idx, row in target_games.iterrows():
        game_id = row['game_id']
        
        try:
            url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            game_data = data.get('gameData', {})
            status_code = game_data.get('status', {}).get('statusCode')
            
            if status_code not in ['F', 'O']:
                continue
            
            live_data = data.get('liveData', {})
            linescore = live_data.get('linescore', {})
            
            away_score = linescore.get('teams', {}).get('away', {}).get('runs')
            home_score = linescore.get('teams', {}).get('home', {}).get('runs')
            
            if away_score is None or home_score is None:
                continue
            
            actual_winner = 'away' if away_score > home_score else 'home'
            
            model_away_prob = row['model_away_prob']
            model_home_prob = row['model_home_prob']
            
            predicted_winner = 'away' if model_away_prob > model_home_prob else 'home'
            
            correct = 1 if predicted_winner == actual_winner else 0
            
            df.loc[idx, 'actual_winner'] = actual_winner
            df.loc[idx, 'correct'] = correct
            df.loc[idx, 'away_score'] = away_score
            df.loc[idx, 'home_score'] = home_score
            
            away_team = row['away_team']
            home_team = row['home_team']
            
            print(f"✅ {away_team} {away_score} - {home_score} {home_team}")
            
            updated_count += 1
        
        except Exception as e:
            print(f"⚠️ Game {game_id} 업데이트 실패: {e}")
    
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    print()
    print(f"✅ {updated_count}개 경기 결과 업데이트 완료")

def show_stats(days=7):
    """최근 통계 표시"""
    csv_file = 'predictions_v2.csv'  # 직접 지정
    
    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} 파일이 없습니다.")
        print("   아직 예측 데이터가 없습니다.")
        return
    
    df = pd.read_csv(csv_file)
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    recent = df[df['date'] >= cutoff_date]
    
    finished = recent[recent['correct'].notna()]
    
    if len(finished) == 0:
        print(f"⚠️ 최근 {days}일 결과가 없습니다.")
        return
    
    correct_count = int(finished['correct'].sum())
    total_count = len(finished)
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
    
    print("="*60)
    print(f"📊 최근 {days}일 통계")
    print("="*60)
    print(f"✅ 정답: {correct_count}경기")
    print(f"❌ 오답: {total_count - correct_count}경기")
    print(f"📈 정답률: {accuracy:.1f}% ({correct_count}/{total_count})")
    print("="*60)

# ─── 메인 ─────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법:")
        print("  python predict2.py daily           # 매일 루틴")
        print("  python predict2.py generate [날짜] # 예측만")
        print("  python predict2.py update [날짜]   # 결과만")
        print("  python predict2.py stats [일수]    # 통계")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'daily':
        print()
        print("="*60)
        print("🌅 매일 오후 5시 루틴 시작 (상대 전적 포함)")
        print("="*60)
        print()
        
        odds_api_key = input("💡 Odds API 키 (Enter=건너뛰기): ").strip()
        if not odds_api_key:
            odds_api_key = None
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        
        print()
        print(f"📝 STEP 1: {yesterday} 경기 결과 업데이트")
        print()
        update_results(yesterday)
        
        print()
        print(f"🔮 STEP 2: {today} 경기 예측 생성")
        print()
        predictions = generate_predictions(today, odds_api_key)
        if predictions:
            save_predictions(predictions)
        
        print()
        print("📊 STEP 3: 최근 7일 통계")
        print()
        show_stats(7)
        
        print()
        print("="*60)
        print("✅ 완료!")
        print("="*60)
    
    elif command == 'generate':
        date_str = sys.argv[2] if len(sys.argv) > 2 else datetime.now().strftime('%Y-%m-%d')
        odds_api_key = input("Odds API 키 (Enter=건너뛰기): ").strip() or None
        
        predictions = generate_predictions(date_str, odds_api_key)
        if predictions:
            save_predictions(predictions)
    
    elif command == 'update':
        date_str = sys.argv[2] if len(sys.argv) > 2 else (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        update_results(date_str)
    
    elif command == 'stats':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        show_stats(days)
    
    else:
        print(f"❌ 알 수 없는 명령: {command}")

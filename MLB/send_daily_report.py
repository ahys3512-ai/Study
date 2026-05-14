"""
MLB 예측 이메일 리포트 생성기

매일 오후 5시 실행:
1. predict.py 실행
2. 베스트픽 분석
3. HTML 이메일 생성
4. Gmail로 자동 발송

사용법:
python send_daily_report.py
"""

import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import subprocess
import os

# ━━━ 설정 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Gmail 설정
GMAIL_USER = "ahys3512@gmail.com"  # 발신 Gmail
GMAIL_APP_PASSWORD = "tjd39534"  # Gmail 앱 비밀번호
TO_EMAIL = "ahys3512@gmail.com"  # 수신 이메일

CSV_FILE = "predictions.csv"

# ━━━ 분석 함수 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_today_picks():
    """오늘 예측 분석"""
    
    df = pd.read_csv(CSV_FILE)
    today = datetime.now().strftime('%Y-%m-%d')
    today_games = df[df['date'] == today].copy()
    
    if len(today_games) == 0:
        return None, None
    
    # Edge 메리트 분석
    edge_picks = []
    
    for _, row in today_games.iterrows():
        # 선발 확정 경기만
        if not row['away_sp_confirmed'] or not row['home_sp_confirmed']:
            continue
        
        # 원정팀 분석
        away_model = row['model_away_prob']
        away_pinn = row.get('pinn_away_prob')
        away_edge = row.get('away_edge')
        
        if away_pinn and away_edge:
            expected_value = away_model + away_edge
            
            # 역배 메리트 (모델<50% but 실질기댓값≥50%)
            if away_model < 50 and expected_value >= 50:
                grade = 'S급 역배' if expected_value >= 55 else 'A급 역배'
                edge_picks.append({
                    'team': row['away_team'],
                    'opponent': row['home_team'],
                    'location': '원정',
                    'model_prob': away_model,
                    'pinn_prob': away_pinn,
                    'edge': away_edge,
                    'expected_value': expected_value,
                    'grade': grade,
                    'odd': 100 / away_pinn,
                    'away_sp': row['away_sp'],
                    'home_sp': row['home_sp'],
                    'away_era': row.get('away_era', '—'),
                    'home_era': row.get('home_era', '—'),
                    'away_ops': row.get('away_ops_season', '—'),
                    'home_ops': row.get('home_ops_season', '—'),
                    'away_bull': row.get('away_bull_era', '—'),
                    'home_bull': row.get('home_bull_era', '—'),
                })
        
        # 홈팀 분석
        home_model = row['model_home_prob']
        home_pinn = row.get('pinn_home_prob')
        home_edge = row.get('home_edge')
        
        if home_pinn and home_edge:
            expected_value = home_model + home_edge
            
            if home_model < 50 and expected_value >= 50:
                grade = 'S급 역배' if expected_value >= 55 else 'A급 역배'
                edge_picks.append({
                    'team': row['home_team'],
                    'opponent': row['away_team'],
                    'location': '홈',
                    'model_prob': home_model,
                    'pinn_prob': home_pinn,
                    'edge': home_edge,
                    'expected_value': expected_value,
                    'grade': grade,
                    'odd': 100 / home_pinn,
                    'away_sp': row['away_sp'],
                    'home_sp': row['home_sp'],
                    'away_era': row.get('home_era', '—'),
                    'home_era': row.get('away_era', '—'),
                    'away_ops': row.get('home_ops_season', '—'),
                    'home_ops': row.get('away_ops_season', '—'),
                    'away_bull': row.get('home_bull_era', '—'),
                    'home_bull': row.get('away_bull_era', '—'),
                })
    
    # Edge 순 정렬
    edge_picks.sort(key=lambda x: abs(x['edge']), reverse=True)
    
    # 고승률 픽 (모델 60%+, Edge 5%+)
    high_prob_picks = []
    
    for _, row in today_games.iterrows():
        if not row['away_sp_confirmed'] or not row['home_sp_confirmed']:
            continue
        
        away_model = row['model_away_prob']
        away_edge = row.get('away_edge', 0)
        
        if away_model >= 60 and away_edge >= 5:
            high_prob_picks.append({
                'team': row['away_team'],
                'opponent': row['home_team'],
                'location': '원정',
                'model_prob': away_model,
                'pinn_prob': row.get('pinn_away_prob'),
                'edge': away_edge,
                'odd': 100 / row.get('pinn_away_prob', 50),
                'grade': '정배 A급',
                'away_sp': row['away_sp'],
                'home_sp': row['home_sp'],
                'away_era': row.get('away_era', '—'),
                'home_era': row.get('home_era', '—'),
                'away_ops': row.get('away_ops_season', '—'),
                'home_ops': row.get('home_ops_season', '—'),
                'away_bull': row.get('away_bull_era', '—'),
                'home_bull': row.get('home_bull_era', '—'),
            })
        
        home_model = row['model_home_prob']
        home_edge = row.get('home_edge', 0)
        
        if home_model >= 60 and home_edge >= 5:
            high_prob_picks.append({
                'team': row['home_team'],
                'opponent': row['away_team'],
                'location': '홈',
                'model_prob': home_model,
                'pinn_prob': row.get('pinn_home_prob'),
                'edge': home_edge,
                'odd': 100 / row.get('pinn_home_prob', 50),
                'grade': '정배 A급',
                'away_sp': row['home_sp'],
                'home_sp': row['away_sp'],
                'away_era': row.get('home_era', '—'),
                'home_era': row.get('away_era', '—'),
                'away_ops': row.get('home_ops_season', '—'),
                'home_ops': row.get('away_ops_season', '—'),
                'away_bull': row.get('home_bull_era', '—'),
                'home_bull': row.get('away_bull_era', '—'),
            })
    
    # 승률 순 정렬
    high_prob_picks.sort(key=lambda x: x['model_prob'], reverse=True)
    
    return edge_picks[:3], high_prob_picks[:3]

# ━━━ HTML 생성 ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_html_report(edge_picks, high_prob_picks):
    """HTML 이메일 생성"""
    
    today = datetime.now().strftime('%Y년 %m월 %d일')
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: 'Malgun Gothic', sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .section {{
            padding: 30px;
        }}
        .section-title {{
            font-size: 24px;
            color: #333;
            border-left: 4px solid #667eea;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .pick-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #764ba2;
        }}
        .pick-rank {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .pick-grade {{
            display: inline-block;
            background: #ffd700;
            color: #333;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
        .pick-title {{
            font-size: 20px;
            font-weight: bold;
            margin: 10px 0;
            color: #333;
        }}
        .pick-stats {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 15px;
        }}
        .stat-item {{
            background: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }}
        .stat-label {{
            color: #666;
            font-size: 12px;
        }}
        .stat-value {{
            font-weight: bold;
            color: #333;
            font-size: 16px;
        }}
        .highlight {{
            color: #667eea;
            font-weight: bold;
        }}
        .team-stats {{
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 5px;
        }}
        .team-row {{
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px solid #eee;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚾ MLB 베스트픽</h1>
            <p>{today}</p>
        </div>
"""

    # Edge Top 3
    if edge_picks:
        html += """
        <div class="section">
            <h2 class="section-title">🔥 배당 메리트 TOP 3</h2>
"""
        
        for idx, pick in enumerate(edge_picks, 1):
            emoji = "⭐⭐⭐" if pick['grade'] == 'S급 역배' else "⭐⭐"
            
            html += f"""
            <div class="pick-card">
                <span class="pick-rank">{idx}위</span>
                <span class="pick-grade">{emoji} {pick['grade']}</span>
                <div class="pick-title">
                    {pick['team']} ({pick['location']}) vs {pick['opponent']}
                </div>
                
                <div class="pick-stats">
                    <div class="stat-item">
                        <div class="stat-label">모델 승률</div>
                        <div class="stat-value">{pick['model_prob']:.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Pinnacle</div>
                        <div class="stat-value">{pick['pinn_prob']:.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">🎯 Edge</div>
                        <div class="stat-value highlight">{pick['edge']:+.1f}%p</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">실질 기댓값</div>
                        <div class="stat-value highlight">{pick['expected_value']:.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">💰 배당</div>
                        <div class="stat-value">{pick['odd']:.2f}x</div>
                    </div>
                </div>
                
                <div class="team-stats">
                    <strong>📊 주요 스탯</strong>
                    <div class="team-row">
                        <span>{pick['team']} ({pick['location']})</span>
                        <span>ERA {pick['away_era']} | OPS {pick['away_ops']} | 불펜 {pick['away_bull']}</span>
                    </div>
                    <div class="team-row">
                        <span>{pick['opponent']}</span>
                        <span>ERA {pick['home_era']} | OPS {pick['home_ops']} | 불펜 {pick['home_bull']}</span>
                    </div>
                </div>
            </div>
"""
        
        html += "</div>"
    
    # High Prob Top 3
    if high_prob_picks:
        html += """
        <div class="section">
            <h2 class="section-title">💪 고승률 TOP 3</h2>
"""
        
        for idx, pick in enumerate(high_prob_picks, 1):
            html += f"""
            <div class="pick-card">
                <span class="pick-rank">{idx}위</span>
                <span class="pick-grade">🥇 {pick['grade']}</span>
                <div class="pick-title">
                    {pick['team']} ({pick['location']}) vs {pick['opponent']}
                </div>
                
                <div class="pick-stats">
                    <div class="stat-item">
                        <div class="stat-label">모델 승률</div>
                        <div class="stat-value">{pick['model_prob']:.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">Pinnacle</div>
                        <div class="stat-value">{pick['pinn_prob']:.1f}%</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">🎯 Edge</div>
                        <div class="stat-value highlight">{pick['edge']:+.1f}%p</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">💰 배당</div>
                        <div class="stat-value">{pick['odd']:.2f}x</div>
                    </div>
                </div>
                
                <div class="team-stats">
                    <strong>📊 주요 스탯</strong>
                    <div class="team-row">
                        <span>{pick['team']} ({pick['location']})</span>
                        <span>ERA {pick['away_era']} | OPS {pick['away_ops']} | 불펜 {pick['away_bull']}</span>
                    </div>
                    <div class="team-row">
                        <span>{pick['opponent']}</span>
                        <span>ERA {pick['home_era']} | OPS {pick['home_ops']} | 불펜 {pick['home_bull']}</span>
                    </div>
                </div>
            </div>
"""
        
        html += "</div>"
    
    html += """
        <div class="footer">
            <p>MLB 베스트픽 자동 리포트</p>
            <p>매일 오후 5시 업데이트</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

# ━━━ 이메일 발송 ━━━━━━━━━━━━━━━━━━━━━━━━━

def send_email(html_content, edge_picks):
    """Gmail로 이메일 발송"""
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # S급/A급 카운트
    s_count = sum(1 for p in edge_picks if 'S급' in p['grade'])
    a_count = sum(1 for p in edge_picks if 'A급' in p['grade'])
    
    subject = f"[MLB 베스트픽] {today}"
    if s_count > 0:
        subject += f" | S급 {s_count}경기"
    if a_count > 0:
        subject += f", A급 {a_count}경기"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = TO_EMAIL
    
    html_part = MIMEText(html_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 이메일 발송 완료: {TO_EMAIL}")
        return True
    
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
        return False

# ━━━ 메인 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """메인 실행"""
    
    print("="*60)
    print("MLB 자동 리포트 생성 시작")
    print("="*60)
    print()
    
    # 1. predict.py 실행
    print("1️⃣ 예측 생성 중...")
    result = subprocess.run(
        ['python', 'predict.py', 'daily'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ predict.py 실행 실패")
        print(result.stderr)
        return
    
    print("✅ 예측 생성 완료\n")
    
    # 2. 베스트픽 분석
    print("2️⃣ 베스트픽 분석 중...")
    edge_picks, high_prob_picks = analyze_today_picks()
    
    if not edge_picks and not high_prob_picks:
        print("⚠️ 오늘 베스트픽이 없습니다.")
        return
    
    print(f"✅ Edge TOP: {len(edge_picks)}개")
    print(f"✅ 고승률 TOP: {len(high_prob_picks)}개\n")
    
    # 3. HTML 생성
    print("3️⃣ HTML 리포트 생성 중...")
    html = generate_html_report(edge_picks, high_prob_picks)
    print("✅ HTML 생성 완료\n")
    
    # 4. 이메일 발송
    print("4️⃣ 이메일 발송 중...")
    success = send_email(html, edge_picks or [])
    
    print()
    print("="*60)
    if success:
        print("🎉 완료!")
    else:
        print("⚠️ 일부 실패")
    print("="*60)

if __name__ == "__main__":
    main()

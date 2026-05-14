@echo off
REM ════════════════════════════════════════════════════════════
REM MLB 자동 이메일 리포트 (매일 오후 5시)
REM ════════════════════════════════════════════════════════════

cd /d C:\Users\soldesk\Documents\GitHub\Study\MLB

REM Flask 서버 시작
start "Flask Server" python server.py

REM 3초 대기
timeout /t 3 /nobreak

REM 리포트 생성 및 발송
python send_daily_report.py

REM 로그 저장
echo %date% %time% - Report sent >> daily_report.log

REM Flask 서버 종료 (선택)
REM taskkill /FI "WINDOWTITLE eq Flask Server" /F

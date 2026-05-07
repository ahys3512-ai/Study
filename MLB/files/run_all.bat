@echo off
REM ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REM MLB 승부예측 자동화 - 완전 통합 버전
REM 상대 전적 포함
REM ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo.
echo ================================================================
echo MLB 승부예측 자동화 시작
echo ================================================================
echo.

REM 1단계: 기본 예측 생성
echo [1/5] 기본 예측 생성 중...
python predict.py daily
if %errorlevel% neq 0 (
    echo ❌ 예측 생성 실패
    pause
    exit /b 1
)
echo ✅ 예측 생성 완료
echo.

REM 2단계: 상대 전적 분석
echo [2/5] 상대 전적 분석 중...
python analyze_matchups.py
if %errorlevel% neq 0 (
    echo ⚠️  상대 전적 분석 실패 (계속 진행)
)
echo ✅ 상대 전적 분석 완료
echo.

REM 2.5단계: 상대 전적 predictions.csv에 통합
echo [2.5/5] 상대 전적을 예측에 반영 중...
python merge_matchup_scores.py
if %errorlevel% neq 0 (
    echo ⚠️  통합 실패 (계속 진행)
)
echo ✅ 상대 전적 반영 완료
echo.

REM 3단계: 스크린샷 촬영 (선택)
set /p SCREENSHOT="스크린샷 촬영할까요? (y/n, 기본 y): "
if /i "%SCREENSHOT%"=="n" goto skip_screenshot

echo [3/5] 경기별 스크린샷 촬영 중...
python capture_game_matchups.py
if %errorlevel% neq 0 (
    echo ⚠️  스크린샷 실패 (계속 진행)
)
echo ✅ 스크린샷 완료
echo.

:skip_screenshot

REM 4단계: PPT 생성
echo [4/5] PPT 생성 중...
python auto_generate_ppt.py
if %errorlevel% neq 0 (
    echo ❌ PPT 생성 실패
    pause
    exit /b 1
)
echo ✅ PPT 생성 완료
echo.

REM 5단계: 결과 확인
echo [5/5] 생성된 파일 확인
echo.
if exist predictions.csv (
    echo ✓ predictions.csv
)
if exist matchup_scores.csv (
    echo ✓ matchup_scores.csv
)
if exist screenshots\matchups (
    echo ✓ screenshots\matchups\ 폴더
)
for %%f in (MLB_Daily_*.pptx) do (
    echo ✓ %%f
)

echo.
echo ================================================================
echo 완료! 이제 녹화를 시작하세요.
echo ================================================================
echo.

REM 자동으로 PPT 열기 (선택)
set /p OPEN_PPT="PPT 파일을 열까요? (y/n, 기본 n): "
if /i "%OPEN_PPT%"=="y" (
    for %%f in (MLB_Daily_*.pptx) do (
        start "" "%%f"
        goto end
    )
)

:end
pause

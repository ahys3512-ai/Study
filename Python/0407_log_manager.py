import datetime

# 팀 데이터 (Team Data)
team_results = [
    {"name": "Team Seoul", "score": 85, "status": "Win"},
    {"name": "Team Daejeon", "score": 78, "status": "Loss"}
]

def save_results_to_file(data, filename="results.txt"):
    """
    데이터를 파일에 저장하고 기록을 남깁니다.
    Saves data to a file and records the log.
    """
    try:
        # 'a' 모드는 기존 내용 뒤에 덧붙이는(Append) 방식입니다.
        with open(filename, "a", encoding="utf-8") as f:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"--- Log Entry: {current_time} ---\n")
            
            for team in data:
                line = f"[{team['name']}] Score: {team['score']} | Result: {team['status']}\n"
                f.write(line)
            f.write("-" * 30 + "\n")
            
        print(f"Successfully saved to {filename}")
    except Exception as e:
        print(f"Error occurred: {e}")

# 실행 (Execution)
save_results_to_file(team_results)
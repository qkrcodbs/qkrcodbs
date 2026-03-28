from flask import Flask, render_template, request, redirect, session
import json
import os
import datetime
import calendar

app = Flask(__name__)
app.secret_key = "1234"  # 🔥 세션 필수 (로그인 상태 유지)

# 파일 경로
DATA_FILE = "data/users.json"

# 파일 없으면 자동 생성
if not os.path.exists(DATA_FILE):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

# 유저 불러오기
def load_users():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 유저 저장
def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_tasks():
    with open("data/tasks.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 메인 페이지
@app.route("/")
def home():
    return render_template("index.html")

# 로그인
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users and users[username] == password:
            session["user"] = username   # 🔥 로그인 상태 저장
            return redirect("/")         # 🔥 메인으로 이동
        else:
            error = "아이디(로그인 전화번호, 로그인 전용 아이디) 또는 비밀번호가 잘못 되었습니다. 아이디와 비밀번호를 정확히 입력해 주세요."

    return render_template("login.html", error=error)


# 로그아웃
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

# 회원가입
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = load_users()

        if username in users:
            error = "이미 존재하는 아이디입니다."
        else:
            users[username] = password
            save_users(users)
            return redirect("/login")

    return render_template("signup.html", error=error)

#나의 캘린더

@app.route("/my_calendar")
def my_calendar():
    tasks = load_tasks()

    # 현재 연도, 월 가져오기 (쿼리스트링으로 월 변경 가능)
    year = int(request.args.get("year", datetime.datetime.today().year))
    month = int(request.args.get("month", datetime.datetime.today().month))

    # 달력 생성
    cal = calendar.Calendar(firstweekday=6)  # 일요일 시작
    month_days = cal.itermonthdays(year, month)

    # tasks 날짜 문자열을 datetime.date로 변환
    for t in tasks:
        t["date_obj"] = datetime.datetime.strptime(t["date"], "%Y-%m-%d").date()

    return render_template("my_calendar.html", tasks=tasks, year=year, month=month, month_days=list(month_days))


#수행 평가
@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    tasks = load_tasks()
    filtered_tasks = tasks.copy()

    grade = None
    class_num = None
    sort = None

    if request.method == "POST":
        grade = request.form.get("grade")
        class_num = request.form.get("class")
        sort = request.form.get("sort")

        # 🔍 필터링
        if grade and grade != "전체":
            filtered_tasks = [t for t in filtered_tasks if str(t["grade"]) == grade]

        if class_num and class_num != "전체":
            filtered_tasks = [t for t in filtered_tasks if str(t["class"]) == class_num]

    # 🔥 D-day 계산
    import datetime
    for t in filtered_tasks:
        deadline = datetime.datetime.strptime(t["date"], "%Y-%m-%d")
        today = datetime.datetime.today()
        t["d_day"] = (deadline - today).days

    # 🔥 정렬
    if sort == "deadline":
        filtered_tasks.sort(key=lambda x: x["d_day"])
    elif sort == "name":
        filtered_tasks.sort(key=lambda x: x["subject"])

    return render_template("tasks.html", tasks=filtered_tasks)

if __name__ == "__main__":
    app.run(debug=True)
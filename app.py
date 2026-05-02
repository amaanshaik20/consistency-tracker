from flask import Flask, request, redirect, url_for, render_template
from datetime import date, datetime, timedelta

import sqlite3

app = Flask(__name__)

DB_PATH = "day_tracker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            has_text_field BOOLEAN DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS completions (
            task_id INTEGER,
            date TEXT,
            done BOOLEAN DEFAULT 0,
            text_value TEXT,
            PRIMARY KEY (task_id, date),
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

def get_tasks_for_date(selected_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT t.id, t.name, t.has_text_field, COALESCE(c.done, 0) as done, c.text_value FROM tasks t LEFT JOIN completions c ON t.id = c.task_id AND c.date = ?", (selected_date,))
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, has_text_field FROM tasks ORDER BY name")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/add-task", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        task_name = request.form["task_name"]
        has_text_field = request.form.get("has_text_field") == "on"
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO tasks (name, has_text_field) VALUES (?, ?)", (task_name, has_text_field))
            conn.commit()
        except:
            # duplicate, ignore
            pass
        cursor.close()
        conn.close()
        return redirect(url_for("add_task"))

    tasks = get_all_tasks()
    return render_template("add_task.html", tasks=tasks)


@app.route("/delete-task/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete from completions first (foreign key constraint)
    cursor.execute("DELETE FROM completions WHERE task_id = ?", (task_id,))
    # Then delete the task
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("add_task"))


@app.route("/check-tasks", methods=["GET", "POST"])
def check_tasks():
    today = date.today()
    max_past_date = today - timedelta(days=5)

    selected_day_str = request.args.get("day", str(today))
    selected_day = datetime.strptime(selected_day_str, "%Y-%m-%d").date()

    if request.method == "POST":
        # Only allow saving for editable dates (not future and not too far in the past)
        if selected_day <= today and selected_day >= max_past_date:
            checked_task_ids = request.form.getlist("done_tasks")
            conn = get_db_connection()
            cursor = conn.cursor()
            # First, set all to false for the date
            cursor.execute("DELETE FROM completions WHERE date = ?", (selected_day_str,))
            # Then insert done ones with text values
            for task_id in checked_task_ids:
                text_value = request.form.get(f"text_{task_id}", "")
                cursor.execute("INSERT INTO completions (task_id, date, done, text_value) VALUES (?, ?, 1, ?)", (task_id, selected_day_str, text_value))
            conn.commit()
            cursor.close()
            conn.close()

    tasks = get_tasks_for_date(selected_day_str)

    selected_date_obj = datetime.strptime(selected_day_str, "%Y-%m-%d")

    prev_day_obj = selected_date_obj - timedelta(days=1)
    next_day_obj = selected_date_obj + timedelta(days=1)

    prev_day = prev_day_obj.strftime("%Y-%m-%d")
    next_day = next_day_obj.strftime("%Y-%m-%d")

    # Determine if checkboxes should be disabled
    is_future = selected_day > today
    is_too_old = selected_day < max_past_date
    can_edit = not is_future and not is_too_old

    return render_template(
        "check_tasks.html",
        selected_date=selected_day_str,
        tasks=tasks,
        prev_day=prev_day,
        next_day=next_day,
        can_edit=can_edit,
        is_future=is_future,
        is_too_old=is_too_old
    )


@app.route("/stats")
def stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    total_tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    total_completions = cursor.execute("SELECT COUNT(*) FROM completions").fetchone()[0]

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    completed_today = cursor.execute(
        "SELECT COUNT(*) FROM completions WHERE date = ?",
        (today_str,)
    ).fetchone()[0]

    last7_start = (today - timedelta(days=6)).strftime("%Y-%m-%d")
    last7_rows = cursor.execute(
        "SELECT date, COUNT(*) as completed FROM completions WHERE date >= ? GROUP BY date ORDER BY date DESC",
        (last7_start,)
    ).fetchall()

    last7 = []
    for day in last7_rows:
        completed = day[1]
        percent = int((completed / total_tasks) * 100) if total_tasks else 0
        last7.append({
            "date": day[0],
            "percent": percent,
            "completed": completed,
        })

    days_tracked = cursor.execute(
        "SELECT COUNT(DISTINCT date) FROM completions"
    ).fetchone()[0]

    streak_rows = cursor.execute(
        "SELECT date FROM completions GROUP BY date HAVING COUNT(*) = ? ORDER BY date",
        (total_tasks,)
    ).fetchall()
    cursor.close()
    conn.close()

    completed_dates = [datetime.strptime(row[0], "%Y-%m-%d").date() for row in streak_rows] if total_tasks else []
    completed_set = set(completed_dates)

    current_streak = 0
    day_cursor = today
    while day_cursor in completed_set:
        current_streak += 1
        day_cursor -= timedelta(days=1)

    best_streak = 0
    if completed_dates:
        completed_dates.sort()
        streak = 1
        prev_date = completed_dates[0]
        best_streak = 1
        for current_date in completed_dates[1:]:
            if current_date == prev_date + timedelta(days=1):
                streak += 1
            else:
                streak = 1
            best_streak = max(best_streak, streak)
            prev_date = current_date

    completion_rate_today = int((completed_today / total_tasks) * 100) if total_tasks else 0

    return render_template(
        "stats.html",
        total_tasks=total_tasks,
        completed_today=completed_today,
        completion_rate_today=completion_rate_today,
        current_streak=current_streak,
        best_streak=best_streak,
        last7=last7,
        total_completions=total_completions,
        days_tracked=days_tracked,
    )


if __name__ == "__main__":
    app.run(debug=True)

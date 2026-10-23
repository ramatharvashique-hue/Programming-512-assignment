"""database.py - All SQLite work: tables, users, resources, bookings, reports."""
import sqlite3
import hashlib
from datetime import datetime, timedelta
from rules import CAMPUS_RULES, check_booking_rules

DB_NAME = "campus.db"

# Sample resources added the first time the program runs
SAMPLE_RESOURCES = {
    "Durban": [("DBN-LAB1", "Computer Lab 1"), ("DBN-PROJ1", "Projector 1"),
               ("DBN-SEM1", "Seminar Room 1")],
    "Johannesburg": [("JHB-LAB1", "Computer Lab 1"), ("JHB-PROJ1", "Projector 1"),
                     ("JHB-SEM1", "Seminar Room 1")],
    "Cape Town": [("CPT-LAB1", "Computer Lab 1"), ("CPT-PROJ1", "Projector 1"),
                  ("CPT-SEM1", "Seminar Room 1")],
}


def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def setup_database():
    """Create the tables and add starting data if the database is new."""
    conn = connect()
    conn.execute("""CREATE TABLE IF NOT EXISTS campuses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        campus_id INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        campus_id INTEGER NOT NULL,
        active INTEGER DEFAULT 1)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_id INTEGER NOT NULL,
        lecturer_id INTEGER NOT NULL,
        campus_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        start_hour INTEGER NOT NULL,
        duration INTEGER NOT NULL,
        status TEXT DEFAULT 'Active')""")

    # Campuses come from the rules dictionary
    for name in CAMPUS_RULES:
        conn.execute("INSERT OR IGNORE INTO campuses (name) VALUES (?)", (name,))
    conn.commit()

    # Starting users and resources (only if none exist yet)
    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        for c in conn.execute("SELECT * FROM campuses").fetchall():
            admin = "admin_" + c["name"].lower().replace(" ", "_")
            conn.execute("INSERT INTO users (username, password, role, campus_id) "
                         "VALUES (?, ?, 'Campus Administrator', ?)",
                         (admin, hash_password("admin123"), c["id"]))
            for code, name in SAMPLE_RESOURCES.get(c["name"], []):
                conn.execute("INSERT INTO resources (code, name, campus_id) "
                             "VALUES (?, ?, ?)", (code, name, c["id"]))
        conn.execute("INSERT INTO users (username, password, role) "
                     "VALUES ('operator', ?, 'System Operator')",
                     (hash_password("operator123"),))
        conn.commit()
    conn.close()


# ---------------- Users ----------------
def register_lecturer(username, password):
    if len(username) < 3 or len(password) < 4:
        return False, "Username needs 3+ characters and password 4+ characters."
    conn = connect()
    try:
        conn.execute("INSERT INTO users (username, password, role) "
                     "VALUES (?, ?, 'Lecturer')", (username, hash_password(password)))
        conn.commit()
        return True, "Account created. You can now log in."
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    finally:
        conn.close()


def login(username, password):
    conn = connect()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username, hash_password(password))).fetchone()
    conn.close()
    return row


# ---------------- Campuses and resources ----------------
def get_campuses():
    conn = connect()
    rows = conn.execute("SELECT * FROM campuses ORDER BY name").fetchall()
    conn.close()
    return rows


def get_resources(campus_id):
    conn = connect()
    rows = conn.execute("SELECT * FROM resources WHERE campus_id=? AND active=1 "
                        "ORDER BY code", (campus_id,)).fetchall()
    conn.close()
    return rows


def add_resource(code, name, campus_id):
    code = code.strip().upper()
    name = name.strip()
    if code == "" or name == "":
        return False, "Please enter both a code and a name."
    conn = connect()
    # A set of all existing codes makes duplicate detection easy
    existing = set()
    for r in conn.execute("SELECT code FROM resources"):
        existing.add(r["code"])
    if code in existing:
        conn.close()
        return False, f"Resource code {code} already exists."
    conn.execute("INSERT INTO resources (code, name, campus_id) VALUES (?, ?, ?)",
                 (code, name, campus_id))
    conn.commit()
    conn.close()
    return True, "Resource added."


def update_resource(resource_id, new_name):
    if new_name.strip() == "":
        return False, "Please enter a name."
    conn = connect()
    conn.execute("UPDATE resources SET name=? WHERE id=?", (new_name.strip(), resource_id))
    conn.commit()
    conn.close()
    return True, "Resource updated."


def remove_resource(resource_id):
    """Resources are hidden (active=0) so old booking records still make sense."""
    conn = connect()
    conn.execute("UPDATE resources SET active=0 WHERE id=?", (resource_id,))
    conn.execute("UPDATE bookings SET status='Cancelled' WHERE resource_id=? "
                 "AND status='Active'", (resource_id,))
    conn.commit()
    conn.close()
    return True, "Resource removed (its bookings were cancelled)."


# ---------------- Bookings ----------------
def start_time(date_text, hour):
    return datetime.strptime(date_text, "%Y-%m-%d").replace(hour=hour)


def is_available(resource_id, date_text, start, duration):
    """True if no active booking overlaps the requested time."""
    conn = connect()
    clash = conn.execute(
        "SELECT 1 FROM bookings WHERE resource_id=? AND date=? AND status='Active' "
        "AND start_hour < ? AND (start_hour + duration) > ?",
        (resource_id, date_text, start + duration, start)).fetchone()
    conn.close()
    return clash is None


def create_booking(resource_id, lecturer_id, campus_id, campus_name,
                   date_text, start, duration):
    try:
        begin = start_time(date_text, start)
    except ValueError:
        return False, "Date must be in the format YYYY-MM-DD."
    date_text = begin.strftime("%Y-%m-%d")
    if begin < datetime.now():
        return False, "You cannot book a time in the past."

    # Count this lecturer's upcoming bookings on this campus
    conn = connect()
    rows = conn.execute("SELECT date, start_hour, duration FROM bookings "
                        "WHERE lecturer_id=? AND campus_id=? AND status='Active'",
                        (lecturer_id, campus_id)).fetchall()
    conn.close()
    active = 0
    for r in rows:
        end = start_time(r["date"], r["start_hour"]) + timedelta(hours=r["duration"])
        if end > datetime.now():
            active += 1

    error = check_booking_rules(campus_name, start, duration, active)
    if error:
        return False, error
    if not is_available(resource_id, date_text, start, duration):
        return False, "That resource is already booked for the chosen time."

    conn = connect()
    conn.execute("INSERT INTO bookings (resource_id, lecturer_id, campus_id, date, "
                 "start_hour, duration) VALUES (?, ?, ?, ?, ?, ?)",
                 (resource_id, lecturer_id, campus_id, date_text, start, duration))
    conn.commit()
    conn.close()
    return True, "Booking created successfully."


def booking_label(row):
    """Return Cancelled, Past or Active for a booking row."""
    if row["status"] == "Cancelled":
        return "Cancelled"
    end = start_time(row["date"], row["start_hour"]) + timedelta(hours=row["duration"])
    return "Past" if end <= datetime.now() else "Active"


def get_bookings(lecturer_id=None, campus_id=None):
    """Return bookings as a list of tuples, filtered by lecturer and/or campus."""
    sql = ("SELECT b.*, r.name AS resource, u.username AS lecturer, c.name AS campus "
           "FROM bookings b JOIN resources r ON b.resource_id = r.id "
           "JOIN users u ON b.lecturer_id = u.id "
           "JOIN campuses c ON b.campus_id = c.id WHERE 1=1")
    params = []
    if lecturer_id is not None:
        sql += " AND b.lecturer_id=?"
        params.append(lecturer_id)
    if campus_id is not None:
        sql += " AND b.campus_id=?"
        params.append(campus_id)
    sql += " ORDER BY b.date DESC, b.start_hour DESC"
    conn = connect()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append((r["id"], r["campus"], r["resource"], r["lecturer"], r["date"],
                       f"{r['start_hour']:02d}:00", f"{r['duration']}h", booking_label(r)))
    return result


def cancel_booking(booking_id, lecturer_id):
    conn = connect()
    b = conn.execute("SELECT * FROM bookings WHERE id=? AND lecturer_id=?",
                     (booking_id, lecturer_id)).fetchone()
    if b is None:
        conn.close()
        return False, "Booking not found."
    if b["status"] == "Cancelled":
        conn.close()
        return False, "That booking is already cancelled."
    if start_time(b["date"], b["start_hour"]) <= datetime.now():
        conn.close()
        return False, "Only future bookings can be cancelled."
    conn.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (booking_id,))
    conn.commit()
    conn.close()
    return True, "Booking cancelled."


# ---------------- Reports ----------------
def campus_report(campus_id):
    """Total bookings, average duration and the most used resources."""
    conn = connect()
    total, avg = conn.execute(
        "SELECT COUNT(*), AVG(duration) FROM bookings "
        "WHERE campus_id=? AND status='Active'", (campus_id,)).fetchone()
    top = conn.execute(
        "SELECT r.name, COUNT(*) AS uses FROM bookings b "
        "JOIN resources r ON b.resource_id = r.id "
        "WHERE b.campus_id=? AND b.status='Active' "
        "GROUP BY r.id ORDER BY uses DESC LIMIT 3", (campus_id,)).fetchall()
    conn.close()
    if avg is None:
        avg = 0
    top_list = []
    for t in top:
        top_list.append((t["name"], t["uses"]))
    return {"total": total, "average": avg, "top": top_list}

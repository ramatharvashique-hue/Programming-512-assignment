SMART CAMPUS RESOURCE BOOKING SYSTEM (Programming 512)

HOW TO RUN
1. Install Python 3 (Tkinter and SQLite come with it).
2. Open this folder in a terminal and run:  python main.py
   The database file (campus.db) is created automatically on first run.

TEST LOGINS
  Lecturer:             there is no preset login, so create one first:
                        1. Type a username (3+ characters) and a password (4+ characters)
                           on the login screen
                        2. Click "Register as Lecturer" (a success message appears)
                        3. Click "Login" using the same username and password
  Campus Administrator: admin_durban / admin123
                        admin_johannesburg / admin123
                        admin_cape_town / admin123
  System Operator:      operator / operator123

FILES
  main.py      Starts the app
  login_screens.py, main_screen.py, lecturer_screens.py, bookings_screen.py,
  admin_screens.py, report_screens.py, helpers.py   Tkinter GUI screens
  models.py    User classes (inheritance, encapsulation)
  rules.py     Campus booking rules (add a new campus here)
  database.py  SQLite tables, bookings, reports

  GitHub Link
  https://github.com/ramatharvashique-hue/Programming-512-assignment.git

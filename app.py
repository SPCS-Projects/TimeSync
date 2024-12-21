from flask import Flask, request, render_template, redirect, url_for, send_file
import sqlite3
import csv
from hashlib import sha256
from datetime import datetime, timedelta

app = Flask(__name__)

database_loc = "./database/database.db"

# Initialize the database
def init_db():
    conn = sqlite3.connect(database_loc)
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS Employees (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        shift INTEGER NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS TimeLog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        check_in TEXT,
        check_out TEXT,
        date TEXT NOT NULL,
        absent BOOLEAN DEFAULT 0,
        incomplete BOOLEAN DEFAULT 0,
        FOREIGN KEY(employee_id) REFERENCES Employees(id)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Shifts (
        id INTEGER PRIMARY KEY,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Admin (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Helper to hash passwords
def hash_password(password):
    return sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('enter-id.html')

@app.route('/check', methods=['POST'])
def check_employee():
    employee_id = request.form.get('employeeId')
    if employee_id == "-1":
        return redirect(url_for('admin_login'))

    # Validate that the employee ID is numeric
    if not employee_id.isdigit():
        return render_template('error.html', message="Invalid Employee ID")

    # Convert to integer after passing validation
    employee_id = int(employee_id)

    conn = sqlite3.connect(database_loc)
    cursor = conn.cursor()

    # Verify employee exists
    cursor.execute('SELECT name FROM Employees WHERE id = ?', (employee_id,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return render_template('error.html', message="Employee not found")

    name = result[0]
    today = datetime.now().date()

    # Check for existing TimeLog entry for today
    cursor.execute('SELECT id, check_in, check_out FROM TimeLog WHERE employee_id = ? AND date = ?', (employee_id, today))
    log = cursor.fetchone()

    if not log:  # Check-in scenario
        cursor.execute('INSERT INTO TimeLog (employee_id, name, check_in, date) VALUES (?, ?, ?, ?)',
                       (employee_id, name, datetime.now(), today))
        conn.commit()
        conn.close()
        return render_template('checkin.html', name=name)

    else:  # Check-out scenario
        log_id, check_in, _ = log
        check_in_time = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S.%f')
        check_out_time = datetime.now()
        time_diff = check_out_time - check_in_time
        incomplete = not (timedelta(hours=8, minutes=50) <= time_diff <= timedelta(hours=9))

        cursor.execute('UPDATE TimeLog SET check_out = ?, incomplete = ? WHERE id = ?',
                       (check_out_time, incomplete, log_id))
        conn.commit()
        conn.close()
        return render_template('checkout.html', name=name)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin-login.html')

    username = request.form.get('username')
    password = request.form.get('password')
    hashed_password = hash_password(password)
    # print(hashed_password)

    conn = sqlite3.connect(database_loc)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM Admin WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    # print(result, " - ", result[0], " - ", hashed_password)
    if result and result[0] == hashed_password:
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('error.html', message="Invalid admin credentials")

@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin-dashboard.html')

@app.route('/manage_employees')
def manage_employees():
    return render_template('manage_employees.html')

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        shift = request.form['shift']
        conn = sqlite3.connect(database_loc)
        cur = conn.cursor()
        cur.execute("INSERT INTO Employees (name, shift) VALUES (?, ?)", (name, shift))
        conn.commit()
        conn.close()
        return redirect('/manage_employees')
    return render_template('add_employee.html')

@app.route('/edit_delete_employees')
def edit_delete_employees():
    conn = sqlite3.connect(database_loc)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Employees")
    employees = [{'id': row[0], 'name': row[1], 'shift': row[2]} for row in cur.fetchall()]
    return render_template('edit_delete_employees.html', employees=employees)

@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    conn = sqlite3.connect(database_loc)
    cur = conn.cursor()

    if request.method == 'GET':
        # Fetch employee details
        cur.execute("SELECT * FROM Employees WHERE id = ?", (employee_id,))
        employee = cur.fetchone()
        conn.close()
        if not employee:
            return render_template('error.html', message="Employee not found")
        return render_template('edit_employee.html', employee={'id': employee[0], 'name': employee[1], 'shift': employee[2]})

    # POST: Update employee details
    name = request.form['name']
    shift = request.form['shift']
    cur.execute("UPDATE Employees SET name = ?, shift = ? WHERE id = ?", (name, shift, employee_id))
    conn.commit()
    conn.close()
    return redirect('/edit_delete_employees')


@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    conn = sqlite3.connect(database_loc)
    cur = conn.cursor()
    cur.execute("DELETE FROM Employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()
    return redirect('/edit_delete_employees')

@app.route('/manage_shifts', methods=['GET', 'POST'])
def manage_shifts():
    return render_template('manage_shifts.html')

@app.route('/add_shift', methods=['GET', 'POST'])
def add_shift():
    if request.method == 'POST':
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        conn = sqlite3.connect(database_loc)
        cur = conn.cursor()
        cur.execute("INSERT INTO Shifts (start_time, end_time) VALUES (?, ?)", (start_time, end_time))
        conn.commit()
        conn.close()
        return redirect('/manage_shifts')
    return render_template('add_shift.html')


@app.route('/edit_delete_shifts')
def edit_delete_shifts():
    conn = sqlite3.connect(database_loc)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Shifts")
    shifts = [{'id': row[0], 'name': row[1], 'time': row[2]} for row in cur.fetchall()]
    return render_template('edit_delete_shifts.html', shifts=shifts)

@app.route('/edit_shift/<int:shift_id>', methods=['GET', 'POST'])
def edit_shift(shift_id):
    conn = sqlite3.connect(database_loc)
    cur = conn.cursor()

    if request.method == 'GET':
        cur.execute("SELECT * FROM Shifts WHERE id = ?", (shift_id,))
        shift = cur.fetchone()
        conn.close()
        if not shift:
            return render_template('error.html', message="Shift not found")
        return render_template('edit_shift.html', shift={'id': shift[0], 'start_time': shift[1], 'end_time': shift[2]})

    start_time = request.form['start_time']
    end_time = request.form['end_time']
    cur.execute("UPDATE Shifts SET start_time = ?, end_time = ? WHERE id = ?", (start_time, end_time, shift_id))
    conn.commit()
    conn.close()
    return redirect('/edit_delete_shifts')


@app.route('/delete_shift/<int:shift_id>', methods=['POST'])
def delete_shift(shift_id):
    conn = sqlite3.connect(database_loc)
    cur = conn.cursor()
    cur.execute("DELETE FROM Shifts WHERE id = ?", (shift_id,))
    conn.commit()
    conn.close()
    return redirect('/edit_delete_shifts')


@app.route('/export_logs', methods=['GET', 'POST'])
def export_logs():
    return render_template('export_logs.html')



# Export Logs
@app.route('/generate_csv', methods=['POST'])
def generate_csv():
    conn = sqlite3.connect(database_loc)
    cur = conn.cursor()
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    cur.execute("SELECT * FROM TimeLog WHERE date BETWEEN ? AND ?", (start_date, end_date))
    rows = cur.fetchall()

    file_path = "timelog_export.csv"
    with open(file_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["EntryID", "EmployeeID", "Name", "CheckIn", "CheckOut", "Date", "Absent", "Incomplete"])
        csvwriter.writerows(rows)

    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

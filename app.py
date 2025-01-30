from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        department = request.form['department']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO employees (first_name, last_name, email, phone, department)'
            'VALUES (%s, %s, %s, %s, %s)',
            (first_name, last_name, email, phone, department)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('view_employees'))
    return render_template('add_employee.html')

@app.route('/view')
def view_employees():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM employees;')
    employees = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('view_employees.html', employees=employees)

@app.route('/delete/<int:id>')
def delete_employee(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM employees WHERE id = %s', (id,))
    conn.commit()
    cur.execute('SELECT COUNT(*) FROM employees')
    count = cur.fetchone()[0]
    
    if count == 0:  
        cur.execute('ALTER SEQUENCE employees_id_seq RESTART WITH 1')
        conn.commit()
    cur.execute("UPDATE employees SET id = id - 1 WHERE id > %s", (id,))
    conn.commit()

    cur.execute("SELECT MAX(id) FROM employees")
    max_id = cur.fetchone()[0] or 0  

    cur.execute("ALTER SEQUENCE employees_id_seq RESTART WITH %s", (max_id + 1,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('view_employees'))


if __name__ == '__main__':
    app.run(debug=True)
import os
from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
from Encryption import Encryption

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')  # needed so session cookies are signed
crypto = Encryption()   # one instance for the whole app

def get_db_connection():
    conn = sqlite3.connect('contest.db')
    conn.row_factory = sqlite3.Row  # makes rows act like dictionaries
    return conn


# --- ROUTES ---

# home page - only reachable if logged in
@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # render home page based on session['security_level']
    return render_template('home.html', 
                           name=session['name'], 
                           sec_level=session['security_level'])

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user_input = request.form['username']
        pass_input = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        conn.close()

        # iterate users, decrypt, and check credentials
        user_found = None
        for u in users:
            try:
                dec_name = crypto.decrypt(u['name'])
                if dec_name == user_input:
                    dec_pass = crypto.decrypt(u['password'])
                    if dec_pass == pass_input:
                        user_found = u
                        break
            except:
                continue # skip if decryption fails
        
        if user_found:
            # save everything we need for the session
            session['logged_in'] = True
            session['user_id'] = user_found['user_id']
            session['name'] = user_input
            session['security_level'] = user_found['security_level']
            return redirect(url_for('home'))
        else:
            error = "invalid username and/or password!"

    return render_template('login.html', error=error)

# logout - clear the session
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# 1. Add New User Page (Level 3 only)
@app.route('/enternew')
def enternew():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session['security_level'] != 3:
        return render_template('404.html'), 404
    return render_template('enternew.html')

# 2. Add User Action
@app.route('/addrec', methods=['POST'])
def addrec():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session['security_level'] != 3: return render_template('404.html'), 404

    msg = ""
    error_list = []
    
    if request.method == 'POST':
        conn = None
        try:
            nm = request.form['Name']
            age = request.form['Age']
            phone = request.form['Phone']
            sec = request.form['Security']
            pwd = request.form['Password']

            # basic validation
            if not nm or not nm.strip(): error_list.append("You can not enter in an empty name")
            if not age.isdigit() or int(age) <= 0 or int(age) >= 121:
                error_list.append("The Age must be a whole number greater than 0 and less than 121.")
            if not phone or not phone.strip(): error_list.append("You can not enter in an empty phone number")
            if not sec.isdigit() or int(sec) < 1 or int(sec) > 3:
                error_list.append("The Security Level must be a numeric between 1 and 3.")
            if not pwd or not pwd.strip(): error_list.append("You can not enter in an empty pwd")

            if not error_list:
                conn = get_db_connection()
                cur = conn.cursor()
                
                # encrypt sensitive data before saving
                enc_nm = crypto.encrypt(nm)
                enc_phone = crypto.encrypt(phone)
                enc_pwd = crypto.encrypt(pwd)
                cur.execute("INSERT INTO users (name, age, phone, security_level, password) VALUES (?, ?, ?, ?, ?)", 
                            (enc_nm, int(age), enc_phone, int(sec), enc_pwd))
                conn.commit()
                msg = "Record successfully added"
            else:
                msg = "<br>".join(error_list)

        except Exception as e:
            if conn: conn.rollback()
            msg = "Error: " + str(e)
        finally:
            if conn: conn.close()
            return render_template("result.html", msg=msg)

# 3. List All Users Page (Level 2 and 3 only)
@app.route('/list')
def list_users():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session['security_level'] < 2:
        return render_template('404.html'), 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall() 
    conn.close()
    
    # decrypt data for display
    decrypted_rows = []
    for row in rows:
        r = dict(row)
        r['name'] = crypto.decrypt(r['name'])
        r['phone'] = crypto.decrypt(r['phone'])
        r['password'] = crypto.decrypt(r['password'])
        decrypted_rows.append(r)
    return render_template("list.html", rows=decrypted_rows)

# 4. List ALL Contest Results (Level 3 only)
@app.route('/contestResults')
def contest_results():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if session['security_level'] != 3:
        return render_template('404.html'), 404

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM entries")
    rows = cur.fetchall()
    conn.close()
    return render_template("contestResults.html", rows=rows)

# 5. Show Only Current User's Contest Results (All Levels)
@app.route('/myContestResults')
def my_contest_results():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()
    
    # filter by user ID
    cur.execute("SELECT * FROM entries WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return render_template("myContestResults.html", rows=rows)

# 6. Add New Entry Page (All Levels)
@app.route('/addEntry')
def add_entry_page():
    if not session.get('logged_in'): return redirect(url_for('login'))
    return render_template("addEntry.html")

# 7. Submit New Entry (Action)
@app.route('/submitEntry', methods=['POST'])
def submit_entry():
    if not session.get('logged_in'): return redirect(url_for('login'))
    
    msg = ""
    error_list = []
    
    try:
        item = request.form['Item']
        exc = request.form['Excellent']
        ok = request.form['Ok']
        bad = request.form['Bad']

        # validate the votes
        if not item or not item.strip(): error_list.append("The Name of Baking Item is required.")
        if not exc.isdigit() or int(exc) < 0: error_list.append("Num Excellent Votes must be integer >= 0")
        if not ok.isdigit() or int(ok) < 0: error_list.append("Num Ok Votes must be integer >= 0")
        if not bad.isdigit() or int(bad) < 0: error_list.append("Num Bad Votes must be integer >= 0")
        
        if not error_list:
            conn = get_db_connection()
            cur = conn.cursor()
            # insert using session['user_id']
            cur.execute("INSERT INTO entries (user_id, baking_item, excellent_votes, ok_votes, bad_votes) VALUES (?, ?, ?, ?, ?)",
                        (session['user_id'], item, int(exc), int(ok), int(bad)))
            conn.commit()
            conn.close()
            msg = "Record successfully added"
        else:
            msg = "<br>".join(error_list)
            
    except Exception as e:
        msg = "Error: " + str(e)
    return render_template("result.html", msg=msg)

if __name__ == '__main__':
    app.run(debug=True, port=5020)
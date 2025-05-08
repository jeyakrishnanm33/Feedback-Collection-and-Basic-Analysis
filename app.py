from flask import Flask, render_template, request, redirect, url_for
import oracledb

app = Flask(__name__)

connection = oracledb.connect(
    user="kannan",
    password="kannan44",
    dsn="localhost:1521/XEPDB1"
)
cursor = connection.cursor()

@app.route('/')
def home():
    cursor.execute("SELECT COUNT(*) FROM feedback_form")
    feedback_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT email) FROM feedback_form")
    user_count = cursor.fetchone()[0]

    return render_template('home.html', feedback_count=feedback_count, user_count=user_count)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        city = request.form['city']
        issue_on = request.form['issue_on']
        description = request.form['description']

        cursor.execute("""
            INSERT INTO feedback_form (name, email, city, issue_on, description)
            VALUES (:1, :2, :3, :4, :5)
        """, (name, email, city, issue_on, description))
        connection.commit()
        return redirect('/')
    return render_template('feedback_form.html')

@app.route('/submit_questions', methods=['POST'])
def submit_questions():
    # Get data from the form
    name = request.form['name']
    email = request.form['email']
    q1 = request.form['q1']
    q2 = request.form['q2']
    q3 = request.form['q3']

    # Insert the data into the database
    cursor.execute("""
        INSERT INTO questions_form (name, email, experience, issue_resolved, suggestions)
        VALUES (:1, :2, :3, :4, :5)
    """, (name, email, q1, q2, q3))
    connection.commit()

    # Redirect to the home page after form submission
    return redirect('/')


@app.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        question = request.form['q1']  # This corresponds to the 'question' column
        suggestion = request.form['q3']  # This corresponds to the 'suggestion' column

        cursor.execute("""
            INSERT INTO questions_form (name, email, question, suggestion)
            VALUES (:1, :2, :3, :4)
        """, (name, email, question, suggestion))
        connection.commit()
        return redirect('/')
    return render_template('questions_form.html')

@app.route('/admin')
def admin_dashboard():
    cursor.execute("SELECT COUNT(*) FROM feedback_form")
    total_feedbacks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT email) FROM feedback_form")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback_form WHERE LOWER(description) LIKE '%good%'")
    good_feedbacks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedback_form WHERE LOWER(description) LIKE '%bad%' OR LOWER(description) LIKE '%poor%'")
    bad_feedbacks = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM feedback_form ORDER BY id DESC FETCH FIRST 5 ROWS ONLY")
    recent_feedbacks = cursor.fetchall()

    return render_template(
        'admin.html',
        total_feedbacks=total_feedbacks,
        total_users=total_users,
        good_feedbacks=good_feedbacks,
        bad_feedbacks=bad_feedbacks,
        recent_feedbacks=recent_feedbacks
    )



@app.route('/manage')
def manage():
    cursor.execute("SELECT * FROM feedback_form ORDER BY id")
    feedbacks = cursor.fetchall()
    return render_template('manage.html', feedbacks=feedbacks)

@app.route('/delete_feedback/<int:id>')
def delete_feedback(id):
    cursor.execute("DELETE FROM feedback_form WHERE id = :1", (id,))
    connection.commit()
    return redirect(url_for('manage'))

@app.route('/update_feedback/<int:id>', methods=['GET', 'POST'])
def update_feedback(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        city = request.form['city']
        issue_on = request.form['issue_on']
        description = request.form['description']

        cursor.execute("""
            UPDATE feedback_form SET name=:1, email=:2, city=:3, issue_on=:4, description=:5
            WHERE id=:6
        """, (name, email, city, issue_on, description, id))
        connection.commit()
        return redirect(url_for('manage'))

    cursor.execute("SELECT * FROM feedback_form WHERE id = :1", (id,))
    data = cursor.fetchone()
    return render_template('update_form.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)

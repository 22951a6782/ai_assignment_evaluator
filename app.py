from flask import Flask, render_template, json,request, redirect, session, url_for
import mysql.connector
import pymysql
import datetime
from flask import Flask, request, session, redirect, render_template
from textblob import TextBlob
import nltk
import re
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Load Sentence-BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')


app = Flask(__name__)
app.secret_key = 'secret_key'  # Needed for session handling

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # Your MySQL password
        database='ai_assignment'
    )

@app.route('/')
def home():
    if 'user_id' in session:
        if session['user_type'] == 'student':
            return redirect(url_for('student_dashboard'))
        elif session['user_type'] == 'teacher':
            return redirect(url_for('teacher_dashboard'))
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password, user_type) VALUES (%s, %s, %s, %s)",
                           (name, email, password, user_type))
            conn.commit()
            return redirect('/login')
        except mysql.connector.IntegrityError:
            return "Email already registered."
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_type'] = user['user_type']
            return redirect('/dashboard')
        else:
            return "Invalid credentials"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if session['user_type'] == 'teacher':
        return redirect('/teacher/dashboard')
    else:
        return redirect('/student/dashboard')
@app.route('/student/dashboard')
def student_dashboard():
    if session.get('user_type') != 'student':
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all coding assignments
    cursor.execute("SELECT * FROM assignments ORDER BY created_at DESC")
    assignments = cursor.fetchall()

    # Fetch all theory assignments
    cursor.execute("SELECT * FROM theory_assignments ORDER BY created_at DESC")
    theory_assignments = cursor.fetchall()

    # Fetch all code submissions for this student
    cursor.execute("""
        SELECT s.assignment_id, s.code, s.grade, s.submitted_at
        FROM submissions s
        WHERE s.user_id = %s
        ORDER BY s.assignment_id, s.submitted_at DESC
    """, (session['user_id'],))
    all_submissions = cursor.fetchall()

    # Fetch all theory submissions for this student
    cursor.execute("""
        SELECT ts.theory_assignment_id, ts.answers, ts.submitted_at
        FROM theory_submissions ts
        WHERE ts.user_id = %s
        ORDER BY ts.theory_assignment_id, ts.submitted_at DESC
    """, (session['user_id'],))
    all_theory_submissions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student_dashboard.html', 
                           assignments=assignments, 
                           theory_assignments=theory_assignments,
                           all_submissions=all_submissions,
                           all_theory_submissions=all_theory_submissions)



@app.route('/teacher/dashboard')
def teacher_dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch coding assignments
    cursor.execute("SELECT * FROM assignments ORDER BY created_at DESC")
    assignments = cursor.fetchall()

    # Fetch theory assignments
    cursor.execute("SELECT * FROM theory_assignments ORDER BY created_at DESC")
    theory_assignments = cursor.fetchall()

    # Fetch coding submissions
    cursor.execute("""
        SELECT s1.id, u.name AS student_name, a.title AS assignment_title,
               s1.code, s1.submitted_at, s1.grade
        FROM submissions s1
        JOIN users u ON s1.user_id = u.id
        JOIN assignments a ON s1.assignment_id = a.id
        LEFT JOIN submissions s2 
               ON s1.user_id = s2.user_id 
               AND s1.assignment_id = s2.assignment_id 
               AND s1.grade < s2.grade
        WHERE s2.id IS NULL
        ORDER BY s1.submitted_at DESC
    """)
    submissions = cursor.fetchall()

    cursor.close()
    conn.close()

    # Now pass theory_assignments too
    return render_template('teacher_dashboard.html', 
                           assignments=assignments, 
                           submissions=submissions, 
                           theory_assignments=theory_assignments)



@app.route('/create_assignment', methods=['GET', 'POST'])
def create_assignment():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        testcases = request.form['testcases']

        try:
            testcases_json = json.loads(testcases)  # Validate JSON
        except:
            return "Invalid JSON format in testcases."

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assignments (title, description, testcases_json, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (title, description, json.dumps(testcases_json)))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/teacher/dashboard')
    return render_template('create_assignment.html')


@app.route('/submit/<int:assignment_id>', methods=['POST'])
def submit_assignment(assignment_id):
    if session.get('user_type') != 'student':
        return redirect('/login')

    # Use the correct form field name here:
    user_code = request.form['code']  # instead of 'submission'

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch testcases for this assignment.
    cursor.execute("SELECT testcases_json FROM assignments WHERE id = %s", (assignment_id,))
    assignment = cursor.fetchone()
    testcases = json.loads(assignment['testcases_json'])
    
    # Evaluate code using the helper function:
    grade = evaluate_code(user_code, testcases)
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO submissions (user_id, assignment_id, code, grade) VALUES (%s, %s, %s, %s)",
                   (session['user_id'], assignment_id, user_code, grade))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect('/student/dashboard')



def evaluate_code(user_code, testcases):
    try:
        local_vars = {}
        exec(user_code, {}, local_vars)
        user_func = local_vars.get('solution')
        if not callable(user_func):
            return 0

        passed = 0
        for case in testcases:
            result = user_func(*case['input'])
            if result == case['output']:
                passed += 1

        return int((passed / len(testcases)) * 100)
    except Exception as e:
        return 0
    

@app.route('/view_submissions/<int:assignment_id>')
def view_submissions(assignment_id):
    if session.get('user_type') != 'teacher':
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get assignment details (optional)
    cursor.execute("SELECT * FROM assignments WHERE id = %s", (assignment_id,))
    assignment = cursor.fetchone()

    # Get all submissions for the assignment
    cursor.execute("""
        SELECT s.id, u.name as student_name, s.code, s.grade, s.submitted_at
        FROM submissions s
        JOIN users u ON s.user_id = u.id
        WHERE s.assignment_id = %s
        ORDER BY s.submitted_at DESC
    """, (assignment_id,))
    submissions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_submissions.html', assignment=assignment, submissions=submissions)
@app.route('/view_theory_submissions/<int:assignment_id>')
def view_theory_submissions(assignment_id):
    if session.get('user_type') != 'teacher':
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get theory assignment details
    cursor.execute("SELECT * FROM theory_assignments WHERE id = %s", (assignment_id,))
    assignment = cursor.fetchone()

    if assignment is None:
        print(f"No assignment found for ID {assignment_id}")  # Debugging line
    else:
        print(f"Assignment fetched: {assignment}")  # Debugging line

    # Get all submissions for the theory assignment
    cursor.execute("""
        SELECT s.id, u.name as student_name, s.answers, s.grade, s.submitted_at
        FROM theory_submissions s
        JOIN users u ON s.user_id = u.id
        WHERE s.theory_assignment_id = %s
        ORDER BY s.submitted_at DESC
    """, (assignment_id,))
    submissions = cursor.fetchall()

    if not submissions:
        print(f"No submissions found for assignment ID {assignment_id}")  # Debugging line
    else:
        print(f"Submissions fetched: {submissions}")  # Debugging line

    cursor.close()
    conn.close()

    return render_template('view_theory_submissions.html', assignment=assignment, submissions=submissions)



@app.route('/delete_assignment/<int:assignment_id>', methods=['POST'])
def delete_assignment(assignment_id):
    if session.get('user_type') != 'teacher':
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete related submissions first to avoid foreign key constraint error
    cursor.execute("DELETE FROM submissions WHERE assignment_id = %s", (assignment_id,))
    cursor.execute("DELETE FROM assignments WHERE id = %s", (assignment_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect('/teacher/dashboard')

@app.route('/delete_theory_assignment/<int:assignment_id>', methods=['POST'])
def delete_theory_assignment(assignment_id):
    if session.get('user_type') != 'teacher':
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete related submissions first to avoid foreign key constraint error
    cursor.execute("DELETE FROM theory_submissions WHERE theory_assignment_id = %s", (assignment_id,))
    cursor.execute("DELETE FROM theory_assignments WHERE id = %s", (assignment_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect('/teacher/dashboard')


@app.route('/create_theory_assignment', methods=['POST'])
def create_theory_assignment():
    title = request.form['title']
    questions = request.form['questions']
    answers = request.form['answers']

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO theory_assignments (title, questions, answers)
        VALUES (%s, %s, %s)
    """, (title, questions, answers))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('teacher_dashboard'))


# Get synonyms using WordNet
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower())
    return synonyms

# Clean and lemmatize text
def clean_and_lemmatize(text):
    text = text.strip().lower()
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]
    return words

@app.route('/submit_theory/<int:theory_assignment_id>', methods=['GET', 'POST'])
def submit_theory(theory_assignment_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM theory_assignments WHERE id = %s", (theory_assignment_id,))
        theory_assignment = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('theory_submission.html', theory_assignment=theory_assignment)

    else:
        answers = request.form['answers']
        cursor.execute("SELECT answers FROM theory_assignments WHERE id = %s", (theory_assignment_id,))
        correct_answers = cursor.fetchone()['answers']

        student_answers = answers.strip().split('\n')
        correct_answers_list = correct_answers.strip().split('\n')

        correct_count = 0
        total_questions = len(correct_answers_list)

        for i in range(total_questions):
            if i < len(student_answers):
                student_ans = student_answers[i]
                teacher_ans = correct_answers_list[i]

                # Cosine similarity debugging
                student_embedding = model.encode(student_ans)
                teacher_embedding = model.encode(teacher_ans)
                similarity_score = cosine_similarity([student_embedding], [teacher_embedding])[0][0]

                print(f"Question {i + 1} | Teacher's Answer: {teacher_ans}")
                print(f"Question {i + 1} | Student's Answer: {student_ans}")
                print(f"Similarity Score: {similarity_score:.4f}")

                # Keyword + Synonym coverage debugging
                student_keywords = clean_and_lemmatize(student_ans)
                teacher_keywords = clean_and_lemmatize(teacher_ans)

                keyword_match_count = 0
                for t_word in teacher_keywords:
                    t_synonyms = get_synonyms(t_word)
                    if t_word in student_keywords or any(s in student_keywords for s in t_synonyms):
                        keyword_match_count += 1

                coverage = keyword_match_count / len(teacher_keywords) if teacher_keywords else 0
                print(f"Coverage for Question {i + 1}: {coverage:.4f}")

                # Final smart decision (adjusted for logging)
                if similarity_score >= 0.7:
                    correct_count += 1
                elif similarity_score >= 0.6 and coverage >= 0.6:  # Adjust the fallback threshold
                    correct_count += 1

        grade = (correct_count / total_questions) * 100
        print(f"Final Grade: {grade:.2f}%")

        cursor.execute("""
            INSERT INTO theory_submissions (user_id, theory_assignment_id, answers, grade)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], theory_assignment_id, answers, grade))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/student/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
